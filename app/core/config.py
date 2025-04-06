from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings
import secrets
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "LinkedIn Growth Agent"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 Tage
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Datenbank
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./linkedin_agent.db"
    
    # LinkedIn API
    LINKEDIN_API_URL: str = "https://api.linkedin.com/v2"
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    
    # OpenAI API
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: Optional[str] = None
    
    # Scheduler
    SCHEDULER_INTERVAL: int = 60  # Sekunden
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # Sekunden
    
    # Proxy
    PROXY_ENABLED: bool = False
    PROXY_URL: Optional[str] = None
    
    # Browser
    BROWSER_HEADLESS: bool = True
    BROWSER_USER_AGENT: Optional[str] = None
    
    # LinkedIn
    LINKEDIN_EMAIL: str
    LINKEDIN_PASSWORD: str
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # Scheduler
    POST_GENERATION_FREQUENCY: int = 3  # Posts pro Woche
    DAILY_CONNECTION_LIMIT: int = 39
    INTERACTION_INTERVAL_HOURS: int = 4  # Stunden zwischen Interaktionen

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 