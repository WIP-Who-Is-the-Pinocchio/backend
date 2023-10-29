from pydantic import BaseModel

from schema.admin_info_response import AdminInfoResponse


class SignUpResponse(BaseModel):
    data: AdminInfoResponse
    detail: str = "Created new admin account successfully."
