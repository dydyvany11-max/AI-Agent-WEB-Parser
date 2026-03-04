from pydantic import BaseModel
from typing import Dict , Any

class URLRequest(BaseModel):
    url:str


class AuditResponse(BaseModel):
    audit:str
    token_usage:Dict[str, Any]

    