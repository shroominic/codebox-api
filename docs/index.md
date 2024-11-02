# 📦 CodeBox API

[![Version](https://badge.fury.io/py/codeboxapi.svg)](https://badge.fury.io/py/codeboxapi)
[![code-check](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/codeboxapi)
![License](https://img.shields.io/pypi/l/codeboxapi)
![PyVersion](https://img.shields.io/pypi/pyversions/codeboxapi)

## What is CodeBox?

CodeBox is a cloud infrastructure designed to run and test Python code in an isolated environment. It allows developers to execute arbitrary Python code without worrying about security or dependencies.

### Key Features

- 🧪 **Open Source**: Development without internet connection or API key
- 🔒 **Secure Execution**: Code runs in isolated environments
- 🚀 **Easy Scaling**: Scales with your workload
- ⏩️ **Streaming**: Code execution can be streamed
- 💾 **File System**: Upload/download of files
- ⚡ **Async Support**: All interfaces support async
- 🐳 **Docker**: Fully local parallel execution
- 🏭 **Factories**: Create fully custom environments

## Quick Start

```python
from codeboxapi import CodeBox
codebox = CodeBox()
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

- 🤖 **Code Interpreter**: Safe execution of AI-generated code
- 📚 **SWE Agents**: Parallel & secure dev environments
- 🧪 **Testing**: Isolated testing environment
- 🔬 **Security Research**: Safe code execution for analysis
- 🛠️ **Automation**: Automated workflows

## Resources

- 🌐 **CodeBox API**: [codeboxapi.com](https://codeboxapi.com/)
- 📘 **Complete Documentation**: [shroominic.github.io/codebox-api/](https://shroominic.github.io/codebox-api/)
- 🔑 **Get API Key**: [codeboxapi.com/pricing](https://codeboxapi.com/pricing)
- 👾 **Code Interpreter API**: [codeinterpreterapi.com](https://codeinterpreterapi.com)
- 💻 **GitHub Repository**: [github.com/shroominic/codebox-api](https://github.com/shroominic/codebox-api)
- 📦 **PyPI Package**: [pypi.org/project/codeboxapi/](https://pypi.org/project/codeboxapi/)
