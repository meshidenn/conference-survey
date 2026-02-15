"""ヘルスチェックエンドポイントのE2Eテスト."""

import httpx
import pytest

from src.entrypoint.main import app


@pytest.fixture
def client():
    """テスト用HTTPクライアント."""
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_health_check_returns_200(client: httpx.AsyncClient):
    """GET /health が200とhealthyステータスを返す."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
