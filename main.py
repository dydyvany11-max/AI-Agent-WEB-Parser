from fastapi import FastAPI, Form, HTTPException
import asyncio
import sys
import logging

from src.parsing.crawler import fetch_page
from src.parsing.analyzer import HtmlAnalyzer
from src.Agent.ai_agent import GigaChatUnavailableError, generate_audit
from schema import Recommendation, AuditResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="SEO Audit Service")


@app.post("/seo-audit", response_model=AuditResponse)
async def seo_audit(url: str = Form(...)):
    try:
        html = await fetch_page(url)
        analyzer = HtmlAnalyzer(html)
        metrics = analyzer.analyze()
        parsed, usage = generate_audit(metrics)
        recs = [Recommendation(**r) for r in parsed.get("recommendations", [])]
        return AuditResponse(
            audit=parsed.get("audit", ""),
            recommendations=recs,
            token_usage=usage or {}
        )
    except GigaChatUnavailableError as e:
        logging.error(f"GigaChat unavailable: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e).strip() or f"{type(e).__name__}: unexpected server error"
        logging.error(f"SEO audit error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)
