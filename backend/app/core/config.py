"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./governai.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Google Gemini
    GEMINI_API_KEY: str = "AIzaSyBpiuQAS5txu5OaAoHKrCsk_icuwm3ddWE"
    
    # Custom Model Configuration (Xylotech)
    USE_CUSTOM_MODEL: bool = True  # Set to True to use custom model instead of Gemini
    CUSTOM_MODEL_TYPE: str = "ollama"  # Options: "ollama", "huggingface", "finetuned"
    CUSTOM_MODEL_NAME: str = "llama3"  # Model name (e.g., "llama3", "mistral", "microsoft/DialoGPT-medium")
    OLLAMA_BASE_URL: str = "http://localhost:11434"  # Ollama server URL
    TRAINING_DATA_PATH: str = "./training_data.json"  # Path to fine-tuning data
    
    # Pinecone (Optional)
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX_NAME: str = "governai-index"
    
    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

