from uuid import uuid4
from typing import Any
from datetime import datetime
from codeboxapi import settings
from codeboxapi.box import BaseBox
from ..utils import base_request
from ..schema import CodeBoxStatus, CodeBoxOutput


class CodeBox(BaseBox):
    """ 
    Sandboxed Python Interpreter
    """
    
    def __new__(cls, *args, **kwargs):
        if settings.CODEBOX_API_KEY is None:
            from .localbox import LocalBox
            return LocalBox(*args, **kwargs)
        else:
            return super().__new__(cls, *args, **kwargs)
    
    async def astart(self) -> CodeBoxStatus:
        # return self.codebox_request(
        #     method="POST",  # TODO: add start endpoint
        #     endpoint=f"/start",
        # )
        return await self.astatus()
    
    async def codebox_request(
        self, 
        method, 
        endpoint, 
        body=None, 
        files=None,
        content_type="application/json",
    ) -> dict[str, Any]:
        self._update()
        return base_request(
            method=method,
            endpoint=f"/codebox/{self.id//32**10}" + endpoint,
            body=body,
            files=files,
            content_type=content_type,
        )
    
    async def astatus(self):
        return CodeBoxStatus(
            ** await self.codebox_request(
                method="GET",
                endpoint="/",
            )
        )
        
    async def arun(self, code: str):
        return CodeBoxOutput(
            ** await self.codebox_request(
                method="POST",
                endpoint=f"/run",
                body={"code": code},
            )
        )
        
    async def aupload_file(self, name: str, content: bytes) -> dict:
        return await self.codebox_request(
            method="POST",
            endpoint="/upload",
            files={"file": (name, content)},
            content_type=None
        )
    
    async def adownload_file(self, file_name: str) -> dict:
        return await self.codebox_request(
            method="GET",
            endpoint="/download",
            body={"file_name": file_name},
            content_type=None,
        )
        
    async def ainstall_package(self, package_name: str) -> dict:
        return await self.codebox_request(
            method="POST",
            endpoint="/install",
            body={
                "package_name": package_name,
            },
        )
    
    async def aget_available_files(self) -> list[str]:
        return (
            await self.codebox_request(
                method="GET",
                endpoint="/files",
            )
        )["files"]
    
    async def astop(self) -> CodeBoxStatus:
        return CodeBoxStatus(
                ** await self.codebox_request(
                method="POST",
                endpoint="/stop",
            )
        )
