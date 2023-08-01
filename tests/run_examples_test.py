import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


async def run_example(file: Path, local: bool = False):
    process = await asyncio.create_subprocess_exec(
        Path(sys.executable).absolute(),
        file.absolute(),
        env={"CODEBOX_API_KEY": "local" if local else os.environ["CODEBOX_API_KEY"]},
    )
    await process.wait()

    if process.returncode != 0:
        raise Exception(f"Example {file} failed with return code {process.returncode}")


async def run_examples():
    if os.environ.get("CODEBOX_API_KEY") is None:
        return print("Skipping remote examples because CODEBOX_API_KEY is not set")

    await asyncio.gather(
        *[
            asyncio.create_task(run_example(file))
            for file in list(Path("examples").glob("**/*.py"))
        ]
    )


async def run_examples_local():
    for file in list(Path("examples").glob("**/*.py")):
        await run_example(file, local=True)


def test_run_examples():
    """Integration test for running the examples."""
    load_dotenv()
    os.environ["CODEBOX_TEST"] = "True"
    # TODO: Use ENV variable to reuse the same remote codebox
    asyncio.run(run_examples())
    asyncio.run(run_examples_local())


if __name__ == "__main__":
    test_run_examples()
