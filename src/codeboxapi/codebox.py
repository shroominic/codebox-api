"""
CodeBox API
~~~~~~~~~~~

The main class for the CodeBox API.

Usage
-----

.. code-block:: python

    from codeboxapi import CodeBox

    codebox = CodeBox(api_key="local")

    codebox.healthcheck()
    codebox.exec("print('Hello World!')")
    codebox.upload("test.txt", "This is test file content!")
    codebox.exec("!pip install matplotlib", kernel="bash")
    codebox.list_files()
    codebox.download("test.txt")

.. code-block:: python

    from codeboxapi import CodeBox

    codebox = CodeBox(api_key="local")

    await codebox.ahealthcheck()
    await codebox.aexec("print('Hello World!')")
    await codebox.ainstall("matplotlib")
    await codebox.aupload("test.txt", "This is test file content!")
    await codebox.alist_files()
    await codebox.adownload("test.txt")

"""

import os
import typing as t
from importlib import import_module

import anyio

from .utils import async_flatten_exec_result, deprecated, flatten_exec_result, syncify

if t.TYPE_CHECKING:
    from .types import CodeBoxOutput, ExecChunk, ExecResult, RemoteFile


class CodeBox:
    def __new__(
        cls,
        session_id: str | None = None,
        api_key: str | t.Literal["local", "docker"] | None = None,
        factory_id: str | t.Literal["default"] | None = None,
    ) -> "CodeBox":
        """
        Creates a CodeBox session
        """
        api_key = api_key or os.getenv("CODEBOX_API_KEY", "local")
        factory_id = factory_id or os.getenv("CODEBOX_FACTORY_ID", "default")
        if api_key == "local":
            return import_module("codeboxapi.local").LocalBox()

        if api_key == "docker":
            return import_module("codeboxapi.docker").DockerBox()
        return import_module("codeboxapi.remote").RemoteBox()

    def __init__(
        self,
        session_id: str | None = None,
        api_key: str | t.Literal["local", "docker"] | None = None,
        factory_id: str | t.Literal["default"] | None = None,
        **_: bool,
    ) -> None:
        self.session_id = session_id or "local"
        self.api_key = api_key or os.getenv("CODEBOX_API_KEY", "local")
        self.factory_id = factory_id or os.getenv("CODEBOX_FACTORY_ID", "default")

    # SYNC

    def exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> "ExecResult":
        """Execute code inside the CodeBox instance"""
        return flatten_exec_result(self.stream_exec(code, kernel, timeout, cwd))

    def stream_exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> t.Generator["ExecChunk", None, None]:
        """Executes the code and streams the result."""
        raise NotImplementedError("Abstract method, please use a subclass.")

    def upload(
        self,
        remote_file_path: str,
        content: t.BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> "RemoteFile":
        """Upload a file to the CodeBox instance"""
        raise NotImplementedError("Abstract method, please use a subclass.")

    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> t.Generator[bytes, None, None]:
        """Download a file as open BinaryIO. Make sure to close the file after use."""
        raise NotImplementedError("Abstract method, please use a subclass.")

    # ASYNC

    async def aexec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> "ExecResult":
        """Async Execute python code inside the CodeBox instance"""
        return await async_flatten_exec_result(
            self.astream_exec(code, kernel, timeout, cwd)
        )

    def astream_exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> t.AsyncGenerator["ExecChunk", None]:
        """Async Stream Chunks of Execute python code inside the CodeBox instance"""
        raise NotImplementedError("Abstract method, please use a subclass.")

    async def aupload(
        self,
        remote_file_path: str,
        content: t.BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> "RemoteFile":
        """Async Upload a file to the CodeBox instance"""
        raise NotImplementedError("Abstract method, please use a subclass.")

    async def adownload(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> "RemoteFile":
        return [f for f in (await self.alist_files()) if f.path in remote_file_path][0]

    def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> t.AsyncGenerator[bytes, None]:
        """Async Download a file as BinaryIO. Make sure to close the file after use."""
        raise NotImplementedError("Abstract method, please use a subclass.")

    # HELPER METHODS

    async def ahealthcheck(self) -> t.Literal["healthy", "error"]:
        return (
            "healthy"
            if "ok" in (await self.aexec("echo ok", kernel="bash")).text
            else "error"
        )

    async def ainstall(self, *packages: str) -> str:
        # todo make sure it always uses the correct python venv
        await self.aexec(
            "uv pip install " + " ".join(packages),
            kernel="bash",
        )
        return " ".join(packages) + " installed successfully"

    async def alist_files(self) -> list["RemoteFile"]:
        from .types import RemoteFile

        files = (
            await self.aexec(
                "find . -type f -exec du -h {} + | awk '{print $2, $1}' | sort",
                kernel="bash",
            )
        ).text.splitlines()
        return [
            RemoteFile(
                path=parts[0].removeprefix("./"),
                remote=self,
                _size=self._parse_size(parts[1]),
            )
            for file in files
            if (parts := file.split(" ")) and len(parts) == 2
        ]

    def _parse_size(self, size_str: str) -> int:
        """Convert human-readable size to bytes."""
        units = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
        try:
            number = float(size_str[:-1])
            unit = size_str[-1].upper()
            return int(number * units.get(unit, 1))
        except ValueError:
            return -1

    async def alist_packages(self) -> list[str]:
        return (
            await self.aexec(
                "uv pip list | tail -n +3 | cut -d ' ' -f 1",
                kernel="bash",
            )
        ).text.splitlines()

    async def ashow_variables(self) -> dict[str, str]:
        vars = [
            line.strip() for line in (await self.aexec("%who")).text.strip().split()
        ]
        return {v: (await self.aexec(f"print({v}, end='')")).text for v in vars}

    async def arestart(self) -> None:
        """Restart the Jupyter kernel"""
        await self.aexec(r"%restart")

    async def akeep_alive(self, minutes: int = 15) -> None:
        """Keep the CodeBox instance alive for a certain amount of minutes"""

        async def ping(cb: CodeBox, d: int) -> None:
            for _ in range(d):
                await cb.ahealthcheck()
                await anyio.sleep(60)

        async with anyio.create_task_group() as tg:
            tg.start_soon(ping, self, minutes)

    # SYNCIFY

    def download(
        self, remote_file_path: str, timeout: float | None = None
    ) -> "RemoteFile":
        return syncify(self.adownload)(remote_file_path, timeout)

    def healthcheck(self) -> str:
        return syncify(self.ahealthcheck)()

    def install(self, *packages: str) -> str:
        return syncify(self.ainstall)(*packages)

    def list_files(self) -> list["RemoteFile"]:
        return syncify(self.alist_files)()

    def list_packages(self) -> list[str]:
        return syncify(self.alist_packages)()

    def show_variables(self) -> dict[str, str]:
        return syncify(self.ashow_variables)()

    def restart(self) -> None:
        return syncify(self.arestart)()

    def keep_alive(self, minutes: int = 15) -> None:
        return syncify(self.akeep_alive)(minutes)

    # DEPRECATED

    @deprecated(
        "There is no need anymore to explicitly start a CodeBox instance.\n"
        "When calling any method you will get assigned a new session.\n"
        "The `.start` method is deprecated. Use `.healthcheck` instead."
    )
    async def astart(self) -> t.Literal["started", "error"]:
        return "started" if (await self.ahealthcheck()) == "healthy" else "error"

    @deprecated(
        "The `.stop` method is deprecated. "
        "The session will be closed automatically after the last interaction.\n"
        "(default timeout: 15 minutes)"
    )
    async def astop(self) -> t.Literal["stopped"]:
        return "stopped"

    @deprecated(
        "The `.run` method is deprecated. Use `.exec` instead.",
    )
    async def arun(self, code: str | os.PathLike) -> "CodeBoxOutput":
        from .types import CodeBoxOutput

        exec_result = await self.aexec(code, kernel="ipython")
        if exec_result.images:
            return CodeBoxOutput(type="image/png", content=exec_result.images[0])
        if exec_result.errors:
            return CodeBoxOutput(type="stderr", content=exec_result.errors[0])
        return CodeBoxOutput(type="stdout", content=exec_result.text)

    @deprecated(
        "The `.status` method is deprecated. Use `.healthcheck` instead.",
    )
    async def astatus(self) -> t.Literal["started", "running", "stopped"]:
        return "running" if await self.ahealthcheck() == "healthy" else "stopped"

    @deprecated(
        "The `.start` method is deprecated. Use `.healthcheck` instead.",
    )
    def start(self) -> t.Literal["started", "error"]:
        return syncify(self.astart)()

    @deprecated(
        "The `.stop` method is deprecated. "
        "The session will be closed automatically after the last interaction.\n"
        "(default timeout: 15 minutes)"
    )
    def stop(self) -> t.Literal["stopped"]:
        return syncify(self.astop)()

    @deprecated(
        "The `.run` method is deprecated. Use `.exec` instead.",
    )
    def run(self, code: str | os.PathLike) -> "CodeBoxOutput":
        return syncify(self.arun)(code)

    @deprecated(
        "The `.status` method is deprecated. Use `.healthcheck` instead.",
    )
    def status(self) -> t.Literal["started", "running", "stopped"]:
        return syncify(self.astatus)()
