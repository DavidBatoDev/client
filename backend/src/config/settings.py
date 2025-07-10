"""
Configuration settings for the Social Media OCR Backend API
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon key")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service key")
    
    # Google Cloud Document AI
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(..., description="Path to Google service account key")
    GOOGLE_PROJECT_ID: str = Field(..., description="Google Cloud project ID")
    GOOGLE_DOCUMENT_AI_PROCESSOR_ID: str = Field(..., description="Document AI processor ID")
    GOOGLE_DOCUMENT_AI_LOCATION: str = Field(default="us", description="Document AI location")
    
    # Authentication
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    
    # Application Settings
    APP_NAME: str = Field(default="Social Media OCR Backend", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="production", description="Environment")
    
    # CORS Settings
    ALLOWED_ORIGINS: str = Field(default="*", description="Comma-separated list of allowed origins")
    ALLOWED_METHODS: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", description="Comma-separated list of allowed methods")
    ALLOWED_HEADERS: str = Field(default="*", description="Comma-separated list of allowed headers")
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    ALLOWED_FILE_TYPES: str = Field(
        default="image/jpeg,image/png,image/gif,image/webp",
        description="Comma-separated list of allowed file types"
    )
    UPLOAD_DIR: str = Field(default="uploads/", description="Upload directory")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per period")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="Rate limit period in seconds")
    
    @validator('ALLOWED_ORIGINS')
    def validate_origins(cls, v):
        """Validate CORS origins"""
        if v == "*":
            return v
        origins = [origin.strip() for origin in v.split(",")]
        return ",".join(origins)
    
    @validator('ALLOWED_FILE_TYPES')
    def validate_file_types(cls, v):
        """Validate file types"""
        types = [file_type.strip() for file_type in v.split(",")]
        valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"]
        
        for file_type in types:
            if file_type not in valid_types:
                raise ValueError(f"Invalid file type: {file_type}")
        
        return ",".join(types)
    
    @validator('MAX_FILE_SIZE')
    def validate_max_file_size(cls, v):
        """Validate maximum file size"""
        if v <= 0:
            raise ValueError("Maximum file size must be positive")
        if v > 52428800:  # 50MB
            raise ValueError("Maximum file size cannot exceed 50MB")
        return v
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return self.ALLOWED_ORIGINS.split(",")
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list"""
        return self.ALLOWED_FILE_TYPES.split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings() 