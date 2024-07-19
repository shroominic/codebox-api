"""
Local implementation of CodeBox.
This is useful for testing and development.
In case you don't put an api_key,
this is the default CodeBox.
"""

import asyncio
import base64
import io
import os
import re
import subprocess
import sys
import threading
import time
import typing as t
from queue import Queue

from IPython.core.interactiveshell import ExecutionResult, InteractiveShell

from .codebox import CodeBox, CodeBoxFile, ExecChunk
from .utils import check_installed, raise_timeout, resolve_pathlike, run_inside


def _print(*text, stdout):
    _stdout = sys.stdout
    sys.stdout = stdout
    print(*text, flush=True)
    sys.stdout = _stdout


class LocalBox(CodeBox):
    """
    LocalBox is a CodeBox implementation that runs code locally using IPython.
    This is useful for testing and development.
    """

    def __new__(cls, *args, **kwargs) -> "LocalBox":
        # This is a hack to ignore the CodeBox.__new__ factory method.
        return object.__new__(cls)

    def __init__(
        self,
        session_id: str | None = None,
        codebox_cwd: str = ".codebox",
        **kwargs,
    ) -> None:
        self.session_id = session_id or ""
        os.makedirs(codebox_cwd, exist_ok=True)
        self.cwd = os.path.abspath(codebox_cwd)
        check_installed("ipython")
        self.shell = InteractiveShell.instance()
        self.shell.enable_gui = lambda x: None  # type: ignore
        self._patch_matplotlib_show()

    def _patch_matplotlib_show(self) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def custom_show(close=True):
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            print(f"<img src='data:image/png;base64,{img_str}' />")
            if close:
                plt.close(fig)

        plt.show = custom_show

    def stream_exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> t.Generator[ExecChunk, None, None]:
        with raise_timeout(timeout):
            code = resolve_pathlike(code)

            if kernel == "ipython":
                with run_inside(cwd or self.cwd):
                    old_stdout, old_stderr = sys.stdout, sys.stderr
                    temp_output, temp_error = sys.stdout, sys.stderr = (
                        io.StringIO(),
                        io.StringIO(),
                    )
                    try:
                        queue = Queue[ExecChunk | None]()
                        _result: list[ExecutionResult] = []

                        def _run_cell(c: str, result: list[ExecutionResult]) -> None:
                            time.sleep(0.0001)
                            result.append(self.shell.run_cell(c))

                        run_cell = threading.Thread(
                            target=_run_cell, args=(code, _result)
                        )

                        def stream_chunks(_out: io.StringIO, _err: io.StringIO) -> None:
                            while run_cell.is_alive():
                                time.sleep(0.0001)
                                if output := _out.getvalue():
                                    # todo make this more efficient?
                                    sys.stdout = _out = io.StringIO()

                                    if "<img src='data:image/png;base64," in output:
                                        image_pattern = (
                                            r"<img src='data:image/png;base64,(.*?)' />"
                                        )
                                        image_matches = re.findall(
                                            image_pattern, output
                                        )
                                        for img_str in image_matches:
                                            queue.put(
                                                ExecChunk(type="image", content=img_str)
                                            )
                                        output = re.sub(image_pattern, "", output)

                                    if output:
                                        if output.startswith("Out["):
                                            # todo better disable logging somehow
                                            output = re.sub(r"Out[(.*?)]: ", "", output)
                                        queue.put(
                                            ExecChunk(type="text", content=output)
                                        )

                                if error := _err.getvalue():
                                    # todo make this more efficient?
                                    sys.stderr = _err = io.StringIO()
                                    queue.put(ExecChunk(type="error", content=error))

                            queue.put(None)

                        stream = threading.Thread(
                            target=stream_chunks, args=(temp_output, temp_error)
                        )

                        run_cell.start()
                        stream.start()

                        while True:
                            time.sleep(0.001)
                            if queue.qsize() > 0:
                                if chunk := queue.get():
                                    yield chunk
                                else:
                                    break

                        result = _result[0]
                        if result.error_before_exec:
                            yield ExecChunk(
                                type="error",
                                content=str(result.error_before_exec).replace(
                                    "\\n", "\n"
                                ),
                            )
                        elif result.error_in_exec:
                            yield ExecChunk(
                                type="error",
                                content=str(result.error_in_exec).replace("\\n", "\n"),
                            )
                        elif result.result is not None:
                            yield ExecChunk(type="text", content=str(result.result))

                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr

            elif kernel == "bash":
                # todo maybe implement using queue
                process = subprocess.Popen(
                    code,
                    cwd=cwd or self.cwd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if process.stdout:
                    for c in process.stdout:
                        yield ExecChunk(content=c.decode(), type="text")
                if process.stderr:
                    for c in process.stderr:
                        yield ExecChunk(content=c.decode(), type="error")

            else:
                raise ValueError(f"Unsupported kernel: {kernel}")

    async def astream_exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> t.AsyncGenerator[ExecChunk, None]:
        async with asyncio.timeout(timeout):
            code = resolve_pathlike(code)

            if kernel == "ipython":
                with run_inside(cwd or self.cwd):
                    old_stdout, old_stderr = sys.stdout, sys.stderr
                    temp_output, temp_error = sys.stdout, sys.stderr = (
                        io.StringIO(),
                        io.StringIO(),
                    )

                    try:
                        run_cell = asyncio.create_task(
                            asyncio.to_thread(self.shell.run_cell, code)
                        )

                        while not run_cell.done():
                            await asyncio.sleep(0.001)
                            if output := temp_output.getvalue():
                                # todo make this more efficient?
                                sys.stdout = temp_output = io.StringIO()

                                if "<img src='data:image/png;base64," in output:
                                    image_pattern = (
                                        r"<img src='data:image/png;base64,(.*?)' />"
                                    )
                                    image_matches = re.findall(image_pattern, output)
                                    for img_str in image_matches:
                                        yield ExecChunk(type="image", content=img_str)
                                    output = re.sub(image_pattern, "", output)

                                if output:
                                    if output.startswith("Out["):
                                        # todo better disable logging somehow
                                        output = re.sub(
                                            r"Out\[(.*?)\]: ", "", output.strip()
                                        )
                                    yield ExecChunk(type="text", content=output)

                            if error := temp_error.getvalue():
                                sys.stderr = temp_error = io.StringIO()
                                yield ExecChunk(type="error", content=error)

                        result = await run_cell
                        if result.error_before_exec:
                            yield ExecChunk(
                                type="error", content=str(result.error_before_exec)
                            )
                        elif result.error_in_exec:
                            yield ExecChunk(
                                type="error", content=str(result.error_in_exec)
                            )
                        elif result.result is not None:
                            yield ExecChunk(type="text", content=str(result.result))
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr

            elif kernel == "bash":
                process = await asyncio.create_subprocess_shell(
                    code,
                    cwd=cwd or self.cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # todo yield at the same time and not after each other
                if process.stdout:
                    async for chunk in process.stdout:
                        yield ExecChunk(content=chunk.decode(), type="text")

                if process.stderr:
                    async for err in process.stderr:
                        yield ExecChunk(content=err.decode(), type="error")
            else:
                raise ValueError(f"Unsupported kernel: {kernel}")

    async def aupload(
        self,
        file_name: str,
        content: t.BinaryIO | bytes | str,
        timeout: float | None = None,
    ) -> CodeBoxFile:
        import aiofiles.os

        async with asyncio.timeout(timeout):
            file_path = os.path.join(self.cwd, file_name)
            async with aiofiles.open(file_path, "wb") as file:
                if isinstance(content, str):
                    await file.write(content.encode())
                elif isinstance(content, t.BinaryIO):
                    while chunk := content.read(8192):
                        await file.write(chunk)
                else:
                    await file.write(content)

            file_size = await aiofiles.os.path.getsize(file_path)
            return CodeBoxFile(
                remote_path=file_path,
                size=file_size,
                codebox_id=self.session_id,
            )

    def stream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> t.Generator[bytes, None, None]:
        with raise_timeout(timeout):
            with open(os.path.join(self.cwd, remote_file_path), "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

    async def astream_download(
        self,
        remote_file_path: str,
        timeout: float | None = None,
    ) -> t.AsyncGenerator[bytes, None]:
        import aiofiles

        async with asyncio.timeout(timeout):
            async with aiofiles.open(
                os.path.join(self.cwd, remote_file_path), "rb"
            ) as f:
                while chunk := await f.read(8192):
                    yield chunk
