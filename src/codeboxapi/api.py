import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from os import getenv
from tempfile import SpooledTemporaryFile
from typing import AsyncGenerator, Literal

from fastapi import Body, Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .local import LocalBox
from .utils import CodeBoxFile

codebox = LocalBox()
last_interaction = datetime.utcnow()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async def timeout():
        if (_timeout := getenv("CODEBOX_TIMEOUT", "90")).lower() == "none":
            return
        while last_interaction + timedelta(seconds=float(_timeout)) > datetime.utcnow():
            await asyncio.sleep(1)
        exit(0)

    t = asyncio.create_task(timeout())
    yield
    t.cancel()


async def get_codebox() -> AsyncGenerator[LocalBox, None]:
    global codebox, last_interaction
    last_interaction = datetime.utcnow()
    yield codebox


app = FastAPI(title="Codebox API", lifespan=lifespan)
app.get("/")(lambda: {"status": "ok"})


class ExecBody(BaseModel):
    code: str
    kernel: Literal["ipython", "bash"] = "ipython"
    timeout: int | None = None
    cwd: str | None = None


@app.post("/exec")
async def exec(
    exec: ExecBody, codebox: LocalBox = Depends(get_codebox)
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in codebox.astream_exec(
            exec.code, exec.kernel, exec.timeout, exec.cwd
        ):
            yield chunk.__str__()

    return StreamingResponse(event_stream())


@app.get("/files/download/{file_name}")
async def download(
    file_name: str,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> StreamingResponse:
    return StreamingResponse(codebox.astream_download(file_name, timeout))


@app.post("/files/upload")
async def upload(
    file: UploadFile,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> "CodeBoxFile":
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file name is required")
    if isinstance(file.file, SpooledTemporaryFile):
        file.file = file.file
    return await codebox.aupload(file.filename, file.file, timeout)


@app.post("/code/execute")
async def deprecated_exec(
    body: dict = Body(), codebox: LocalBox = Depends(get_codebox)
) -> dict:
    """deprecated: use /exec instead"""
    ex = await codebox.aexec(body["properties"]["code"])
    return {"properties": {"stdout": ex.text, "stderr": ex.errors, "result": ex.text}}


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve()
