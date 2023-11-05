from typing import List

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from admin.politician.politician_service import PoliticianService
from admin.security import get_token
from schema.politician_request import SinglePoliticianRequest
from schema.politician_response import PoliticianRes, BulkPoliticianRes

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
    admin_id: str = Depends(get_token),
    politician_service: PoliticianService = Depends(),
) -> PoliticianRes:
    return await politician_service.create_new_politician_data(**locals())


@router.post(
    "/bulk/{admin_id}",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_201_CREATED: {"description": "Created new politician data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회의원 데이터 대량 추가(엑셀 등록용)",
)
async def add_politician_bulk_handler(
    request: List[SinglePoliticianRequest],
    admin_id: str = Depends(get_token),
    politician_service: PoliticianService = Depends(),
) -> BulkPoliticianRes:
    return await politician_service.create_bulk_politician_data(**locals())
