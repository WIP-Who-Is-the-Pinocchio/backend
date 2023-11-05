from pydantic import BaseModel


class PoliticianRes(BaseModel):
    politician_id: int


class BulkPoliticianRes(BaseModel):
    new_politician_data_count: int
