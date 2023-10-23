# Usage

To use CodeBox, you first need to obtain an API key from [the CodeBox website](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE).

You can then start a CodeBox session:

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:
  codebox.run("a = 'Hello World!'")
  codebox.run("print(a)")
```

The context manager (`with * as *:`) will automatically start and shutdown the CodeBox.

You can also use CodeBox asynchronously:

```python
import asyncio
from codeboxapi import CodeBox

async def main():
  async with CodeBox() as codebox:
    await codebox.astatus()
    await codebox.arun("print('Hello World!')")

asyncio.run(main())
```

## CodeBox API Key

If you want to use remote code execution, you will need to obtain an [API Key](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE). This is nessesary for deployment when you care about security of your backend system and you want to serve multiple users in parallel. The CodeBox API Cloud service provides auto scaled infrastructure to run your code in a secure sandboxed environment.

## LocalBox

If you just want to experiment local with this you dont need an api key and by not inserting one the system will automatically use a LocalBox in the background when you call the CodeBox() class.
