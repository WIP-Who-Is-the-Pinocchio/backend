import logging
from typing import List

from schema.dashboard_response import (
    AdminLogRes,
    DuplicatedJurisdictionResSchema,
    DuplicatedJurisdictionPoliticianResSchema,
    IntegrityErrorRes,
)

logger = logging.getLogger("uvicorn")


async def get_admin_log(**kwargs) -> List[AdminLogRes]:
    admin_repo = kwargs["admin_repository"]
    politician_info_repo = kwargs["politician_info_repository"]

    admin_log_list = admin_repo.select_admin_log_data()
    return_res = []
    for admin_log in admin_log_list:
        politician_data = politician_info_repo.select_politician_data_by_id(
            admin_log.politician_id
        )
        data = {
            "admin_nickname": admin_log.nickname,
            "action": admin_log.action,
            "politician_name": politician_data.name,
            "created_at": admin_log.created_at,
        }
        return_res.append(AdminLogRes(**data))
    return return_res


async def get_integrity_error_data(**kwargs) -> IntegrityErrorRes:
    politician_info_repo = kwargs["politician_info_repository"]
    area_repo = kwargs["area_repository"]

    duplicated_jurisdiction_data_list = area_repo.get_duplicated_jurisdiction()

    duplicated_data = []
    for constituency_data in duplicated_jurisdiction_data_list:
        constituency_id = constituency_data[0]
        constituency_data = area_repo.select_constituency_data_by_id(constituency_id)
        politician_id_list = list(
            map(
                lambda x: x[0],
                area_repo.select_politician_id_by_constituency_id(constituency_id),
            )
        )
        politician_data_list = politician_info_repo.select_politician_data_by_id_list(
            politician_id_list
        )
        politician_list = [
            DuplicatedJurisdictionPoliticianResSchema(
                id=politician[0].id, name=politician[0].name
            )
            for politician in politician_data_list
        ]
        data = {
            "region": constituency_data.region,
            "district": constituency_data.district,
            "section": constituency_data.section,
            "politician_list": politician_list,
        }
        duplicated_data.append(DuplicatedJurisdictionResSchema(**data))
    return IntegrityErrorRes(duplicated_jurisdiction=duplicated_data)
