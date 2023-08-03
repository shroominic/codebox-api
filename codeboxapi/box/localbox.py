"""
Local implementation of CodeBox.
This is useful for testing and development.c
In case you don't put an api_key,
this is the default CodeBox.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from asyncio.subprocess import Process
from pathlib import Path
from typing import List, Optional, Union
from uuid import uuid4

import aiohttp
import requests
from typing_extensions import Self
from websockets.client import WebSocketClientProtocol
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError
from websockets.sync.client import ClientConnection
from websockets.sync.client import connect as ws_connect_sync

from codeboxapi.box import BaseBox
from codeboxapi.schema import CodeBoxFile, CodeBoxOutput, CodeBoxStatus

from ..config import settings


class LocalBox(BaseBox):
    """
    LocalBox is a CodeBox implementation that runs code locally.
    This is useful for testing and development.
    """

    _instance: Optional[Self] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        else:
            if settings.SHOW_INFO:
                print(
                    "INFO: Using a LocalBox which is not fully isolated\n"
                    "      and not scalable across multiple users.\n"
                    "      Make sure to use a CODEBOX_API_KEY in production.\n"
                    "      Set envar SHOW_INFO=False to not see this again.\n"
                )
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self.port: int = 8888
        self.kernel_id: Optional[dict] = None
        self.ws: Union[WebSocketClientProtocol, ClientConnection, None] = None
        self.jupyter: Union[Process, subprocess.Popen, None] = None
        self.session: Optional[aiohttp.ClientSession] = None

    def start(self) -> CodeBoxStatus:
        os.makedirs(".codebox", exist_ok=True)
        self._check_port()
        if settings.VERBOSE:
            print("Starting kernel...")
            out = None
        else:
            out = subprocess.PIPE
        self._check_installed()
        try:
            python = Path(sys.executable).absolute()
            self.jupyter = subprocess.Popen(
                [
                    python,
                    "-m",
                    "jupyter",
                    "kernelgateway",
                    "--KernelGatewayApp.ip='0.0.0.0'",
                    f"--KernelGatewayApp.port={self.port}",
                ],
                stdout=out,
                stderr=out,
                cwd=".codebox",
            )
        except FileNotFoundError:
            raise ModuleNotFoundError(
                "Jupyter Kernel Gateway not found, please install it with:\n"
                "`pip install jupyter_kernel_gateway`\n"
                "to use the LocalBox."
            )
        while True:
            try:
                response = requests.get(self.kernel_url, timeout=90)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            if settings.VERBOSE:
                print("Waiting for kernel to start...")
            time.sleep(1)

        response = requests.post(
            f"{self.kernel_url}/kernels",
            headers={"Content-Type": "application/json"},
            timeout=90,
        )
        self.kernel_id = response.json()["id"]
        if self.kernel_id is None:
            raise Exception("Could not start kernel")

        self.ws = ws_connect_sync(f"{self.ws_url}/kernels/{self.kernel_id}/channels")

        return CodeBoxStatus(status="started")

    def _check_port(self) -> None:
        try:
            response = requests.get(f"http://localhost:{self.port}", timeout=90)
        except requests.exceptions.ConnectionError:
            pass
        else:
            if response.status_code == 200:
                self.port += 1
                self._check_port()

    def _check_installed(self) -> None:
        """if jupyter-kernel-gateway is installed"""
        import pkg_resources  # type: ignore

        try:
            pkg_resources.get_distribution("jupyter-kernel-gateway")
        except pkg_resources.DistributionNotFound:
            print(
                "Make sure 'jupyter-kernel-gateway' is installed "
                "when using without a CODEBOX_API_KEY.\n"
                "You can install it with 'pip install jupyter-kernel-gateway'."
            )
            raise

    async def astart(self) -> CodeBoxStatus:
        os.makedirs(".codebox", exist_ok=True)
        self.session = aiohttp.ClientSession()
        await self._acheck_port()
        if settings.VERBOSE:
            print("Starting kernel...")
            out = None
        else:
            out = asyncio.subprocess.PIPE
        self._check_installed()
        python = Path(sys.executable).absolute()
        try:
            self.jupyter = await asyncio.create_subprocess_exec(
                python,
                "-m",
                "jupyter",
                "kernelgateway",
                "--KernelGatewayApp.ip='0.0.0.0'",
                f"--KernelGatewayApp.port={self.port}",
                stdout=out,
                stderr=out,
                cwd=".codebox",
            )
        except Exception as e:
            print(e)
            raise ModuleNotFoundError(
                "Jupyter Kernel Gateway not found, please install it with:\n"
                "`pip install jupyter_kernel_gateway`\n"
                "to use the LocalBox."
            )
        while True:
            try:
                response = await self.session.get(self.kernel_url)
                if response.status == 200:
                    break
            except aiohttp.ClientConnectorError:
                pass
            except aiohttp.ServerDisconnectedError:
                pass
            if settings.VERBOSE:
                print("Waiting for kernel to start...")
            await asyncio.sleep(1)

        response = await self.session.post(
            f"{self.kernel_url}/kernels", headers={"Content-Type": "application/json"}
        )
        self.kernel_id = (await response.json())["id"]
        if self.kernel_id is None:
            raise Exception("Could not start kernel")
        self.ws = await ws_connect(f"{self.ws_url}/kernels/{self.kernel_id}/channels")

        return CodeBoxStatus(status="started")

    async def _acheck_port(self) -> None:
        try:
            if self.session is None:
                self.session = aiohttp.ClientSession()
            response = await self.session.get(f"http://localhost:{self.port}")
        except aiohttp.ClientConnectorError:
            pass
        except aiohttp.ServerDisconnectedError:
            pass
        else:
            if response.status == 200:
                self.port += 1
                await self._acheck_port()

    def status(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            status="running"
            if self.kernel_id
            and requests.get(self.kernel_url, timeout=90).status_code == 200
            else "stopped"
        )

    async def astatus(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            status="running"
            if self.kernel_id
            and self.session
            and (await self.session.get(self.kernel_url)).status == 200
            else "stopped"
        )

    def run(
        self,
        code: Optional[str] = None,
        file_path: Optional[os.PathLike] = None,
        retry=3,
    ) -> CodeBoxOutput:
        if not code and not file_path:
            raise ValueError("Code or file_path must be specified!")

        if code and file_path:
            raise ValueError("Can only specify code or the file to read_from!")

        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

        # run code in jupyter kernel
        if retry <= 0:
            raise RuntimeError("Could not connect to kernel")
        if not self.ws:
            self.start()
            if not self.ws:
                raise RuntimeError("Could not connect to kernel")

        if settings.VERBOSE:
            print("Running code:\n", code)

        # send code to kernel
        self.ws.send(
            json.dumps(
                {
                    "header": {
                        "msg_id": (msg_id := uuid4().hex),
                        "msg_type": "execute_request",
                    },
                    "parent_header": {},
                    "metadata": {},
                    "content": {
                        "code": code,
                        "silent": False,
                        "store_history": True,
                        "user_expressions": {},
                        "allow_stdin": False,
                        "stop_on_error": True,
                    },
                    "channel": "shell",
                    "buffers": [],
                }
            )
        )
        result = ""
        while True:
            try:
                if isinstance(self.ws, WebSocketClientProtocol):
                    raise RuntimeError("Mixing asyncio and sync code is not supported")
                received_msg = json.loads(self.ws.recv())
            except ConnectionClosedError:
                self.start()
                return self.run(code, file_path, retry - 1)

            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                if "Requirement already satisfied:" in msg:
                    continue
                result += msg + "\n"
                if settings.VERBOSE:
                    print("Output:\n", result)

            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                result += received_msg["content"]["data"]["text/plain"].strip() + "\n"
                if settings.VERBOSE:
                    print("Output:\n", result)

            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )
                if "text/plain" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
                return CodeBoxOutput(
                    type="error",
                    content="Could not parse output",
                )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                if len(result) > 500:
                    result = "[...]\n" + result[-500:]
                return CodeBoxOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = (
                    f"{received_msg['content']['ename']}: "
                    f"{received_msg['content']['evalue']}"
                )
                if settings.VERBOSE:
                    print("Error:\n", error)
                return CodeBoxOutput(type="error", content=error)

    async def arun(
        self,
        code: str,
        file_path: Optional[os.PathLike] = None,
        retry=3,
    ) -> CodeBoxOutput:
        if file_path:
            raise NotImplementedError(
                "Reading from file is not supported in async mode"
            )

        # run code in jupyter kernel
        if retry <= 0:
            raise RuntimeError("Could not connect to kernel")
        if not self.ws:
            await self.astart()
            if not self.ws:
                raise RuntimeError("Could not connect to kernel")

        if settings.VERBOSE:
            print("Running code:\n", code)

        if not isinstance(self.ws, WebSocketClientProtocol):
            raise RuntimeError("Mixing asyncio and sync code is not supported")

        await self.ws.send(
            json.dumps(
                {
                    "header": {
                        "msg_id": (msg_id := uuid4().hex),
                        "msg_type": "execute_request",
                    },
                    "parent_header": {},
                    "metadata": {},
                    "content": {
                        "code": code,
                        "silent": False,
                        "store_history": True,
                        "user_expressions": {},
                        "allow_stdin": False,
                        "stop_on_error": True,
                    },
                    "channel": "shell",
                    "buffers": [],
                }
            )
        )
        result = ""
        while True:
            try:
                received_msg = json.loads(await self.ws.recv())
            except ConnectionClosedError:
                await self.astart()
                return await self.arun(code, file_path, retry - 1)

            if (
                received_msg["header"]["msg_type"] == "stream"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                msg = received_msg["content"]["text"].strip()
                if "Requirement already satisfied:" in msg:
                    continue
                result += msg + "\n"
                if settings.VERBOSE:
                    print("Output:\n", result)

            elif (
                received_msg["header"]["msg_type"] == "execute_result"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                result += received_msg["content"]["data"]["text/plain"].strip() + "\n"
                if settings.VERBOSE:
                    print("Output:\n", result)

            elif received_msg["header"]["msg_type"] == "display_data":
                if "image/png" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="image/png",
                        content=received_msg["content"]["data"]["image/png"],
                    )
                if "text/plain" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="text",
                        content=received_msg["content"]["data"]["text/plain"],
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):
                if len(result) > 500:
                    result = "[...]\n" + result[-500:]
                return CodeBoxOutput(
                    type="text", content=result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = (
                    f"{received_msg['content']['ename']}: "
                    f"{received_msg['content']['evalue']}"
                )
                if settings.VERBOSE:
                    print("Error:\n", error)
                return CodeBoxOutput(type="error", content=error)

    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        os.makedirs(".codebox", exist_ok=True)
        with open(os.path.join(".codebox", file_name), "wb") as f:
            f.write(content)

        return CodeBoxStatus(status=f"{file_name} uploaded successfully")

    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        return await asyncio.to_thread(self.upload, file_name, content)

    def download(self, file_name: str) -> CodeBoxFile:
        with open(os.path.join(".codebox", file_name), "rb") as f:
            content = f.read()

        return CodeBoxFile(name=file_name, content=content)

    async def adownload(self, file_name: str) -> CodeBoxFile:
        return await asyncio.to_thread(self.download, file_name)

    def install(self, package_name: str) -> CodeBoxStatus:
        self.run(f"!pip install -q {package_name}")
        # restart kernel if needed TODO
        return CodeBoxStatus(status=f"{package_name} installed successfully")

    async def ainstall(self, package_name: str) -> CodeBoxStatus:
        await self.arun(f"!pip install -q {package_name}")
        # restart kernel if needed TODO
        return CodeBoxStatus(status=f"{package_name} installed successfully")

    def list_files(self) -> List[CodeBoxFile]:
        return [
            CodeBoxFile(name=file_name, content=None)
            for file_name in os.listdir(".codebox")
        ]

    async def alist_files(self) -> List[CodeBoxFile]:
        return await asyncio.to_thread(self.list_files)

    def restart(self) -> CodeBoxStatus:
        if self.jupyter is not None:
            self.stop()
        else:
            self.start()
        return CodeBoxStatus(status="restarted")

    async def arestart(self) -> CodeBoxStatus:
        if self.jupyter is not None:
            await self.astop()
        else:
            await self.astart()
        return CodeBoxStatus(status="restarted")

    def stop(self) -> CodeBoxStatus:
        if self.ws is not None:
            try:
                self.ws.close()
            except ConnectionClosedError:
                pass
            self.ws = None

        if self.jupyter is not None:
            self.jupyter.terminate()
            self.jupyter.wait()
            self.jupyter = None
            time.sleep(2)

        return CodeBoxStatus(status="stopped")

    async def astop(self) -> CodeBoxStatus:
        if self.ws is not None:
            try:
                if not isinstance(self.ws, WebSocketClientProtocol):
                    raise RuntimeError("Mixing asyncio and sync code is not supported")
                await self.ws.close()
            except ConnectionClosedError:
                pass
            self.ws = None

        if self.jupyter is not None:
            self.jupyter.terminate()
            self.jupyter = None
            await asyncio.sleep(2)

        if self.session is not None:
            await self.session.close()
            self.session = None

        return CodeBoxStatus(status="stopped")

    @property
    def kernel_url(self) -> str:
        """Return the url of the kernel."""
        return f"http://localhost:{self.port}/api"

    @property
    def ws_url(self) -> str:
        """Return the url of the websocket."""
        return f"ws://localhost:{self.port}/api"
