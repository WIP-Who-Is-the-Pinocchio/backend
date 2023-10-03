from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from admin.schema.login_request import LogInRequest
from admin.schema.login_response import LoginResponse
from admin.schema.signup_response import SignUpResponse
from database.repositories.admin_repository import AdminRepository
from admin.auth.auth_manager import AuthManager
from admin.auth.auth_service import create_admin, admin_login
from admin.schema.signup_request import SignUpRequest

router = APIRouter()


@router.post(
    "/signup",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {"description": "Created new admin account"},
        HTTP_400_BAD_REQUEST: {"description": "Password shortage"},
        HTTP_409_CONFLICT: {"description": "Duplicate value has been requested"},
    },
    summary="관리자 회원가입",
)
async def admin_signup_handler(
    request: SignUpRequest,
    auth_manager: AuthManager = Depends(),
    admin_repository: AdminRepository = Depends(),
) -> SignUpResponse:
    return await create_admin(**locals())


@router.post(
    "/login",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Login success", "model": LoginResponse},
        HTTP_401_UNAUTHORIZED: {"description": "Wrong password"},
        HTTP_404_NOT_FOUND: {"description": "Login name not found"},
    },
    summary="관리자 로그인",
)
async def admin_login_handler(
    request: LogInRequest,
    auth_manager: AuthManager = Depends(),
    admin_repository: AdminRepository = Depends(),
):
    return await admin_login(**locals())
