"""FastAPIアプリケーションエントリポイント."""

from fastapi import FastAPI

from src.core.config import settings
from src.presentation.routes.surveys import router as surveys_router

app = FastAPI(
    title=settings.app_name,
    description="学会論文サーベイアプリ - 論文のタグ生成・階層化・要約をマインドマップで表示",
    version="0.1.0",
)

# ルーター登録
app.include_router(surveys_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント."""
    return {"status": "healthy"}


def dev() -> None:
    """開発サーバー起動."""
    import uvicorn

    uvicorn.run("src.entrypoint.main:app", host="0.0.0.0", port=8000, reload=True)
