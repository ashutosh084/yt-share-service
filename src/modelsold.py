# models.py
from sqlalchemy import Column, Integer, String, create_engine, DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "sqlite:///yt.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class YTList(Base):
    __tablename__ = "yt_list"
    id = Column(Integer, primary_key=True, index=True)
    list_name = Column(String, unique=False, index=True)
    channel_id = Column(String, unique=False, index=False)
    channel_name = Column(String, unique=False, index=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))

# User -> list -> 5 channel -> redis

# 500 job
# url share
# redis/server expire

# channel_id = comma separated
# redis (yt-api: channel_id)


# redis -> channels -> sets channel id and other metadata

# if expire