from pydantic import BaseModel


class PoliticianRes(BaseModel):
    politician_id: int
