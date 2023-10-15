from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED


def get_token(
    authorization: HTTPAuthorizationCredentials
    | None = Depends(HTTPBearer(auto_error=False)),
) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No token.",
        )
    return authorization.credentials
