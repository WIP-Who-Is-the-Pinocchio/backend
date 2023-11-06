from typing import List

from fastapi import APIRouter, Depends, Path
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
)

from admin.politician.politician_service import PoliticianService
from admin.security import get_token
from schema.politician_request import SinglePoliticianRequest
from schema.politician_response import (
    AddPoliticianDataRes,
    AddBulkPoliticianDataRes,
    GetSinglePoliticianDataRes,
    ConstituencyResSchema,
)

router = APIRouter()


@router.post(
    "",
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
) -> AddPoliticianDataRes:
    return await politician_service.create_new_politician_data(**locals())


@router.post(
    "/bulk",
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
) -> AddBulkPoliticianDataRes:
    return await politician_service.create_bulk_politician_data(**locals())


@router.get(
    "/{assembly_term}/{politician_id}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get single politician data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회의원 데이터 개별 조회",
)
async def get_single_politician_handler(
    admin_id: str = Depends(get_token),
    assembly_term: int = Path(..., description="국회 회기"),
    politician_id: int = Path(..., description="의원 id"),
    politician_service: PoliticianService = Depends(),
) -> GetSinglePoliticianDataRes:
    return politician_service.get_politician_by_id(assembly_term, politician_id)


@router.get(
    "/constituency/{assembly_term}/{region}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get single politician data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회 회기별 지역구 데이터 조회",
)
async def get_constituency_handler(
    admin_id: str = Depends(get_token),
    assembly_term: int = Path(..., description="국회 회기"),
    region: str = Path(..., description="대분류 지역구(영문 소문자)"),
    politician_service: PoliticianService = Depends(),
) -> List[ConstituencyResSchema]:
    return politician_service.get_constituency_data(assembly_term, region)
