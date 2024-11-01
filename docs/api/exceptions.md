# Exceptions API Reference

## CodeBoxError

The main exception class for CodeBox-related errors. Provides detailed context about API errors.

### Attributes:

- `status_code`: HTTP status code from the API response
- `response_json`: Parsed JSON body from the response
- `headers`: Response headers

### Common Error Cases

```python
from codeboxapi import CodeBox, CodeBoxError

try:
    with CodeBox() as codebox:
        codebox.exec("invalid python code")
except CodeBoxError as e:
    print(f"Error {e.status_code}: {e.response_json}")
```

### Error Types
1. Authentication Errors (401)
2. Rate Limit Errors (429)
3. Execution Errors (400)
4. Server Errors (500)