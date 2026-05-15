# conference-survey
summarize conference

## 起動方法

### バックエンド (FastAPI)

```bash
cd app/api
uv sync
uv run uvicorn src.entrypoint.main:app --reload
# → http://localhost:8000
```

### フロントエンド (React + Vite)

```bash
cd app/web
npm install
npm run dev
# → http://localhost:5173
```

フロントエンドは Vite proxy 経由で `/api/*` を `localhost:8000` に転送します。
