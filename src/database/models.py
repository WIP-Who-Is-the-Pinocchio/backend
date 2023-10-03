from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    login_name = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    nickname = Column(String(256), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    def __repr__(self):
        return f"Admin(id={self.id}, login_name={self.login_name}, nickname={self.nickname})"

    @classmethod
    def create(cls, login_name: str, hashed_password: str, nickname: str) -> "Admin":
        return cls(login_name=login_name, password=hashed_password, nickname=nickname)
