# Схема ответа audit - ответ. token_usage сколько токенов ушло на ответ

from pydantic import BaseModel, Field
from typing import Dict , Any

class URLRequest(BaseModel):
    url:str


class AuditResponse(BaseModel):
    audit: str = Field(..., title="Полный SEO аудит")
    recommendations: str = Field(..., title="Текст рекомендаций") 
    token_usage: Dict[str, Any] = Field(..., title="Статистика токенов")
    