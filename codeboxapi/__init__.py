import os
from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

from codeboxapi.config import settings
from codeboxapi.utils import set_api_key
from codeboxapi.codebox import CodeBox

if TYPE_CHECKING:
    from aiohttp import ClientSession


aiosession: ContextVar[Optional["ClientSession"]] = ContextVar(
    "aiohttp-session", default=None
)


__all__ = [
    "CodeBox", 
    "set_api_key", 
    "settings",
    "aiosession"
]