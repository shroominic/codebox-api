# Quick Start

## Installation
CodeBox can be installed via pip:

```bash
pip install codeboxapi
```

This will install the `codeboxapi` package and all dependencies.

For local development without an API key, you will also need to install:

```bash
pip install jupyter-kernel-gateway ipython

pip install matplotlib

pip install typing-extensions
```

## API Key Configuration

For local development, no API key is required. For production use, obtain an API key from [CodeBox website](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE) and set it:

```python
codebox = CodeBox(api_key="your-api-key")
```

Or via environment variable:

```bash
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

## Running Your First Example

1. Create a file `main.py`:

```python
from codeboxapi import CodeBox

def main():
    codebox = CodeBox(api_key="local")
    # Basic example
    result = codebox.exec("print('Hello World!')")
    print("Basic result:", result.text)

    # Example with matplotlib
    result = codebox.exec("""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 2, 3])
plt.title('Example plot')
plt.show()
""")
    print("Plot generated:", len(result.images) > 0)

    # Example with files
    codebox.upload("data.csv", "1,2,3\n4,5,6")
    files = codebox.list_files()
    print("Files in the directory:", files)

if __name__ == "__main__":
    main()
```

2. Run the example:
```bash
python main.py
```

3. You should see:
```
Basic result: Hello World!

Plot generated: True
Files in the directory: [RemoteFile(data.csv, 4096 bytes)]
```

The example demonstrates:
- Basic Python code execution
- Generating plots with matplotlib
- Handling files in the CodeBox environment
