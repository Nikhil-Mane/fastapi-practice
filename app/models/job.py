from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    id: str
    status: str
    result: Optional[dict] = None 