# Схема ответа audit - ответ. token_usage сколько токенов ушло на ответ

from pydantic import BaseModel, Field
from typing import Dict , Any, List



class Recommendation(BaseModel):
    action: str
    details: str
    priority: str


class AuditResponse(BaseModel):
    audit: str = Field(..., title="Полный SEO аудит", description="Текстовый отчёт по странице")
    recommendations: List[Recommendation] = Field(..., title="Рекомендации", description="Список конкретных SEO-действий")
    token_usage: Dict[str, Any] = Field(..., title="Использованные токены")

