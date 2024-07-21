import os
import signal
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial, reduce, wraps
from importlib.metadata import PackageNotFoundError, distribution
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Generator,
    Iterator,
    Literal,
    NoReturn,
    ParamSpec,
    TypeVar,
)
from warnings import warn

import anyio
from anyio._core._eventloop import threadlocals

if TYPE_CHECKING:
    from .codebox import CodeBox


@dataclass
class ExecChunk:
    type: Literal["text", "image", "stream", "error"]
    content: str

    @classmethod
    def decode(cls, text: str) -> "ExecChunk":
        type, content = text.split(";\n")
        assert type in ["text", "image", "stream", "error"]
        return cls(type=type, content=content)  # type: ignore[arg-type]

    def __str__(self) -> str:
        return f"{self.type};\n{self.content}"


@dataclass
class ExecResult:
    chunks: list[ExecChunk]

    @property
    def text(self) -> str:
        return "".join(
            chunk.content
            for chunk in self.chunks
            if chunk.type == "text" or chunk.type == "stream"
        )

    @property
    def images(self) -> list[str]:
        return [chunk.content for chunk in self.chunks if chunk.type == "image"]

    @property
    def errors(self) -> list[str]:
        return [chunk.content for chunk in self.chunks if chunk.type == "error"]


# todo move somewhere more clean
@dataclass
class CodeBoxOutput:
    """Deprecated CodeBoxOutput class"""

    content: str
    type: Literal["stdout", "stderr", "image/png", "error"]

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.content == other
        if isinstance(other, CodeBoxOutput):
            return self.content == other.content and self.type == other.type
        return False


@dataclass
class CodeBoxFile:
    remote_path: str
    size: int
    codebox_id: str
    _content: bytes | None = None

    @property
    def codebox(self) -> "CodeBox":
        from .codebox import CodeBox

        return CodeBox(self.codebox_id)

    @property
    def name(self) -> str:
        return self.remote_path.split("/")[-1]

    @property
    def content(self) -> bytes:
        return self._content or b"".join(self.codebox.stream_download(self.remote_path))

    @property
    async def acontent(self) -> bytes:
        return self._content or b"".join([
            chunk async for chunk in self.codebox.astream_download(self.remote_path)
        ])

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            for chunk in self.codebox.stream_download(self.remote_path):
                f.write(chunk)

    async def asave(self, path: str) -> None:
        import aiofiles

        async with aiofiles.open(path, "wb") as f:
            async for chunk in self.codebox.astream_download(self.remote_path):
                await f.write(chunk)


T = TypeVar("T")
P = ParamSpec("P")


def deprecated(message: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if os.getenv("IGNORE_DEPRECATION_WARNINGS", "false").lower() == "true":
                return func(*args, **kwargs)
            warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def resolve_pathlike(file: str | os.PathLike) -> str:
    if isinstance(file, os.PathLike):
        with open(file, "r") as f:
            return f.read()
    return file


IT = TypeVar("IT")


def _syncify_generator(
    async_gen: AsyncGenerator[IT, None],
) -> Generator[IT, None, None]:
    # todo is this even possible?
    while True:
        try:
            if not getattr(threadlocals, "current_async_backend", None):
                yield anyio.run(async_gen.__anext__)
            else:
                yield anyio.from_thread.run(async_gen.__anext__)
        except StopAsyncIteration:
            break


def reduce_bytes(async_gen: Iterator[bytes]) -> bytes:
    return reduce(lambda x, y: x + y, async_gen)


def flatten_exec_result(result: ExecResult | Iterator[ExecChunk]) -> ExecResult:
    if not isinstance(result, ExecResult):
        result = ExecResult(chunks=[c for c in result])
    # todo todo todo todo todo todo
    # remove empty text chunks
    # merge text chunks
    # remove empty stream chunks
    # merge stream chunks
    # remove empty error chunks
    # merge error chunks
    # ...
    return result


async def async_flatten_exec_result(
    async_gen: AsyncGenerator[ExecChunk, None],
) -> ExecResult:
    # todo todo todo todo todo todo
    # remove empty text chunks
    # merge text chunks
    # remove empty stream chunks
    # merge stream chunks
    # remove empty error chunks
    # merge error chunks
    # ...
    return ExecResult(chunks=[c async for c in async_gen])


def syncify(async_function: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    """
    Take an async function and create a regular one that receives the same keyword and
    positional arguments, and that when called, calls the original async function in
    the main async loop from the worker thread using `anyio.to_thread.run()`.
    """

    @wraps(async_function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        partial_f = partial(async_function, *args, **kwargs)

        if not getattr(threadlocals, "current_async_backend", None):
            return anyio.run(partial_f)
        return anyio.from_thread.run(partial_f)

    return wrapper


def check_installed(package: str) -> None:
    """
    Check if the given package is installed.
    """
    try:
        distribution(package)
    except PackageNotFoundError:
        if os.getenv("DEBUG", "false").lower() == "true":
            print(
                f"\nMake sure '{package}' is installed "
                "when using without a CODEBOX_API_KEY.\n"
                f"You can install it with 'pip install {package}'.\n"
            )
        raise


def debug_mode() -> bool:
    return os.getenv("DEBUG", "false").lower() == "true"


@contextmanager
def raise_timeout(timeout: float | None = None):
    def timeout_handler(signum, frame):
        raise TimeoutError("Execution timed out")

    if timeout is not None:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

    try:
        yield
    finally:
        if timeout is not None:
            signal.alarm(0)


@contextmanager
def run_inside(directory: str):
    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def raise_error(message: str) -> NoReturn:
    raise Exception(message)
