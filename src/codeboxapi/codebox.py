"""
CodeBox API
~~~~~~~~~~~

The main class for the CodeBox API.

Usage
-----

.. code-block:: python

    from codeboxapi import CodeBox

    codebox.healthcheck()
    codebox.exec("print('Hello World!')")
    codebox.install("matplotlib")
    codebox.upload("test.txt", "This is test file content!")
    codebox.files()
    codebox.download("test.txt")

.. code-block:: python

    from codeboxapi import CodeBox

    await codebox.healthcheck()
    await codebox.exec("print('Hello World!')")
    await codebox.install("matplotlib")
    await codebox.upload("test.txt", "This is test file content!")
    await codebox.files()
    await codebox.download("test.txt")

"""

from abc import ABC, abstractmethod
from functools import partial, wraps
from os import PathLike
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    BinaryIO,
    Callable,
    Coroutine,
    Generator,
    Iterator,
    Literal,
    ParamSpec,
    TypeVar,
)
from warnings import warn

import anyio
from pydantic import BaseModel

from . import utils


class ExecChunk(BaseModel):
    type: Literal["text", "image", "stream", "error"]
    content: str


class ExecResult(BaseModel):
    content: list[ExecChunk]

    @property
    def text(self) -> str:
        return "".join(
            chunk.content
            for chunk in self.content
            if chunk.type == "text" or chunk.type == "stream"
        )

    @property
    def images(self) -> list[str]:
        return [chunk.content for chunk in self.content if chunk.type == "image"]

    @property
    def errors(self) -> list[str]:
        return [chunk.content for chunk in self.content if chunk.type == "error"]


# todo move somewhere more clean
class CodeBoxOutput(BaseModel):
    """Deprecated CodeBoxOutput class"""

    content: str
    type: Literal["stdout", "stderr", "error"]


class CodeBoxFile(BaseModel):
    remote_path: str
    size: int
    codebox: "CodeBox"
    _content: bytes | None = None

    @property
    def name(self) -> str:
        return self.remote_path.split("/")[-1]

    @property
    def content(self) -> bytes:
        return self._content or b"".join(self.codebox.stream_download(self.remote_path))

    @property
    async def acontent(self) -> bytes:
        return self._content or b"".join([
            chunk async for chunk in self.codebox.astream_download(self.remote_path)
        ])

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            for chunk in self.codebox.stream_download(self.remote_path):
                f.write(chunk)

    async def asave(self, path: str) -> None:
        import aiofiles

        async with aiofiles.open(path, "wb") as f:
            async for chunk in self.codebox.astream_download(self.remote_path):
                await f.write(chunk)


T = TypeVar("T")
P = ParamSpec("P")


def deprecated(message: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


class CodeBox(ABC):
    """CodeBox Abstract Base Class"""

    @classmethod
    def create(
        cls,
        api_key: str | None = None,
        factory_id: str | None = None,
    ) -> "CodeBox":
        """
        Creates a CodeBox session
        """
        from .local import LocalBox
        from .remote import RemoteBox

        if api_key == "local":
            return LocalBox()

        if api_key == "docker":
            # return DockerBox()
            raise NotImplementedError("DockerBox is not implemented yet")

        return RemoteBox(factory_id, api_key)

    # SYNC

    def exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> ExecResult:
        """Execute python code inside the CodeBox instance"""
        # todo think about if this maybe better not scripted
        return utils.flatten_exec_result(self.stream_exec(code, language, timeout, cwd))

    @abstractmethod
    def stream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> Generator[ExecChunk, None, None]:
        """Stream Chunks of Execute python code inside the CodeBox instance"""

    @abstractmethod
    def upload(
        self,
        remote_file_path: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        """Upload a file to the CodeBox instance"""

    @abstractmethod
    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> Iterator[bytes]:
        """Download a file as open BinaryIO. Make sure to close the file after use."""

    # ASYNC

    async def aexec(
        self,
        code: str | PathLike,
        language: Literal[
            "python", "bash"
        ] = "python",  # todo differentiate python and jupyter
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> ExecResult:
        """Async Execute python code inside the CodeBox instance"""
        return await utils.async_flatten_exec_result(
            self.astream_exec(code, language, timeout, cwd)
        )

    @abstractmethod
    def astream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> AsyncGenerator[ExecChunk, None]:
        """Async Stream Chunks of Execute python code inside the CodeBox instance"""

    @abstractmethod
    async def aupload(
        self,
        remote_file_path: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        """Async Upload a file to the CodeBox instance"""

    async def adownload(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        return next(
            f for f in (await self.alist_files()) if f.remote_path == remote_file_path
        )

    @abstractmethod
    def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> AsyncIterator[bytes]:
        """Async Download a file as BinaryIO. Make sure to close the file after use."""

    # SCRIPTED METHODS

    async def ahealthcheck(self) -> Literal["healthy", "error"]:
        health = (await self.aexec("echo 'ok'", language="bash")).text
        if health == "ok":
            return "healthy"
        return "error"

    async def ainstall(self, *packages: str) -> str:
        # todo make sure it always uses the correct python venv
        await self.aexec(
            "uv pip install " + " ".join(packages),
            language="bash",
        )
        return " ".join(packages) + " installed successfully"

    async def alist_files(self) -> list[CodeBoxFile]:
        files = (
            await self.aexec(
                "find . -type f -exec du -h {} + | awk '{print $2, $1}' | sort",
                language="bash",
            )
        ).text.splitlines()
        return [
            CodeBoxFile(remote_path=parts[0], size=int(parts[1]), codebox=self)
            for file in files
            if (parts := file.split()) and len(parts) == 2
        ]

    async def alist_packages(self) -> list[str]:
        return (await self.aexec("uv pip list", language="bash")).text.splitlines()

    async def alist_variables(self) -> list[str]:
        return (await self.aexec("%who")).text.splitlines()

    async def arestart(self) -> None:
        """Restart the Jupyter kernel"""
        await self.aexec(r"%restart")

    # DEPRECATED

    @deprecated(
        "There is no need anymore to explicitly start a CodeBox instance.\n"
        "When calling any method you will get assigned a new session.\n"
        "The `.start` method is deprecated. Use `.healthcheck` instead."
    )
    async def astart(self) -> Literal["started", "error"]:
        return "started" if await self.ahealthcheck() == "healthy" else "error"

    @deprecated(
        "The `.stop` method is deprecated. "
        "The session will be closed automatically after the last interaction.\n"
        "(default timeout: 15 minutes)"
    )
    async def astop(self) -> Literal["stopped"]:
        return "stopped"

    @deprecated(
        "The `.run` method is deprecated. Use `.exec` instead.",
    )
    async def arun(self, code: str) -> CodeBoxOutput:
        exec_result = await self.aexec(code, language="python")
        return CodeBoxOutput(type="stdout", content=exec_result.text)

    @deprecated(
        "The `.status` method is deprecated. Use `.healthcheck` instead.",
    )
    async def astatus(self) -> Literal["started", "running", "stopped"]:
        return "running" if await self.ahealthcheck() == "healthy" else "stopped"

    # SYNCIFY

    def __init__(self):
        def syncify(async_func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
            return partial(anyio.run, async_func)

        self.healthcheck = syncify(self.ahealthcheck)
        self.list_files = syncify(self.alist_files)
        self.list_packages = syncify(self.alist_packages)
        self.list_variables = syncify(self.alist_variables)
        self.download = syncify(self.adownload)
        self.restart = syncify(self.arestart)
        self.install = syncify(self.ainstall)
        self.start = syncify(self.astart)
        self.stop = syncify(self.astop)
        self.run = syncify(self.arun)
        self.status = syncify(self.astatus)
