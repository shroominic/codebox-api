# Advanced Examples

## Custom Kernel Usage

```python
from codeboxapi import CodeBox
with CodeBox() as codebox:
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
with CodeBox() as codebox:
    # Upload large file with streaming
    with open("large_file.dat", "rb") as f:
        file = codebox.upload("remote_file.dat", f)
    print(f"Uploaded file size: {file.get_size()} bytes")
    # Download with streaming and custom chunk size
    for chunk in codebox.stream_download("remote_file.dat"):
        process_chunk(chunk)
``` 

## Comprehensive Error Handling

```python
from codeboxapi import CodeBox, CodeBoxError
from httpx import TimeoutException
try:
    with CodeBox() as codebox:
        # Execution errors
        result = codebox.exec("import non_existent_package")
        if result.errors:
            print(f"Execution error: {result.errors[0]}")
        # File operations
        try:
            file = codebox.download("non_existent.txt")
        except FileNotFoundError as e:
            print(f"File error: {e}")
except CodeBoxError as e:
    if e.status_code == 401:
        print("Authentication failed")
    elif e.status_code == 429:
        print("Rate limit exceeded")
    elif e.status_code == 503:
        print("Service unavailable")
    else:
        print(f"API Error: {e.response_json}")
except TimeoutException:
    print("Operation timed out")
```

## Docker Implementation

```python
from codeboxapi import CodeBox
# Using DockerBox with custom port and image
codebox = CodeBox(
    api_key="docker",
    factory_id="custom/image:latest",
    port_range=(8000, 9000)
)
# Execute code in container
result = codebox.exec("import sys; print(sys.version)")
print(result.text)
```

## Error Handling

```python
from codeboxapi import CodeBox, CodeBoxError

try:
    with CodeBox() as codebox:
        codebox.exec("import non_existent_package")
except CodeBoxError as e:
    if e.status_code == 401:
        print("Authentication failed")
    elif e.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"Error: {e.response_json}")
```