import re
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

    def __new__(cls, *args, **kwargs) -> "RemoteBox":
        # This is a hack to ignore the CodeBox.__new__ factory method.
        return object.__new__(cls)

    def __init__(
        self,
        session_id: str | None = None,
        api_key: str | Literal["local", "docker"] | None = None,
        factory_id: str | Literal["default"] | None = None,
        base_url: str | None = None,
    ) -> None:
        self.session_id = session_id or uuid4().hex
        self.factory_id = factory_id or getenv("CODEBOX_FACTORY_ID", "default")
        assert self.factory_id is not None
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
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while match := re.match(
                    r"<(txt|img|err)>(.*?)</\1>", buffer, re.DOTALL
                ):
                    _, end = match.span()
                    t, c = match.groups()
                    yield ExecChunk(type=t, content=c)  # type: ignore[arg-type]
                    buffer = buffer[end:]

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
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    while match := re.match(
                        r"<(txt|img|err)>(.*?)</\1>", buffer, re.DOTALL
                    ):
                        _, end = match.span()
                        t, c = match.groups()
                        yield ExecChunk(type=t, content=c)  # type: ignore[arg-type]
                        buffer = buffer[end:]
        except RuntimeError as e:
            if "loop is closed" not in str(e):
                raise e
            await anyio.sleep(0.1)
            async for c in self.astream_exec(code, kernel, timeout, cwd):
                yield c

    def upload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        if isinstance(content, str):
            content = content.encode("utf-8")
        response = self.client.post(
            url="/files/upload",
            files={"file": (file_name, content)},
            timeout=timeout,
        )
        json = response.json()
        # todo fix: this is bad code
        del json["codebox_id"]
        del json["codebox_api_key"]
        del json["codebox_factory_id"]
        return CodeBoxFile(
            **json,
            codebox_api_key=self.api_key,
            codebox_factory_id=self.factory_id,
            codebox_id=self.session_id,
        )

    async def aupload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        if isinstance(content, str):
            content = content.encode("utf-8")
        response = await self.aclient.post(
            url="/files/upload",
            files={"file": (file_name, content)},
            timeout=timeout,
        )
        json = response.json()
        # todo this is a sign of bad design
        del json["codebox_id"]
        del json["codebox_api_key"]
        del json["codebox_factory_id"]
        return CodeBoxFile(
            **json,
            codebox_api_key=self.api_key,
            codebox_factory_id=self.factory_id,
            codebox_id=self.session_id,
        )

    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> Generator[bytes, None, None]:
        with self.client.stream(
            method="GET",
            url=f"/files/download/{remote_file_path}",
            timeout=timeout,
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
            url=f"/files/download/{remote_file_path}",
            timeout=timeout,
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
