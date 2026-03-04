from fastapi import FastAPI, Form, HTTPException
from typing import Any, Dict, List
from pydantic import BaseModel, Field
import logging

from crawler import fetch_page
from analyzer import analyze_html
from ai_agent import generate_audit
from schema import Recommendation, AuditResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="SEO Audit Service")


@app.post("/seo-audit", response_model=AuditResponse)
async def seo_audit(url: str = Form(..., description="URL страницы для SEO аудита")):
    try:
        html = fetch_page(url)
        metrics = analyze_html(html)

        parsed, usage = generate_audit(metrics)


        recs = [Recommendation(**r) for r in parsed.get("recommendations", [])]

        return AuditResponse(
            audit=parsed.get("audit", ""),
            recommendations=recs,
            token_usage=usage or {}
        )
    except Exception as e:
        logging.error(f"Ошибка SEO аудита: {e}")
        raise HTTPException(status_code=500, detail=str(e))