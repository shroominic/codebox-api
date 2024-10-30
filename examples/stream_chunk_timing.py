import asyncio
import time

from codeboxapi import CodeBox, ExecChunk


def sync_stream_exec(cb: CodeBox) -> None:
    chunks: list[tuple[ExecChunk, float]] = []
    t0 = time.perf_counter()
    for chunk in cb.stream_exec(
        "import time;\nfor i in range(3): time.sleep(1); print(i)"
    ):
        chunks.append((chunk, time.perf_counter() - t0))

    for chunk, t in chunks:
        print(f"{t:.5f}: {chunk}")


async def async_stream_exec(cb: CodeBox) -> None:
    chunks: list[tuple[ExecChunk, float]] = []
    t0 = time.perf_counter()
    async for chunk in cb.astream_exec(
        "import time;\nfor i in range(3): time.sleep(1); print(i)"
    ):
        chunks.append((chunk, time.perf_counter() - t0))

    for chunk, t in chunks:
        print(f"{t:.5f}: {chunk}")


print("remote")
cb = CodeBox()
sync_stream_exec(cb)
asyncio.run(async_stream_exec(cb))

print("local")
local = CodeBox(api_key="local")
sync_stream_exec(local)
asyncio.run(async_stream_exec(local))

print("docker")
docker = CodeBox(api_key="docker")
sync_stream_exec(docker)
asyncio.run(async_stream_exec(docker))
