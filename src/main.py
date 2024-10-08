import json
from dotenv import load_dotenv
from types import SimpleNamespace
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from src.models.user import User
from src.models.yt import YTList
from src.db import Base, engine, get_db
from jose import JWTError
from src.interfaces import RegisterRequest,YTListRequest
from src.core.youtube import fetch_channels
from src.utils.redis import get_from_cache, save_to_cache
from src.utils.hash import get_password_hash, compare_hash
from src.utils.jwt import create_access_token, decode_token
import traceback

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# apply middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = token.split(" ")[1]  # Remove the "Bearer " part
    try:
        payload = decode_token(token=token)
        email: str = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(request.password)
    user = User(email=request.email, hashed_password=hashed_password)
    print("User = ", request.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"email": user.email}

@app.post("/login")
def login(request: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not compare_hash(source=request.password.encode("utf-8"), target=user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token_data = {"sub": user.email}
    token = create_access_token(token_data)
    
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return {"msg": "Login successful"}

@app.get("/protected")
def read_protected_data(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.email}"}

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"msg": "Logged out"}

@app.get("/fetchChannels")
def fc(q: str  = ""):
    return fetch_channels(q)

@app.post("/ytList")
async def ytlist(request: YTListRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): 
    ytList = YTList(
        list_name=request.name,
        channel_id=','.join([channel.id for channel in request.list]),
        channel_name=','.join([channel.name for channel in request.list]),
        created_at=func.now(),
        created_by=current_user.id,
        updated_at=func.now()
    )
    db.add(ytList)
    db.commit()
    try:
        for channel in request.list:
            await save_to_cache(channel.id, json.dumps(channel, default=lambda x: x.__dict__))
    except Exception:
        db.rollback()
        raise
    db.refresh(ytList) 
    return ytList.id


@app.get("/ytList")
async def ytlist(request: YTListRequest, db: Session = Depends(get_db)):
    query = db.query(YTList)
    if request.name:
        query = query.filter(YTList.list_name.like(f"%{request.name}%"))
    ytlist = query.all()
    try:
        for yt in ytlist:
            channel_ids = yt.channel_id.split(',')
            thumbnails = []
            for channel_id in channel_ids:
                channel_str = await get_from_cache(channel_id)
                if channel_str:
                    channel = json.loads(channel_str, object_hook=lambda d: SimpleNamespace(**d))
                if channel:
                    thumbnails.append(channel.thumbnail)
            yt.list_thumbnail = ','.join(thumbnails)
    except Exception:
        traceback.print_exc()
    return ytlist

def fc(q: str  = "", current_user: User = Depends(get_current_user)):
    print(f"Hello, {current_user.email}")
    return fetch_channels(q)

@app.get("/authcheck")
def user_auth_status(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.email}"}
