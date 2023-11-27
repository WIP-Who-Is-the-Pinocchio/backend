import logging
from typing import List

from schema.dashboard_response import AdminLogRes


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
