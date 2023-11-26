from pydantic import BaseModel

from schema.admin_info_response import AdminInfoResponse


class LoginRes(BaseModel):
    admin: AdminInfoResponse
    access_token: str
    refresh_token: str


class LogoutRes(BaseModel):
    detail: str = "Logout success"
