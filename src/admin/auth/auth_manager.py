import json
import logging
from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError
from starlette.status import HTTP_401_UNAUTHORIZED

from schema.token_response import TokenDecodeResponse
from config import settings


logger = logging.getLogger("uvicorn")


class AuthManager:
    encoding: str = "UTF-8"
    jwt_algorithm: str = settings.jwt_algorithm
    access_token_secret_key: str = settings.access_token_secret_key
    refresh_token_secret_key: str = settings.refresh_token_secret_key
    access_token_exp: int = settings.access_token_exp
    refresh_token_exp: int = settings.refresh_token_exp

    def hash_text(self, plain_text: str) -> str:
        hashed_text: bytes = bcrypt.hashpw(
            plain_text.encode(self.encoding), salt=bcrypt.gensalt()
        )
        return hashed_text.decode(self.encoding)

    def verify_text(self, plain_text: str, hashed_text: str) -> bool:
        return bcrypt.checkpw(
            plain_text.encode(self.encoding), hashed_text.encode(self.encoding)
        )

    def create_access_token(
        self,
        admin_id: int,
        nickname: str,
        uuid_jti: str,
    ) -> str:
        current_time = datetime.now()
        return jwt.encode(
            {
                "sub": json.dumps([admin_id, nickname]),
                "iat": current_time,
                "exp": current_time + timedelta(minutes=self.access_token_exp),
                "jti": uuid_jti,
            },
            self.access_token_secret_key,
            algorithm=self.jwt_algorithm,
        )

    def create_refresh_token(
        self,
        admin_id: int,
        nickname: str,
        uuid_jti: str,
    ) -> str:
        current_time = datetime.now()
        return jwt.encode(
            {
                "sub": json.dumps([admin_id, nickname]),
                "iat": current_time,
                "exp": current_time + timedelta(minutes=self.refresh_token_exp),
                "jti": uuid_jti,
            },
            self.refresh_token_secret_key,
            algorithm=self.jwt_algorithm,
        )

    def decode_token(self, access_token: str = None, refresh_token: str = None):
        secret_key = (
            self.access_token_secret_key
            if access_token
            else self.refresh_token_secret_key
        )
        token = access_token if access_token else refresh_token

        try:
            payload: dict = jwt.decode(
                token, secret_key, algorithms=[self.jwt_algorithm]
            )
            exp = payload["exp"]
            if exp < datetime.now().timestamp():
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Expired token.",
                )
            sub = json.loads(payload["sub"])
            sub_data = {
                "admin_id": sub[0],
                "nickname": sub[1],
                "uuid_jti": payload["jti"],
            }
            return TokenDecodeResponse(**sub_data)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Expired token.",
            )
        except Exception as e:
            logger.info(e)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )
