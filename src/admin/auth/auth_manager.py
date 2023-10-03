from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import jwt

from config import settings


class AuthManager:
    encoding: str = "UTF-8"
    secret_key: str = settings.secret_key
    jwt_algorithm: str = settings.jwt_algorithm
    access_token_exp: int = settings.access_token_exp

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.encoding)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding), hashed_password.encode(self.encoding)
        )

    def create_access_token(self, login_name: str, nickname: str) -> str:
        current_time = datetime.now()
        return jwt.encode(
            {
                "sub": [login_name, nickname],
                "iat": current_time,
                "exp": current_time + timedelta(minutes=self.access_token_exp),
                "jti": str(uuid4()),
            },
            self.secret_key,
            algorithm=self.jwt_algorithm,
        )
