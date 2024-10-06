# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Base, User, SessionLocal, engine,YTList
from jose import JWTError, jwt
from interfaces import RegisterRequest,YTListRequest
import bcrypt
from fetch_channels.main import fetch_channels
import aioredis
from cache_helper import get_from_cache, save_to_cache

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
Base.metadata.create_all(bind=engine)

app = FastAPI()
redis = aioredis.from_url("redis://localhost")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = token.split(" ")[1]  # Remove the "Bearer " part
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"email": user.email}

@app.post("/login")
def login(request: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not bcrypt.checkpw(request.password.encode("utf-8"), user.hashed_password):
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
def ytlist(request: YTListRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): 
    ytList = YTList(
        list_name=request.name,
        channel_id=','.join([channel.id for channel in request.list]),
        channel_name=','.join([channel.name for channel in request.list]),
        created_at=func.now(),
        created_by=current_user.id,
        updated_at=func.now()
    )
    db.add(ytList)
    try:
        db.commit()
        for channel in request.list:
            save_to_cache(channel.id, channel)
    except Exception:
        db.rollback()
        raise
    db.refresh(ytList) 
    return ytList.id


@app.get("/ytList")
def ytlist(request: YTListRequest, db: Session = Depends(get_db)):
    query = db.query(YTList)
    if request.name:
        query = query.filter(YTList.list_name == request.name)
    ytlist = query.all()
    for yt in ytlist:
        channel_ids = yt.channel_id.split(',')
        thumbnails = []
        for channel_id in channel_ids:
            channel = get_from_cache(channel_id)
            if channel:
                thumbnails.append(channel.thumbnail)
        yt.channel_thumbnail = ','.join(thumbnails)
