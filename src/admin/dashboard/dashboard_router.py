from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from admin.dashboard.dashboard_service import get_admin_log
from admin.security import get_auth_info_from_token
from repositories.admin_repository import AdminRepository
from repositories.politician_info_repository import PoliticianInfoRepository

router = APIRouter()


@router.get(
    "/admin-log",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Admin action log list"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
    summary="관리자 활동 로그 조회",
    description="최신순으로 목록 응답. 액션 종류: bulk_create(대량 등록), create(등록), update(수정), delete(삭제)",
)
async def admin_action_log_handler(
    admin_id: str = Depends(get_auth_info_from_token),
    admin_repository: AdminRepository = Depends(),
    politician_info_repository: PoliticianInfoRepository = Depends(),
):
    return await get_admin_log(**locals())
