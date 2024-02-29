"""
CodeBox is the simplest cloud infrastructure for your LLM Apps and Services.

The `codeboxapi` package provides a Python API Wrapper for the Codebox API.
The package includes modules for configuring the client, setting the API key,
and interacting with Codebox instances.
"""
from .box import CodeBox
from .config import settings

__all__ = [
    "CodeBox",
    "settings",
]
