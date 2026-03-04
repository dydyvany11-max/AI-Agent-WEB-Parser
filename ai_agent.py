import requests
import logging
import json
import re
from gs_auth import get_access_token

GIGACHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def safe_json_parse(text: str) -> dict:
    
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return json.loads(text)


def generate_audit(metrics: dict):
    token = get_access_token()

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

    response = requests.post(GIGACHAT_URL, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    data = response.json()

   
    content = data["choices"][0]["message"]["content"]

    
    parsed = safe_json_parse(content)

    usage = data.get("usage", {})

    if usage:
        logging.info(
            f"Token usage | Prompt: {usage.get('prompt_tokens')} | "
            f"Completion: {usage.get('completion_tokens')} | Total: {usage.get('total_tokens')}"
        )
    else:
        logging.warning("No token usage returned from API")

    return parsed, usage