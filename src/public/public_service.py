import logging
from functools import lru_cache
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST

from common.enums import RegionType
from database.connection import engine
from database.models import Region, Constituency
from repositories.area_repository import AreaRepository
from schema.politician_response import (
    JurisdictionResSchema,
    GetPoliticianElementOfListRes,
)
from schema.public_response import (
    PublicConstituencyResSchema,
    PublicPoliticianListElementResSchema,
)

logger = logging.getLogger("uvicorn")


@lru_cache()
def get_constituency_data_from_db(region_name: str):
    region_id = next(
        (region.value[0] for region in RegionType if region.value[1] == region_name),
        None,
    )

    with engine.connect() as connection:
        query = (
            select(
                Region.region,
                Constituency.district,
                Constituency.section,
            )
            .select_from(Constituency)
            .filter_by(region_id=region_id)
            .join(
                Region,
                Region.id == Constituency.region_id,
            )
        )
        constituency_obj_list = connection.execute(query).all()
        constituency_list = [
            PublicConstituencyResSchema(
                region=data[0], district=data[1], section=data[2]
            )
            for data in constituency_obj_list
        ]
        return constituency_list


def get_public_constituency_data(
    region: str, area_repository: AreaRepository
) -> List[PublicConstituencyResSchema]:
    region_name = RegionType[region.upper()].value[1]

    cached_data = get_constituency_data_from_db(region_name)
    logger.info(
        f"public constituency_data {get_constituency_data_from_db.cache_info()}"
    )
    if cached_data is not None:
        return cached_data
    logger.info(f"public constituency_data cache none")

    updated_data = area_repository.select_constituency_data_by_region(region_name)
    constituency_list = [
        PublicConstituencyResSchema(region=data[0], district=data[1], section=data[2])
        for data in updated_data
    ]

    return constituency_list


async def get_public_politician_list(**kwargs):
    assembly_term = kwargs["assembly_term"]
    sort_type = kwargs["sort_type"]
    page = kwargs["page"]
    size = kwargs["size"]
    politician_info_repo = kwargs["politician_info_repository"]
    area_repo = kwargs["area_repository"]

    offset = page * size
    politician_list = politician_info_repo.get_politician_list_data_for_admin(
        assembly_term, offset, size
    )
    return_res = []
    for politician in politician_list:
        jurisdiction_data = area_repo.select_jurisdiction_data_by_politician_id(
            politician[0].id
        )
        jurisdiction_list = [
            JurisdictionResSchema(
                id=data[0], region=data[1], district=data[2], section=data[3]
            )
            for data in jurisdiction_data
        ]
        politician_res = PublicPoliticianListElementResSchema.model_validate(
            politician[0]
        )

        completed_promise_count = politician[0].completed_promise_count
        total_promise_count = politician[0].completed_promise_count

        if total_promise_count:
            politician_res.promise_execution_rate = (
                completed_promise_count / total_promise_count
            ) * 100
        politician_res.constituency = jurisdiction_list
        return_res.append(politician_res)

    is_reverse = True if sort_type == "desc" else False
    sorted_res = sorted(
        return_res,
        key=lambda x: x.promise_execution_rate
        if x.promise_execution_rate is not None
        else float("-inf"),
        reverse=is_reverse,
    )
    return sorted_res


async def get_public_politician_list_by_keyword(
    **kwargs,
) -> List[PublicPoliticianListElementResSchema]:
    assembly_term = (kwargs["assembly_term"],)
    name = kwargs["name"]
    party = kwargs["party"]
    region = kwargs["region"]
    page = kwargs["page"]
    size = kwargs["size"]
    offset = page * size
    politician_info_repo = kwargs["politician_info_repository"]
    area_repo = kwargs["area_repository"]

    return_res = []
    if name or party:
        politician_list = politician_info_repo.get_politician_search_data_for_admin(
            offset=offset,
            size=size,
            assembly_term=assembly_term,
            name=name,
            party=party,
        )

        for politician in politician_list:
            jurisdiction_data = area_repo.select_jurisdiction_data_by_politician_id(
                politician[0].id
            )
            jurisdiction_list = [
                JurisdictionResSchema(
                    id=data[0], region=data[1], district=data[2], section=data[3]
                )
                for data in jurisdiction_data
            ]
            politician_res = PublicPoliticianListElementResSchema.model_validate(
                politician[0]
            )

            completed_promise_count = politician[0].completed_promise_count
            total_promise_count = politician[0].completed_promise_count

            if total_promise_count:
                politician_res.promise_execution_rate = (
                    completed_promise_count / total_promise_count
                ) * 100
            politician_res.constituency = jurisdiction_list
            return_res.append(politician_res)
    else:
        region_searched_keyword_replacements = {
            "seoul": "서울",
            "busan": "부산",
            "incheon": "인천",
            "daegu": "대구",
            "gwangju": "광주",
            "daejeon": "대전",
            "ulsan": "울산",
            "gyeonggi": "경기",
            "sejong": "세종",
            "jeju": "제주",
        }

        if region not in region_searched_keyword_replacements.keys():
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Invalid region query string"
            )

        area = region_searched_keyword_replacements[region]
        region_data = area_repo.get_region_data_by_random_text(area)

        jurisdiction_politician_id_list = (
            area_repo.select_jurisdiction_data_by_region_id_and_text(
                offset, size, region_data[0]
            )
        )

        for politician in jurisdiction_politician_id_list:
            politician_id = politician[0]
            politician_data = politician_info_repo.select_total_politician_data_by_id(
                politician_id
            )
            jurisdiction_data = area_repo.select_jurisdiction_data_by_politician_id(
                politician_id
            )
            jurisdiction_list = [
                JurisdictionResSchema(
                    id=data[0], region=data[1], district=data[2], section=data[3]
                )
                for data in jurisdiction_data
            ]
            politician_res = PublicPoliticianListElementResSchema.model_validate(
                politician_data
            )

            completed_promise_count = politician_data.completed_promise_count
            total_promise_count = politician_data.completed_promise_count

            if total_promise_count:
                politician_res.promise_execution_rate = (
                    completed_promise_count / total_promise_count
                ) * 100
            politician_res.constituency = jurisdiction_list
            return_res.append(politician_res)

    sorted_res = sorted(
        return_res,
        key=lambda x: x.promise_execution_rate
        if x.promise_execution_rate is not None
        else float("-inf"),
        reverse=True,
    )
    return sorted_res
