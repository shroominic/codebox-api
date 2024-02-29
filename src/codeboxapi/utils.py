""" Utility functions for API requests """

import json
from io import BytesIO
from typing import Optional

import requests
from aiohttp import ClientResponse, ClientSession, FormData
from aiohttp.payload import BytesIOPayload

from .config import settings
from .errors import CodeBoxError


def build_request_data(
    method: str,
    endpoint: str,
    body: Optional[dict] = None,
    files: Optional[dict] = None,
) -> dict:
    """
    Builds a request data dictionary for the requests library.
    """
    return {
        "method": method,
        "url": settings.base_url + endpoint,
        "headers": {
            "Authorization": f"Bearer {settings.api_key}",
        },
        "json": body,
        "files": files,
    }


def handle_response(response: requests.Response):
    """
    Handles a response from the requests library.
    """
    handlers = {
        "application/json": lambda r: json.loads(r.content.decode()),
        "application/octet-stream": lambda r: {
            "content": BytesIO(r.content).read(),
            "name": r.headers["Content-Disposition"].split("=")[1],
        },
        # Add other content type handlers here
    }
    handler = handlers.get(
        response.headers["Content-Type"].split(";")[0], lambda r: r.content.decode()
    )
    if response.status_code != 200:
        raise CodeBoxError(
            http_status=response.status_code,
            content=response.content.decode(),
            headers=dict(response.headers.items()),
        )
    return handler(response)


async def handle_response_async(response: ClientResponse) -> dict:
    """
    Handles a response from the aiohttp library.
    """

    async def json_handler(r: ClientResponse) -> dict:
        return json.loads(await r.text())

    async def file_handler(r: ClientResponse) -> dict:
        return {
            "content": await r.read(),
            "name": r.headers["Content-Disposition"].split("=")[1],
        }

    async def text_handler(r: ClientResponse) -> dict:
        return {"content": await r.text()}

    async def default_handler(r: ClientResponse) -> dict:
        return {"content": await r.text()}

    handlers = {
        "application/json": json_handler,
        "application/octet-stream": file_handler,
        "text/plain": text_handler,
        # Add other content type handlers here
    }
    handler = handlers.get(
        response.headers["Content-Type"].split(";")[0], default_handler
    )
    if response.status != 200:
        error_content = await handler(response)
        raise CodeBoxError(
            http_status=response.status,
            content=str(error_content),
            headers=dict(response.headers.items()),
        )
    return await handler(response)


def base_request(
    method: str,
    endpoint: str,
    body: Optional[dict] = None,
    files: Optional[dict] = None,
) -> dict:
    """
    Makes a request to the CodeBox API.
    """
    request_data = build_request_data(method, endpoint, body, files)
    response = requests.request(**request_data, timeout=270)
    return handle_response(response)


async def abase_request(
    session: ClientSession,
    method: str,
    endpoint: str,
    body: Optional[dict] = None,
    files: Optional[dict] = None,
) -> dict:
    """
    Makes an asynchronous request to the CodeBox API.
    """
    request_data = build_request_data(method, endpoint, body, files)
    if files is not None:
        data = FormData()
        for key, file_tuple in files.items():
            filename, fileobject = file_tuple[
                :2
            ]  # Get the filename and fileobject from the tuple
            payload = BytesIOPayload(BytesIO(fileobject))
            data.add_field(
                key, payload, filename=filename
            )  # Use the filename from the tuple
        request_data.pop("files")
        request_data.pop("json")
        request_data["data"] = data
        response = await session.request(**request_data)
    else:
        request_data.pop("files")
        response = await session.request(**request_data)
    return await handle_response_async(response)


def set_api_key(api_key: str) -> None:
    """
    Manually set the CODEBOX_API_KEY.
    """
    settings.api_key = api_key
