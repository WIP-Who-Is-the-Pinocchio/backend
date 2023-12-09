import logging
from functools import lru_cache
from typing import List

from sqlalchemy import select

from common.enums import RegionType
from database.connection import engine
from database.models import Region, Constituency
from repositories.area_repository import AreaRepository
from schema.politician_response import JurisdictionResSchema
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
