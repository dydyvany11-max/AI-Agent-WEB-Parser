from fastapi import APIRouter, Form

from src.api.schemas import AuditResponse
from src.services.seo_audit_service import SeoAuditService

router = APIRouter()
service = SeoAuditService()


@router.post("/seo-audit", response_model=AuditResponse)
async def seo_audit(url: str = Form(...)):
    return await service.build_audit(url)
