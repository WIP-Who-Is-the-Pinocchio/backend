import logging

from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from starlette.status import HTTP_400_BAD_REQUEST

logger = logging.getLogger("uvicorn")


class SignUpRequest(BaseModel):
    login_name: str
    password: str
    nickname: str

    @field_validator("password", mode="before")
    def validate_password_length(cls, password):
        if len(password) < 8:
            logger.info("Received password with less than 8 characters.")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The password must be at least 8 characters long.",
            )
