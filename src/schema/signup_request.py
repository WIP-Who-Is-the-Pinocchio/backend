import logging

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, constr, EmailStr
from starlette.status import HTTP_400_BAD_REQUEST

logger = logging.getLogger("uvicorn")


class SignUpRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=1)
    nickname: constr(min_length=1)

    @field_validator("password", mode="before")
    @classmethod
    def validate_password_length(cls, password):
        if len(password) < 8:
            logger.info("Received password with less than 8 characters.")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The password must be at least 8 characters long.",
            )
        return password
