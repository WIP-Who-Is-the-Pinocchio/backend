import logging
import random
from datetime import datetime
from uuid import uuid4

import redis
from fastapi import HTTPException
from redis import RedisError
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
)

from admin.schema.login_response import (
    LoginResponse,
    LoginResponseData,
)
from admin.schema.admin_info_response import (
    AdminInfoResponse,
    NicknameUniquenessResponse,
)
from admin.schema.auth_num_response import SendAuthNumResponse, VerifyAuthNumResponse
from admin.schema.signup_response import SignUpResponse
from admin.schema.token_response import (
    RefreshTokensResponse,
    Tokens,
    TokenDecodeResponse,
)
from config import settings
from database.models import Admin


logger = logging.getLogger("uvicorn")


REDIS_CONFIG = settings.redis_settings
redis_client = redis.Redis(
    host=REDIS_CONFIG.redis_host,
    port=REDIS_CONFIG.redis_port,
    encoding="UTF-8",
    decode_responses=True,
)


async def create_admin(**kwargs) -> SignUpResponse:
    new_account_data = kwargs["request"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]
    email, password, nickname = (
        new_account_data.email,
        new_account_data.password,
        new_account_data.nickname,
    )

    admin_repository.check_uniqueness(email, nickname)

    hashed_password: str = auth_manager.hash_text(password)
    new_admin: Admin = Admin.create_admin_object(email, hashed_password, nickname)
    admin_created: Admin = admin_repository.save_admin_data(new_admin)
    logger.info(f"New admin account is created: {admin_created}")

    return SignUpResponse(data=AdminInfoResponse.model_validate(admin_created))


async def admin_login(**kwargs) -> LoginResponse:
    login_data = kwargs["request"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]
    email, plain_password = (
        login_data.email,
        login_data.password,
    )

    admin: Admin | None = admin_repository.get_admin_data(email=email)
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
        f"Admin login - Email: {admin.email}, Nickname: {admin.nickname}, Time: {datetime.now()}"
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
        f"Refreshed tokens - Email: {admin.email}, Nickname: {admin.nickname}, Time: {datetime.now()}"
    )
    token_data = Tokens(access_token=access_token, refresh_token=refresh_token)
    return RefreshTokensResponse(data=token_data)


async def send_auth_number_email(**kwargs) -> SendAuthNumResponse:
    email = kwargs["email"]
    smtp_manager = kwargs["smtp_manager"]

    auth_number = random.randint(111111, 999999)
    smtp_manager.send_auth_num(email, auth_number)

    auth_number_data = get_auth_number(email)
    if auth_number_data is not None:
        delete_auth_number(email)
    add_auth_number(email, auth_number)

    return SendAuthNumResponse(email=email)


def add_auth_number(email: str, auth_number: int):
    try:
        redis_client.set(name=f"auth_num_{email}", value=auth_number, ex=180)
    except RedisError as e:
        logger.error(f"RedisError: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with redis insert"
        )


def get_auth_number(email: str) -> int | None:
    try:
        return redis_client.get(f"auth_num_{email}")
    except RedisError as e:
        logger.error(f"RedisError: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with redis search"
        )


def delete_auth_number(email: str):
    try:
        redis_client.delete(f"auth_num_{email}")
    except RedisError as e:
        logger.error(f"RedisError: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with redis delete"
        )


async def verify_email_auth_number(**kwargs) -> VerifyAuthNumResponse:
    email = kwargs["email"]
    auth_number = kwargs["auth_number"]

    auth_number_data = int(get_auth_number(email))
    if auth_number_data is None:
        logger.info(f"{email} auth number not found.")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No auth data with {email}"
        )
    elif auth_number != auth_number_data:
        logger.info(f"{email} auth number unmatched.")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Wrong auth number"
        )

    delete_auth_number(email)
    return VerifyAuthNumResponse()


async def check_nickname_uniqueness(**kwargs) -> NicknameUniquenessResponse:
    nickname = kwargs["nickname"]
    admin_repository = kwargs["admin_repository"]

    search_result = admin_repository.get_admin_data(nickname=nickname)
    if search_result:
        return NicknameUniquenessResponse(detail="Nickname already exists.")
    return NicknameUniquenessResponse(detail="Available nickname.")
