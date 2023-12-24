import json
import logging
from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, ExpiredSignatureError
from starlette.status import HTTP_401_UNAUTHORIZED

from config import settings
from repositories.admin_repository import AdminRepository

logger = logging.getLogger("uvicorn")


def get_auth_info_from_token(
    authorization: HTTPAuthorizationCredentials
    | None = Depends(HTTPBearer(auto_error=False)),
    admin_repository: AdminRepository = Depends(),
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

        admin_id = sub_data["admin_id"]
        uuid_jti = sub_data["uuid_jti"]
        current_auth_validation = admin_repository.check_jti_data(admin_id, uuid_jti)
        if not current_auth_validation:
            logger.info(f"Abnormal access with admin {admin_id}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token for now.",
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Expired token.",
        )

    return admin_id
