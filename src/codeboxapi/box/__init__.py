"""
This module contains the box classes that are used to run code in a sandboxed
environment. The `BaseBox` class is the base class for all box classes.
The `LocalBox` class is used to run code in a local testing environment. The
`CodeBox` class is used to run code in a remote sandboxed environment.
"""

from .base import BaseBox
from .local import LocalBox
from .remote import RemoteBox as CodeBox

__all__ = [
    "BaseBox",
    "CodeBox",
    "LocalBox",
]
