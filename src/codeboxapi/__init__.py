"""
CodeBox is the simplest cloud infrastructure for your LLM Apps and Services.

The `codeboxapi` package provides a Python API Wrapper for the Codebox API.
The package includes modules for configuring the client, setting the API key,
and interacting with Codebox instances.
"""
from codeboxapi.box.codebox import CodeBox
from codeboxapi.config import settings
from codeboxapi.utils import set_api_key

__all__ = [
    "CodeBox",
    "set_api_key",
    "settings",
]
