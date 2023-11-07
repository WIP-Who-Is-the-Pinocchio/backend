from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
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
    GetPoliticianElementOfListRes,
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
        HTTP_201_CREATED: {"description": "Created new multiple politician data"},
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
    "/single/{assembly_term}/{politician_id}",
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
        HTTP_200_OK: {"description": "Get region data"},
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


@router.get(
    "/list/{assembly_term}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get politician data list"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회의원 데이터 목록 조회",
)
async def get_politician_list_handler(
    admin_id: str = Depends(get_token),
    assembly_term: int = Path(..., description="국회 회기"),
    politician_service: PoliticianService = Depends(),
) -> List[GetPoliticianElementOfListRes]:
    return politician_service.get_politician_list(assembly_term)


@router.get(
    "/search/{assembly_term}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get politician search data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
    summary="국회의원 데이터 조건별 검색 조회",
)
async def get_politician_list_handler(
    admin_id: str = Depends(get_token),
    assembly_term: int = Path(..., description="국회 회기"),
    name: Optional[str] = Query(None, description="의원 이름"),
    party: Optional[str] = Query(None, description="소속 정당"),
    jurisdiction: Optional[str] = Query(None, description="관할 지역구"),
    politician_service: PoliticianService = Depends(),
) -> List[GetPoliticianElementOfListRes] | str:
    return politician_service.get_politician_search_data(
        assembly_term, name=name, party=party, jurisdiction=jurisdiction
    )
