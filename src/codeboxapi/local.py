"""
Local implementation of CodeBox.
This is useful for testing and development.c
In case you don't put an api_key,
this is the default CodeBox.
"""

import asyncio
import os
import subprocess
from os import PathLike
from queue import Queue
from threading import Thread
from typing import (
    AsyncGenerator,
    AsyncIterator,
    BinaryIO,
    Generator,
    Iterator,
    Literal,
    Self,
    Union,
)

from jupyter_client.manager import KernelManager

from . import utils
from .codebox import CodeBox, CodeBoxFile, ExecChunk
from .config import settings


# todo implement inactivity timeout to close kernel after 10 minutes of last method call
class LocalBox(CodeBox):
    """
    LocalBox is a CodeBox implementation that runs code locally.
    This is useful for testing and development.
    """

    _instance: Self | None = None

    def __new__(cls, *_, **__):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        else:
            if settings.debug:
                print(
                    "INFO: Using a LocalBox which is not fully isolated\n"
                    "      and not scalable across multiple parallel users.\n"
                    "      Make sure to use a CODEBOX_API_KEY in production.\n"
                    "      Set envar CODEBOX_DEBUG=False to not see this again.\n"
                )
        return cls._instance

    def __init__(self, /, **kwargs) -> None:
        super().__init__()
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
        self.kernel = KernelManager()
        self.cwd = settings.default_working_dir
        # startup
        utils.check_installed("jupyter-client")
        os.makedirs(self.cwd, exist_ok=True)
        if not self.kernel.is_alive():
            self.kernel = KernelManager(ip=os.getenv("LOCALHOST", "127.0.0.1"))
        self.kernel.start_kernel(cwd=self.cwd)

    def stream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> Generator[ExecChunk, None, None]:
        """
        Creates a Generator that streams chunks of the output of the code execution
        """
        code = utils.resolve_pathlike(code)

        if language == "python":
            msg_queue: Queue[dict | None] = Queue()

            def output_hook(msg):
                msg_queue.put(msg)

            def execute_code():
                self.kernel.client().execute_interactive(code, output_hook=output_hook)
                msg_queue.put(None)

            execution_thread = Thread(target=execute_code)
            execution_thread.start()

            while True:
                msg = msg_queue.get()
                if msg is None:
                    break
                yield utils.parse_message(msg)

            execution_thread.join()

        elif language == "bash":
            with utils.raise_timeout(timeout):
                process = subprocess.Popen(
                    code,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                if process.stdout:
                    for line in process.stdout:
                        yield ExecChunk(type="stream", content=line.strip())
                process.wait()
                if process.returncode != 0:
                    yield ExecChunk(type="error", content="Command execution failed")
        else:
            raise ValueError(f"Unsupported language: {language}")

    def upload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        with utils.raise_timeout(timeout):
            file_path = os.path.join(self.cwd, file_name)
            with open(file_path, "wb") as file:
                if isinstance(content, str):
                    file.write(content.encode())
                elif isinstance(content, BinaryIO):
                    while chunk := content.read(8192):
                        file.write(chunk)
                else:
                    file.write(content)
            file_size = os.path.getsize(file_path)
            return CodeBoxFile(
                remote_path=file_path,
                size=file_size,
                codebox=self,
            )

    def stream_download(
        self,
        file_name: str,
        timeout: float | None = None,
    ) -> Iterator[bytes]:
        with utils.raise_timeout(timeout):
            with open(os.path.join(self.cwd, file_name), "rb") as file:
                yield file.read()

    async def astream_exec(
        self,
        code: Union[str, PathLike],
        language: Literal["python", "bash"] = "python",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> AsyncGenerator[ExecChunk, None]:
        code = utils.resolve_pathlike(code)

        if language == "python":
            msg_queue: asyncio.Queue = asyncio.Queue()

            async def output_hook(msg):
                await msg_queue.put(msg)

            execution_task = asyncio.create_task(
                self.kernel.client()._async_execute_interactive(
                    code, output_hook=output_hook, timeout=timeout
                )
            )

            try:
                while not execution_task.done() or not msg_queue.empty():
                    msg = await msg_queue.get()
                    yield utils.parse_message(msg)
            finally:
                if not execution_task.done():
                    execution_task.cancel()
                    try:
                        await execution_task
                    except asyncio.CancelledError:
                        pass

        elif language == "bash":
            async with asyncio.timeout(timeout):
                process = await asyncio.create_subprocess_shell(
                    code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=cwd,
                )
                if process.stdout:
                    async for line in process.stdout:
                        yield ExecChunk(type="stream", content=line.decode().strip())
                await process.wait()
                if process.returncode != 0:
                    yield ExecChunk(type="error", content="Command execution failed")

        else:
            raise ValueError(f"Unsupported language: {language}")

    async def aupload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        import aiofiles

        async with asyncio.timeout(timeout):
            file_path = os.path.join(self.cwd, file_name)
            async with aiofiles.open(file_path, "wb") as file:
                if isinstance(content, str):
                    await file.write(content.encode())
                elif isinstance(content, BinaryIO):
                    while chunk := content.read(8192):
                        await file.write(chunk)
                else:
                    await file.write(content)

            file_size = await aiofiles.os.path.getsize(file_path)
            return CodeBoxFile(
                remote_path=file_path,
                size=file_size,
                codebox=self,
            )

    async def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> AsyncIterator[bytes]:
        import aiofiles

        async with asyncio.timeout(timeout):
            async with aiofiles.open(
                os.path.join(self.cwd, remote_file_path), "rb"
            ) as f:
                yield await f.read()

    def __del__(self):
        self.kernel.shutdown_kernel()
