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

from datetime import datetime
from os import PathLike
from typing import Any, Dict, List, Optional
from uuid import UUID

from aiohttp import ClientSession

from codeboxapi.box.basebox import BaseBox
from codeboxapi.config import settings
from codeboxapi.schema import CodeBoxFile, CodeBoxOutput, CodeBoxStatus
from codeboxapi.utils import abase_request, base_request


class CodeBox(BaseBox):
    """
    Sandboxed Python Interpreter
    """

    def __new__(cls, *args, **kwargs):
        if (
            kwargs.pop("local", False)
            or settings.CODEBOX_API_KEY is None
            or settings.CODEBOX_API_KEY == "local"
        ):
            from .localbox import LocalBox

            return LocalBox(*args, **kwargs)

        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session_id: Optional[UUID] = kwargs.get("id", None)
        self.aiohttp_session: Optional[ClientSession] = None

    @classmethod
    def from_id(cls, session_id: UUID) -> "CodeBox":
        return cls(session_id=session_id)

    def _update(self) -> None:
        """Update last interaction time"""
        if self.session_id is not None:
            raise RuntimeError("Make sure to start your CodeBox before using it.")
        self.last_interaction = datetime.now()

    def codebox_request(self, method, endpoint, *args, **kwargs) -> Dict[str, Any]:
        """Basic request to the CodeBox API"""
        self._update()
        return base_request(
            method, f"/codebox/{self.session_id}" + endpoint, *args, **kwargs
        )

    async def acodebox_request(
        self, method, endpoint, *args, **kwargs
    ) -> Dict[str, Any]:
        """Basic async request to the CodeBox API"""
        self._update()
        if self.aiohttp_session is None:
            self.aiohttp_session = ClientSession()
        return await abase_request(
            self.aiohttp_session,
            method,
            f"/codebox/{self.session_id}" + endpoint,
            *args,
            **kwargs,
        )

    def start(self) -> CodeBoxStatus:
        self.session_id = base_request(
            method="GET",
            endpoint="/codebox/start",
        )["id"]
        return CodeBoxStatus(status="started")

    async def astart(self) -> CodeBoxStatus:
        self.aiohttp_session = ClientSession()
        self.session_id = (
            await abase_request(
                self.aiohttp_session,
                method="GET",
                endpoint="/codebox/start",
            )
        )["id"]
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

    def run(
        self, code: Optional[str] = None, file_path: Optional[PathLike] = None
    ) -> CodeBoxOutput:
        if not code and not file_path:  # R0801
            raise ValueError("Code or file_path must be specified!")

        if code and file_path:
            raise ValueError("Can only specify code or the file to read_from!")

        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

        return CodeBoxOutput(
            **self.codebox_request(
                method="POST",
                endpoint="/run",
                body={"code": code},
            )
        )

    async def arun(
        self, code: str, file_path: Optional[PathLike] = None
    ) -> CodeBoxOutput:
        if file_path:  # TODO: Implement this
            raise NotImplementedError(
                "Reading from FilePath is not supported in async mode yet!"
            )

        return CodeBoxOutput(
            **await self.acodebox_request(
                method="POST",
                endpoint="/run",
                body={"code": code},
            )
        )

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
