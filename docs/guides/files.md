# File Operations

CodeBox provides a complete API for handling files, including synchronous and asynchronous operations.

## Basic Operations

```python
from codeboxapi import CodeBox
codebox = CodeBox()
# Upload a file
codebox.upload("data.txt", "File content")
# List files
files = codebox.list_files()
print(files)
# Download a file
file = codebox.download("data.txt")
print(file.content)
```

## Download Streaming

For large files, CodeBox supports streaming:

```python
codebox = CodeBox()
# Download streaming
for chunk in codebox.stream_download("large_file.dat"):
    process_chunk(chunk)
```

## Asynchronous Operations

```python
codebox = CodeBox()
# Upload a file
await codebox.aupload("data.txt", "File content")
# Asynchronous streaming
async for chunk in codebox.astream_download("large_file.dat"):
    await process_chunk(chunk)
```

### RemoteFile Methods

```python
#Get file content
content = file.get_content() # sync
content = await file.aget_content() # async
#Get file size
size = file.get_size() # sync
size = await file.aget_size() # async
#Save file locally
file.save("local_path.txt") # sync
await file.asave("local_path.txt") # async
```
