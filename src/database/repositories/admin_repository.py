from fastapi import Depends
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import Admin


class AdminRepository:
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session

    def check_uniqueness(self, login_name: str, nickname: str) -> bool:
        select_query = select(Admin).where(
            or_(Admin.login_name == login_name, Admin.nickname == nickname)
        )
        search_result = self.session.scalar(select_query)

        return search_result is None

    def create_admin(self, admin: Admin) -> Admin:
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        return admin
