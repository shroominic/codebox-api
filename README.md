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
import codeboxapi as cb

cb.set_api_key("your-api-key")
# or put your api key inside the .env file
# CODEBOX_API_KEY=your-api-key

# create and startup
codebox = CodeBox()
codebox.start()

# check if it's running
print(codebox.status() == "running")

# run some code
result = codebox.run("print('Hello, World!')")

# print the result
print(result)

codebox.stop()
```

## Contributing

Feel free to contribute to this project.
You can open an issue or submit a pull request.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

You can contact me at [pleurae-berets.0u@icloud.com](mailto:pleurae-berets.0u@icloud.com)
