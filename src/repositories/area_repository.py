from typing import List, Union

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, func, delete
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from schema.politician_request import ConstituencyReqSchema, JurisdictionUpdateReqSchema
from common.enums import RegionType
from database.connection import get_db
from database.models import Region, Constituency, Jurisdiction


class AreaRepository:
    region_model = Region
    constituency_model = Constituency
    jurisdiction_model = Jurisdiction

    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session

    @staticmethod
    def get_region_id(region_name: str) -> int:
        return next(
            (
                region.value[0]
                for region in RegionType
                if region.value[1] == region_name
            ),
            None,
        )

    @staticmethod
    def get_region_data_by_random_text(area_text: str) -> (int, str) or None:
        region_data = next(
            (region.value for region in RegionType if region.value[1] in area_text),
            None,
        )
        return region_data if region_data else None

    def get_constituency_id(
        self, data: Union[ConstituencyReqSchema or JurisdictionUpdateReqSchema]
    ) -> int:
        id, region, district, section = data
        region_name = region[1]
        district_name = district[1]
        section_name = section[1]

        region_id = self.get_region_id(region_name)
        if not region_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Region info not found",
            )

        query = select(self.constituency_model).filter(
            self.constituency_model.region_id == region_id,
            self.constituency_model.district == district_name,
            self.constituency_model.section == section_name,
        )
        search_result = self.session.execute(query).scalar()

        if not search_result:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Constituency info not found",
            )

        return search_result.id

    def insert_jurisdiction_data(self, politician_id: int, constituency_id: int):
        query = insert(self.jurisdiction_model).values(
            politician_id=politician_id, constituency_id=constituency_id
        )
        self.session.execute(query)

    def bulk_insert_jurisdiction_data(self, data: List[dict]):
        query = insert(self.jurisdiction_model).values(data)
        self.session.execute(query)

    def select_jurisdiction_data_by_politician_id(self, politician_id: int):
        query = (
            select(
                self.jurisdiction_model.id,
                self.constituency_model.assembly_term,
                self.region_model.region,
                self.constituency_model.district,
                self.constituency_model.section,
                self.jurisdiction_model.constituency_id,
            )
            .select_from(self.constituency_model)
            .filter(self.jurisdiction_model.politician_id == politician_id)
            .join(
                self.jurisdiction_model,
                self.constituency_model.id == self.jurisdiction_model.constituency_id,
            )
            .join(
                self.region_model,
                self.region_model.id == self.constituency_model.region_id,
            )
        )
        select_result = self.session.execute(query).all()
        return select_result

    def select_constituency_data_by_region(self, assembly_term: int, region_name: str):
        region_id = self.get_region_id(region_name)
        query = (
            select(
                self.region_model.region,
                self.constituency_model.district,
                self.constituency_model.section,
            )
            .select_from(self.constituency_model)
            .filter_by(
                region_id=region_id,
                assembly_term=assembly_term,
            )
            .join(
                self.region_model,
                self.region_model.id == self.constituency_model.region_id,
            )
        )
        select_result = self.session.execute(query).all()
        return select_result

    def select_jurisdiction_data_by_random_text(
        self, assembly_term: int, random_text: str, offset: int, size: int
    ):
        distinct_subquery = (
            select(
                func.distinct(self.jurisdiction_model.politician_id).label(
                    "politician_id"
                )
            )
            .select_from(self.jurisdiction_model)
            .filter(
                self.constituency_model.district.like(f"%{random_text}%"),
                self.constituency_model.assembly_term == assembly_term,
            )
            .join(
                self.constituency_model,
                self.constituency_model.id == self.jurisdiction_model.constituency_id,
            )
            .join(
                self.region_model,
                self.region_model.id == self.constituency_model.region_id,
            )
        ).alias("distinct_subquery")

        numbered_query = (
            select(
                distinct_subquery.c.politician_id,
                func.row_number().over().label("row_num"),
            )
            .select_from(distinct_subquery)
            .alias("numbered_query")
        )

        final_query = select(numbered_query.c.politician_id).offset(offset).limit(size)
        search_result = self.session.execute(final_query).all()
        return search_result

    def select_jurisdiction_data_by_region_id_and_text(
        self,
        offset: int,
        size: int,
        assembly_term: int,
        region_id: int,
        constituency_text: str = None,
    ):
        distinct_subquery = (
            select(
                func.distinct(self.jurisdiction_model.politician_id).label(
                    "politician_id"
                )
            )
            .select_from(self.jurisdiction_model)
            .filter(
                self.constituency_model.region_id == region_id,
                self.constituency_model.assembly_term == assembly_term,
            )
            .join(
                self.constituency_model,
                self.constituency_model.id == self.jurisdiction_model.constituency_id,
            )
            .join(
                self.region_model,
                self.region_model.id == self.constituency_model.region_id,
            )
        )
        if constituency_text:
            distinct_subquery = distinct_subquery.filter(
                self.constituency_model.district.like(f"%{constituency_text}%")
            )
        distinct_subquery = distinct_subquery.alias("distinct_subquery")

        numbered_query = (
            select(
                distinct_subquery.c.politician_id,
                func.row_number().over().label("row_num"),
            )
            .select_from(distinct_subquery)
            .alias("numbered_query")
        )

        final_query = select(numbered_query.c.politician_id).offset(offset).limit(size)

        select_result = self.session.execute(final_query).all()
        return select_result

    def check_jurisdiction_match(
        self, politician_id: int, constituency_id: int
    ) -> bool:
        query = select(self.jurisdiction_model).filter_by(
            politician_id=politician_id, constituency_id=constituency_id
        )
        search_result = self.session.execute(query).scalar()
        return True if search_result else False

    def delete_jurisdiction_data(self, jurisdiction_id: int):
        query = delete(self.jurisdiction_model).where(
            self.jurisdiction_model.id == jurisdiction_id
        )
        self.session.execute(query)
