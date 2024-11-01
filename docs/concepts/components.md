# Concepts

## Concepts Overview

| name | description |
|-|-|
| BaseBox | Abstract base class for isolated code execution environments |
| LocalBox | Local implementation of BaseBox for testing |
| CodeBox | Remote API wrapper for executing code on CodeBox cloud service |
| CodeBoxSettings | Configuration settings for the API client |
| CodeBoxError | Custom exception class for API errors |

## BaseBox

The BaseBox class is an abstract base class that defines the interface for isolated code execution environments, also called CodeBoxes. It contains abstract methods like `run`, `upload`, `download` etc. that all concrete CodeBox implementations need to implement. The BaseBox handles session management and enforces the core interface.

BaseBox aims to provide a common interface to interact with any code execution sandbox. It is designed to be extended by subclasses for specific implementations like LocalBox or CodeBox.

## LocalBox

LocalBox is a concrete implementation of BaseBox that runs code locally using a Jupyter kernel. It is intended for testing and development purposes.

The key aspects are:

- Spins up a local Jupyter kernel gateway to execute code
- Implements all BaseBox methods like `run`, `upload` etc locally
- Provides a sandboxed local environment without needing access to CodeBox cloud
- Useful for testing code before deploying to CodeBox cloud

LocalBox is the default CodeBox used when no API key is specified. It provides a seamless way to develop locally and then switch to the cloud.

## CodeBox

CodeBox is the main class that provides access to the remote CodeBox cloud service. It handles:

- Authentication using the API key
- Making requests to the CodeBox API
- Parsing responses and converting to common schema
- Providing both sync and async access

It extends BaseBox and implements all the core methods to execute code on the remote servers.

The key methods are:

- `start() / astart()` - Starts a new CodeBox instance
- `stop() / astop()` - Stops and destroys a CodeBox instance
- `run() / arun()` - Executes python code in the CodeBox
- `upload() / aupload()` - Uploads a file into the CodeBox
- `download() / adownload()` - Downloads a file from the CodeBox
- `list_files() / alist_files()` - Lists all files in the CodeBox
- `install() / ainstall()` - Installs a PyPI package into the CodeBox
- `restart() / arestart()` - Restarts the Python kernel. This can be useful to clear state between executions.

The CodeBox class provides a simple way to leverage the remote cloud infrastructure with minimal code changes.

## CodeBoxSettings

This contains the client configuration like:

- API key for authentication
- Base URL for the API
- Timeout values
- Debug settings

It loads values from environment variables and provides an easy way to configure the client.

## CodeBoxError

Custom exception class raised when there is an error response from the API. It includes additional context like:

- HTTP status code
- Response JSON body
- Response headers

This provides an easy way to handle errors with additional context.