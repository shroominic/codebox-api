# CodeBox

[![Version](https://badge.fury.io/py/codeboxapi.svg)](https://badge.fury.io/py/codeboxapi)
[![code-check](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml/badge.svg)](https://github.com/shroominic/codebox-api/actions/workflows/code-check.yml)
![Downloads](https://img.shields.io/pypi/dm/codeboxapi)
![License](https://img.shields.io/pypi/l/codeboxapi)

CodeBox is the simplest cloud infrastructure for your LLM Apps and Services.
It allows you to run python code in an isolated/sandboxed environment.
Additionally, it provides simple fileIO (and vector database support coming soon).

## Installation

You can install CodeBox with pip:

```bash
pip install codeboxapi
```

## Usage

```bash
export CODEBOX_API_KEY=sk-***************
```

```python
from codeboxapi import CodeBox

# startup and automatically shutdown a new codebox
with CodeBox() as codebox:
    # check if it's running
    print(codebox.status())

    # run some code
    codebox.run("a = 'Hello'")
    codebox.run("b = 'World!'")
    codebox.run("result = a + ', ' + b")
    result = codebox.run("print(result)")

    print(result)
    # Hello, World!

```

## Where to get your api-key?

Checkout the [pricing page](https://codeboxapi.com/pricing) of CodeBoxAPI. By subscribing to a plan,
you will recieve an account with an api-key.
Bear in mind, we don't have many automations set up right now,
so you'll need to write an [email](mailto:team@codeboxapi.com) for things like refunds,
sub cancellations, or upgrades.

## Docs

Checkout the [documentation](https://shroominic.github.io/codebox-api/) for more details!

## Contributing

Feel free to contribute to this project.
You can open an issue or submit a pull request.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

You can contact me at [team@codeboxapi.com](mailto:team@codeboxapi.com)
