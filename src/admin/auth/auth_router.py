from fastapi import APIRouter, Depends, Path, Query, Body
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from admin.auth.smtp_manager import SmtpManager
from schema.admin_info_response import NicknameUniquenessResponse
from schema.login_request import LogInRequest
from schema.login_response import LoginResponse
from schema.auth_num_response import SendAuthNumResponse, VerifyAuthNumResponse
from schema.signup_response import SignUpResponse
from schema.token_response import RefreshTokensResponse, RefreshTokensRequest
from admin.security import get_token
from repositories.admin_repository import AdminRepository
from admin.auth.auth_manager import AuthManager
from admin.auth.auth_service import (
    create_admin,
    admin_login,
    refresh_access_token,
    send_auth_number_email,
    verify_email_auth_number,
    check_nickname_uniqueness,
)
from schema.signup_request import SignUpRequest

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
        HTTP_404_NOT_FOUND: {"description": "Email not found"},
    },
    summary="관리자 로그인",
)
async def admin_login_handler(
    request: LogInRequest,
    auth_manager: AuthManager = Depends(),
    admin_repository: AdminRepository = Depends(),
    smtp_manager: SmtpManager = Depends(),
):
    return await admin_login(**locals())


@router.post(
    "/refresh/{admin_id}",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {"description": "Generated new access token"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized refresh token"},
        HTTP_404_NOT_FOUND: {"description": "Admin not found"},
    },
    summary="Access token 재발급",
)
async def refresh_handler(
    admin_id: int = Path(..., description="admin id"),
    auth_manager: AuthManager = Depends(),
    admin_repository: AdminRepository = Depends(),
    smtp_manager: SmtpManager = Depends(),
    body: RefreshTokensRequest = Body(...),
) -> RefreshTokensResponse:
    return await refresh_access_token(**locals())


@router.post(
    "/email/authorization/{email}",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {
            "description": "Send email with auth number and saved in-memory data successfully"
        },
        HTTP_400_BAD_REQUEST: {
            "description": "Cannot send authorization email to existing admin"
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Redis error occurred"},
    },
    summary="인증번호 이메일 발송",
)
async def send_signup_email_handler(
    email: str = Path(..., description="가입 대기 이메일"),
    smtp_manager: SmtpManager = Depends(),
    admin_repository: AdminRepository = Depends(),
) -> SendAuthNumResponse:
    return await send_auth_number_email(**locals())


@router.get(
    "/email/verification",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Passed email verification with auth number"},
        HTTP_400_BAD_REQUEST: {"description": "Wrong auth number"},
        HTTP_404_NOT_FOUND: {"description": "No auth number with the requested email"},
        HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Redis error occurred"},
    },
    summary="이메일 인증번호 검증",
)
async def email_authorization_handler(
    email: str = Query(..., description="이메일"),
    auth_number: int = Query(..., description="검증 번호"),
    smtp_manager: SmtpManager = Depends(),
) -> VerifyAuthNumResponse:
    return await verify_email_auth_number(**locals())


@router.get(
    "/nickname/{nickname}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Nickname unique check result"},
        HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Database error occurred"},
    },
    summary="닉네임 중복체크",
)
async def nickname_unique_check_handler(
    nickname: str = Path(..., description="중복 확인 대상 닉네임"),
    admin_repository: AdminRepository = Depends(),
) -> NicknameUniquenessResponse:
    return await check_nickname_uniqueness(**locals())
