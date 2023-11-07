from typing import List, Optional

from pydantic import BaseModel


class AddPoliticianDataRes(BaseModel):
    politician_id: int


class AddBulkPoliticianDataRes(BaseModel):
    new_politician_data_count: int


class PromiseCountDetailResSchema(BaseModel):
    completed_national_promise_count: Optional[int] = None
    total_national_promise_count: Optional[int] = None
    completed_local_promise_count: Optional[int] = None
    total_local_promise_count: Optional[int] = None
    completed_legislative_promise_count: Optional[int] = None
    total_legislative_promise_count: Optional[int] = None
    completed_financial_promise_count: Optional[int] = None
    total_financial_promise_count: Optional[int] = None
    completed_in_term_promise_count: Optional[int] = None
    total_in_term_promise_count: Optional[int] = None
    completed_after_term_promise_count: Optional[int] = None
    total_after_term_promise_count: Optional[int] = None
    completed_ongoing_business_promise_count: Optional[int] = None
    total_ongoing_business_promise_count: Optional[int] = None
    completed_new_business_promise_count: Optional[int] = None
    total_new_business_promise_count: Optional[int] = None

    class Config:
        from_attributes = True


class PoliticianCommitteeResSchema(BaseModel):
    is_main: bool
    name: str

    class Config:
        from_attributes = True


class ConstituencyResSchema(BaseModel):
    region: str
    district: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


class PoliticianResSchema(BaseModel):
    id: int
    name: str
    assembly_term: Optional[int] = None
    profile_url: Optional[str] = None
    political_party: str
    elected_count: int
    total_promise_count: Optional[int] = None
    completed_promise_count: Optional[int] = None
    in_progress_promise_count: Optional[int] = None
    pending_promise_count: Optional[int] = None
    discarded_promise_count: Optional[int] = None
    other_promise_count: Optional[int] = None
    resolve_required_promise_count: Optional[int] = None
    resolved_promise_count: Optional[int] = None
    total_required_funds: Optional[int] = None
    total_secured_funds: Optional[int] = None
    total_executed_funds: Optional[int] = None

    class Config:
        from_attributes = True


class GetSinglePoliticianDataRes(PoliticianResSchema):
    promise_count_detail: PromiseCountDetailResSchema
    committee: List[PoliticianCommitteeResSchema]
    constituency: Optional[List[ConstituencyResSchema]] = None

    class Config:
        from_attributes = True


class GetPoliticianElementOfListRes(PoliticianResSchema):
    constituency: Optional[List[ConstituencyResSchema]] = None

    class Config:
        from_attributes = True
