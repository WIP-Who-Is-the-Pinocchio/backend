import logging
from typing import List

from fastapi import APIRouter, Path, Depends, Query
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from admin.politician.politician_service import PoliticianService
from public.public_service import (
    get_public_constituency_data,
    get_public_politician_list,
)
from repositories.area_repository import AreaRepository
from repositories.politician_info_repository import PoliticianInfoRepository
from schema.politician_response import GetSinglePoliticianDataRes
from schema.public_response import (
    PublicConstituencyResSchema,
    PublicPoliticianListElementResSchema,
)

router = APIRouter()


logger = logging.getLogger("uvicorn")


@router.get(
    "/constituency/{region}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get region data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
    summary="지역구 데이터 조회",
)
def get_constituency_public_handler(
    region: str = Path(..., description="대분류 지역구(영문 소문자)"),
    area_repository: AreaRepository = Depends(),
) -> List[PublicConstituencyResSchema]:
    return get_public_constituency_data(region, area_repository)


@router.get(
    "/politician/list/{assembly_term}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get politician data list"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
    summary="국회의원 데이터 초기 전체 목록 조회",
)
async def get_politician_list_public_handler(
    assembly_term: int = Path(..., description="국회 회기"),
    sort_type: str = Query("desc", description="정렬 기준(desc, asc)"),
    page: int = Query(..., description="페이지네이션 0부터 시작"),
    size: int = Query(default=10),
    politician_info_repository: PoliticianInfoRepository = Depends(),
    area_repository: AreaRepository = Depends(),
) -> List[PublicPoliticianListElementResSchema]:
    return await get_public_politician_list(**locals())


@router.get(
    "/politician/single/{politician_id}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get single politician data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
    summary="국회의원 데이터 개별 조회",
)
async def get_single_politician_public_handler(
    politician_id: int = Path(..., description="의원 id"),
    politician_service: PoliticianService = Depends(),
) -> GetSinglePoliticianDataRes:
    return politician_service.get_politician_by_id(politician_id)
