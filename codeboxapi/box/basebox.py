from uuid import uuid4
from datetime import datetime
from typing_extensions import Self
from abc import ABC
from ..schema import (
    CodeBoxStatus, 
    CodeBoxOutput,
    CodeBoxFile,
)


class BaseBox(ABC):
    """ 
    ABC for Isolated Execution Environments
    """
    
    def __init__(self) -> None:
        self.id = uuid4().int
        self.last_interaction = datetime.now()

    def _update(self) -> None:
        self.last_interaction = datetime.now()
    
    def start(self) -> CodeBoxStatus:
        ...
    
    async def astart(self) -> CodeBoxStatus:
        ...
        
    def status(self) -> CodeBoxStatus:
        ...
    
    async def astatus(self) -> CodeBoxStatus:
        ...
        
    def run(self, code: str) -> CodeBoxOutput:
        ...
    
    async def arun(self, code: str) -> CodeBoxOutput:
        ...
        
    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        ...
    
    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        ...
    
    def download(self, file_name: str) -> CodeBoxFile:
        ...
    
    async def adownload(self, file_name: str) -> CodeBoxFile:
        ...
    
    def install(self, package_name: str) -> CodeBoxStatus:
        ...
    
    async def ainstall(self, package_name: str) -> CodeBoxStatus:
        ...
    
    def list_files(self) -> list[CodeBoxFile]:
        ...
    
    async def alist_files(self) -> list[CodeBoxFile]:
        ...
    
    def restart(self) -> CodeBoxStatus:
        ...
        
    async def arestart(self) -> CodeBoxStatus:
        ...
    
    def stop(self) -> CodeBoxStatus:
        ...
    
    async def astop(self) -> CodeBoxStatus:
        ...
        
    def __enter__(self) -> Self:
        self.start()
        return self
    
    async def __aenter__(self) -> Self:
        await self.astart()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
        
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.astop()

