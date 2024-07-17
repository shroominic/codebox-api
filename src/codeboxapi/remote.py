from os import PathLike, getenv
from typing import AsyncGenerator, BinaryIO, Generator, Literal
from uuid import uuid4

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
        base_url: str = "https://codeboxapi.com/api/v2",
        _new: bool = False,
    ) -> None:
        self.session_id = session_id or uuid4().hex
        self.factory_id = factory_id
        self.api_key = (
            api_key
            or getenv("CODEBOX_API_KEY")
            or raise_error("CODEBOX_API_KEY is required")
        )
        self.base_url = f"{base_url}/codebox/{self.session_id}"
        self.headers = {"Factory-Id": self.factory_id} if self.factory_id else None
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)
        self.aclient = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)

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
            url="/stream",
            timeout=timeout,
            params={"code": code, "kernel": kernel, "cwd": cwd},
        ) as response:
            for chunk in response.iter_text():
                yield ExecChunk.decode(chunk)

    async def astream_exec(
        self,
        code: str | PathLike,
        kernel: Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> AsyncGenerator[ExecChunk, None]:
        code = resolve_pathlike(code)
        async with self.aclient.stream(
            method="POST",
            url="/stream",
            timeout=timeout,
            params={"code": code, "kernel": kernel, "cwd": cwd},
        ) as response:
            async for chunk in response.aiter_text():
                yield ExecChunk.decode(chunk)

    async def aupload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        if isinstance(content, str):
            content = content.encode("utf-8")
        return CodeBoxFile(
            **(
                await self.aclient.post(
                    url="/upload",
                    files={"file": (file_name, content)},
                    timeout=timeout,
                )
            ).json(),
            codebox_id=self.session_id,
        )

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
