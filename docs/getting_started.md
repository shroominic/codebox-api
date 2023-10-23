# Getting Started

## Welcome

CodeBox is the simplest cloud infrastructure for running and testing python code in an isolated environment. It allows developers to execute arbitrary python code without worrying about security or dependencies. Some key features include:

- Securely execute python code in a sandboxed container
- Easily install python packages into the environment
- Built-in file storage for uploading and downloading files
- Support for running code asynchronously using asyncio
- Local testing mode for development without an internet connection
- Coming soon: Vector DB support

## Installation

CodeBox can be installed via pip:

```
pip install codeboxapi
```

This will install the `codeboxapi` package and all dependencies.

For local development without an API key, you will also need to install `jupyter-kernel-gateway`:

```
pip install codeboxapi[local_support]
```

## Usage

To use CodeBox, you first need to obtain an API key from [the CodeBox website](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE).

Then set your API key:

```python
import os
os.environ["CODEBOX_API_KEY"] = "sk-..."

from codeboxapi import CodeBox
```

You can then start a CodeBox session:

```python
with CodeBox() as codebox:
  print(codebox.status())

  codebox.run("print('Hello World!')")
```

The context manager will automatically start and shutdown the CodeBox.

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
