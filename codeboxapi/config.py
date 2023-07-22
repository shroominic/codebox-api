from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

# .env file
load_dotenv()


class CodeBoxSettings(BaseSettings):
    """
    CodeBox API Config
    """
    VERBOSE: bool = False
    
    CODEBOX_API_KEY: Optional[str] = None
    CODEBOX_BASE_URL: str = "https://codeboxapi.com/api/v1"
    CODEBOX_TIMEOUT: int = 20
    

settings = CodeBoxSettings()
