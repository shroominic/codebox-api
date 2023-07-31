import asyncio
import os, sys
from pathlib import Path


async def run_example(file: Path):
    # Add the examples directory to the path
    sys.path.append(str(file.parent))

    # Run the example
    process = await asyncio.create_subprocess_exec("python", file.absolute())
    print(f"Running example {file}...")
    await process.wait()

    # check the return code
    if process.returncode != 0:
        raise Exception(f"Example {file} failed with return code {process.returncode}")

    # Remove the examples directory from the path
    sys.path.remove(str(file.parent))


async def run_examples():
    example_files = list(Path("examples").glob("**/*.py"))
    # Create a task for each example file
    tasks = [asyncio.create_task(run_example(file)) for file in example_files]
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)


def test_run_examples():
    """ Integration test for running the examples. """
    asyncio.run(run_examples())
    
    
if __name__ == "__main__":
    test_run_examples()
