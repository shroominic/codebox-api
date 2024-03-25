"""
Local implementation of CodeBox.
This is useful for testing and development.c
In case you don't put an api_key,
this is the default CodeBox.
"""

import asyncio
import os
import subprocess
from asyncio import sleep as asleep
from importlib.metadata import PackageNotFoundError, distribution
from os import PathLike
from queue import Queue
from threading import Thread
from time import sleep
from typing import AsyncGenerator, Generator, List, Optional, Union

from jupyter_client.manager import KernelManager

from ..box import BaseBox
from ..config import settings
from ..schema import CodeBoxFile, CodeBoxOutput, CodeBoxStatus


class LocalBox(BaseBox):
    """
    LocalBox is a CodeBox implementation that runs code locally.
    This is useful for testing and development.
    """

    _instance: Optional["LocalBox"] = None

    def __new__(cls, *_, **__):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        else:
            if settings.show_info:
                print(
                    "INFO: Using a LocalBox which is not fully isolated\n"
                    "      and not scalable across multiple users.\n"
                    "      Make sure to use a CODEBOX_API_KEY in production.\n"
                    "      Set envar CODEBOX_SHOW_INFO=False to not see this again.\n"
                )
        return cls._instance

    def __init__(self, /, **kwargs) -> None:
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
        super().__init__(session_id=kwargs.pop("session_id", "local"))
        self.kernel = KernelManager()
        self.cwd = settings.default_working_dir

    def start(self) -> CodeBoxStatus:
        self._check_installed()
        os.makedirs(self.cwd, exist_ok=True)
        if not self.kernel.is_alive():
            self.kernel = KernelManager(
                ip=os.getenv("LOCALHOST", "127.0.0.1"),
            )
        self.kernel.start_kernel()
        return CodeBoxStatus(status="started")

    def _check_installed(self) -> None:
        try:
            distribution("jupyter-client")
        except PackageNotFoundError:
            print(
                "Make sure 'jupyter-client' is installed "
                "when using without a CODEBOX_API_KEY.\n"
                "You can install it with 'pip install jupyter-client'.\n"
            )
            raise

    async def astart(self) -> CodeBoxStatus:
        self._check_installed()
        os.makedirs(self.cwd, exist_ok=True)
        if not await self.kernel._async_is_alive():
            self.kernel = KernelManager(
                ip=os.getenv("LOCALHOST", "127.0.0.1"),
            )
        await self.kernel._async_start_kernel()
        return CodeBoxStatus(status="started")

    def status(self) -> CodeBoxStatus:
        return CodeBoxStatus(status="running" if self.kernel.is_alive() else "stopped")

    async def astatus(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            status="running" if await self.kernel._async_is_alive() else "stopped"
        )

    def run(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        code = self._resolve_pathlike(code)

        if settings.verbose:
            print(f"\033[90m{code}\033[0m")

        msg_stream = []
        self.kernel.client().execute_interactive(
            code, output_hook=lambda msg: msg_stream.append(msg)
        )
        return self._parse_messages(msg_stream)

    async def arun(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        code = self._resolve_pathlike(code)

        msg_stream = []
        await self.kernel.client()._async_execute_interactive(
            code, output_hook=lambda msg: msg_stream.append(msg)
        )
        return self._parse_messages(msg_stream)

    def stream_run(
        self, code: Union[str, PathLike]
    ) -> Generator[CodeBoxOutput, None, None]:
        code = self._resolve_pathlike(code)
        msg_queue = Queue[dict | None]()

        def output_hook(msg):
            msg_queue.put(msg)

        def execute_code():
            self.kernel.client().execute_interactive(code, output_hook=output_hook)
            # Signal the end of execution
            msg_queue.put(None)

        # Start code execution in a separate thread
        execution_thread = Thread(target=execute_code)
        execution_thread.start()

        # Yield messages from the queue as they arrive
        while True:
            msg = msg_queue.get()  # This will block until a message is available
            if msg is None:
                break  # None is used as a signal to indicate the end of execution
            yield self._parse_message(msg)

        # Wait for the execution thread to finish
        execution_thread.join()

    async def astream_run(
        self, code: Union[str, PathLike]
    ) -> AsyncGenerator[CodeBoxOutput, None]:
        code = self._resolve_pathlike(code)
        msg_queue: asyncio.Queue = asyncio.Queue()

        async def output_hook(msg):
            await msg_queue.put(msg)

        execution_task = asyncio.create_task(
            self.kernel.client()._async_execute_interactive(
                code, output_hook=output_hook
            )
        )

        try:
            while not execution_task.done() or not msg_queue.empty():
                msg = await msg_queue.get()
                yield self._parse_message(msg)
        finally:
            if not execution_task.done():
                execution_task.cancel()
                try:
                    await execution_task
                except asyncio.CancelledError:
                    pass

    def _parse_message(self, message: dict) -> CodeBoxOutput:
        msg = message
        if msg["msg_type"] == "stream":
            return CodeBoxOutput(content=msg["content"]["text"].strip(), type="stream")
        elif msg["msg_type"] == "execute_result":
            CodeBoxOutput(
                content=msg["content"]["data"]["text/plain"].strip(), type="text"
            )
        elif msg["msg_type"] == "display_data":
            if "image/png" in msg["content"]["data"]:
                return CodeBoxOutput(
                    type="image/png",
                    content=msg["content"]["data"]["image/png"],
                )
            if "text/plain" in msg["content"]["data"]:
                return CodeBoxOutput(type="text", content=msg["data"]["text/plain"])

            return CodeBoxOutput(type="error", content="Could not parse output")
        elif msg["msg_type"] == "error":
            error = f"{msg['content']['ename']}: " f"{msg['content']['evalue']}"
            if settings.verbose:
                print("Error:\n", error)
            return CodeBoxOutput(type="error", content=error)
        return CodeBoxOutput(type="empty", content="")

    def _parse_messages(self, messages: List[dict]) -> CodeBoxOutput:
        result = ""
        for msg in messages:
            if msg["msg_type"] == "stream":
                result += msg["content"]["text"].strip() + "\n"
            elif msg["msg_type"] == "execute_result":
                result += msg["content"]["data"]["text/plain"].strip() + "\n"
            elif msg["msg_type"] == "display_data":
                if "image/png" in msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="image/png",
                        content=msg["content"]["data"]["image/png"],
                    )
                if "text/plain" in msg["content"]["data"]:
                    return CodeBoxOutput(type="text", content=msg["data"]["text/plain"])

                return CodeBoxOutput(type="error", content="Could not parse output")
            elif (
                msg["msg_type"] == "status"
                and msg["content"]["execution_state"] == "idle"
            ):
                if len(result) > 500:
                    result = "[...]\n" + result[-500:]
                return CodeBoxOutput(
                    type="text", content=result or "run successfully (no output)"
                )
            elif msg["msg_type"] == "error":
                error = f"{msg['content']['ename']}: " f"{msg['content']['evalue']}"
                if settings.verbose:
                    print("Error:\n", error)
                return CodeBoxOutput(type="error", content=error)
        return CodeBoxOutput(type="error", content="No output")

    def shell(self, cmd: str) -> CodeBoxOutput:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return CodeBoxOutput(type="text", content=result.stdout)
        except subprocess.CalledProcessError as e:
            return CodeBoxOutput(type="error", content=e.stderr)

    async def ashell(self, cmd: str) -> CodeBoxOutput:
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return CodeBoxOutput(type="text", content=stdout.decode())
            else:
                return CodeBoxOutput(type="error", content=stderr.decode())
        except Exception as e:
            return CodeBoxOutput(type="error", content=str(e))

    def shell_stream(self, cmd: str) -> Generator[CodeBoxOutput, None, None]:
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if process.stdout:
            for line in process.stdout:
                yield CodeBoxOutput(type="stream", content=line.strip())
        process.wait()
        if process.returncode != 0:
            yield CodeBoxOutput(type="error", content="Command execution failed")

    async def ashell_stream(self, cmd: str) -> AsyncGenerator[CodeBoxOutput, None]:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        if process.stdout:
            async for line in process.stdout:
                yield CodeBoxOutput(type="stream", content=line.decode().strip())
        await process.wait()
        if process.returncode != 0:
            yield CodeBoxOutput(type="error", content="Command execution failed")

    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        os.makedirs(self.cwd, exist_ok=True)
        with open(os.path.join(self.cwd, file_name), "wb") as f:
            f.write(content)

        return CodeBoxStatus(status=f"{file_name} uploaded successfully")

    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        return await asyncio.to_thread(self.upload, file_name, content)

    def download(self, file_name: str) -> CodeBoxFile:
        with open(os.path.join(self.cwd, file_name), "rb") as f:
            content = f.read()

        return CodeBoxFile(name=file_name, content=content)

    async def adownload(self, file_name: str) -> CodeBoxFile:
        return await asyncio.to_thread(self.download, file_name)

    def install(self, package_name: str) -> CodeBoxStatus:
        if "ERROR" in str(logs := self.run(f"!uv pip install {package_name}")):
            return CodeBoxStatus(status="Error: " + logs.content)
        self.restart()
        if "No module named" in str(
            logs := self.run(
                f"try:\n    import {package_name}\nexcept Exception as e:\n    print(e)"
            )
        ):
            return CodeBoxStatus(status="Error: " + logs.content)
        return CodeBoxStatus(status=f"{package_name} installed successfully")

    async def ainstall(self, package_name: str) -> CodeBoxStatus:
        if "ERROR" in str(logs := await self.arun(f"!uv pip install {package_name}")):
            return CodeBoxStatus(status="Error: " + logs.content)
        await self.arestart()
        if "No module named" in str(
            logs := await self.arun(
                f"try:\n    import {package_name}\nexcept Exception as e:\n    print(e)"
            )
        ):
            return CodeBoxStatus(status="Error: " + logs.content)
        return CodeBoxStatus(status=f"{package_name} installed successfully")

    def list_files(self) -> List[CodeBoxFile]:
        return [
            CodeBoxFile(name=file_name, content=None)
            for file_name in os.listdir(self.cwd)
        ]

    async def alist_files(self) -> List[CodeBoxFile]:
        return await asyncio.to_thread(self.list_files)

    def restart(self) -> CodeBoxStatus:
        self.kernel.restart_kernel()
        sleep(3)
        return CodeBoxStatus(status="restarted")

    async def arestart(self) -> CodeBoxStatus:
        await self.kernel._async_restart_kernel()
        await asleep(3)
        return CodeBoxStatus(status="restarted")

    def stop(self) -> CodeBoxStatus:
        self.kernel.shutdown_kernel()
        return CodeBoxStatus(status="stopped")

    async def astop(self) -> CodeBoxStatus:
        await self.kernel._async_shutdown_kernel()
        return CodeBoxStatus(status="stopped")
