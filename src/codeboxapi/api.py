import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from os import getenv
from typing import Annotated, AsyncGenerator, Literal

from fastapi import Body, Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from .local import LocalBox
from .utils import CodeBoxFile

codebox = LocalBox()
last_interaction = datetime.utcnow()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async def timeout():
        timeout_secs = float(getenv("CODEBOX_TIMEOUT", "900"))
        while last_interaction + timedelta(seconds=timeout_secs) > datetime.utcnow():
            await asyncio.sleep(1)
        exit(0)

    t = asyncio.create_task(timeout())
    yield
    t.cancel()


app = FastAPI(title="Codebox API", lifespan=lifespan)


async def get_codebox() -> AsyncGenerator[LocalBox, None]:
    global codebox, last_interaction
    last_interaction = datetime.utcnow()
    yield codebox


@app.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/exec")
async def exec(
    code: Annotated[str, Body()],
    kernel: Literal["ipython", "bash"] = "ipython",
    timeout: int | None = None,
    cwd: str | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> StreamingResponse:
    print("code", code)

    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in codebox.astream_exec(code, kernel, timeout, cwd):
            print("chunk", chunk)
            yield chunk.__str__()

    return StreamingResponse(event_stream())


@app.get("/download/{file_name}")
async def download(
    file_name: str,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> StreamingResponse:
    return StreamingResponse(codebox.astream_download(file_name, timeout))


@app.post("/upload")
async def upload(
    file: UploadFile,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> "CodeBoxFile":
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file name is required")
    return await codebox.aupload(file.filename, file.file, timeout)


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=getenv("CODEBOX_PORT", 8069))
