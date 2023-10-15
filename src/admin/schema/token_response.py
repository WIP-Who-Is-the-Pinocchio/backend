from pydantic import BaseModel


class TokenDecodeResponse(BaseModel):
    admin_id: int
    nickname: str
    uuid_jti: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokensResponse(BaseModel):
    data: Tokens
    detail: str = "Refreshed token data"
