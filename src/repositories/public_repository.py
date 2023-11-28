from functools import lru_cache

from sqlalchemy import select

from common.enums import RegionType
from database.connection import engine
from database.models import Region, Constituency
from schema.public_response import PublicConstituencyResSchema


@lru_cache()
def get_constituency_data_from_db(assembly_term, region_name):
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
            .filter_by(
                region_id=region_id,
                assembly_term=assembly_term,
            )
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
