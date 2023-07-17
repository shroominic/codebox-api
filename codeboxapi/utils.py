import json
import requests  # type: ignore
from typing import Optional
from aiohttp import ClientSession, ClientResponse, FormData
from codeboxapi.config import settings


def build_request_data(
    method: str, 
    endpoint: str, 
    body: Optional[dict] = None,
    files: Optional[dict] = None, 
    content_type: str = "application/json"
) -> dict:
    return {
        "method": method,
        "url": settings.CODEBOX_BASE_URL + endpoint,
        "headers": {
            "Content-Type": content_type,
            "Authorization": f"Bearer {settings.CODEBOX_API_KEY}",
        },
        "json": body,
        "files": files,
    }


def handle_response(response: requests.Response):
    handlers = {
        "application/json": lambda r: json.loads(r.content.decode()),
        # Add other content type handlers here
    }
    handler = handlers.get(response.headers['Content-Type'].split(';')[0], lambda r: r.content.decode())
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} {response.content.decode()}")
    return handler(response)


async def handle_response_async(response: ClientResponse) -> dict:
    async def json_handler(r: ClientResponse) -> dict:
        return json.loads(await r.text())
        
    async def default_handler(r: ClientResponse) -> dict:
        return {"text": await r.text()}  # TODO: fix schema
    
    handlers = {
        "application/json": json_handler,
        # Add other content type handlers here
    }
    handler = handlers.get(response.headers['Content-Type'].split(';')[0], default_handler)
    if response.status != 200:
        raise Exception(f"Error: {response.status} {await response.text()}")
    return await handler(response)


def base_request(
    method: str, 
    endpoint: str, 
    body: Optional[dict] = None,
    files: Optional[dict] = None, 
    content_type: str = "application/json"
) -> dict:
    request_data = build_request_data(method, endpoint, body, files, content_type)
    response = requests.request(**request_data)
    return handle_response(response)


async def abase_request(
    session: ClientSession, 
    method: str, 
    endpoint: str, 
    body: Optional[dict] = None,
    files: Optional[dict] = None,
    content_type: str = "application/json"
) -> dict:
    request_data = build_request_data(method, endpoint, body, files, content_type)
    if files is not None:
        data = FormData()
        for key, file in files.items():
            data.add_field(key, file)
        request_data.pop("files")
        request_data.pop("json")
        request_data["data"] = data
        response = await session.request(method, request_data["url"], data=data)
    else:
        request_data.pop("files")
        response = await session.request(**request_data)
    return await handle_response_async(response)


def set_api_key(api_key: str) -> None:
    settings.CODEBOX_API_KEY = api_key
