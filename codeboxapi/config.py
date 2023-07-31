"""
CodeBox API Config:
Automatically loads environment variables from .env file
"""

from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

# .env file
load_dotenv("./.env")


class CodeBoxSettings(BaseSettings):
    """
    CodeBox API Config
    """

    VERBOSE: bool = False
    SHOW_INFO: bool = True

    CODEBOX_API_KEY: Optional[str] = None
    CODEBOX_BASE_URL: str = "https://codeboxapi.com/api/v1"
    CODEBOX_TIMEOUT: int = 20


settings = CodeBoxSettings()
