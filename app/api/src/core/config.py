"""アプリケーション設定."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定.

    環境変数から設定を読み込む。
    """

    # アプリケーション設定
    app_name: str = "Conference Survey API"
    debug: bool = False

    # LLM設定
    llm_api_base: str = "http://localhost:11434"
    llm_model_name: str = "ollama/gemma3:4b"

    # データベース設定
    database_url: str = "sqlite:///./data/survey.db"

    class Config:
        """Pydantic設定."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
