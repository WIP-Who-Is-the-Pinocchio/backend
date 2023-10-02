from pydantic import BaseModel, constr


class LogInRequest(BaseModel):
    login_name: constr(min_length=1)
    password: constr(min_length=1)
