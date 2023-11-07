import logging
from typing import List

from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from schema.politician_request import (
    PoliticianReqSchema,
    PromiseCountDetailReqSchema,
    PoliticianCommitteeReqSchema,
)
from database.connection import get_db
from database.models import Politician, PromiseCountDetail, Committee

logger = logging.getLogger("uvicorn")


class PoliticianInfoRepository:
    politician_model = Politician
    promise_count_detail_model = PromiseCountDetail
    committee_model = Committee

    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session

    def insert_politician_data(self, data: PoliticianReqSchema) -> int:
        query = insert(self.politician_model).values(data.model_dump())
        politician_id = self.session.execute(query).lastrowid
        return politician_id

    def insert_promise_count_detail_data(
        self, politician_id: int, data: PromiseCountDetailReqSchema
    ):
        data = data.model_dump()
        data["politician_id"] = politician_id
        query = insert(self.promise_count_detail_model).values(**data)
        self.session.execute(query)

    def insert_committee_data(
        self, politician_id: int, committee_list: List[PoliticianCommitteeReqSchema]
    ):
        bulk_data = []
        for committee in committee_list:
            data = dict()
            data["politician_id"] = politician_id
            data["is_main"] = committee.is_main
            data["name"] = committee.name
            bulk_data.append(data)
        query = insert(self.committee_model).values(bulk_data)
        self.session.execute(query)

    def bulk_insert_politician_data(self, data: List[dict]) -> List[int]:
        inserted_politician_id_list = []
        for single_data in data:
            query = insert(self.politician_model).values(single_data)
            insert_result = self.session.execute(query).inserted_primary_key
            inserted_politician_id_list.append(insert_result[0])
        return inserted_politician_id_list

    def bulk_insert_committee_data(self, data: List[dict]) -> None:
        query = insert(self.committee_model).values(data)
        self.session.execute(query)

    def bulk_insert_promise_count_detail_data(self, data: List[dict]):
        query = insert(self.promise_count_detail_model).values(data)
        self.session.execute(query)

    def select_politician_data_by_id(self, politician_id: int):
        query = (
            select(
                self.politician_model,
                self.committee_model,
                self.promise_count_detail_model,
            )
            .select_from(self.politician_model)
            .filter_by(id=politician_id)
            .join(
                self.committee_model,
                self.committee_model.politician_id == politician_id,
            )
            .join(
                self.promise_count_detail_model,
                self.promise_count_detail_model.politician_id == politician_id,
            )
        )
        select_result = self.session.execute(query).scalar()
        return select_result

    def get_politician_list_data_for_admin(self):
        total_politician_data = self.session.execute(
            select(self.politician_model)
        ).all()
        return total_politician_data
