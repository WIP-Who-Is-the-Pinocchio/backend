from pydantic import BaseModel


class SignUpResponse(BaseModel):
    id: int
    login_name: str
    nickname: str

    class Config:
        from_attributes = True
