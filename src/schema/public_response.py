from typing import Optional, List

from pydantic import BaseModel

from schema.politician_response import JurisdictionResSchema


class PublicConstituencyResSchema(BaseModel):
    region: str
    district: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


class PublicSinglePoliticianResSchema(BaseModel):
    id: int
    name: str
    profile_url: Optional[str] = None
    political_party: str
    total_promise_count: Optional[int] = None
    completed_promise_count: Optional[int] = None
    promise_execution_rate: Optional[int] = None

    class Config:
        from_attributes = True


class PublicPoliticianListElementResSchema(PublicSinglePoliticianResSchema):
    constituency: Optional[List[JurisdictionResSchema]] = None

    class Config:
        from_attributes = True
