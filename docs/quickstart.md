# Quick Start

## Installation
CodeBox can be installed via pip:

```bash
pip install codeboxapi
```

This will install the `codeboxapi` package and all dependencies.

For local development without an API key, you will also need to install `jupyter-kernel-gateway`:

```bash
pip install jupyter-kernel-gateway
```

## Jupyter Setup for Local Development

After installing `jupyter-kernel-gateway`, you can start using CodeBox locally without an API key. The LocalBox implementation will automatically manage the Jupyter kernel for you.

Note: Make sure you have IPython installed in your environment:

```bash
pip install ipython
``` 

## Local Development

CodeBox provides a local execution environment using IPython for development and testing:

```python
from codeboxapi import CodeBox

# Local execution (no API key needed)
with CodeBox(api_key="local") as codebox:
    # Execute Python code
    result = codebox.exec("print('Hello World!')")
    print(result.text)
    # Use matplotlib (automatically handles display)
    result = codebox.exec("""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 2, 3])
plt.show()
""")
    # Work with files in local .codebox directory
    codebox.upload("data.csv", "1,2,3\n4,5,6")
    files = codebox.list_files()
    # Install packages locally
    codebox.install("pandas")
```

You can also specify a custom working directory:

```python
with CodeBox(api_key="local", codebox_cwd="./my_workspace") as codebox:
    codebox.exec("print('Working in custom directory')")
```

## API Key Configuration

For local development, no API key is required. For production use, obtain an API key from [CodeBox website](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE) and set it:

```python
codebox = CodeBox(api_key="your-api-key")
```

Or via environment variable:

```python
export CODEBOX_API_KEY="your-api-key"
```

## Implementation Options

CodeBox provides three execution environments:

1. **LocalBox** (Development):
```python
codebox = CodeBox(api_key="local")
```

2. **DockerBox** (Local Isolation):
```python
codebox = CodeBox(api_key="docker")
```

3. **RemoteBox** (Production):
```python
codebox = CodeBox(api_key="your-api-key")
```
