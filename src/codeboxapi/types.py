import typing as t
from dataclasses import dataclass

from .codebox import CodeBox


@dataclass
class RemoteFile:
    path: str
    remote: CodeBox
    _size: t.Optional[int] = None
    _content: t.Optional[bytes] = None

    @property
    def name(self) -> str:
        return self.path.split("/")[-1]

    def get_content(self) -> bytes:
        if self._content is None:
            self._content = b"".join(self.remote.stream_download(self.path))
        return self._content

    async def aget_content(self) -> bytes:
        if self._content is None:
            self._content = b""
            async for chunk in self.remote.astream_download(self.path):
                self._content += chunk
        return self._content

    def get_size(self) -> int:
        if self._size is None:
            self._size = len(self.get_content())
        return self._size

    async def aget_size(self) -> int:
        if self._size is None:
            self._size = len(await self.aget_content())
        return self._size

    def save(self, local_path: str) -> None:
        with open(local_path, "wb") as f:
            for chunk in self.remote.stream_download(self.path):
                f.write(chunk)

    async def asave(self, local_path: str) -> None:
        try:
            import aiofiles  # type: ignore
        except ImportError:
            raise RuntimeError(
                "aiofiles is not installed. Please install it with "
                '`pip install "codeboxapi[local]"`'
            )

        async with aiofiles.open(local_path, "wb") as f:
            async for chunk in self.remote.astream_download(self.path):
                await f.write(chunk)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if self._size is None:
            return f"RemoteFile({self.path})"
        return f"RemoteFile({self.path}, {self._size} bytes)"


@dataclass
class ExecChunk:
    """
    A chunk of output from an execution.
    The type is one of:
    - txt: text output
    - img: image output
    - err: error output
    """

    type: t.Literal["txt", "img", "err"]
    content: str


@dataclass
class ExecResult:
    chunks: list[ExecChunk]

    @property
    def text(self) -> str:
        return "".join(chunk.content for chunk in self.chunks if chunk.type == "txt")

    @property
    def images(self) -> list[str]:
        return [chunk.content for chunk in self.chunks if chunk.type == "img"]

    @property
    def errors(self) -> list[str]:
        return [chunk.content for chunk in self.chunks if chunk.type == "err"]


@dataclass
class CodeBoxOutput:
    """Deprecated CodeBoxOutput class"""

    content: str
    type: t.Literal["stdout", "stderr", "image/png", "error"]

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.content == other
        if isinstance(other, CodeBoxOutput):
            return self.content == other.content and self.type == other.type
        return False


class CodeBoxFile:
    """Deprecated CodeBoxFile class"""

    def __init__(self, name: str, content: t.Optional[bytes] = None) -> None:
        from .utils import deprecated

        deprecated(
            "The CodeBoxFile class is deprecated. Use RemoteFile for file handling "
            "or plain bytes for content instead."
        )(lambda: None)()
        self.name = name
        self.content = content

    @classmethod
    def from_path(cls, path: str) -> "CodeBoxFile":
        import os

        with open(path, "rb") as f:
            return cls(name=os.path.basename(path), content=f.read())
