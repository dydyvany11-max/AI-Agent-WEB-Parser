import requests
import logging
from gs_auth import get_access_token

GIGACHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def generate_audit(metrics: dict):

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Ты профессиональный SEO-специалист.
    Данные страницы:
    {metrics}
    Сделай аудит.
    """

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(GIGACHAT_URL, headers=headers, json=payload, verify=False)
    response.raise_for_status()

    data = response.json()

    audit_text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

   
    if usage:
        logging.info(
            f"Token usage | "
            f"Prompt: {usage.get('prompt_tokens')} | "
            f"Completion: {usage.get('completion_tokens')} | "
            f"Total: {usage.get('total_tokens')}"
        )
    else:
        logging.warning("No token usage returned from API")

    return audit_text, usage