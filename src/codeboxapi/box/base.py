""" Abstract Base Class for Isolated Execution Environments (CodeBox's) """

from abc import ABC, abstractmethod
from datetime import datetime
from os import PathLike
from typing import List, Union

from codeboxapi.schema import CodeBoxFile, CodeBoxOutput, CodeBoxStatus


class BaseBox(ABC):
    """CodeBox Abstract Base Class"""

    def __init__(self, session_id: str = "local") -> None:
        """Initialize the CodeBox instance"""
        self.session_id = session_id
        self.last_interaction = datetime.now()

    @abstractmethod
    def start(self) -> CodeBoxStatus:
        """Startup the CodeBox instance"""

    @abstractmethod
    async def astart(self) -> CodeBoxStatus:
        """Async Startup the CodeBox instance"""

    @abstractmethod
    def status(self) -> CodeBoxStatus:
        """Get the current status of the CodeBox instance"""

    @abstractmethod
    async def astatus(self) -> CodeBoxStatus:
        """Async Get the current status of the CodeBox instance"""

    @abstractmethod
    def run(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        """Execute python code inside the CodeBox instance"""

    @abstractmethod
    async def arun(self, code: Union[str, PathLike]) -> CodeBoxOutput:
        """Async Execute python code inside the CodeBox instance"""

    # TODO: STREAMING

    # TODO: SHELL

    @abstractmethod
    def upload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        """Upload a file as bytes to the CodeBox instance"""

    @abstractmethod
    async def aupload(self, file_name: str, content: bytes) -> CodeBoxStatus:
        """Async Upload a file as bytes to the CodeBox instance"""

    @abstractmethod
    def download(self, file_name: str) -> CodeBoxFile:
        """Download a file as CodeBoxFile schema"""

    @abstractmethod
    async def adownload(self, file_name: str) -> CodeBoxFile:
        """Async Download a file as CodeBoxFile schema"""

    @abstractmethod
    def install(self, package_name: str) -> CodeBoxStatus:
        """Install a python package to the venv"""

    @abstractmethod
    async def ainstall(self, package_name: str) -> CodeBoxStatus:
        """Async Install a python package to the venv"""

    @abstractmethod
    def list_files(self) -> List[CodeBoxFile]:
        """List all available files inside the CodeBox instance"""

    @abstractmethod
    async def alist_files(self) -> List[CodeBoxFile]:
        """Async List all available files inside the CodeBox instance"""

    @abstractmethod
    def restart(self) -> CodeBoxStatus:
        """Restart the jupyter kernel inside the CodeBox instance"""

    @abstractmethod
    async def arestart(self) -> CodeBoxStatus:
        """Async Restart the jupyter kernel inside the CodeBox instance"""

    @abstractmethod
    def stop(self) -> CodeBoxStatus:
        """Terminate the CodeBox instance"""

    @abstractmethod
    async def astop(self) -> CodeBoxStatus:
        """Async Terminate the CodeBox instance"""

    def _update(self) -> None:
        self.last_interaction = datetime.now()

    def _resolve_pathlike(self, code: Union[str, PathLike]) -> str:
        if isinstance(code, PathLike):
            with open(code, "r", encoding="utf-8") as f:
                return f.read()
        return code

    def __enter__(self) -> "BaseBox":
        self.start()
        return self

    async def __aenter__(self) -> "BaseBox":
        await self.astart()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.astop()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.session_id}>"

    def __str__(self) -> str:
        return self.__repr__()
