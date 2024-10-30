import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from os import getenv, path
from typing import AsyncGenerator, Literal

from fastapi import Body, Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from .local import LocalBox

codebox = LocalBox()
last_interaction = datetime.now(UTC)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async def timeout():
        if (_timeout := getenv("CODEBOX_TIMEOUT", "15")).lower() == "none":
            return
        while last_interaction + timedelta(minutes=float(_timeout)) > datetime.now(UTC):
            await asyncio.sleep(1)
        exit(0)

    t = asyncio.create_task(timeout())
    yield
    t.cancel()


async def get_codebox() -> AsyncGenerator[LocalBox, None]:
    global codebox, last_interaction
    last_interaction = datetime.now(UTC)
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
        ):  # protocol is <type>content</type>
            yield f"<{chunk.type}>{chunk.content}</{chunk.type}>"

    return StreamingResponse(event_stream())


@app.get("/files/download/{file_name}")
async def download(
    file_name: str,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> FileResponse:
    async with asyncio.timeout(timeout):
        file_path = path.join(codebox.cwd, file_name)
        return FileResponse(
            path=file_path, media_type="application/octet-stream", filename=file_name
        )


@app.post("/files/upload")
async def upload(
    file: UploadFile,
    timeout: int | None = None,
    codebox: LocalBox = Depends(get_codebox),
) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file name is required")
    async with asyncio.timeout(timeout):
        await codebox.aupload(file.filename, file.file)


@app.post("/code/execute")
async def deprecated_exec(
    body: dict = Body(), codebox: LocalBox = Depends(get_codebox)
) -> dict:
    """deprecated: use /exec instead"""
    ex = await codebox.aexec(body["properties"]["code"])
    return {"properties": {"stdout": ex.text, "stderr": ex.errors, "result": ex.text}}


def serve():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(getenv("PORT", 8069)))


if __name__ == "__main__":
    serve()
