from pydantic import BaseModel


class SignUpRequest(BaseModel):
    login_name: str
    password: str
    nickname: str
