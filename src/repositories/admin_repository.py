import logging

from fastapi import Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from starlette.status import HTTP_409_CONFLICT

from database.connection import get_db
from database.models import Admin


logger = logging.getLogger("uvicorn")


class AdminRepository:
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session

    def check_uniqueness(self, email: str, nickname: str) -> bool | None:
        select_query = select(Admin).where(
            or_(Admin.email == email, Admin.nickname == nickname)
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
        select_query = select(Admin).where(getattr(Admin, field) == value)
        search_result = self.session.scalar(select_query)
        return search_result

    def check_jti_data(self, admin_id: int, uuid_jti: str) -> bool:
        admin_data = self.get_admin_data(id=admin_id)
        return True if admin_data.uuid_jti == uuid_jti else False
