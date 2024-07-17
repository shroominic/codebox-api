"""
Local implementation of CodeBox.
This is useful for testing and development.c
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
import typing as t
from io import StringIO
from typing import Generator

from IPython.core.interactiveshell import InteractiveShell

from .codebox import CodeBox, CodeBoxFile, ExecChunk
from .utils import check_installed, raise_timeout, resolve_pathlike


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
        os.chdir(self.cwd)
        check_installed("ipython")
        self.shell = InteractiveShell.instance()
        self.shell.enable_gui = lambda x: None  # type: ignore
        self._patch_matplotlib_show()

    def _patch_matplotlib_show(self) -> None:
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
        code = resolve_pathlike(code)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = StringIO()
        redirected_error = sys.stderr = StringIO()

        try:
            if kernel == "ipython":
                result = self.shell.run_cell(code)
                output = redirected_output.getvalue()
                error = redirected_error.getvalue()

                if "<img src='data:image/png;base64," in output:
                    image_pattern = r"<img src='data:image/png;base64,(.*?)' />"
                    image_matches = re.findall(image_pattern, output)
                    for img_str in image_matches:
                        yield ExecChunk(type="image", content=img_str)
                elif output:
                    yield ExecChunk(type="text", content=output)
                if error:
                    yield ExecChunk(type="error", content=error)
                if result.result is not None:
                    yield ExecChunk(type="text", content=str(result.result))

            elif kernel == "bash":
                try:
                    process = subprocess.Popen(
                        code,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=cwd,
                    )
                    try:
                        stdout, stderr = process.communicate(timeout=timeout)
                        if stdout:
                            yield ExecChunk(type="text", content=stdout)
                        if stderr:
                            yield ExecChunk(type="error", content=stderr)
                        if process.returncode != 0:
                            yield ExecChunk(
                                type="error",
                                content="Command failed with "
                                f"exit code {process.returncode}",
                            )
                    except subprocess.TimeoutExpired:
                        process.kill()
                        yield ExecChunk(type="error", content="Command timed out")
                except Exception as e:
                    yield ExecChunk(type="error", content=str(e))
            else:
                raise ValueError(f"Unsupported kernel: {kernel}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    async def astream_exec(
        self,
        code: str | os.PathLike,
        kernel: t.Literal["ipython", "bash"] = "ipython",
        timeout: float | None = None,
        cwd: str | None = None,
    ) -> t.AsyncGenerator[ExecChunk, None]:
        code = resolve_pathlike(code)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = StringIO()
        redirected_error = sys.stderr = StringIO()

        try:
            if kernel == "ipython":
                result = await self.shell.run_cell_async(
                    code, store_history=False, silent=True
                )
                output = redirected_output.getvalue()
                error = redirected_error.getvalue()
                if "<img src='data:image/png;base64," in output:
                    image_pattern = r"<img src='data:image/png;base64,(.*?)' />"
                    image_matches = re.findall(image_pattern, output)
                    for img_str in image_matches:
                        yield ExecChunk(type="image", content=img_str)
                elif output:
                    yield ExecChunk(type="text", content=output)
                if error:
                    yield ExecChunk(type="error", content=error)
                if result.result is not None:
                    yield ExecChunk(type="text", content=str(result.result))
            elif kernel == "bash":
                try:
                    process = await asyncio.create_subprocess_shell(
                        code,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd,
                    )
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=timeout
                    )
                    if stdout:
                        yield ExecChunk(type="text", content=stdout.decode())
                    if stderr:
                        yield ExecChunk(type="error", content=stderr.decode())
                    if process.returncode != 0:
                        yield ExecChunk(
                            type="error",
                            content="Command failed with "
                            f"exit code {process.returncode}",
                        )
                except asyncio.TimeoutError:
                    yield ExecChunk(type="error", content="Command timed out")
            else:
                raise ValueError(f"Unsupported kernel: {kernel}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

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
    ) -> Generator[bytes, None, None]:
        with raise_timeout(timeout):
            with open(os.path.join(self.cwd, remote_file_path), "rb") as f:
                yield f.read()

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
                yield await f.read()
