import logging
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from starlette.status import (
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
)

from admin.schema.login_response import (
    LoginResponse,
    LoginResponseData,
)
from admin.schema.admin_info_response import AdminInfoResponse
from admin.schema.signup_response import SignUpResponse
from admin.schema.token_response import (
    RefreshTokensResponse,
    Tokens,
    TokenDecodeResponse,
)
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

    hashed_password: str = auth_manager.hash_text(password)
    new_admin: Admin = Admin.create_admin_object(login_name, hashed_password, nickname)
    admin_created: Admin = admin_repository.save_admin_data(new_admin)
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

    admin: Admin | None = admin_repository.get_admin_data(login_name=login_name)
    if not admin:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Login name not found."
        )

    password_verified: bool = auth_manager.verify_text(plain_password, admin.password)
    if not password_verified:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    uuid_jti = str(uuid4())
    access_token: str = auth_manager.create_access_token(
        admin.id, admin.nickname, uuid_jti
    )
    refresh_token: str = auth_manager.create_refresh_token(
        admin.id, admin.nickname, uuid_jti
    )

    hashed_refresh_token: str = auth_manager.hash_text(refresh_token)
    admin.update_token(hashed_refresh_token, uuid_jti)
    admin_repository.save_admin_data(admin)

    logger.info(
        f"Admin login - ID: {admin.login_name}, Nickname: {admin.nickname}, Time: {datetime.now()}"
    )
    login_response_data = LoginResponseData(
        admin=admin, access_token=access_token, refresh_token=refresh_token
    )
    return LoginResponse(data=login_response_data)


async def refresh_access_token(**kwargs) -> RefreshTokensResponse:
    admin_id = kwargs["admin_id"]
    refresh_token = kwargs["token"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]

    admin: Admin | None = admin_repository.get_admin_data(id=admin_id)
    if not admin:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Admin not found.")

    refresh_token_verified: bool = auth_manager.verify_text(
        refresh_token, admin.hashed_refresh_token
    )
    if not refresh_token_verified:
        logger.info("Refresh token verify fail")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
        )

    payload_data: TokenDecodeResponse = auth_manager.decode_token(
        refresh_token=refresh_token
    )
    if payload_data.admin_id != admin_id or payload_data.uuid_jti != admin.uuid_jti:
        logger.info("Unmatched admin_id or uuid_jti")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
        )

    uuid_jti = str(uuid4())
    access_token: str = auth_manager.create_access_token(
        admin.id, admin.nickname, uuid_jti
    )
    refresh_token: str = auth_manager.create_refresh_token(
        admin.id, admin.nickname, uuid_jti
    )

    hashed_refresh_token: str = auth_manager.hash_text(refresh_token)
    admin.update_token(hashed_refresh_token, uuid_jti)
    admin_repository.save_admin_data(admin)

    logger.info(
        f"Refreshed tokens - ID: {admin.login_name}, Nickname: {admin.nickname}, Time: {datetime.now()}"
    )
    token_data = Tokens(access_token=access_token, refresh_token=refresh_token)
    return RefreshTokensResponse(data=token_data)
