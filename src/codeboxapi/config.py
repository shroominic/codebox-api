"""
CodeBox API Config:
Automatically loads environment variables from .env file
"""

from pydantic_settings import BaseSettings


class CodeBoxSettings(BaseSettings):
    """
    CodeBox API Config
    """

    debug: bool = False
    show_info: bool = True

    api_key: str = "local"
    default_working_dir: str = ".codebox"
    base_url: str = "https://codeboxapi.com/api/v2"

    class Config:
        env_file = ".env"
        env_prefix = "CODEBOX_"
        extra = "ignore"


settings = CodeBoxSettings()
