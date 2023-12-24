from typing import List

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from admin.dashboard.dashboard_service import get_admin_log, get_integrity_error_data
from admin.security import get_auth_info_from_token
from repositories.admin_repository import AdminRepository
from repositories.area_repository import AreaRepository
from repositories.politician_info_repository import PoliticianInfoRepository
from schema.dashboard_response import AdminLogRes, IntegrityErrorRes

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
) -> List[AdminLogRes]:
    return await get_admin_log(**locals())


@router.get(
    "/integrity-error",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Data integrity error list"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
    summary="국회의원 지역구 데이터 중복 조회",
)
async def integrity_error_notification_handler(
    admin_id: str = Depends(get_auth_info_from_token),
    politician_info_repository: PoliticianInfoRepository = Depends(),
    area_repository: AreaRepository = Depends(),
) -> IntegrityErrorRes:
    return await get_integrity_error_data(**locals())
