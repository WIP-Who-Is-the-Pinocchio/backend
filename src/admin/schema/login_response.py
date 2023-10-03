from pydantic import BaseModel

from admin.schema.admin_info_response import AdminInfoResponse


class LoginResponseData(BaseModel):
    admin: AdminInfoResponse
    access_token: str


class LoginResponse(BaseModel):
    data: LoginResponseData
    message: str = "Login success response with access token"
