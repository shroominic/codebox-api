import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from os import getenv
from typing import Annotated, AsyncGenerator, Literal

from codeboxapi import CodeBox
from codeboxapi.codebox import CodeBoxFile
from codeboxapi.local import LocalBox
from fastapi import Depends, FastAPI, HTTPException, Path, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

TIMEOUT = float(getenv("TIMEOUT", "900"))

last_interaction = datetime.utcnow()

codebox = CodeBox.create(api_key="local")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async def timeout():
        # todo maybe mode timeout into LocalBox
        while last_interaction + timedelta(seconds=TIMEOUT) > datetime.utcnow():
            await asyncio.sleep(1)
        exit(0)

    t = asyncio.create_task(timeout())
    yield
    t.cancel()


app = FastAPI(title="Codebox API", lifespan=lifespan)


async def get_codebox() -> AsyncGenerator[CodeBox, None]:
    global codebox, last_interaction
    last_interaction = datetime.utcnow()
    yield codebox


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


class RunCodeInput(BaseModel):
    code: str


@app.post("/exec")
async def exec(
    codebox: Annotated[LocalBox, Depends(get_codebox)],
    code: str,
    language: Literal["python", "bash"],
    timeout: int | None = None,
    cwd: str | None = None,
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in codebox.astream_exec(code, language, timeout, cwd):
            yield chunk.model_dump_json()

    return StreamingResponse(event_stream())


@app.get("/download/{file_name}")
async def download(
    codebox: Annotated[LocalBox, Depends(get_codebox)],
    file_name: Annotated[str, Path()],
    timeout: int | None = None,
) -> StreamingResponse:
    return StreamingResponse(codebox.astream_download(file_name, timeout))


@app.post("/upload")
async def upload(
    file: UploadFile,
    codebox: Annotated[LocalBox, Depends(get_codebox)],
    timeout: int | None = None,
) -> CodeBoxFile:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file name is required")
    return await codebox.aupload(file.filename, file.file, timeout)
