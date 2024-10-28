import os
import signal
import typing as t
from contextlib import contextmanager
from functools import partial, reduce, wraps
from importlib.metadata import PackageNotFoundError, distribution
from warnings import warn

import anyio
from anyio._core._eventloop import threadlocals

if t.TYPE_CHECKING:
    from .types import ExecChunk, ExecResult

T = t.TypeVar("T")
P = t.ParamSpec("P")


def deprecated(message: str) -> t.Callable[[t.Callable[P, T]], t.Callable[P, T]]:
    def decorator(func: t.Callable[P, T]) -> t.Callable[P, T]:
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


def reduce_bytes(async_gen: t.Iterator[bytes]) -> bytes:
    return reduce(lambda x, y: x + y, async_gen)


def flatten_exec_result(
    result: "ExecResult" | t.Iterator["ExecChunk"],
) -> "ExecResult":
    from .types import ExecResult

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
    async_gen: t.AsyncGenerator["ExecChunk", None],
) -> "ExecResult":
    # todo todo todo todo todo todo
    # remove empty text chunks
    # merge text chunks
    # remove empty stream chunks
    # merge stream chunks
    # remove empty error chunks
    # merge error chunks
    # ...
    from .types import ExecResult

    return ExecResult(chunks=[c async for c in async_gen])


def syncify(
    async_function: t.Callable[P, t.Coroutine[t.Any, t.Any, T]],
) -> t.Callable[P, T]:
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


def raise_error(message: str) -> t.NoReturn:
    raise Exception(message)
