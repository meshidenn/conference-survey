"""AclAnthologyFetcherのテスト."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.models.value_objects import Conference, ConferenceType
from src.infrastructure.paper_fetchers.acl_anthology_fetcher import AclAnthologyFetcher


class TestAclAnthologyFetcher:
    """AclAnthologyFetcherのテスト."""

    def test_supports_acl_conferences(self):
        """ACL系学会をサポートする."""
        fetcher = AclAnthologyFetcher()

        assert fetcher.supports(Conference(type=ConferenceType.ACL, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.NAACL, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.EMNLP, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.EACL, year=2024))

    @pytest.mark.asyncio
    async def test_fetch_papers_from_api(self):
        """APIから論文を取得できる."""
        # モックレスポンスを作成
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "papers": [
                {
                    "id": "2024.acl-long.1",
                    "title": "Test Paper 1",
                    "authors": ["Author A", "Author B"],
                    "abstract": "This is a test abstract.",
                },
                {
                    "id": "2024.acl-long.2",
                    "title": "Test Paper 2",
                    "authors": ["Author C"],
                    "abstract": "Another test abstract.",
                },
            ]
        }

        # HTTPクライアントをモック
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 2
        assert papers[0].id.value == "2024.acl-long.1"
        assert papers[0].title == "Test Paper 1"
        assert papers[0].authors == ["Author A", "Author B"]
        assert papers[0].abstract == "This is a test abstract."

        # 正しいURLが呼ばれたことを確認
        mock_client.get.assert_called_once_with(
            "https://aclanthology.org/2024.acl.json"
        )

    @pytest.mark.asyncio
    async def test_fetch_naacl_papers(self):
        """NAACL論文を取得できる."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"papers": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.NAACL, year=2024)
        await fetcher.fetch(conference)

        mock_client.get.assert_called_once_with(
            "https://aclanthology.org/2024.naacl.json"
        )

    @pytest.mark.asyncio
    async def test_fetch_empty_response(self):
        """論文がない場合は空リストを返す."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"papers": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert papers == []

    @pytest.mark.asyncio
    async def test_fetch_handles_missing_fields(self):
        """フィールドが欠けている場合もエラーにならない."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "papers": [
                {
                    "id": "2024.acl-long.1",
                    # title, authors, abstract が欠けている
                }
            ]
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 1
        assert papers[0].title == ""
        assert papers[0].authors == []
        assert papers[0].abstract == ""
