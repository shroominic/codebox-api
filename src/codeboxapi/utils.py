import signal
from contextlib import contextmanager
from functools import reduce
from importlib.metadata import PackageNotFoundError, distribution
from os import PathLike
from typing import AsyncIterator, Iterator, TypeVar

from .codebox import ExecChunk, ExecResult
from .config import settings


def resolve_pathlike(file: str | PathLike) -> str:
    if isinstance(file, PathLike):
        with open(file, "r") as f:
            return f.read()
    return file


T = TypeVar("T")


async def collect_async_gen(async_gen: AsyncIterator[T]) -> Iterator[T]:
    return iter([item async for item in async_gen])


def reduce_bytes(async_gen: Iterator[bytes]) -> bytes:
    return reduce(lambda x, y: x + y, async_gen)


def flatten_exec_result(result: ExecResult | Iterator[ExecChunk]) -> ExecResult:
    if not isinstance(result, ExecResult):
        result = ExecResult(content=[c for c in result])
    # todo
    # remove empty text chunks
    # merge text chunks
    # remove empty stream chunks
    # merge stream chunks
    # remove empty error chunks
    # merge error chunks
    # ...
    return result


async def async_flatten_exec_result(async_gen: AsyncIterator[ExecChunk]) -> ExecResult:
    return flatten_exec_result(await collect_async_gen(async_gen))


def parse_message(msg: dict) -> ExecChunk:
    """
    Parse a message from the Jupyter kernel.
    The message is a dictionary which is a part of the message stream.
    The output is a chunk of the execution result.
    """
    if msg["msg_type"] == "stream":
        return ExecChunk(type="stream", content=msg["content"]["text"])
    elif msg["msg_type"] == "execute_result":
        return ExecChunk(type="text", content=msg["content"]["data"]["text/plain"])
    elif msg["msg_type"] == "display_data":
        if "image/png" in msg["content"]["data"]:
            return ExecChunk(type="image", content=msg["content"]["data"]["image/png"])
        if "text/plain" in msg["content"]["data"]:
            return ExecChunk(type="text", content=msg["data"]["text/plain"])
        return ExecChunk(type="error", content="Could not parse output")
    elif msg["msg_type"] == "status" and msg["content"]["execution_state"] == "idle":
        return ExecChunk(type="text", content="")
    elif msg["msg_type"] == "error":
        return ExecChunk(
            type="error",
            content=msg["content"]["ename"] + ": " + msg["content"]["evalue"],
        )
    else:
        return ExecChunk(
            type="error", content="Could not parse output: Unsupported message type"
        )


def parse_messages(messages: list[dict]) -> ExecResult:
    """
    Parse a list of messages from the Jupyter kernel.
    The output is a list of chunks of the execution result.
    """
    chunks = []
    for msg in messages:
        if chunk := parse_message(msg):
            chunks.append(chunk)
    else:
        chunks.append(
            ExecChunk(type="text", content="/* exec successful - no output */")
        )
    return ExecResult(content=chunks)


def check_installed(package: str) -> None:
    """
    Check if the given package is installed.
    """
    try:
        distribution(package)
    except PackageNotFoundError:
        if settings.debug:
            print(
                f"\nMake sure '{package}' is installed "
                "when using without a CODEBOX_API_KEY.\n"
                f"You can install it with 'pip install {package}'.\n"
            )
        raise


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
