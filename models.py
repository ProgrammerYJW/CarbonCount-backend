from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UsersEntity(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phonenumber = Column(String(255), nullable=True)
    createTime = Column(DateTime, nullable=True)  # 修正：允许NULL
    is_deleted = Column(String(1), default=None, nullable=True)  # 修正：允许NULL，初始为None
    authority = Column(String(255), nullable=True)

class UserRecordEntity(Base):
    __tablename__ = 'UserRecord'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    activityType = Column(String(255), nullable=True)
    activityValue = Column(String(255), nullable=True)
    createTime = Column(DateTime, nullable=True)  # 修正：允许NULL
    is_deleted = Column(String(1), default=None, nullable=True)  # 修正：允许NULL

class ZoneListEntity(Base):
    __tablename__ = 'ZoneList'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    zonename = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    square = Column(String(255), nullable=True)  # 注意：不是 countNumber！
    createTime = Column(DateTime, nullable=True)  # 修正：允许NULL
    is_deleted = Column(String(1), default=None, nullable=True)  # 修正：允许NULL