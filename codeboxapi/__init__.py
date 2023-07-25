from contextvars import ContextVar
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from codeboxapi.config import settings
from codeboxapi.utils import set_api_key
from codeboxapi.box.codebox import CodeBox

if TYPE_CHECKING:
    from aiohttp import ClientSession


aiosession: ContextVar[Optional["ClientSession"]] = ContextVar(
    "aiohttp-session", default=None
)

FILES_DIR = Path(__file__).parent / "files"

__all__ = [
    "CodeBox", 
    "set_api_key", 
    "settings",
]