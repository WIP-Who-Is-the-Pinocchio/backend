from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, and_
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from schema.politician_request import ConstituencyReqSchema
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

    def get_constituency_id(self, data: ConstituencyReqSchema) -> int:
        region, district, section = data
        region_name = region[1]
        district_name = district[1]
        section_name = section[1]

        region_id = self.get_region_id(region_name)
        # region_id = next(
        #     (
        #         region.value[0]
        #         for region in RegionType
        #         if region.value[1] == region_name
        #     ),
        #     None,
        # )

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
                self.constituency_model.assembly_term,
                self.region_model.region,
                self.constituency_model.district,
                self.constituency_model.section,
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

    def select_constituency_data_by_region(
        self, assembly_term: int, region_name: str
    ) -> List[any]:
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
