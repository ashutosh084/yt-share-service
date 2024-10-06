# interfaces.py
from pydantic import BaseModel
from typing import List

class RegisterRequest(BaseModel):
    email: str
    password: str
    
class channel(BaseModel):
    id: str
    name: str = None
    url: str  = None
    thumbnail: str = None
    
class YTListRequest(BaseModel):
    name: str = None
    list: List[channel] = None