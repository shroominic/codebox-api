"""Utility functions for API requests"""

import json
from asyncio import sleep as asleep
from io import BytesIO
from time import sleep
from typing import Optional

import requests
from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout, FormData
from aiohttp.payload import BytesIOPayload

from codeboxapi.config import settings
from codeboxapi.errors import CodeBoxError


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
        "url": settings.CODEBOX_BASE_URL + endpoint,
        "headers": {
            "Authorization": f"Bearer {settings.CODEBOX_API_KEY}",
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
        try:
            json_body = response.json()
        except Exception:
            json_body = {"": response.text}
        raise CodeBoxError(
            http_status=response.status_code,
            json_body=json_body,
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

    async def default_handler(r: ClientResponse) -> dict:
        return {"content": await r.text()}

    handlers = {
        "application/json": json_handler,
        "application/octet-stream": file_handler,
        # Add other content type handlers here
    }
    if response.status != 200:
        try:
            json_body = await response.json()
        except Exception:
            json_body = {"": await response.text()}

        raise CodeBoxError(
            http_status=response.status,
            json_body=json_body,
            headers=dict(response.headers.items()),
        )
    handler = handlers.get(
        response.headers["Content-Type"].split(";")[0], default_handler
    )
    return await handler(response)


def base_request(
    method: str,
    endpoint: str,
    body: Optional[dict] = None,
    files: Optional[dict] = None,
    timeout: int = 420,
    retries: int = 3,
    backoff_factor: float = 0.3,
) -> dict:
    """
    Makes a request to the CodeBox API with retry logic.

    Args:
    - method: HTTP method as a string.
    - endpoint: API endpoint as a string.
    - body: Optional dictionary containing the JSON body.
    - files: Optional dictionary containing file data.
    - retries: Maximum number of retries on failure.
    - backoff_factor: Multiplier for delay between retries (exponential backoff).

    Returns:
    - A dictionary response from the API.
    """
    request_data = build_request_data(method, endpoint, body, files)
    for attempt in range(retries):
        try:
            response = requests.request(**request_data, timeout=timeout)
            return handle_response(response)
        except requests.RequestException as e:
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2**attempt)
                sleep(sleep_time)
            else:
                raise e
    raise CodeBoxError(http_status=500, json_body={"error": "Max retries exceeded"})


async def abase_request(
    session: ClientSession,
    method: str,
    endpoint: str,
    body: Optional[dict] = None,
    files: Optional[dict] = None,
    timeout: int = 420,
    retries: int = 3,
    backoff_factor: float = 0.3,
) -> dict:
    """
    Makes an asynchronous request to the CodeBox API with retry functionality.

    Args:
    - session: The aiohttp ClientSession.
    - method: HTTP method as a string.
    - endpoint: API endpoint as a string.
    - body: Optional dictionary containing the JSON body.
    - files: Optional dictionary containing file data.
    - retries: Maximum number of retries on failure.
    - backoff_factor: Multiplier for delay between retries (exponential backoff).

    Returns:
    - A dictionary response from the API.
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
    else:
        request_data.pop("files")

    for attempt in range(retries):
        try:
            response = await session.request(
                **request_data, timeout=ClientTimeout(total=timeout)
            )
            return await handle_response_async(response)
        except ClientError as e:
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2**attempt)
                await asleep(sleep_time)
            else:
                raise e
    raise CodeBoxError(http_status=500, json_body={"error": "Max retries exceeded"})


def set_api_key(api_key: str) -> None:
    """
    Manually set the CODEBOX_API_KEY.
    """
    settings.CODEBOX_API_KEY = api_key
