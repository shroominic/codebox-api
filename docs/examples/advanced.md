# Advanced Examples

## Custom Kernel Usage

```python
from codeboxapi import CodeBox
codebox = CodeBox()
    # Execute bash commands
    result = codebox.exec("ls -la", kernel="bash")
    print(result.text)
    # Install system packages with timeout
    result = codebox.exec(
        "apt-get update && apt-get install -y ffmpeg",
        kernel="bash",
        timeout=300
    )
    print(result.text)
```

## File Streaming with Chunks

```python
from codeboxapi import CodeBox
codebox = CodeBox()
# Upload large file with streaming
with open("large_file.dat", "rb") as f:
    file = codebox.upload("remote_file.dat", f)
print(f"Uploaded file size: {file.get_size()} bytes")
# Download with streaming and custom chunk size
for chunk in codebox.stream_download("remote_file.dat"):
    process_chunk(chunk)
```

## Docker Implementation

```python
from codeboxapi import CodeBox
# Using DockerBox with custom port and image
codebox = CodeBox(api_key="docker")
# Execute code in container
result = codebox.exec("import sys; print(sys.version)")
print(result.text)
```

## Error Handling

```python
from codeboxapi import CodeBox

codebox = CodeBox()
codebox.exec("import non_existent_package")
```
