# Схема ответа audit - ответ. token_usage сколько токенов ушло на ответ

from pydantic import BaseModel, Field
from typing import Dict , Any, List

class URLRequest(BaseModel):
    url:str

from pydantic import BaseModel
from typing import List, Dict, Any


class Recommendation(BaseModel):
    action: str
    details: str
    priority: str


class AuditResponse(BaseModel):
    audit: str
    recommendations: List[Recommendation]
    token_usage: Dict[str, Any]

