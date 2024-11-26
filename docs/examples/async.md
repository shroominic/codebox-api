# Async CodeBox API

## Parallel Execution

Run multiple CodeBoxes in parallel:

```python
import asyncio
from codeboxapi import CodeBox

async def process_codebox(id: int):
    codebox = CodeBox()
    # Execute code
    result = await codebox.aexec(f"print('CodeBox {id}')")
    print(result.text)
    
    # Install package
    await codebox.ainstall("pandas")
    
    # Run computation
    result = await codebox.aexec(
        "import pandas as pd; print(pd.__version__)"
    )
    return result.text

async def main():
    # Run 5 CodeBoxes in parallel
    results = await asyncio.gather(
        *[process_codebox(i) for i in range(5)]
    )
    print(f"Results: {results}")

asyncio.run(main())
```

## Async File Operations with Progress

```python
import asyncio
from tqdm import tqdm
from codeboxapi import CodeBox

async def upload_with_progress(codebox, filename: str):
    total_size = os.path.getsize(filename)
    with tqdm(total=total_size, desc="Uploading") as pbar:
        async with aiofiles.open(filename, "rb") as f:
            file = await codebox.aupload(filename, f)
            pbar.update(total_size)
    return file

async def main():
    codebox = CodeBox()
    file = await upload_with_progress(codebox, "large_file.dat")
    print(f"Uploaded: {file.path}, Size: {await file.aget_size()}")

asyncio.run(main())
```
