from pydantic import BaseModel, EmailStr


class AdminInfoResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str

    class Config:
        from_attributes = True
