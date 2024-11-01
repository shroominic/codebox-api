# Package Management

CodeBox provides simple package management capabilities through the `install` method.

## Installing Packages

```python
from codeboxapi import CodeBox

with CodeBox() as codebox:
    # Install a single package
    codebox.install("pandas")
    
    # Install multiple packages
    codebox.install("numpy", "matplotlib")
    
    # Install specific versions
    codebox.install("requests==2.28.1")
```

## Async Installation

```python
async with CodeBox() as codebox:
    await codebox.ainstall("pandas", "numpy")
```

## Verifying Installations

```python
with CodeBox() as codebox:
    codebox.install("pandas")
    result = codebox.exec("import pandas as pd; print(pd.__version__)")
    print(result.text)
```

## Error handling during installation

```python
try:
    codebox.install("non-existent-package")
except CodeBoxError as e:
    print(f"Installation failed: {e}")
```

## Requirements file installation

```python
with open("requirements.txt") as f:
    packages = f.read().splitlines()
    codebox.install(packages)
```