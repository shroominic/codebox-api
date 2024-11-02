# CodeBox Class API Reference

## Constructor

```python
CodeBox(
    session_id: str | None = None,
    api_key: str | Literal["local", "docker"] | None = None,
    factory_id: str | Literal["default"] | None = None,
)
```

## Core Methods

*Note*: Async methods are available when appened with `a` (e.g. `aexec()`).

### Code Execution

- `exec(code: str, kernel: Literal["ipython", "bash"] = "ipython") -> ExecResult`
- `stream_exec(code: str, kernel: Literal["ipython", "bash"] = "ipython") -> AsyncGenerator[str, None]`

### File Operations

- `upload(remote_file_path: str, content: Union[BinaryIO, bytes, str]) -> RemoteFile`
- `download(remote_file_path: str) -> RemoteFile`
- `stream_download(remote_file_path: str) -> AsyncGenerator[bytes, None]`
- `list_files() -> list[RemoteFile]`

### Utility Methods

- `healthcheck() -> Literal["healthy", "error"]`
- `show_variables() -> dict[str, str]`
- `restart() -> None`
- `keep_alive(minutes: int = 15) -> None`
- `install(*packages: str) -> str`
