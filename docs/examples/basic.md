## Basic Usage

Run code in a new CodeBox:

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:
  print(codebox.status())

  codebox.run("print('Hello World!')")
```

Run async code:

```python
import asyncio
from codeboxapi import CodeBox

async def main():
  async with CodeBox() as codebox:
    await codebox.astatus()
    await codebox.arun("print('Hello World!')")

asyncio.run(main())
```
