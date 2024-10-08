from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.sql import func
from src.db import Base

class YTList(Base):
    __tablename__ = "yt_list"
    id = Column(Integer, primary_key=True, index=True)
    list_name = Column(String, unique=False, index=True)
    channel_id = Column(String, unique=False, index=False)
    channel_name = Column(String, unique=False, index=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
