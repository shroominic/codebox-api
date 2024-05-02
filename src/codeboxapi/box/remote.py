"""
CodeBox API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the CodeBox API.

Usage
-----

.. code-block:: python

    from codeboxapi import CodeBox

    with CodeBox() as codebox:
        codebox.status()
        codebox.run(code="print('Hello World!')")
        codebox.install("python-package")
        codebox.upload("test.txt", b"Hello World!")
        codebox.list_files()
        codebox.download("test.txt")

.. code-block:: python

    from codeboxapi import CodeBox

    async with CodeBox() as codebox:
        await codebox.astatus()
        await codebox.arun(code="print('Hello World!')")
        await codebox.ainstall("python-package")
        await codebox.aupload("test.txt", b"Hello World!")
        await codebox.alist_files()
        await codebox.adownload("test.txt")

"""

from asyncio import sleep as asleep
from os import PathLike
from time import sleep
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from aiohttp import ClientSession

from ..config import settings
from ..schema import CodeBoxFile, CodeBoxOutput, CodeBoxStatus
from ..utils import abase_request, base_request
from .base import BaseBox


class RemoteBox(BaseBox):
    """
    Sandboxed Python Interpreter
    """

    def __new__(cls, *args, **kwargs):
        if kwargs.pop("local", False) or settings.api_key == "local":
            from .local import LocalBox

            return LocalBox(*args, **kwargs)

        return super().__new__(cls)

    def __init__(self, session_id: Optional[str] = None, **kwargs) -> None:
        self._temp_id_cache = uuid4().hex
        super().__init__(session_id or self._temp_id_cache, **kwargs)
        self.aiohttp_session: Optional[ClientSession] = None

    @classmethod
    def from_id(cls, session_id: Union[int, UUID, str], **kwargs) -> "RemoteBox":
        return cls(
            session_id=(
                UUID(int=session_id).hex
                if isinstance(session_id, int)
                else session_id.hex
                if isinstance(session_id, UUID)
                else session_id
            ),
            **kwargs,
        )

    def codebox_request(self, method, endpoint, *args, **kwargs) -> Dict[str, Any]:
        """General request to the CodeBox API"""
        self._update()
        # temp fix
        session_id = UUID(self.session_id).int
        return base_request(
            method,
            f"/codebox/{session_id}" + endpoint,
            *args,
            **kwargs,
        )

    async def acodebox_request(
        self, method, endpoint, *args, **kwargs
    ) -> Dict[str, Any]:
        """General async request to the CodeBox API"""
        self._update()
        self.aiohttp_session = self.aiohttp_session or ClientSession()
        # temp fix
        session_id = UUID(self.session_id).int
        return await abase_request(
            self.aiohttp_session,
            method,
            f"/codebox/{session_id}" + endpoint,
            *args,
            **kwargs,
        )

    # def start(self) -> CodeBoxStatus:
    #     return self.status()

    # async def astart(self) -> CodeBoxStatus:
    #     return await self.astatus()

    def start(self) -> CodeBoxStatus:
        if self.session_id != self._temp_id_cache:
            while self.status().status == "starting":
                sleep(1)
            return self.status()
        self.session_id = UUID(
            int=base_request(
                method="GET",
                endpoint="/codebox/start",
            )["id"]
        ).hex
        return CodeBoxStatus(status="started")

    async def astart(self) -> CodeBoxStatus:
        self.aiohttp_session = self.aiohttp_session or ClientSession()
        if self.session_id != self._temp_id_cache:
            while (await self.astatus()).status == "starting":
                await asleep(1)
            return await self.astatus()
        self.session_id = UUID(
            int=(
                await abase_request(
                    self.aiohttp_session, method="GET", endpoint="/codebox/start"
                )
            )["id"]
        ).hex
        return CodeBoxStatus(status="started")

    def status(self):
        return CodeBoxStatus(
            **self.codebox_request(
                method="GET",
                endpoint="/",
            )
        )

    async def astatus(self):
        return CodeBoxStatus(
            **await self.acodebox_request(
                method="GET",
                endpoint="/",
            )
        )

    def run(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        return CodeBoxOutput(
            **self.codebox_request(
                method="POST",
                endpoint="/run",
                body={"code": self._resolve_pathlike(code)},
            )
        )

    async def arun(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        return CodeBoxOutput(
            **await self.acodebox_request(
                method="POST",
                endpoint="/run",
                body={"code": self._resolve_pathlike(code)},
            )
        )

    # TODO: STREAMING

    # TODO: SHELL

    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        return CodeBoxStatus(
            **self.codebox_request(
                method="POST",
                endpoint="/upload",
                files={"file": (file_name, content)},
            )
        )

    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        return CodeBoxStatus(
            **await self.acodebox_request(
                method="POST",
                endpoint="/upload",
                files={"file": (file_name, content)},
            )
        )

    def download(self, file_name: str) -> CodeBoxFile:
        return CodeBoxFile(
            **self.codebox_request(
                method="GET",
                endpoint="/download",
                body={"file_name": file_name},
            )
        )

    async def adownload(self, file_name: str) -> CodeBoxFile:
        return CodeBoxFile(
            **await self.acodebox_request(
                method="GET",
                endpoint="/download",
                body={"file_name": file_name},
            )
        )

    def install(self, package_name: str) -> CodeBoxStatus:
        return CodeBoxStatus(
            **self.codebox_request(
                method="POST",
                endpoint="/install",
                body={
                    "package_name": package_name,
                },
            )
        )

    async def ainstall(self, package_name: str) -> CodeBoxStatus:
        return CodeBoxStatus(
            **await self.acodebox_request(
                method="POST",
                endpoint="/install",
                body={
                    "package_name": package_name,
                },
            )
        )

    def list_files(self) -> List[CodeBoxFile]:
        return [
            CodeBoxFile(name=file_name, content=None)
            for file_name in (
                self.codebox_request(
                    method="GET",
                    endpoint="/files",
                )
            )["files"]
        ]

    async def alist_files(self) -> List[CodeBoxFile]:
        return [
            CodeBoxFile(name=file_name, content=None)
            for file_name in (
                await self.acodebox_request(
                    method="GET",
                    endpoint="/files",
                )
            )["files"]
        ]

    def restart(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            **self.codebox_request(
                method="POST",
                endpoint="/restart",
            )
        )

    async def arestart(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            **await self.acodebox_request(
                method="POST",
                endpoint="/restart",
            )
        )

    def stop(self) -> CodeBoxStatus:
        return CodeBoxStatus(
            **self.codebox_request(
                method="POST",
                endpoint="/stop",
            )
        )

    async def astop(self) -> CodeBoxStatus:
        status = CodeBoxStatus(
            **await self.acodebox_request(
                method="POST",
                endpoint="/stop",
            )
        )
        if self.aiohttp_session:
            await self.aiohttp_session.close()
            self.aiohttp_session = None
        return status

    def __del__(self):
        if self.aiohttp_session:
            import asyncio

            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.aiohttp_session.close())
            self.aiohttp_session = None
