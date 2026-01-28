# schemas.py - 修正后的代码
from pydantic import BaseModel
from typing import Optional # 确保导入
from datetime import datetime

# --- 通用返回格式 R<T> ---
class R(BaseModel):
    code: int
    success: bool
    # ✅ 正确：data 字段的类型是 Optional[object] (即 object 或 None)，默认值是 None
    data: Optional[object] = None # 泛型T可以是任意对象
    msg: str

# --- 用于接收查询参数的模型 (对应Java中的Entity) ---
class UsersQueryParams(BaseModel):
    id: Optional[int] = None
    class Config:
        extra = 'allow' # 允许接收id之外的参数，但不验证

class UserRecordQueryParams(BaseModel):
    id: Optional[int] = None
    class Config:
        extra = 'allow'

class ZoneListQueryParams(BaseModel):
    id: Optional[int] = None
    class Config:
        extra = 'allow'

# --- 用于接收创建请求的模型 ---
class UsersCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    authority: Optional[str] = None

class UserRecordCreate(BaseModel):
    username: str
    activityType: Optional[str] = None
    activityValue: Optional[str] = None

class ZoneListCreate(BaseModel):
    username: str
    zonename: Optional[str] = None
    location: Optional[str] = None
    square: Optional[str] = None

# --- 用于接收更新请求的模型 ---
class UsersUpdate(BaseModel):
    id: int
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    authority: Optional[str] = None

class UserRecordUpdate(BaseModel):
    id: int
    username: str
    activityType: Optional[str] = None
    activityValue: Optional[str] = None

class ZoneListUpdate(BaseModel):
    id: int
    username: str
    zonename: Optional[str] = None
    location: Optional[str] = None
    square: Optional[str] = None

# --- 用于接收登录请求的模型 (复用Create，因为只需要username和password) ---
class UsersLogin(BaseModel):
    username: str
    password: str