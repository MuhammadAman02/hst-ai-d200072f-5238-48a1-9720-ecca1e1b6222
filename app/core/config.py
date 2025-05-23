from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """Application configuration with validation."""
    
    # Application Settings
    APP_NAME: str = Field(default="Skin Tone Color Advisor")
    APP_VERSION: str = Field(default="1.0.0")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Upload settings
    UPLOAD_FOLDER: str = Field(default="app/static/uploads")
    MAX_CONTENT_LENGTH: int = Field(default=16 * 1024 * 1024)  # 16MB max upload
    ALLOWED_EXTENSIONS: set = Field(default={"png", "jpg", "jpeg"})
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)