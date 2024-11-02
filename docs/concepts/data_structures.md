# Data Structures

## Core Types

### RemoteFile

Represents a file in the CodeBox environment:

```python
class RemoteFile:
    path: str          # File path in CodeBox
    remote: CodeBox    # Associated CodeBox instance
```

### Methods

- `get_content():` Get file contents
- `aget_content():` Async get contents
- `save(path):` Save to local path
- `asave(path):` Async save to local path

### ExecChunk

Represents an execution output chunk:

```python
class ExecChunk:
    type: Literal["txt", "img", "err"]  # Output type
    content: str                        # Chunk content
```

### Types

- `txt:` Text output
- `img:` Base64 encoded image
- `err:` Error message

### ExecResult

Complete execution result:

```python
class ExecResult:
    chunks: List[ExecChunk]  # List of output chunks
```

### Properties

- `text:` Combined text output
- `images:` List of image outputs
- `errors:` List of error messages

### Usage Examples

```python
# File handling
codebox = CodeBox()
    # Upload and get file
    file = codebox.upload("test.txt", "content")
    content = file.get_content()
    
    # Execute code and handle result
    result = codebox.exec("print('hello')")
    print(result.text)  # Text output
    print(result.errors)  # Any errors
```
