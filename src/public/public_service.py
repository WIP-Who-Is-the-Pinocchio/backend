import logging
from typing import List

from common.enums import RegionType
from repositories.area_repository import AreaRepository
from repositories.public_repository import get_constituency_data_from_db
from schema.public_response import PublicConstituencyResSchema


logger = logging.getLogger("uvicorn")


def get_public_constituency_data(
    assembly_term: int, region: str, area_repository: AreaRepository
) -> List[PublicConstituencyResSchema]:
    region_name = RegionType[region.upper()].value[1]

    cached_data = get_constituency_data_from_db(assembly_term, region_name)
    logger.info(
        f"public constituency_data {get_constituency_data_from_db.cache_info()}"
    )
    if cached_data is not None:
        return cached_data
    logger.info(f"public constituency_data cache none")

    updated_data = area_repository.select_constituency_data_by_region(
        assembly_term, region_name
    )
    constituency_list = [
        PublicConstituencyResSchema(region=data[0], district=data[1], section=data[2])
        for data in updated_data
    ]

    return constituency_list
