from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    action: str
    details: str
    priority: str


class AuditResponse(BaseModel):
    audit: str = Field(..., title="SEO Audit", description="Text report for the page")
    recommendations: List[Recommendation] = Field(..., title="Recommendations", description="Concrete SEO actions")
    token_usage: Dict[str, Any] = Field(..., title="Token Usage")
