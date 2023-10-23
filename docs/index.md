
# 📦 CodeBox API

[![Version](https://badge.fury.io/py/codeboxapi.svg)](https://badge.fury.io/py/codeboxapi)
[![code-check](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/codeboxapi)
![License](https://img.shields.io/pypi/l/codeboxapi)
![PyVersion](https://img.shields.io/pypi/pyversions/codeboxapi)

CodeBox is the simplest cloud infrastructure for running and testing python code in an isolated environment. It allows developers to execute arbitrary python code without worrying about security or dependencies. Some key features include:

- Securely execute python code in a sandboxed container
- Easily install python packages into the environment
- Built-in file storage for uploading and downloading files
- Support for running code asynchronously using asyncio
- Local testing mode for development without an internet connection

## Why is SandBoxing important?

When deploying LLM Agents to production, it is important to ensure
that the code they run is safe and does not contain any malicious code.
This is especially important when considering prompt injection, which
could give an attacker access to the entire system.

## How does CodeBox work?

CodeBox uses a cloud hosted system to run hardened containers
that are designed to be secure. These containers are then used to
run the code that is sent to the API. This ensures that the code
is run in a secure environment, and that the code cannot access
the host system.

## Links & Resources

- [CodeInterpreterAPI](https://github.com/shroominic/codeinterpreter-api)
- [Documentation](https://shroominic.github.io/codebox-api/)
- [REST API](https://codeboxapi.com/docs)
- [Get API Key](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE)
- [Github Repo](https://github.com/shroominic/codebox-api)
- [PyPI Package](https://pypi.org/project/codeboxapi/)
