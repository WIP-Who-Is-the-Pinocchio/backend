import logging
from itertools import chain
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from common.enums import RegionType
from database.connection import get_db
from repositories.area_repository import AreaRepository
from repositories.politician_info_repository import PoliticianInfoRepository
from schema.politician_response import (
    AddPoliticianDataRes,
    AddBulkPoliticianDataRes,
    GetSinglePoliticianDataRes,
    ConstituencyResSchema,
    GetPoliticianElementOfListRes,
)

logger = logging.getLogger("uvicorn")


class PoliticianService:
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session
        self.politician_info_repo = PoliticianInfoRepository(session)
        self.area_repo = AreaRepository(session)

    async def create_new_politician_data(self, **kwargs) -> AddPoliticianDataRes:
        admin_id = kwargs["admin_id"]
        new_politician_data = kwargs["request"]

        try:
            new_politician_id: int = self.politician_info_repo.insert_politician_data(
                new_politician_data.base_info
            )
            self.politician_info_repo.insert_committee_data(
                new_politician_id, new_politician_data.committee
            )
            self.politician_info_repo.insert_promise_count_detail_data(
                new_politician_id, new_politician_data.promise_count_detail
            )
            for constituency_data in new_politician_data.constituency:
                constituency_id = self.area_repo.get_constituency_id(constituency_data)
                self.area_repo.insert_jurisdiction_data(
                    new_politician_id, constituency_id
                )

            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            logger.exception(str(e))
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        finally:
            self.session.close()

        logger.info(f"admin {admin_id} inserted politician data: {new_politician_data}")
        return AddPoliticianDataRes(politician_id=new_politician_id)

    async def create_bulk_politician_data(self, **kwargs) -> AddBulkPoliticianDataRes:
        admin_id = kwargs["admin_id"]
        new_politician_data_list = kwargs["request"]

        try:
            parsed_politician_data = [
                single_politician.base_info.model_dump()
                for single_politician in new_politician_data_list
            ]
            inserted_politician_id_list = (
                self.politician_info_repo.bulk_insert_politician_data(
                    parsed_politician_data
                )
            )

            committee_data_list = list(
                chain.from_iterable(
                    [
                        [
                            {"politician_id": politician_id, **committee.dict()}
                            for committee in politician.committee
                        ]
                        for politician_id, politician in zip(
                            inserted_politician_id_list, new_politician_data_list
                        )
                    ]
                )
            )
            self.politician_info_repo.bulk_insert_committee_data(committee_data_list)

            promise_count_detail_data_list = list(
                chain.from_iterable(
                    [
                        [
                            {
                                "politician_id": politician_id,
                                **politician.promise_count_detail.dict(),
                            }
                        ]
                        for politician_id, politician in zip(
                            inserted_politician_id_list, new_politician_data_list
                        )
                    ]
                )
            )
            self.politician_info_repo.bulk_insert_promise_count_detail_data(
                promise_count_detail_data_list
            )

            jurisdiction_data_list = list(
                chain.from_iterable(
                    [
                        [
                            {
                                "politician_id": politician_id,
                                "constituency_id": self.area_repo.get_constituency_id(
                                    constituency
                                ),
                            }
                            for constituency in politician.constituency
                        ]
                        for politician_id, politician in zip(
                            inserted_politician_id_list, new_politician_data_list
                        )
                    ]
                )
            )
            self.area_repo.bulk_insert_jurisdiction_data(jurisdiction_data_list)

            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            logger.exception(str(e))
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        finally:
            self.session.close()

        data_count = len(new_politician_data_list)
        logger.info(f"admin {admin_id} inserted {data_count} politician data")
        return AddBulkPoliticianDataRes(new_politician_data_count=data_count)

    def get_politician_by_id(
        self, assembly_term: int, politician_id: int
    ) -> GetSinglePoliticianDataRes:
        politician_data = self.politician_info_repo.select_politician_data_by_id(
            politician_id
        )
        jurisdiction_data = self.area_repo.select_jurisdiction_data_by_politician_id(
            politician_id
        )
        constituency_list = [
            ConstituencyResSchema(region=data[1], district=data[2], section=data[3])
            for data in jurisdiction_data
        ]

        return_res = GetSinglePoliticianDataRes.model_validate(politician_data)
        return_res.assembly_term = assembly_term
        return_res.constituency = constituency_list
        return return_res

    def get_constituency_data(
        self, assembly_term: int, region: str
    ) -> List[ConstituencyResSchema]:
        region_name = RegionType[region.upper()].value[1]
        constituency_obj_list = self.area_repo.select_constituency_data_by_region(
            assembly_term, region_name
        )
        constituency_list = [
            ConstituencyResSchema(region=data[0], district=data[1], section=data[2])
            for data in constituency_obj_list
        ]
        return constituency_list

    def get_politician_list(
        self, assembly_term: int
    ) -> List[GetPoliticianElementOfListRes]:
        politician_list = self.politician_info_repo.get_politician_list_data_for_admin()
        return_res = []
        for politician in politician_list:
            jurisdiction_data = (
                self.area_repo.select_jurisdiction_data_by_politician_id(
                    politician[0].id
                )
            )
            constituency_list = [
                ConstituencyResSchema(region=data[1], district=data[2], section=data[3])
                for data in jurisdiction_data
            ]
            politician_res = GetPoliticianElementOfListRes.model_validate(politician[0])
            politician_res.constituency = constituency_list
            return_res.append(politician_res)
        return return_res
