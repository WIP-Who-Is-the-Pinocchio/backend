import logging
import re
from itertools import chain
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from common.enums import RegionType
from database.connection import get_db
from repositories.admin_repository import AdminRepository
from repositories.area_repository import AreaRepository
from repositories.politician_info_repository import PoliticianInfoRepository
from schema.politician_response import (
    AddPoliticianDataRes,
    AddBulkPoliticianDataRes,
    GetSinglePoliticianDataRes,
    JurisdictionResSchema,
    GetPoliticianElementOfListRes,
    ConstituencyResSchema,
)

logger = logging.getLogger("uvicorn")


class PoliticianService:
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session
        self.politician_info_repo = PoliticianInfoRepository(session)
        self.area_repo = AreaRepository(session)
        self.admin_repo = AdminRepository(session)

    async def create_new_politician_data(self, **kwargs) -> AddPoliticianDataRes:
        admin_id = kwargs["admin_id"]
        new_politician_data = kwargs["request"]

        try:
            new_politician_id: int = self.politician_info_repo.insert_politician_data(
                new_politician_data.base_info
            )
            self.politician_info_repo.insert_promise_count_detail_data(
                new_politician_id, new_politician_data.promise_count_detail
            )
            if new_politician_data.committee:
                self.politician_info_repo.insert_committee_data(
                    new_politician_id, new_politician_data.committee
                )
            for constituency_data in new_politician_data.constituency:
                constituency_id = self.area_repo.get_constituency_id(constituency_data)
                self.area_repo.insert_jurisdiction_data(
                    new_politician_id, constituency_id
                )

            self.admin_repo.insert_admin_log_data(admin_id, "create", new_politician_id)
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

            self.admin_repo.insert_admin_log_data(admin_id, "bulk_create")
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

    async def update_single_politician_data(self, **kwargs) -> AddPoliticianDataRes:
        admin_id = kwargs["admin_id"]
        politician_data = kwargs["request"]
        politician_id = politician_data.politician_id

        try:
            self.politician_info_repo.update_politician_data(
                politician_id, politician_data.base_info
            )

            self.politician_info_repo.update_promise_count_detail_data(
                politician_id, politician_data.promise_count_detail
            )

            original_committee_data = self.politician_info_repo.select_committee_data(
                politician_id
            )
            original_committee_id_list = list(
                map(lambda x: x[0], original_committee_data)
            )
            new_committee_id_list = list(
                map(lambda x: x.model_dump()["id"], politician_data.committee)
            )
            deleted_committee_id_list = list(
                set(original_committee_id_list).difference(new_committee_id_list)
            )
            for committee_id in deleted_committee_id_list:
                self.politician_info_repo.delete_committee_data(committee_id)
            self.politician_info_repo.update_committee_data(
                politician_id, politician_data.committee
            )

            original_jurisdiction_data = (
                self.area_repo.select_jurisdiction_data_by_politician_id(politician_id)
            )
            original_jurisdiction_id_list = list(
                map(lambda x: x[0], original_jurisdiction_data)
            )
            original_constituency_id_list = list(
                map(lambda x: x[5], original_jurisdiction_data)
            )
            new_jurisdiction_id_list = list(
                map(lambda x: x.model_dump()["id"], politician_data.jurisdiction)
            )
            deleted_jurisdiction_id_list = list(
                set(original_jurisdiction_id_list).difference(new_jurisdiction_id_list)
            )
            for jurisdiction_id in deleted_jurisdiction_id_list:
                self.area_repo.delete_jurisdiction_data(jurisdiction_id)

            for constituency_data in politician_data.jurisdiction:
                constituency_id = self.area_repo.get_constituency_id(constituency_data)
                if constituency_id not in original_constituency_id_list:
                    self.area_repo.insert_jurisdiction_data(
                        politician_id, constituency_id
                    )

            self.admin_repo.insert_admin_log_data(admin_id, "update", politician_id)
            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            logger.exception(str(e))
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        finally:
            self.session.close()

        logger.info(f"admin {admin_id} updated politician data: {politician_id}")
        return AddPoliticianDataRes(politician_id=politician_id)

    def get_politician_by_id(
        self, assembly_term: int, politician_id: int
    ) -> GetSinglePoliticianDataRes:
        politician_data = self.politician_info_repo.select_total_politician_data_by_id(
            politician_id
        )
        jurisdiction_data = self.area_repo.select_jurisdiction_data_by_politician_id(
            politician_id
        )
        jurisdiction_list = [
            JurisdictionResSchema(
                id=data[0], region=data[2], district=data[3], section=data[4]
            )
            for data in jurisdiction_data
        ]

        return_res = GetSinglePoliticianDataRes.model_validate(politician_data)
        return_res.assembly_term = assembly_term
        return_res.constituency = jurisdiction_list
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
        self, assembly_term: int, page: int, size: int
    ) -> List[GetPoliticianElementOfListRes]:
        offset = page * size
        politician_list = self.politician_info_repo.get_politician_list_data_for_admin(
            offset, size
        )
        return_res = []
        for politician in politician_list:
            jurisdiction_data = (
                self.area_repo.select_jurisdiction_data_by_politician_id(
                    politician[0].id
                )
            )
            jurisdiction_list = [
                JurisdictionResSchema(
                    id=data[0], region=data[2], district=data[3], section=data[4]
                )
                for data in jurisdiction_data
            ]
            politician_res = GetPoliticianElementOfListRes.model_validate(politician[0])
            politician_res.assembly_term = assembly_term
            politician_res.constituency = jurisdiction_list
            return_res.append(politician_res)
        return return_res

    def get_politician_search_data(
        self,
        assembly_term: int,
        page: int,
        size: int,
        name: str = None,
        party: str = None,
        jurisdiction: str = None,
    ) -> List[GetPoliticianElementOfListRes]:
        offset = page * size
        if name or party:
            politician_list = (
                self.politician_info_repo.get_politician_search_data_for_admin(
                    offset=offset, size=size, name=name, party=party
                )
            )
            return_res = []
            for politician in politician_list:
                jurisdiction_data = (
                    self.area_repo.select_jurisdiction_data_by_politician_id(
                        politician[0].id
                    )
                )
                jurisdiction_list = [
                    JurisdictionResSchema(
                        id=data[0], region=data[2], district=data[3], section=data[4]
                    )
                    for data in jurisdiction_data
                ]
                politician_res = GetPoliticianElementOfListRes.model_validate(
                    politician[0]
                )
                politician_res.assembly_term = assembly_term
                politician_res.constituency = jurisdiction_list
                return_res.append(politician_res)
                return return_res
        else:
            area_text = jurisdiction.replace(" ", "")
            abbreviated_area_text = re.sub(r"(특별|광역)시", "", area_text)
            region_searched_keyword_replacements = {
                "서울시": "서울",
                "부산시": "부선",
                "인천시": "인천",
                "대구시": "대구",
                "광주시": "광주",
                "대전시": "대전",
                "울산시": "울산",
                "경기도": "경기",
                "세종시": "세종",
                "제주도": "제주",
            }
            for key, value in region_searched_keyword_replacements.items():
                abbreviated_area_text = abbreviated_area_text.replace(key, value)

            region_data = self.area_repo.get_region_data_by_random_text(
                abbreviated_area_text
            )

            if not region_data:
                logger.info(f"Only constituency searched: {abbreviated_area_text}")
                jurisdiction_politician_id_list = (
                    self.area_repo.select_jurisdiction_data_by_random_text(
                        assembly_term, abbreviated_area_text, offset, size
                    )
                )
            else:
                region_id, region_name = region_data
                area_text_without_region = abbreviated_area_text.replace(
                    region_name, ""
                )
                if not area_text_without_region:
                    logger.info(f"Only region searched: {abbreviated_area_text}")
                    jurisdiction_politician_id_list = (
                        self.area_repo.select_jurisdiction_data_by_region_id_and_text(
                            offset, size, assembly_term, region_id
                        )
                    )
                else:
                    logger.info(
                        f"Both region and constituency searched: {abbreviated_area_text}"
                    )
                    jurisdiction_politician_id_list = (
                        self.area_repo.select_jurisdiction_data_by_region_id_and_text(
                            offset,
                            size,
                            assembly_term,
                            region_id,
                            area_text_without_region,
                        )
                    )

            return_res = []
            for politician in jurisdiction_politician_id_list:
                politician_id = politician[0]
                politician_data = (
                    self.politician_info_repo.select_total_politician_data_by_id(
                        politician_id
                    )
                )
                jurisdiction_data = (
                    self.area_repo.select_jurisdiction_data_by_politician_id(
                        politician_id
                    )
                )
                jurisdiction_list = [
                    JurisdictionResSchema(
                        id=data[0], region=data[2], district=data[3], section=data[4]
                    )
                    for data in jurisdiction_data
                ]
                politician_res = GetPoliticianElementOfListRes.model_validate(
                    politician_data
                )
                politician_res.assembly_term = assembly_term
                politician_res.constituency = jurisdiction_list
                return_res.append(politician_res)
            return return_res
