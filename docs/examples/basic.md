# Basic Usage

Run code in a new CodeBox:

```python
from codeboxapi import CodeBox

codebox = CodeBox()

codebox.exec("print('Hello World!')")
```

Run async code:

```python
from codeboxapi import CodeBox

codebox = CodeBox()

async def main():
  await codebox.aexec("print('Hello World!')")
```
