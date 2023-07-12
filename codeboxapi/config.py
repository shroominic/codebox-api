from pydantic import BaseSettings
from dotenv import load_dotenv

# .env file
load_dotenv()


class CodeBoxSettings(BaseSettings):
    """
    CodeBox API Config
    """
    VERBOSE: bool = False
    
    CODEBOX_API_KEY: str | None = None
    CODEBOX_BASE_URL: str = "https://codeinterpreterapi.com/api/v1"
    
    OPENAI_API_KEY: str | None = None
    

settings = CodeBoxSettings()
