from datetime import datetime
from typing_extensions import Self
from abc import ABC, abstractmethod
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
        self.id: int | None = None
        self.last_interaction = datetime.now()

    def _update(self) -> None:
        self.last_interaction = datetime.now()
    
    @abstractmethod
    def start(self) -> CodeBoxStatus: ...
    
    @abstractmethod
    async def astart(self) -> CodeBoxStatus: ...
    
    @abstractmethod        
    def status(self) -> CodeBoxStatus: ...

    @abstractmethod
    async def astatus(self) -> CodeBoxStatus: ...
    
    @abstractmethod
    def run(self, code: str) -> CodeBoxOutput: ...
    
    @abstractmethod
    async def arun(self, code: str) -> CodeBoxOutput: ...
    
    @abstractmethod
    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus: ...
    
    @abstractmethod
    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus: ...

    @abstractmethod
    def download(self, file_name: str) -> CodeBoxFile: ...
    
    @abstractmethod
    async def adownload(self, file_name: str) -> CodeBoxFile: ...
    
    @abstractmethod
    def install(self, package_name: str) -> CodeBoxStatus: ...
    
    @abstractmethod
    async def ainstall(self, package_name: str) -> CodeBoxStatus: ...
    
    @abstractmethod
    def list_files(self) -> list[CodeBoxFile]: ...
    
    @abstractmethod
    async def alist_files(self) -> list[CodeBoxFile]: ...
    
    # @abstractmethod  # TODO: implement
    # def restart(self) -> CodeBoxStatus: ...
    
    # @abstractmethod  # TODO: implement
    # async def arestart(self) -> CodeBoxStatus: ...
    
    @abstractmethod
    def stop(self) -> CodeBoxStatus: ...
    
    @abstractmethod
    async def astop(self) -> CodeBoxStatus: ...
        
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

