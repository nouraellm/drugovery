from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Drug Discovery Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/drugdiscovery"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5001"
    MLFLOW_EXPERIMENT_NAME: str = "drug_discovery"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # External APIs
    CHEMBL_API_URL: str = "https://www.ebi.ac.uk/chembl/api/data"
    PUBCHEM_API_URL: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
