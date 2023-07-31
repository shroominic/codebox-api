"""
This module contains the box classes that are used to run code in a sandboxed
environment. The `BaseBox` class is the base class for all box classes.
The `LocalBox` class is used to run code in a local testing environment. The
`CodeBox` class is used to run code in a remote sandboxed environment.
"""

from .basebox import BaseBox
from .codebox import CodeBox
from .localbox import LocalBox

__all__ = [
    "BaseBox",
    "CodeBox",
    "LocalBox",
]
