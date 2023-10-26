# Settings

## Settings Class Overview

The configuration settings are encapsulated within the `CodeBoxSettings` class, which inherits from Pydantic's `BaseSettings` class.

`codeboxapi/config.py`
```python
class CodeBoxSettings(BaseSettings):
    ...
```

## Setting Descriptions

### Logging Settings

- `VERBOSE: bool = False`
  Determines if verbose logging is enabled or not.

- `SHOW_INFO: bool = True`
  Determines if information-level logging is enabled.

### CodeBox API Settings

- `CODEBOX_API_KEY: Optional[str] = None`
  The API key for CodeBox.

- `CODEBOX_BASE_URL: str = "https://codeboxapi.com/api/v1"`
  The base URL for the CodeBox API.

- `CODEBOX_TIMEOUT: int = 20`
  Timeout for CodeBox API requests, in seconds.
