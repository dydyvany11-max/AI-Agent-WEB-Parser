import os
import time
import uuid

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

_token = None
_token_expire_time = 0


class GigaChatAuthClient:
    def __init__(self, oauth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"):
        self.oauth_url = oauth_url

    def get_access_token(self) -> str:
        global _token, _token_expire_time

        if _token and time.time() < _token_expire_time:
            return _token

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {os.getenv('GIGACHAT_AUTH_KEY')}",
        }
        payload = {"scope": "GIGACHAT_API_PERS"}

        response = requests.post(self.oauth_url, headers=headers, data=payload, verify=False, timeout=20)
        response.raise_for_status()
        data = response.json()

        _token = data["access_token"]
        _token_expire_time = data["expires_at"] - 60
        return _token
