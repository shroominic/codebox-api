# Settings API Reference

## CodeBoxSettings

The `CodeBoxSettings` class manages the configuration for the CodeBox client. It inherits from Pydantic's `BaseSettings` class and loads values from environment variables.

### Environment Variables and Settings

#### API Settings
- `CODEBOX_API_KEY: str | None = None`
  Your API key for authentication
- `CODEBOX_BASE_URL: str = "https://codeboxapi.com/api/v2"`
  Base URL for the API
- `CODEBOX_TIMEOUT: int = 20`
  Request timeout in seconds

#### Additional Settings
- `CODEBOX_FACTORY_ID: str = "default"`
  Custom Docker image or environment
- `CODEBOX_SESSION_ID: str | None = None`
  Custom session identifier

#### Logging Settings
- `VERBOSE: bool = False`
  Determines if verbose logging is enabled
- `SHOW_INFO: bool = True`
  Determines if information-level logging is enabled

### Usage

```python
from codeboxapi import CodeBox
# Using environment variables
codebox = CodeBox()
# Or explicitly in code
codebox = CodeBox(
    api_key="your-api-key",
    base_url="https://custom-url.com/api/v1",
    timeout=30
)
``` 