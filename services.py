from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import UsersEntity, UserRecordEntity, ZoneListEntity
from pydantic import BaseModel


class BaseService:
    model = None

    def __init__(self, model):
        self.model = model

    def get_by_id(self, db: Session, id: int):
        # 修正：is_deleted 可能是 NULL 或 "0"，只要不是 "1" 就算未删除
        return db.query(self.model).filter(
            and_(
                self.model.id == id,
                or_(self.model.is_deleted == None, self.model.is_deleted == "0")
            )
        ).first()

    def delete_logic(self, db: Session, ids: list):
        if not ids:
            db.commit()
            return True
        affected_rows = db.query(self.model).filter(
            and_(
                self.model.id.in_(ids),
                or_(self.model.is_deleted == None, self.model.is_deleted == "0")
            )
        ).update({"is_deleted": "1"}, synchronize_session=False)
        db.commit()
        return affected_rows > 0

    def update_by_id(self, db: Session, entity_update: BaseModel, update_id: int, update_username: str):
        db_obj = db.query(self.model).filter(
            and_(
                self.model.id == update_id,
                self.model.username == update_username,
                or_(self.model.is_deleted == None, self.model.is_deleted == "0")
            )
        ).first()

        if db_obj:
            for key, value in entity_update.dict(exclude={'id', 'username'}, exclude_unset=True).items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            return True
        return False

    def save(self, db: Session, entity_create: BaseModel):
        db_obj = self.model(**entity_create.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class UsersService(BaseService):
    def __init__(self):
        super().__init__(UsersEntity)

    def get_user_by_username(self, db: Session, username: str):
        # 修正：查询 is_deleted 为 NULL 或 "0" 的用户
        return db.query(self.model).filter(
            and_(
                self.model.username == username,
                or_(self.model.is_deleted == None, self.model.is_deleted == "0")
            )
        ).first()

    def save_user(self, db: Session, user_data: dict):
        username_to_check = user_data.get('username')
        if not username_to_check:
            return None

        # 修正：检查用户名是否已存在（is_deleted 为 NULL 或 "0"）
        existing_user_count = db.query(self.model).filter(
            and_(
                self.model.username == username_to_check,
                or_(self.model.is_deleted == None, self.model.is_deleted == "0")
            )
        ).count()

        if existing_user_count == 0:
            new_user = self.model(**user_data)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        return None


users_service = UsersService()
user_record_service = BaseService(UserRecordEntity)
zone_list_service = BaseService(ZoneListEntity)