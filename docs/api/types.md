# Types API Reference

## RemoteFile Class

Represents a file stored in the remote CodeBox environment.

```python
RemoteFile(
    path: str,
    remote: CodeBox,
    _size: int | None = None,
    _content: bytes | None = None,
)
```

### Properties

- `name: str` - Returns the filename from the path
- `_size: int | None` - Cached file size
- `_content: bytes | None` - Cached file content

### Methods

*Note*: Async methods are available when appended with `a` (e.g. `aget_content()`).

- `get_size() -> int` - Gets file size
- `get_content() -> bytes` - Retrieves and caches file content
- `save(local_path: str) -> None` - Saves file to local path

## ExecChunk Class

Represents a single chunk of execution output.

```python
ExecChunk(
    type: Literal["txt", "img", "err"],
    content: str
)
```

The `type` field can be one of:

- `txt`: Text output
- `img`: Image output (base64 encoded)
- `err`: Error output

## ExecResult Class

Container for execution results composed of multiple chunks.

```python
ExecResult(
    chunks: list[ExecChunk]
)
```

- `text: str` - Concatenated text output
- `images: list[str]` - List of base64 encoded images
- `errors: list[str]` - List of error messages
