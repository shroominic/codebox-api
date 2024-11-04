# Async CodeBox API

For detailed information about async operations, see:

- [Core Methods](../api/codebox.md#core-methods)
- [Data Structures](../concepts/data_structures.md)

## Basic Async Operations
```python
from codeboxapi import CodeBox

async def async_examples():
    codebox = CodeBox()
    
    # Async Code Execution
    result = await codebox.aexec("print('Async Hello!')")
    print(result.text)

    # Async File Operations
    await codebox.aupload("async_file.txt", b"Async content")
    downloaded = await codebox.adownload("async_file.txt")
    print("File content:", downloaded.get_content())

    # Async Package Installation
    await codebox.ainstall("requests")
```
Reference: `async_example.py` lines 6-18

## Async Streaming
```python
async def async_stream_exec(cb: CodeBox) -> None:
    chunks: list[tuple[ExecChunk, float]] = []
    t0 = time.perf_counter()
    async for chunk in cb.astream_exec(
        "import time;\nfor i in range(3): time.sleep(1); print(i)"
    ):
        chunks.append((chunk, time.perf_counter() - t0))
        print(f"{chunks[-1][1]:.5f}: {chunk}")
```
Reference: `stream_chunk_timing.py` lines 53-62

## Docker Parallel Processing
> Note: Docker must be installed and running on your system to use these features.
> Requirements:
> - Docker must be installed and running (start Docker Desktop or docker daemon)
> - Port 8069 must be available
> - User must have permissions to run Docker commands

```python
import asyncio
from codeboxapi import CodeBox

async def train_model(codebox: CodeBox, data_split: int) -> dict:
    # Install required packages
    await codebox.ainstall("pandas")
    await codebox.ainstall("scikit-learn")
    
    # Execute training code
    result = await codebox.aexec(f"""
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        
        # Training code with split {data_split}
        X_train, X_test = train_test_split(X, y, random_state={data_split})
    """)
    return {"split": data_split, "output": result.text, "errors": result.errors}

async def main():
    # Create multiple Docker instances
    num_parallel = 4
    codeboxes = [CodeBox(api_key="docker") for _ in range(num_parallel)]
    
    # Create and execute tasks
    tasks = [train_model(codebox, i) for i, codebox in enumerate(codeboxes)]
    results = await asyncio.gather(*tasks)
```
Reference: `docker_parallel_execution.py` lines 17-80

For more details on async implementations, see:

- [Implementation Overview](../concepts/implementations.md)
- [API Reference](../api/codebox.md#core-methods)