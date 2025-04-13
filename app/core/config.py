from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, validator, ConfigDict, computed_field
from pydantic_settings import BaseSettings
import secrets
from pathlib import Path
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "LinkedIn Growth Agent"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 Tage
    ALGORITHM: str = "HS256"
    
    # React App Settings
    REACT_APP_API_URL: str = "http://localhost:8000/api"
    REACT_APP_LINKEDIN_API_URL: str = "https://api.linkedin.com/v2"
    REACT_APP_OPENAI_API_URL: str = "https://api.openai.com/v1"
    
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
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "linkedin_agent")
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Alias für DATABASE_URL für SQLAlchemy Kompatibilität"""
        return self.DATABASE_URL or "sqlite:///linkedin_agent.db"

    # LinkedIn OAuth2
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8501/callback")
    
    # LinkedIn API
    LINKEDIN_API_URL: str = "https://api.linkedin.com/v2"
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    
    # Scheduler
    POST_CREATION_DAYS: List[str] = ["mon", "wed", "fri"]
    POST_CREATION_HOUR: int = 10
    CONNECTION_HOUR: int = 9
    FOLLOW_UP_HOUR: int = 14
    INTERACTION_HOURS: List[int] = [11, 13, 15, 17]
    HASHTAG_COMMENT_HOURS: List[int] = [10, 12, 14, 16]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 Stunde
    
    # Proxy
    PROXY_ENABLED: bool = False
    PROXY_URL: Optional[str] = None
    
    # Browser
    BROWSER_HEADLESS: bool = True
    BROWSER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Agent-Einstellungen
    POSTS_PER_WEEK: int = 3
    CONNECTIONS_PER_DAY: int = 39
    MAX_INTERACTIONS_PER_DAY: int = 50
    TARGET_HASHTAGS: List[str] = ["marketing", "sales", "ai", "digitalmarketing", "business"]
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings() 