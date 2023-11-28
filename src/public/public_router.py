import logging
from typing import List

from fastapi import APIRouter, Path, Depends
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from public.public_service import get_public_constituency_data
from repositories.area_repository import AreaRepository
from schema.public_response import PublicConstituencyResSchema

router = APIRouter()


logger = logging.getLogger("uvicorn")


@router.get(
    "/constituency/{assembly_term}/{region}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Get region data"},
        HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
    summary="국회 회기별 지역구 데이터 조회",
)
def get_constituency_public_handler(
    assembly_term: int = Path(..., description="국회 회기"),
    region: str = Path(..., description="대분류 지역구(영문 소문자)"),
    area_repository: AreaRepository = Depends(),
) -> List[PublicConstituencyResSchema]:
    return get_public_constituency_data(assembly_term, region, area_repository)
