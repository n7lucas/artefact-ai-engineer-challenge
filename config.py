from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Main provider (OpenRouter)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    primary_model: str = "stealth/crouton-alpha"

    #Fallback Provider (OpenAI)
    openai_api_key: str
    fallback_model: str = "gpt-4o-mini"

    # DB and RAG configurations
    db_path: str = "emporio_musica.db"
    pdf_path: str = "políticas_da_loja.pdf"

    #LangSmith Obervability
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    langchain_project: str = "emporio-musica-agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
