from typing import List

from src.api.schemas import AuditResponse, Recommendation
from src.clients.gigachat_client import GigaChatClient
from src.parsing.analyzer import HtmlAnalyzer
from src.parsing.crawler import fetch_page


class SeoAuditService:
    def __init__(self, gigachat_client: GigaChatClient | None = None):
        self.gigachat_client = gigachat_client or GigaChatClient()

    async def build_audit(self, url: str) -> AuditResponse:
        html = await fetch_page(url)
        analyzer = HtmlAnalyzer(html)
        metrics = analyzer.analyze()
        parsed, usage = self.gigachat_client.generate_audit(metrics)

        recommendations_raw = parsed.get("recommendations", [])
        recommendations: List[Recommendation] = [Recommendation(**item) for item in recommendations_raw]

        return AuditResponse(
            audit=parsed.get("audit", ""),
            recommendations=recommendations,
            token_usage=usage or {},
        )
