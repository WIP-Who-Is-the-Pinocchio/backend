from typing import Optional

from pydantic import BaseModel


class PublicConstituencyResSchema(BaseModel):
    region: str
    district: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True
