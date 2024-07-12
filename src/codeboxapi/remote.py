from json import loads
from os import PathLike
from typing import AsyncGenerator, AsyncIterator, BinaryIO, Generator, Iterator, Literal
from uuid import uuid4

import anyio
import httpx

from . import utils
from .codebox import CodeBox, CodeBoxFile, ExecChunk
from .config import settings


class RemoteBox(CodeBox):
    """
    Sandboxed Python Interpreter
    """

    def __new__(cls, *args, **kwargs):
        if kwargs.pop("local", False) or settings.api_key == "local":
            from .local import LocalBox

            return LocalBox(*args, **kwargs)
        return super().__new__(cls)

    def __init__(
        self,
        factory_id: str | None = None,
        api_key: str | None = None,
    ) -> None:
        super().__init__()
        self.session_id = uuid4().hex
        self.factory_id = factory_id
        self.api_key = api_key or settings.api_key
        self.aclient = httpx.AsyncClient(
            base_url=f"{settings.base_url}/codebox/{self.session_id}"
        )

    def stream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> Generator[ExecChunk, None, None]:
        async_gen = self.astream_exec(code, language, timeout, cwd)
        return (chunk for chunk in anyio.run(utils.collect_async_gen, async_gen))

    def upload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        return anyio.run(self.aupload, file_name, content, timeout)

    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> Iterator[bytes]:
        return anyio.run(
            utils.collect_async_gen, self.astream_download(remote_file_path, timeout)
        )

    async def astream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> AsyncGenerator[ExecChunk, None]:
        code = utils.resolve_pathlike(code)
        async with self.aclient.stream(
            method="POST",
            url="/stream",
            timeout=timeout,
            params={"code": code, "language": language, "cwd": cwd},
        ) as response:
            async for chunk in response.aiter_text():
                yield ExecChunk(**loads(chunk))

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
            codebox=self,
        )

    async def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> AsyncIterator[bytes]:
        async with self.aclient.stream(
            method="GET",
            url="/download",
            timeout=timeout,
            params={"file_name": remote_file_path},
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
