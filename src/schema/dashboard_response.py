from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class AdminLogRes(BaseModel):
    admin_nickname: str
    action: str
    politician_name: Optional[str] = None
    created_at: datetime


class DuplicatedJurisdictionPoliticianResSchema(BaseModel):
    id: int
    name: str


class DuplicatedJurisdictionResSchema(BaseModel):
    region: str
    district: Optional[str] = None
    section: Optional[str] = None
    politician_list: List[DuplicatedJurisdictionPoliticianResSchema]


class IntegrityErrorRes(BaseModel):
    duplicated_jurisdiction: List[DuplicatedJurisdictionResSchema] = None
    incomplete_politician: List = None
