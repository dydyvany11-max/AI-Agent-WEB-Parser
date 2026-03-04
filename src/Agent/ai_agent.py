import requests
import logging
import json
import re
import os
from typing import Any, Dict, List, Tuple
from requests import RequestException
from .gs_auth import get_access_token

DEFAULT_GIGACHAT_URLS = [
    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
    "https://ngw.devices.sberbank.ru:9443/api/v1/chat/completions",
]


def safe_json_parse(text: str) -> dict:
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return json.loads(text)


class GigaChatUnavailableError(Exception):
    pass


def _resolve_gigachat_urls() -> List[str]:
    url_from_env = os.getenv("GIGACHAT_URL", "").strip()
    urls = [url_from_env] if url_from_env else []
    for default_url in DEFAULT_GIGACHAT_URLS:
        if default_url not in urls:
            urls.append(default_url)
    return urls


def generate_audit(metrics: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    try:
        token = get_access_token()
    except RequestException as exc:
        logging.error("GigaChat auth unavailable: %s", exc)
        raise GigaChatUnavailableError(f"GigaChat auth unavailable: {exc}") from exc

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    prompt = f"""
        Ты senior SEO-специалист.

        На основе данных страницы:
        {metrics}

        Верни ответ строго в формате JSON.

        Формат:

        {{
        "audit": "краткий текст аудита",
        "recommendations": [
            {{
            "action": "что сделать",
            "details": "что конкретно изменить",
            "priority": "High | Medium | Low"
            }}
        ]
        }}

        Никакого текста вне JSON.
        Не используй markdown.
        Не добавляй комментарии.
        """

    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    errors: List[str] = []
    data = None
    for url in _resolve_gigachat_urls():
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except RequestException as exc:
            errors.append(f"{url}: {exc}")

    if data is None:
        logging.error("GigaChat unavailable on all endpoints: %s", " | ".join(errors))
        raise GigaChatUnavailableError("GigaChat unavailable on all endpoints")

   
    content = data["choices"][0]["message"]["content"]

    try:
        parsed = safe_json_parse(content)
    except Exception as exc:
        logging.error("Invalid GigaChat JSON output: %s", exc)
        raise ValueError("GigaChat returned invalid JSON") from exc

    usage = data.get("usage", {})

    if usage:
        logging.info(
            f"Token usage | Prompt: {usage.get('prompt_tokens')} | "
            f"Completion: {usage.get('completion_tokens')} | Total: {usage.get('total_tokens')}"
        )
    else:
        logging.warning("No token usage returned from API")

    return parsed, usage
