import logging
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select, or_, insert
from sqlalchemy.orm import Session
from starlette.status import HTTP_409_CONFLICT

from database.connection import get_db
from database.models import Admin, AdminLog

logger = logging.getLogger("uvicorn")


class AdminRepository:
    admin_model = Admin
    admin_log_model = AdminLog

    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session

    def check_uniqueness(self, email: str, nickname: str) -> bool | None:
        select_query = select(self.admin_model).where(
            or_(self.admin_model.email == email, self.admin_model.nickname == nickname)
        )
        search_result = self.session.scalar(select_query)
        if search_result is None:
            return
        elif search_result.email == email:
            logger.info("Received duplicated email.")
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Email should be unique.",
            )
        elif search_result.nickname == nickname:
            logger.info("Received duplicated nickname.")
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Nickname should be unique.",
            )

    def save_admin_data(self, admin: Admin) -> Admin:
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        return admin

    def get_admin_data(self, **kwargs) -> Admin | None:
        field = list(kwargs.keys())[0]
        value = list(kwargs.values())[0]
        select_query = select(self.admin_model).where(getattr(Admin, field) == value)
        search_result = self.session.scalar(select_query)
        return search_result

    def check_jti_data(self, admin_id: int, uuid_jti: str) -> bool:
        admin_data = self.get_admin_data(id=admin_id)
        return True if admin_data.uuid_jti == uuid_jti else False

    def insert_admin_log_data(
        self,
        admin_id: int,
        action: str,
        politician_id: Optional[int] = None,
        detail: Optional[dict] = None,
    ):
        data = {
            "admin_id": admin_id,
            "politician_id": politician_id,
            "action": action,
            "detail": detail,
        }
        query = insert(self.admin_log_model).values(data)
        self.session.execute(query)

    def select_admin_log_data(self):
        select_query = (
            select(
                self.admin_model.nickname,
                self.admin_log_model.action,
                self.admin_log_model.politician_id,
                self.admin_log_model.created_at,
            )
            .select_from(self.admin_log_model)
            .join(
                self.admin_model,
                self.admin_model.id == self.admin_log_model.admin_id,
            )
            .order_by(self.admin_log_model.created_at.desc())
        )
        select_result = self.session.execute(select_query).all()
        return select_result
