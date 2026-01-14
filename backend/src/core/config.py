from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Atikon CRM/Intranet"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Database
    database_url: str = "postgresql+asyncpg://intra_user:intra_password@localhost:5432/intra_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Email/SMTP
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@example.com"
    smtp_from_name: str = "Atikon CRM"
    
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
