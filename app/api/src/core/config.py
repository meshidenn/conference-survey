"""アプリケーション設定."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定.

    環境変数から設定を読み込む。
    """

    # アプリケーション設定
    app_name: str = "Conference Survey API"
    debug: bool = False

    # LLM設定（LM Studio: OpenAI互換API, デフォルト http://localhost:1234/v1）
    llm_api_base: str = "http://localhost:1234/v1"
    llm_model_name: str = "google/gemma-4-e4b"
    llm_max_concurrent: int = 3

    # データベース設定
    database_url: str = "sqlite:///./data/survey.db"

    class Config:
        """Pydantic設定."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
