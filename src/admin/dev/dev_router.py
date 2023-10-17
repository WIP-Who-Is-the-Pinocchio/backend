from fastapi import APIRouter, Depends, Path, HTTPException
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from admin.auth.auth_manager import AuthManager
from admin.security import get_token
from database.models import Admin
from database.repositories.admin_repository import AdminRepository

router = APIRouter()


@router.get(
    "/access-token/{admin_id}",
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: {"description": "Access token pass"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        HTTP_404_NOT_FOUND: {"description": "Admin id not found"},
    },
    summary="Access token 사용 및 재발급을 위한 작업용 API",
    description="Bearer {access token} 값을 Authorization Header로 추가해서 요청",
)
async def access_token_check_dev_handler(
    admin_id: int = Path(..., description="admin_id"),
    token: str = Depends(get_token),
    auth_manager: AuthManager = Depends(),
    admin_repository: AdminRepository = Depends(),
):
    payload_data = auth_manager.decode_token(access_token=token)

    admin: Admin | None = admin_repository.get_admin_data(id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Admin id not found."
        )

    if payload_data.admin_id != admin_id or payload_data.uuid_jti != admin.uuid_jti:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid access token."
        )

    return {"detail": "Access token verified"}
