import logging

from fastapi import Depends, HTTPException
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED

from database.connection import get_db
from database.models import Admin
from repositories.area_repository import AreaRepository
from repositories.politician_info_repository import PoliticianInfoRepository
from schema.politician_response import PoliticianRes
from schema.token_response import TokenDecodeResponse

logger = logging.getLogger("uvicorn")


class PoliticianService:
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session
        self.politician_info_repo = PoliticianInfoRepository(session)
        self.area_repo = AreaRepository(session)

    async def create_new_politician_data(self, **kwargs):
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
                constituency_result = self.area_repo.search_constituency_data(
                    constituency_data
                )
                self.area_repo.insert_jurisdiction_data(
                    new_politician_id, constituency_result.id
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
        return PoliticianRes(politician_id=new_politician_id)
