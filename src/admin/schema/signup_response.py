from pydantic import BaseModel

from admin.schema.admin_info_response import AdminInfoResponse


class SignUpResponse(BaseModel):
    data: AdminInfoResponse
    message: str = "Created new admin account successfully."
