# Advanced Examples

For detailed information about security and architecture, see:

- [Why Sandboxing is Important](../concepts/architecture.md#why-is-sandboxing-important)
- [Implementation Comparison](../concepts/implementations.md#implementation-comparison)

## Custom Kernel Usage

```python
from codeboxapi import CodeBox
codebox = CodeBox()

# Execute bash commands
result = codebox.exec("ls -la", kernel="bash")
print(result.text)

# Create and run Python scripts via bash
result = codebox.exec("echo \"print('Running from file')\" > script.py", kernel="bash")
result = codebox.exec("python script.py", kernel="bash")
```

## File Streaming with Chunks

```python
from codeboxapi import CodeBox
from codeboxapi import ExecChunk
import time

def sync_stream_exec(cb: CodeBox) -> None:
    chunks: list[tuple[ExecChunk, float]] = []
    t0 = time.perf_counter()
    for chunk in cb.stream_exec(
        "import time;\nfor i in range(3): time.sleep(1); print(i)"
    ):
        chunks.append((chunk, time.perf_counter() - t0))
        print(f"{chunks[-1][1]:.5f}: {chunk}")
```
Reference: `stream_chunk_timing.py` lines 41-50

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

# Run multiple instances in parallel
codeboxes = [CodeBox(api_key="docker") for _ in range(4)]
tasks = [train_model(codebox, i) for i, codebox in enumerate(codeboxes)]
results = await asyncio.gather(*tasks)
```
Reference: `docker_parallel_execution.py` lines 17-62

For more details on Docker implementation, see:
- [Docker Implementation](../concepts/implementations.md#dockerbox)
- [Data Structures](../concepts/data_structures.md)

## Error Handling

```python
from codeboxapi import CodeBox

codebox = CodeBox()

# Handle execution errors
result = codebox.exec("import non_existent_package")
if result.errors:
    print("Error occurred:", result.errors[0])

# Handle runtime errors with try/except
result = codebox.exec("""
try:
    1/0
except Exception as e:
    print(f"Error: {str(e)}")
""")
print(result.text)
```
Reference: `getting_started.py` lines 79-81

For more advanced usage patterns, see:

- [Components Overview](../concepts/components.md)
- [API Types Reference](../api/types.md)
