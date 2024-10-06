# interfaces.py
from pydantic import BaseModel
from typing import List

class RegisterRequest(BaseModel):
    email: str
    password: str
    
class channel(BaseModel):
    id: str
    name: str
    url: str
    thumbnail: str
    
class YTListRequest(BaseModel):
    name: str
    list: List[channel]
    