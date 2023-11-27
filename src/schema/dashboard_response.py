from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminLogRes(BaseModel):
    admin_nickname: str
    action: str
    politician_name: Optional[str] = None
    created_at: datetime
