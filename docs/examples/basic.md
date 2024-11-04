# Basic Usage

For detailed information about CodeBox concepts and architecture, see:

- [What is CodeBox?](../index.md#what-is-codebox)
- [Core Components](../concepts/architecture.md#core-components)

## Simple Execution:
```python
from codeboxapi import CodeBox
codebox = CodeBox()

# Basic execution
result = codebox.exec("print('Hello World!')")
print(result.text)

# Error handling
result = codebox.exec("1/0")
if result.errors:
    print("Error:", result.errors[0])
```
## Async Execution
```python
from codeboxapi import CodeBox
import asyncio

async def main():
    codebox = CodeBox()
    result = await codebox.aexec("print('Hello World!')")
    print(result.text)

if __name__ == "__main__":
    asyncio.run(main())
```

For more details on configuration and setup, see:

- [Quick Start Guide](../quickstart.md)
- [API Reference](../api/codebox.md)