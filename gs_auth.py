import requests
import time
import uuid
import os
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


load_dotenv()

_token = None
_token_expire_time = 0


def get_access_token():
    global _token, _token_expire_time

    if _token and time.time() < _token_expire_time:
        return _token

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = {
        "scope": "GIGACHAT_API_PERS"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {os.getenv('GIGACHAT_AUTH_KEY')}"
    }

    response = requests.post(url, headers=headers, data=payload, verify = False)
    response.raise_for_status()

    data = response.json()

    _token = data["access_token"]
    _token_expire_time = data["expires_at"] - 60  

    return _token