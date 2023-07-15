import os
import json
import time
import requests  # type: ignore
import asyncio
import aiohttp
import subprocess
from uuid import uuid4
from typing_extensions import Self
from websockets.exceptions import ConnectionClosedError
from websockets.client import WebSocketClientProtocol, connect as ws_connect
from websockets.sync.client import connect as ws_connect_sync, ClientConnection
from codeboxapi.box import BaseBox
from codeboxapi.schema import (
    CodeBoxStatus, 
    CodeBoxOutput, 
    CodeBoxFile
)
from ..config import settings


class LocalBox(BaseBox):
    """
    LocalBox is a CodeBox implementation that runs code locally.
    This is useful for testing and development.c
    In case you don't put an api_key, 
    this is the default CodeBox.
    """
    _instance: Self | None = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        else:
            print(
                "INFO: Using a LocalBox which is not isolated.\n"
                "      This is only for testing and development.\n"
                "      Make sure to put an API-Key in production.\n"
            )
        return cls._instance
        
    def __init__(self, port: int = 8888) -> None:
        super().__init__()
        self.port = port
        self.kernel: dict | None = None
        self.ws: WebSocketClientProtocol | ClientConnection | None = None
        self.subprocess: asyncio.subprocess.Process | subprocess.Popen | None = None
        self.session: aiohttp.ClientSession | None = None
    
    def start(self) -> CodeBoxStatus:
        os.makedirs(".codebox", exist_ok=True)
        self._check_port()
        if settings.VERBOSE:
            print("Starting kernel...")
            out = None
        else:
            out = subprocess.PIPE
        self.subprocess = subprocess.Popen(
            [
                "jupyter",
                "kernelgateway",
                "--KernelGatewayApp.ip='0.0.0.0'",
                f"--KernelGatewayApp.port={self.port}",
            ],
            stdout=out,
            stderr=out,
            cwd=".codebox",
        )
        while True:
            try:
                response = requests.get(self.kernel_url)
                if response.status_code == 200: break
            except requests.exceptions.ConnectionError:
                pass
            if settings.VERBOSE:
                print("Waiting for kernel to start...")
            time.sleep(1)
        
        response = requests.post(
            f"{self.kernel_url}/kernels", headers={"Content-Type": "application/json"}
        )
        self.kernel = response.json()
        if self.kernel is None:
            raise Exception("Could not start kernel")
        
        self.ws = ws_connect_sync(
            f"{self.ws_url}/kernels/{self.kernel['id']}/channels"
        )
        
        return CodeBoxStatus(status="started")
    
    def _check_port(self) -> None:
        try:
            response = requests.get(f"http://localhost:{self.port}")
        except requests.exceptions.ConnectionError:
            pass
        else:
            if response.status_code == 200:
                self.port += 1
                self._check_port()
    
    async def astart(self) -> CodeBoxStatus:
        os.makedirs(".codebox", exist_ok=True)
        self.session = aiohttp.ClientSession()
        await self._acheck_port()
        if settings.VERBOSE:
            print("Starting kernel...")
            out = None
        else:
            out = asyncio.subprocess.PIPE
        self.subprocess = await asyncio.create_subprocess_exec(
            "jupyter",
            "kernelgateway",
            "--KernelGatewayApp.ip='0.0.0.0'",
            f"--KernelGatewayApp.port={self.port}",
            stdout=out,
            stderr=out,
            cwd=".codebox"
        )
        while True:
            try:
                response = await self.session.get(self.kernel_url)
                if response.status == 200: break
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
        self.kernel = await response.json()
        if self.kernel is None:
            raise Exception("Could not start kernel")
        self.ws = await ws_connect(
            f"{self.ws_url}/kernels/{self.kernel['id']}/channels"
        )
        
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
            status = "running" 
                if self.kernel 
                    and requests.get(self.kernel_url).status_code == 200
                else "stopped"
        )
    
    async def astatus(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            status = "running" 
                if self.kernel 
                    and self.session
                    and (await self.session.get(self.kernel_url)).status == 200
                else "stopped"
        )
    
    def run(self, code: str, retry=3) -> CodeBoxOutput:
        # run code in jupyter kernel
        if retry <= 0: 
            raise RuntimeError("Could not connect to kernel")
        if not self.ws: 
            self.start()
            if not self.ws: raise RuntimeError("Could not connect to kernel")
        
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
                return self.run(code, retry-1)
            
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
                        content=received_msg["content"]["data"]["image/png"]
                    )
                elif "text/plain" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="text", 
                        content=received_msg["content"]["data"]["text/plain"]
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):  
                if len(result) > 500: 
                    result = "[...]\n" + result[-500:]
                return CodeBoxOutput(
                    type = "text", 
                    content = result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                if settings.VERBOSE:
                    print("Error:\n", error)
                return CodeBoxOutput(
                    type="error", 
                    content=error
                )
    
    async def arun(self, code: str, retry=3) -> CodeBoxOutput:
        # run code in jupyter kernel
        if retry <= 0: 
            raise RuntimeError("Could not connect to kernel")
        if not self.ws: 
            await self.astart()
            if not self.ws: raise RuntimeError("Could not connect to kernel")
        
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
                return await self.arun(code, retry-1)
            
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
                        content=received_msg["content"]["data"]["image/png"]
                    )
                elif "text/plain" in received_msg["content"]["data"]:
                    return CodeBoxOutput(
                        type="text", 
                        content=received_msg["content"]["data"]["text/plain"]
                    )
            elif (
                received_msg["header"]["msg_type"] == "status"
                and received_msg["parent_header"]["msg_id"] == msg_id
                and received_msg["content"]["execution_state"] == "idle"
            ):  
                if len(result) > 500: 
                    result = "[...]\n" + result[-500:]
                return CodeBoxOutput(
                    type = "text", 
                    content = result or "code run successfully (no output)"
                )

            elif (
                received_msg["header"]["msg_type"] == "error"
                and received_msg["parent_header"]["msg_id"] == msg_id
            ):
                error = f"{received_msg['content']['ename']}: {received_msg['content']['evalue']}"
                if settings.VERBOSE:
                    print("Error:\n", error)
                return CodeBoxOutput(
                    type="error", 
                    content=error
                )
        
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
        
        return CodeBoxFile(
            name=file_name,
            content=content
        )
        
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
    
    def list_files(self) -> list[CodeBoxFile]:
        return [
            CodeBoxFile(name=file_name, content=None)
            for file_name in os.listdir(".codebox")
        ]
        
    async def alist_files(self) -> list[CodeBoxFile]:
        return await asyncio.to_thread(self.list_files)
    
    def stop(self) -> CodeBoxStatus:
        if self.ws is not None:
            try:
                self.ws.close()
            except ConnectionClosedError:
                pass
            self.ws = None
        
        if self.subprocess is not None:
            self.subprocess.terminate()
            self.subprocess.wait()
            self.subprocess = None
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
            
        if self.subprocess is not None:
            self.subprocess.terminate()
            self.subprocess = None
            await asyncio.sleep(2)
            
        if self.session is not None:
            await self.session.close()
            self.session = None
        
        return CodeBoxStatus(status="stopped")

    @property
    def kernel_url(self) -> str:
        return f"http://localhost:{self.port}/api"
    
    @property
    def ws_url(self) -> str:
        return f"ws://localhost:{self.port}/api"
