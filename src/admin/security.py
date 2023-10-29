import json
import logging
from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, ExpiredSignatureError
from starlette.status import HTTP_401_UNAUTHORIZED

from config import settings

logger = logging.getLogger("uvicorn")


def get_token(
    authorization: HTTPAuthorizationCredentials
    | None = Depends(HTTPBearer(auto_error=False)),
) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No token.",
        )

    access_token = authorization.credentials

    try:
        payload: dict = jwt.decode(
            access_token,
            settings.access_token_secret_key,
            algorithms=[settings.jwt_algorithm],
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
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Expired token.",
        )
    except Exception as e:
        logger.info(e)
        print("??")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token.{str(e)}",
        )

    return sub_data["admin_id"]
