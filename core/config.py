"""Zentrale Konfiguration via pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Provider (Cloud-Only)
    llm_provider: str = "mistral"
    llm_model: str | None = None
    llm_temperature: float = 0.1
    llm_max_retries: int = 3

    # Optional: API-Keys über Environment (Standard ist verschlüsselte Speicherung in der UI)
    anthropic_api_key: str | None = None
    xai_api_key: str | None = None
    moonshot_api_key: str | None = None
    mistral_api_key: str | None = None
    deepseek_api_key: str | None = None

    # Streamlit
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "localhost"

    # App
    app_ocr_enabled: bool = True
    app_ocr_lang: str = "deu"
    app_default_output_format: str = "docx"
    app_max_upload_size_mb: int = 50
    app_gnotkg_check_enabled: bool = True
    app_data_dir: str = "data"
    app_history_dir: str = "history"
    app_fee_tables_dir: str = "data/fee_tables"

    # Geschäftsparameter
    app_vat_rate: float = 0.19
    app_business_value_max: float = 100_000_000.0

    @property
    def data_dir_path(self) -> Path:
        return Path(self.app_data_dir).resolve()

    @property
    def history_dir_path(self) -> Path:
        return Path(self.app_history_dir).resolve()

    @property
    def fee_tables_dir_path(self) -> Path:
        return Path(self.app_fee_tables_dir).resolve()

    @property
    def provider_keys_path(self) -> Path:
        return self.data_dir_path / "provider_keys.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
