from pydantic import BaseModel, constr, EmailStr


class LogInRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=1)
