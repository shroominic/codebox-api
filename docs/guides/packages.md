# Package Management

CodeBox provides simple package management capabilities through the `install` method.

## Installing Packages

```python
from codeboxapi import CodeBox

codebox = CodeBox()
# Install a single package
nstall("pandas")

# Install multiple packages
nstall("numpy", "matplotlib")

# Install specific versions
codebox.install("requests==2.28.1")
```

## Async Installation

```python
codebox = CodeBox()
await codebox.ainstall("pandas", "numpy")
```

## Verifying Installations

```python
codebox = CodeBox()
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
