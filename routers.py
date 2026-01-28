from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_  # 修复：添加这个导入
from database import get_db
from schemas import (
    R, UsersQueryParams, UserRecordQueryParams, ZoneListQueryParams,
    UsersCreate, UserRecordCreate, ZoneListCreate,
    UsersUpdate, UserRecordUpdate, ZoneListUpdate,
    UsersLogin
)
from services import users_service, user_record_service, zone_list_service
import json
from extract_net_carbon_emission import extract_net_carbon_emission
from typing import Any

router = APIRouter(prefix="/api")

# --- Users ---
@router.get("/users/query")
def detail_users(test: UsersQueryParams = Depends(), db: Session = Depends(get_db)):
    detail = users_service.get_by_id(db, test.id)
    if detail:
        detail_dict = {c.name: getattr(detail, c.name) for c in detail.__table__.columns}
        return R(code=200, success=True, data=detail_dict, msg="操作成功")
    else:
        return R(code=200, success=True, data=None, msg="暂无承载数据")

@router.post("/users/create")
def create_users(user: UsersCreate, db: Session = Depends(get_db)):
    saved_user = users_service.save_user(db, user.dict())
    success = saved_user is not None
    return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")

@router.post("/users/update")
def update_users(user: UsersUpdate, db: Session = Depends(get_db)):
    existing_query = db.query(users_service.model).filter(
        and_(
            users_service.model.id == user.id,
            users_service.model.username == user.username,
            users_service.model.is_deleted == "0"
        )
    )
    existing_count = existing_query.count()

    if existing_count > 0:
        success = users_service.update_by_id(db, user, user.id, user.username)
        return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")
    else:
        return R(code=300, success=False, data=None, msg="用户不存在")

@router.post("/users/remove")
async def remove_users(request: Request, db: Session = Depends(get_db)):
    json_data = await request.json()
    id_str = json_data.get("id", "")
    id_list = []
    if id_str:
        try:
            id_list = [int(x.strip()) for x in id_str.split(",") if x.strip().isdigit()]
        except ValueError:
            pass

    success = users_service.delete_logic(db, id_list)
    return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")

@router.post("/users/login")
def login_users(userentity: UsersLogin, db: Session = Depends(get_db)):
    username_from_request = userentity.username
    password_from_request = userentity.password

    user = users_service.get_user_by_username(db, username_from_request)

    result_map = {}
    if user:
        stored_password = user.password
        if password_from_request == stored_password:
            result_map["success"] = "登录成功"
        else:
            result_map["fail"] = "密码错误，请重试"
    else:
        result_map["fail"] = "请先注册"
    return result_map

# --- UserRecord ---
@router.get("/userrecord/query")
def detail_userrecord(test: UserRecordQueryParams = Depends(), db: Session = Depends(get_db)):
    detail = user_record_service.get_by_id(db, test.id)
    if detail:
        detail_dict = {c.name: getattr(detail, c.name) for c in detail.__table__.columns}
        return R(code=200, success=True, data=detail_dict, msg="操作成功")
    else:
        return R(code=200, success=True, data=None, msg="暂无承载数据")

@router.post("/userrecord/create")
def create_userrecord(user: UserRecordCreate, db: Session = Depends(get_db)):
    user_record_service.save(db, user)
    return R(code=200, success=True, data=None, msg="操作成功")

@router.post("/userrecord/update")
def update_userrecord(user: UserRecordUpdate, db: Session = Depends(get_db)):
    existing_query = db.query(user_record_service.model).filter(
        and_(
            user_record_service.model.id == user.id,
            user_record_service.model.username == user.username,
            user_record_service.model.is_deleted == "0"
        )
    )
    existing_count = existing_query.count()

    if existing_count > 0:
        success = user_record_service.update_by_id(db, user, user.id, user.username)
        return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")
    else:
        return R(code=300, success=False, data=None, msg="用户不存在")

@router.post("/userrecord/remove")
async def remove_userrecord(request: Request, db: Session = Depends(get_db)):
    json_data = await request.json()
    id_str = json_data.get("id", "")
    id_list = []
    if id_str:
        try:
            id_list = [int(x.strip()) for x in id_str.split(",") if x.strip().isdigit()]
        except ValueError:
            pass

    success = user_record_service.delete_logic(db, id_list)
    return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")

# --- ZoneList ---
@router.get("/zonelist/query")
def detail_zonelist(test: ZoneListQueryParams = Depends(), db: Session = Depends(get_db)):
    detail = zone_list_service.get_by_id(db, test.id)
    if detail:
        detail_dict = {c.name: getattr(detail, c.name) for c in detail.__table__.columns}
        return R(code=200, success=True, data=detail_dict, msg="操作成功")
    else:
        return R(code=200, success=True, data=None, msg="暂无承载数据")

@router.post("/zonelist/create")
def create_zonelist(user: ZoneListCreate, db: Session = Depends(get_db)):
    zone_list_service.save(db, user)
    return R(code=200, success=True, data=None, msg="操作成功")

@router.post("/zonelist/update")
def update_zonelist(user: ZoneListUpdate, db: Session = Depends(get_db)):
    existing_query = db.query(zone_list_service.model).filter(
        and_(
            zone_list_service.model.id == user.id,
            zone_list_service.model.username == user.username,
            zone_list_service.model.is_deleted == "0"
        )
    )
    existing_count = existing_query.count()

    if existing_count > 0:
        success = zone_list_service.update_by_id(db, user, user.id, user.username)
        return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")
    else:
        return R(code=300, success=False, data=None, msg="用户不存在")

@router.post("/zonelist/remove")
async def remove_zonelist(request: Request, db: Session = Depends(get_db)):
    json_data = await request.json()
    id_str = json_data.get("id", "")
    id_list = []
    if id_str:
        try:
            id_list = [int(x.strip()) for x in id_str.split(",") if x.strip().isdigit()]
        except ValueError:
            pass

    success = zone_list_service.delete_logic(db, id_list)
    return R(code=200, success=success, data=None, msg="操作成功" if success else "操作失败")

# --- 提取NCF ---
@router.post("/getNCF")
async def get_ncf(request: dict[str, Any]):
    location = request.get("location")
    if not location:
        return R(code=400, success=False, data=None, msg="缺少 location 参数")

    extractNCF = extract_net_carbon_emission()
    result = extractNCF.extract(location)  # ✅ 现在 extract 返回的是 dict/list，不是字符串

    # ✅ 统一处理：如果 result 是 dict 且含 "error"，则返回错误
    if isinstance(result, dict) and "error" in result:
        return R(code=400, success=False, data=None, msg=result["error"])

    return R(code=200, success=True, data=result, msg="操作成功")
