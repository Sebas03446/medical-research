from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Union
from pathlib import Path
from dotenv import load_dotenv


ENV_PATH = Path(__file__).parent.parent.parent / '.env'

load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical"
    API_V1_STR: str = "/api/v1"
    SENTRY_DSN: Union[str, None] = None
    ENVIRONMENT: str = "local"  
    CORS_ORIGINS: List[str] = ["http://localhost:8080"]  

    API_KEY_MEDICAL_API: str
    SECRET_KEY_MEDICAL_API: str
    ANTHROPIC_API_KEY: str
    
    # model_config = ConfigDict(env_file=".env") 
    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        case_sensitive=True,
        validate_default=True,
        protected_namespaces=('model_', ),
        extra='ignore'  # Changed from 'allow' to 'ignore'
    )



try:
    settings = Settings(_env_file=str(ENV_PATH))
except Exception as e:
    print(f"Error initializing settings: {str(e)}")
    print(f"Looking for .env file at: {ENV_PATH}")
    print(f".env file exists: {ENV_PATH.exists()}")
    raise
