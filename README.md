# CodeBox

CodeBox is the simplest cloud infrastructure for your LLM Apps and Services.
It allows you to run python code in an isolated/sandboxed environment.
Additionally, it provides simple fileIO (and vector database support coming soon).

## Installation

You can install CodeBox with pip:

```bash
pip install codeboxapi
```

## Usage

```python
# Make sure to set the api-key as environment variable:
# CODEBOX_API_KEY=sk-*******************************

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

CodeBox is currently in early development so I created a stripe [payment link as login](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE) system.
As BetaTester you get 70% with the code `BETA`.
Bear in mind, we don't have many automations set up right now,
so you'll need to write an [email](mailto:contact@codeboxapi.com) for things like refunds,
sub cancellations, or upgrades.

## Contributing

Feel free to contribute to this project.
You can open an issue or submit a pull request.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

You can contact me at [contact@codeboxapi.com](mailto:contact@codeboxapi.com)
