from pydantic import BaseSettings
from dotenv import load_dotenv

# .env file
load_dotenv()


class CodeBoxSettings(BaseSettings):
    """
    CodeBox API Config
    """
    CODEBOX_API_KEY: str = None
    CODEBOX_BASE_URL: str = "https://codeinterpreterapi.com/api/v1"
    CODEBOX_VERBOSE: bool = False
    
    OPENAI_API_KEY: str = ""
    

settings = CodeBoxSettings()
