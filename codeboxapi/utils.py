from codeboxapi.config import settings
import requests
import json


def base_request(
    method: str, 
    endpoint: str,  
    body: dict | None = None,
    files: dict | None = None,
    content_type: str = "application/json",
) -> dict:
    response = requests.request(
        method=method,
        url=settings.CODEBOX_BASE_URL + endpoint,
        headers={
            "Content-Type": content_type,
            "Authorization": f"Bearer {settings.CODEBOX_API_KEY}",
        },
        json=body,
        files=files,
    )
    content = response.content.decode()
    if response.status_code == 200:
        if response.headers['Content-Type'] == 'application/json':
            return json.loads(content)
        else:
            return content
    else:
        raise Exception(f"Error: {response.status_code} {content}")


def set_api_key(api_key: str) -> None:
    settings.CODEBOX_API_KEY = api_key
