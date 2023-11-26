import logging
from typing import List

from fastapi import Depends
from sqlalchemy import insert, select, update, CursorResult, delete
from sqlalchemy.orm import Session

from schema.politician_request import (
    PoliticianReqSchema,
    PromiseCountDetailReqSchema,
    PoliticianCommitteeReqSchema,
    PoliticianCommitteeUpdateReqSchema,
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
            data = {
                "politician_id": politician_id,
                "is_main": committee.is_main,
                "name": committee.name,
            }
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
            .outerjoin(
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

    def get_politician_list_data_for_admin(self, offset: int, size: int):
        total_politician_data = self.session.execute(
            select(self.politician_model).offset(offset).limit(size)
        ).all()
        return total_politician_data

    def get_politician_search_data_for_admin(
        self, offset: int, size: int, name: str = None, party: str = None
    ):
        query = select(self.politician_model)
        filtered_query = (
            query.filter(self.politician_model.name.like(f"%{name}%"))
            if name
            else query.filter(self.politician_model.political_party.like(f"%{party}%"))
        )
        search_result = self.session.execute(
            filtered_query.offset(offset).limit(size)
        ).all()
        return search_result

    def select_committee_data(self, politician_id: int):
        query = select(
            self.committee_model.id,
            self.committee_model.is_main,
            self.committee_model.name,
        ).filter_by(politician_id=politician_id)
        search_result = self.session.execute(query).all()
        return search_result

    def update_politician_data(
        self, politician_id: int, data: PoliticianReqSchema
    ) -> CursorResult[int]:
        query = (
            update(self.politician_model)
            .where(self.politician_model.id == politician_id)
            .values(data.model_dump())
        )
        update_result = self.session.execute(query)
        return update_result

    def delete_committee_data(self, committee_id: int):
        query = delete(self.committee_model).where(
            self.committee_model.id == committee_id
        )
        self.session.execute(query)

    def update_committee_data(
        self,
        politician_id: int,
        committee_list: List[PoliticianCommitteeUpdateReqSchema],
    ):
        for committee in committee_list:
            committee = committee.model_dump()
            if committee["id"]:
                committee_id = committee["id"]
                del committee["id"]
                query = (
                    update(self.committee_model)
                    .where(self.committee_model.id == committee_id)
                    .values(committee)
                )
                self.session.execute(query)
            else:
                new_committee_data = {
                    "politician_id": politician_id,
                    "is_main": committee["is_main"],
                    "name": committee["name"],
                }
                query = insert(self.committee_model).values(new_committee_data)
                self.session.execute(query)

    def update_promise_count_detail_data(
        self, politician_id: int, data: PromiseCountDetailReqSchema
    ) -> CursorResult[int]:
        data = data.model_dump()
        query = (
            update(self.promise_count_detail_model)
            .where(self.politician_model.id == politician_id)
            .values(**data)
        )
        update_result = self.session.execute(query)
        return update_result
