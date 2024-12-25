# File Operations Examples

## Basic File Operations

```python
from codeboxapi import CodeBox

codebox = CodeBox()

# Upload text file
file = codebox.upload("data.txt", "Hello World!")
print(f"File size: {file.get_size()} bytes")

# Upload binary data
binary_data = b"Binary content"
file = codebox.upload("data.bin", binary_data)

# List all files
for file in codebox.list_files():
    print(f"- {file.path}: {file.get_size()} bytes")
    
# Download and save locally
remote_file = codebox.download("data.txt")
remote_file.save("local_data.txt")
```

## Streaming Operations

```python
from codeboxapi import CodeBox
import aiofiles

# Synchronous streaming
codebox = CodeBox()
# Stream upload
with open("large_file.dat", "rb") as f:
    codebox.upload("remote_file.dat", f.read())

# Stream download with progress
from tqdm import tqdm
total_size = file.get_size()
with tqdm(total=total_size) as pbar:
    with open("downloaded.dat", "wb") as f:
        for chunk in codebox.stream_download("remote_file.dat"):
            f.write(chunk)
                pbar.update(len(chunk))

# Asynchronous streaming
async def stream_example():
    codebox = CodeBox()

    async with aiofiles.open("large_file.dat", "rb") as f:
        file = await codebox.aupload("remote_file.dat", f)
        
    async for chunk in codebox.astream_download("remote_file.dat"):
        await process_chunk(chunk)
```
