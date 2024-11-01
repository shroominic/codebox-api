# Usage

To use CodeBox, you first need to obtain an API key from [the CodeBox website](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE).

You can then start a CodeBox session:

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:
    print(codebox.healthcheck())
    result = codebox.exec("print('Hello World!')")
    print(result.text)
```

The context manager (`with * as *:`) will automatically start and shutdown the CodeBox.

You can also use CodeBox asynchronously:

```python
from codeboxapi import CodeBox

async def main():
    async with CodeBox() as codebox:
        await codebox.ahealthcheck()
        result = await codebox.aexec("print('Hello World!')")
        print(result.text)
```
