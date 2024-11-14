# Async CodeBox API

For detailed information about async operations, see:

- [Core Methods](../api/codebox.md#core-methods)
- [Data Structures](../concepts/data_structures.md)


## Basic Async Operations

Install aiofiles:

```bash
pip install aiofiles
```
Update main.py with the following examples:

```python
from codeboxapi import CodeBox
import asyncio

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

if __name__ == "__main__":
    asyncio.run(async_examples())
```

Then run the example with:

```bash
python main.py
```

### Result:

```bash
Async Hello!
File content: Async content
```

Reference: `async_example.py` lines 6-18


## Async Streaming:

Update again main.py with the following example:
```python
import asyncio
from codeboxapi import CodeBox

async def async_stream_exec(cb: CodeBox) -> None:
    result = await cb.aexec("""
import time
import asyncio
t0 = time.perf_counter()
for i in range(3):
    await asyncio.sleep(1)
    print(f"{time.perf_counter() - t0:.5f}: {i}")
""")
    print(f"Complete result:\n{result.text}")

if __name__ == "__main__":
    codebox = CodeBox(api_key="local")
    asyncio.run(async_stream_exec(codebox))
```

### Result:

```bash
Complete result:
1.00121: 0
2.00239: 1
3.00352: 2
```
Reference: `stream_chunk_timing.py` lines 53-62

## Docker Parallel Processing
> Note: Docker must be installed and running on your system to use these features.
> Requirements:
> - Docker must be installed and running (start Docker Desktop or docker daemon)
> - Port 8069 must be available
> - User must have permissions to run Docker commands

Install tenacity:

```bash
pip install tenacity
```
Then, update main file:

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

### Result:

```bash
[{'split': 0, 'output': 'Score for split 0: 1.0\n', 'errors': []}, {'split': 1, 'output': 'Score for split 1: 1.0\n', 'errors': []}, {'split': 2, 'output': 'Score for split 2: 1.0\n', 'errors': []}]
```

Reference: `docker_parallel_execution.py` lines 17-80

For more details on async implementations, see:

- [Implementation Overview](../concepts/implementations.md)
- [API Reference](../api/codebox.md#core-methods)