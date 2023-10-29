from fastapi import APIRouter, Depends, Path
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from admin.auth.auth_manager import AuthManager
from admin.politician.politician_service import PoliticianService
from admin.security import get_token
from repositories.admin_repository import AdminRepository
from schema.politician_request import SinglePoliticianRequest

router = APIRouter()


@router.post(
    "/{admin_id}",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {"description": "Created new politician data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회의원 데이터 개별 추가",
)
async def add_politician_handler(
    request: SinglePoliticianRequest,
    # admin_id: int = Path(..., description="작업하는 관리자 id"),
    admin_id: str = Depends(get_token),
    # auth_manager: AuthManager = Depends(),
    # admin_repository: AdminRepository = Depends(),
    politician_service: PoliticianService = Depends(),
):
    return await politician_service.create_new_politician_data(**locals())
