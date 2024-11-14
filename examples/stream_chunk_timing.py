"""
This example demonstrates the timing differences between sync and async execution
in different CodeBox modes.

To test different modes, set CODEBOX_API_KEY in your environment to:
- 'local' for single instance local execution (default)
- 'docker' for local parallel execution (requires Docker setup)
- Your API key from https://codeboxapi.com/pricing for remote execution

Requirements for different modes:
- Local: No additional setup needed
- Docker: 
  * Docker must be installed and running (start Docker Desktop or docker daemon)
  * Port 8069 must be available
  * User must have permissions to run Docker commands
  * If you get error 125, check:
    - Is Docker running? Start Docker Desktop or docker daemon
    - Is port 8069 in use? Try stopping other services
    - Do you have Docker permissions? Run 'docker ps' to verify
- Remote: Valid API key from https://codeboxapi.com

Note: LocalBox (CODEBOX_API_KEY='local') only allows one instance at a time.
"""

import asyncio
import os
import subprocess
import time

from codeboxapi import CodeBox, ExecChunk


def check_docker_running() -> bool:
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


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


api_key = os.getenv("CODEBOX_API_KEY", "local")
display_key = "remote API key" if api_key.startswith("sk-") else f"'{api_key}'"
print(f"Running with CODEBOX_API_KEY={display_key}\n")

if api_key == "docker" and not check_docker_running():
    print("Error: Docker is not running!")
    print("Please:")
    print("1. Start Docker Desktop (or docker daemon)")
    print("2. Wait a few seconds for Docker to initialize")
    print("3. Run 'docker ps' to verify Docker is running")
    print("4. Try this example again")
    exit(1)

if api_key == "local":
    # LocalBox only allows one instance
    print("Testing single LocalBox instance:")
    cb = CodeBox()
    sync_stream_exec(cb)
    asyncio.run(async_stream_exec(cb))
else:
    # Docker and Remote modes allow multiple instances
    mode = "Remote" if api_key.startswith("sk-") else api_key.capitalize()
    print(f"Testing multiple {mode} instances:\n")
    
    print("Instance 1:")
    cb1 = CodeBox()
    sync_stream_exec(cb1)
    asyncio.run(async_stream_exec(cb1))

    print("\nInstance 2:")
    cb2 = CodeBox()
    sync_stream_exec(cb2)
    asyncio.run(async_stream_exec(cb2))
