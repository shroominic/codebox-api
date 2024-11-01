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

### Code Execution

- `exec(code: str, kernel: Literal["ipython", "bash"] = "ipython") -> ExecResult`
- `aexec(code: str, kernel: Literal["ipython", "bash"] = "ipython") -> ExecResult`

### File Operations

- `upload(remote_file_path: str, content: Union[BinaryIO, bytes, str]) -> RemoteFile`
- `download(remote_file_path: str) -> RemoteFile`
- `list_files() -> List[RemoteFile]`

### Package Management

- `install(*packages: str) -> str`
- `ainstall(*packages: str) -> str`

### Health Checks

- `healthcheck() -> Literal["healthy", "error"]`
- `ahealthcheck() -> Literal["healthy", "error"]`

## Deprecated Methods

The following methods are deprecated and should be replaced with their newer alternatives:

- `run()` → Use `exec()` instead
- `arun()` → Use `aexec()` instead
- `status()` → Use `healthcheck()` instead
- `astatus()` → Use `ahealthcheck()` instead