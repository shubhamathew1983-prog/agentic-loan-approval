from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    debug: bool = True
    app_name: str = "Agentic Loan Approval System"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Anthropic
    anthropic_api_key: str = ""

    # Streamlit
    streamlit_port: int = 8501

    # Storage
    storage_mode: str = "memory"  # memory or json
    data_persistence_file: str = "data/application_data.json"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # LLM
    llm_model: str = "claude-haiku-4-5-20251001-v1:0"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
