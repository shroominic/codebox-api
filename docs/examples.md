# Examples

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

## File IO

Upload and download files:

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:

  # Upload file
  codebox.upload("data.csv", b"1,2,3\
4,5,6")

  # List files
  print(codebox.list_files())
  
  # Download file
  data = codebox.download("data.csv")
  print(data.content)
```

## Package Installation

Install packages into the CodeBox:

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:

  # Install packages
  codebox.install("pandas")
  codebox.install("matplotlib")
  
  # Use them
  codebox.run("import pandas as pd")
  codebox.run("import matplotlib.pyplot as plt")
```

## Restoring Sessions

Restore a CodeBox session from its ID:

```python
from codeboxapi import CodeBox

# Start CodeBox and save ID
codebox = CodeBox()
codebox.start()
session_id = codebox.session_id

#delete session
del session

# Restore session
codebox = CodeBox.from_id(session_id)
print(codebox.status())
```

## Parallel Execution

Run multiple CodeBoxes in parallel:

```python
import asyncio
from codeboxapi import CodeBox

async def run_codebox():
  async with CodeBox() as codebox:
    await codebox.arun("print('Hello World!')")

async def main():
  await asyncio.gather(*[run_codebox() for i in range(10)])

asyncio.run(main())
```
