import re
import typing as t
from os import PathLike, getenv
from uuid import uuid4

import anyio
import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .codebox import CodeBox
from .types import ExecChunk, RemoteFile
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
        session_id: t.Optional[str] = None,
        api_key: t.Optional[t.Union[str, t.Literal["local", "docker"]]] = None,
        factory_id: t.Optional[t.Union[str, t.Literal["default"]]] = None,
        base_url: t.Optional[str] = None,
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

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    def stream_exec(
        self,
        code: t.Union[str, PathLike],
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: t.Optional[float] = None,
        cwd: t.Optional[str] = None,
    ) -> t.Generator[ExecChunk, None, None]:
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

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    async def astream_exec(
        self,
        code: t.Union[str, PathLike],
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: t.Optional[float] = None,
        cwd: t.Optional[str] = None,
    ) -> t.AsyncGenerator[ExecChunk, None]:
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

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    def upload(
        self,
        file_name: str,
        content: t.Union[t.BinaryIO, bytes, str],
        timeout: t.Optional[float] = None,
    ) -> "RemoteFile":
        from .types import RemoteFile

        if isinstance(content, str):
            content = content.encode("utf-8")
        self.client.post(
            url="/files/upload",
            files={"file": (file_name, content)},
            timeout=timeout,
        ).raise_for_status()
        return RemoteFile(path=file_name, remote=self)

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    async def aupload(
        self,
        remote_file_path: str,
        content: t.Union[t.BinaryIO, bytes, str],
        timeout: t.Optional[float] = None,
    ) -> "RemoteFile":
        from .types import RemoteFile

        if isinstance(content, str):
            content = content.encode("utf-8")
        response = await self.aclient.post(
            url="/files/upload",
            files={"file": (remote_file_path, content)},
            timeout=timeout,
        )
        response.raise_for_status()
        return RemoteFile(path=remote_file_path, remote=self)

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    def stream_download(
        self,
        remote_file_path: str,
        timeout: t.Optional[float] = None,
    ) -> t.Generator[bytes, None, None]:
        with self.client.stream(
            method="GET",
            url=f"/files/download/{remote_file_path}",
            timeout=timeout,
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_bytes():
                yield chunk

    @retry(
        retry=retry_if_exception(
            lambda e: isinstance(e, httpx.HTTPStatusError)
            and e.response.status_code == 502
        ),
        wait=wait_exponential(multiplier=1, min=5, max=150),
        stop=stop_after_attempt(3),
    )
    async def astream_download(
        self,
        remote_file_path: str,
        timeout: t.Optional[float] = None,
    ) -> t.AsyncGenerator[bytes, None]:
        async with self.aclient.stream(
            method="GET",
            url=f"/files/download/{remote_file_path}",
            timeout=timeout,
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk
