from os import PathLike, getenv
from typing import AsyncGenerator, BinaryIO, Generator, Literal
from uuid import uuid4

import anyio
import httpx

from .codebox import CodeBox, CodeBoxFile, ExecChunk
from .utils import raise_error, resolve_pathlike


class RemoteBox(CodeBox):
    """
    Sandboxed Python Interpreter
    """

    def __new__(cls) -> "RemoteBox":
        # This is a hack to ignore the CodeBox.__new__ factory method.
        return object.__new__(cls)

    def __init__(
        self,
        session_id: str | None = None,
        api_key: str | Literal["local", "docker"] = "local",
        factory_id: str | Literal["default"] = "default",
        base_url: str | None = None,
    ) -> None:
        self.session_id = session_id or uuid4().hex
        self.factory_id = factory_id
        self.api_key = (
            api_key
            or getenv("CODEBOX_API_KEY")
            or raise_error("CODEBOX_API_KEY is required")
        )
        self.base_url = base_url or getenv(
            "CODEBOX_BASE_URL", "https://codeboxapi.com/api/v2"
        )
        self.url = f"{self.base_url}/codebox/{self.session_id}"
        self.headers = {
            "Factory-Id": self.factory_id,
            "Authorization": f"Bearer {self.api_key}",
        }
        self.client = httpx.Client(base_url=self.url, headers=self.headers)
        self.aclient = httpx.AsyncClient(base_url=self.url, headers=self.headers)

    def stream_exec(
        self,
        code: str | PathLike,
        kernel: Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> Generator[ExecChunk, None, None]:
        code = resolve_pathlike(code)
        with self.client.stream(
            method="POST",
            url="/exec",
            timeout=timeout,
            json={"code": code, "kernel": kernel, "cwd": cwd},
        ) as response:
            response.raise_for_status()
            img_buffer = ""
            for chunk in response.iter_text():
                if chunk.startswith("img;") and not chunk.endswith("=="):
                    img_buffer += chunk
                elif img_buffer and chunk.endswith("=="):
                    yield ExecChunk.decode(img_buffer + chunk)
                    img_buffer = ""
                else:
                    yield ExecChunk.decode(chunk)

    async def astream_exec(
        self,
        code: str | PathLike,
        kernel: Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> AsyncGenerator[ExecChunk, None]:
        code = resolve_pathlike(code)
        try:
            async with self.aclient.stream(
                method="POST",
                url="/exec",
                timeout=timeout,
                json={"code": code, "kernel": kernel, "cwd": cwd},
            ) as response:
                response.raise_for_status()
                img_buffer = ""
                async for chunk in response.aiter_text():
                    if chunk.startswith("img;") and not chunk.endswith("=="):
                        img_buffer += chunk
                    elif img_buffer and chunk.endswith("=="):
                        yield ExecChunk.decode(img_buffer + chunk)
                        img_buffer = ""
                    else:
                        yield ExecChunk.decode(chunk)
        except RuntimeError as e:
            if "loop is closed" not in str(e):
                raise e
            await anyio.sleep(0.1)
            async for c in self.astream_exec(code, kernel, timeout, cwd):
                yield c

    def upload(
        self,
        remote_file_path: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        if isinstance(content, str):
            content = content.encode("utf-8")
        response = self.client.post(
            url="/upload",
            files={"file": (remote_file_path, content)},
            timeout=timeout,
        )
        return CodeBoxFile(**response.json())

    async def aupload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        if isinstance(content, str):
            content = content.encode("utf-8")
        response = await self.aclient.post(
            url="/upload",
            files={"file": (file_name, content)},
            timeout=timeout,
        )
        return CodeBoxFile(**response.json())

    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> Generator[bytes, None, None]:
        with self.client.stream(
            method="GET",
            url="/download",
            timeout=timeout,
            params={"file_name": remote_file_path},
        ) as response:
            for chunk in response.iter_bytes():
                yield chunk

    async def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> AsyncGenerator[bytes, None]:
        async with self.aclient.stream(
            method="GET",
            url="/download",
            timeout=timeout,
            params={"file_name": remote_file_path},
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
