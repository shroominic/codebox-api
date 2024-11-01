# 📦 CodeBox API

[![Version](https://badge.fury.io/py/codeboxapi.svg)](https://badge.fury.io/py/codeboxapi)
[![code-check](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/codeboxapi)
![License](https://img.shields.io/pypi/l/codeboxapi)
![PyVersion](https://img.shields.io/pypi/pyversions/codeboxapi)

## What is CodeBox?

CodeBox is a cloud infrastructure designed to run and test Python code in an isolated environment. It allows developers to execute arbitrary Python code without worrying about security or dependencies.

### Key Features

- 🔒 **Secure Execution**: Code runs in isolated containers
- 📦 **Package Management**: Easy Python package installation
- 💾 **Built-in Storage**: File system for upload/download
- ⚡ **Async Support**: Compatible with asyncio
- 🧪 **Local Mode**: Development without internet connection

## Quick Start

```python
from codeboxapi import CodeBox
with CodeBox() as codebox:
    # Execute Python code
    result = codebox.exec("print('Hello World!')")
    print(result.text)
    # Install packages
    codebox.install("pandas", "numpy")
    # Handle files
    codebox.upload("data.csv", "1,2,3\n4,5,6")
    files = codebox.list_files()
```

## Use Cases

- 🤖 **LLM Agents**: Safe execution of AI-generated code
- 🧪 **Testing**: Isolated testing environment
- 📚 **Education**: Interactive learning platforms
- 🔬 **Data Analysis**: Notebooks and analysis scripts
- 🛠️ **Automation**: Automated workflows

## Implementation Types

- 📘 **Complete Documentation**: [shroominic.github.io/codebox-api/](https://shroominic.github.io/codebox-api/)
- 🔑 **Get API Key**: [pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE)
- 💻 **GitHub Repository**: [github.com/shroominic/codebox-api](https://github.com/shroominic/codebox-api)
- 📦 **PyPI Package**: [pypi.org/project/codeboxapi/](https://pypi.org/project/codeboxapi/)
- 🌐 **REST API**: [codeboxapi.com/docs](https://codeboxapi.com/docs)

