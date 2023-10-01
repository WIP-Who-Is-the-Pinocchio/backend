from fastapi import APIRouter, Depends
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from src.database.repositories.admin_repository import AdminRepository
from src.admin.auth.auth_manager import AuthManager
from src.admin.auth.auth_service import create_admin
from src.admin.schema.signup_request import SignUpRequest

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
):
    return await create_admin(**locals())
