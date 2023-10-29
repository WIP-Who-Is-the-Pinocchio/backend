from pydantic import BaseModel

from schema.admin_info_response import AdminInfoResponse


class LoginResponseData(BaseModel):
    admin: AdminInfoResponse
    access_token: str
    refresh_token: str


class LoginResponse(BaseModel):
    data: LoginResponseData
    detail: str = "Login success response with access token"
