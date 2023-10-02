import logging
from datetime import datetime

from fastapi import HTTPException
from starlette.status import (
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
)

from admin.schema.login_response import LoginResponse, LoginResponseData
from admin.schema.admin_info_response import AdminInfoResponse
from admin.schema.signup_response import SignUpResponse
from database.models import Admin


logger = logging.getLogger("uvicorn")


async def create_admin(**kwargs) -> SignUpResponse:
    new_account_data = kwargs["request"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]
    login_name, password, nickname = (
        new_account_data.login_name,
        new_account_data.password,
        new_account_data.nickname,
    )

    is_unique = admin_repository.check_uniqueness(login_name, nickname)
    if not is_unique:
        logger.info("Received duplicated value.")
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Both login_name and nickname should be unique.",
        )

    hashed_password: str = auth_manager.hash_password(password)
    new_admin: Admin = Admin.create(login_name, hashed_password, nickname)
    admin_created: Admin = admin_repository.create_admin(new_admin)
    logger.info(f"New admin account is created: {admin_created}")

    return SignUpResponse(data=AdminInfoResponse.model_validate(admin_created))


async def admin_login(**kwargs) -> LoginResponse:
    login_data = kwargs["request"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]
    login_name, plain_password = (
        login_data.login_name,
        login_data.password,
    )

    admin: Admin | None = admin_repository.get_admin(login_name)
    if not admin:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Login name not found."
        )

    password_verified: bool = auth_manager.verify_password(
        plain_password, admin.password
    )
    if not password_verified:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    access_token: str = auth_manager.create_access_token(
        admin.login_name, admin.nickname
    )

    logger.info(
        f"Admin login - ID: {admin.login_name}, Nickname: {admin.nickname}, Time: {datetime.now()}"
    )
    login_response_data = LoginResponseData(admin=admin, access_token=access_token)
    return LoginResponse(data=login_response_data)
