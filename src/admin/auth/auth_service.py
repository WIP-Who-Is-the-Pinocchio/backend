import logging

from fastapi import HTTPException
from starlette.status import HTTP_409_CONFLICT

from admin.schema.signup_response import SignUpResponse
from database.models import Admin


logger = logging.getLogger("uvicorn")


async def create_admin(**kwargs):
    new_account_data = kwargs["request"]
    auth_manager = kwargs["auth_manager"]
    admin_repository = kwargs["admin_repository"]
    login_name, password, nickname = (
        new_account_data.login_name,
        new_account_data.password,
        new_account_data.nickname,
    )

    is_unique = admin_repository.check_uniqueness(login_name, nickname)
    if not is_unique:
        logger.info("Received duplicated value.")
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Both login_name and nickname should be unique.",
        )

    hashed_password: str = auth_manager.hash_password(password)
    new_admin: Admin = Admin.create(login_name, hashed_password, nickname)
    admin_created: Admin = admin_repository.create_admin(new_admin)
    logger.info(f"New admin account is created: {admin_created}")

    return {
        "data": SignUpResponse.model_validate(admin_created),
        "message": "Created new admin account successfully.",
    }
