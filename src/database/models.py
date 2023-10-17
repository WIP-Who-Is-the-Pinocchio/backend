from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    nickname = Column(String(256), unique=True, nullable=False)
    hashed_refresh_token = Column(String(256), nullable=True)
    uuid_jti = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    def __repr__(self):
        return f"Admin(id={self.id}, email={self.email}, nickname={self.nickname})"

    @classmethod
    def create_admin_object(
        cls, email: str, hashed_password: str, nickname: str
    ) -> "Admin":
        return cls(email=email, password=hashed_password, nickname=nickname)

    def update_token(self, hashed_refresh_token: str, uuid_jti: str):
        self.hashed_refresh_token = hashed_refresh_token
        self.uuid_jti = uuid_jti
        return self
