from pydantic import BaseModel, EmailStr


class SendAuthNumResponse(BaseModel):
    email: EmailStr
    detail: str = "Send email with auth number"


class VerifyAuthNumResponse(BaseModel):
    detail: str = "Email verified"
