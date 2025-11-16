"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    app_name: str = "Road Safety Intervention API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Google Gemini API
    gemini_api_key: str
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_pro_model: str = "gemini-1.5-pro"
    gemini_embedding_model: str = "text-embedding-004"

    # Authentication
    api_keys: str  # Comma-separated API keys

    # Environment
    environment: str = "development"
    log_level: str = "info"

    # Caching
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Database
    database_url: str = "sqlite:///./backend/data/processed/interventions.db"

    # Vector Store
    chroma_persist_dir: str = "./backend/data/chroma_db"
    collection_name: str = "road_safety_interventions"

    # Search Settings
    default_search_strategy: str = "hybrid"
    max_results: int = 5
    rag_top_k: int = 10

    # Server
    port: int = 8000
    host: str = "0.0.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string."""
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / "backend" / "data"

    @property
    def raw_data_dir(self) -> Path:
        """Get raw data directory."""
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        """Get processed data directory."""
        return self.data_dir / "processed"

    @property
    def chroma_dir(self) -> Path:
        """Get ChromaDB directory."""
        return self.data_dir / "chroma_db"


# Global settings instance
settings = Settings()
