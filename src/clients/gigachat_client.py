import json
import re
from typing import Any, Dict, Tuple

import requests

from src.clients.gigachat_auth import GigaChatAuthClient


class GigaChatClient:
    def __init__(
        self,
        base_url: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        auth_client: GigaChatAuthClient | None = None,
    ):
        self.base_url = base_url
        self.auth_client = auth_client or GigaChatAuthClient()

    @staticmethod
    def _safe_json_parse(text: str) -> dict:
        cleaned = (text or "").strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        if not cleaned or not cleaned.startswith("{"):
            return {"audit": "Модель вернула ответ не в формате JSON.", "recommendations": []}

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"audit": "Не удалось разобрать JSON-ответ модели.", "recommendations": []}

    def _repair_to_json(self, raw_content: str, headers: Dict[str, str]) -> dict:
        repair_prompt = f"""
                        Преобразуй следующий текст в СТРОГО валидный JSON и ничего больше.
                        Если в тексте нет части данных, заполни разумно на основе текста.

                        Требуемый формат:
                        {{
                        "audit": "строка",
                        "recommendations": [
                            {{
                            "action": "строка",
                            "details": "строка",
                            "priority": "High | Medium | Low"
                            }}
                        ]
                        }}

                        Текст для преобразования:
                        {raw_content}
                        """

        payload = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": repair_prompt}],
            "temperature": 0,
        }

        response = requests.post(self.base_url, headers=headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return self._safe_json_parse(content)

    def generate_audit(self, metrics: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        token = self.auth_client.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        prompt = f"""
                Ты senior SEO-специалист.

                Проанализируй ВСЕ переданные метрики страницы и верни полный SEO-аудит.
                Не ограничивайся 2-3 пунктами: перечисли все существенные проблемы, которые видны по данным.

                Метрики страницы:
                {metrics}

                Требования к ответу:
                1) Верни строго JSON, без markdown и без текста вне JSON.
                2) Поле recommendations должно содержать минимум 8 пунктов, если по метрикам есть проблемы.
                3) Обязательно покрой: title, meta description, H1-H3, изображения и alt, canonical, robots, внутренние/внешние ссылки, Open Graph, structured data, объём текста.
                4) Не дублируй рекомендации.
                5) priority только из: High, Medium, Low.

                Формат JSON:
                {{
                "audit": "Краткий, но содержательный вывод по SEO-состоянию страницы",
                "recommendations": [
                    {{
                    "action": "Что сделать",
                    "details": "Конкретно что исправить и какие целевые значения",
                    "priority": "High | Medium | Low"
                    }}
                ]
                }}
                """

        payload = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }

        response = requests.post(self.base_url, headers=headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = self._safe_json_parse(content)
        if parsed.get("audit", "").startswith("Не удалось разобрать JSON") or parsed.get("audit", "").startswith("Модель вернула ответ не в формате JSON"):
            parsed = self._repair_to_json(content, headers)

        usage = data.get("usage", {})
        return parsed, usage
