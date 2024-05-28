"""Abstract Base Class for Isolated Execution Environments (CodeBox's)"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import PathLike
from typing import AsyncIterator, BinaryIO, Iterator, Literal, TypedDict


class ExecResult(TypedDict):
    content: str
    content_type: Literal["text", "image"]
    error: str | None


@dataclass
class MetaFile: ...


class BaseBox(ABC):
    """CodeBox Abstract Base Class"""

    @abstractmethod
    def exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
    ) -> ExecResult:
        """Execute python code inside the CodeBox instance"""

    @abstractmethod
    async def aexec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
    ) -> ExecResult:
        """Async Execute python code inside the CodeBox instance"""

    @abstractmethod
    def stream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
    ) -> Iterator[ExecResult]:
        """Stream Chunks of Execute python code inside the CodeBox instance"""

    @abstractmethod
    async def astream_exec(
        self,
        code: str | PathLike,
        language: Literal["python", "bash"] = "python",
    ) -> AsyncIterator[ExecResult]:
        """Async Stream Chunks of Execute python code inside the CodeBox instance"""

    @abstractmethod
    def upload(
        self,
        file_name: str,
        content: BinaryIO | bytes | str,
    ) -> MetaFile:
        """Upload a file as bytes to the CodeBox instance"""

    @abstractmethod
    async def aupload(
        self,
        data: BinaryIO,
        remote_file_path: str,
    ) -> MetaFile:
        """Async Upload a file as bytes to the CodeBox instance"""

    @abstractmethod
    def download(self, remote_file_path: str) -> BinaryIO:
        """Download a file as CodeBoxFile schema"""

    @abstractmethod
    async def adownload(self, remote_file_path: str) -> BinaryIO:
        """Async Download a file as CodeBoxFile schema"""

    @abstractmethod
    def install(
        self,
        packages: list[str],
        installer: Literal["pip", "apt"],
    ) -> bool:
        """Install a python package to the venv"""

    @abstractmethod
    async def ainstall(
        self,
        packages: str,
        installer: Literal["pip", "apt"],
    ) -> bool:
        """Async Install a python package to the venv"""

    @abstractmethod
    def list_files(self) -> list[MetaFile]:
        """List all available files inside the CodeBox instance"""

    @abstractmethod
    async def alist_files(self) -> list[MetaFile]:
        """Async List all available files inside the CodeBox instance"""

    @abstractmethod
    def restart(self) -> bool:
        """Restart the jupyter kernel inside the CodeBox instance"""

    @abstractmethod
    async def arestart(self) -> bool:
        """Async Restart the jupyter kernel inside the CodeBox instance"""

    def _resolve_pathlike(self, code: str | PathLike) -> str:
        if isinstance(code, PathLike):
            with open(code, "r", encoding="utf-8") as f:
                return f.read()
        return code
