"""ACL Anthology論文取得器."""

import httpx

from src.domain.models.paper import Paper
from src.domain.models.value_objects import Conference, ConferenceType, PaperId
from src.domain.services.paper_fetcher import PaperFetcher


class AclAnthologyFetcher(PaperFetcher):
    """ACL Anthology APIから論文を取得する.

    ACL, NAACL, EMNLP, EACLの論文を取得する。
    """

    # サポートする学会
    SUPPORTED_CONFERENCES = {
        ConferenceType.ACL,
        ConferenceType.NAACL,
        ConferenceType.EMNLP,
        ConferenceType.EACL,
    }

    # 学会名のマッピング（ACL Anthology APIで使用される名前）
    CONFERENCE_MAPPING = {
        ConferenceType.ACL: "acl",
        ConferenceType.NAACL: "naacl",
        ConferenceType.EMNLP: "emnlp",
        ConferenceType.EACL: "eacl",
    }

    BASE_URL = "https://aclanthology.org"

    def __init__(self, client: httpx.AsyncClient | None = None):
        """初期化.

        Args:
            client: HTTPクライアント（テスト用にモック可能）
        """
        self._client = client

    async def fetch(self, conference: Conference) -> list[Paper]:
        """指定された学会の論文を取得する.

        Args:
            conference: 対象の学会

        Returns:
            論文のリスト

        Raises:
            ValueError: サポートされていない学会の場合
        """
        if not self.supports(conference):
            raise ValueError(f"Unsupported conference: {conference}")

        conf_name = self.CONFERENCE_MAPPING[conference.type]
        venue_id = f"{conference.year}.{conf_name}"

        # HTTPクライアントを取得または作成
        client = self._client or httpx.AsyncClient()
        should_close = self._client is None

        try:
            papers = await self._fetch_papers_from_api(client, venue_id)
            return papers
        finally:
            if should_close:
                await client.aclose()

    async def _fetch_papers_from_api(
        self, client: httpx.AsyncClient, venue_id: str
    ) -> list[Paper]:
        """APIから論文を取得する.

        Args:
            client: HTTPクライアント
            venue_id: 会場ID（例: "2024.acl"）

        Returns:
            論文のリスト
        """
        # ACL Anthology APIエンドポイント
        url = f"{self.BASE_URL}/{venue_id}.json"
        response = await client.get(url)
        response.raise_for_status()

        data = response.json()
        papers = []

        for paper_data in data.get("papers", []):
            paper = Paper(
                id=PaperId(paper_data.get("id", "")),
                title=paper_data.get("title", ""),
                authors=paper_data.get("authors", []),
                abstract=paper_data.get("abstract", ""),
            )
            papers.append(paper)

        return papers

    def supports(self, conference: Conference) -> bool:
        """この取得器が指定された学会をサポートするかどうか.

        Args:
            conference: 対象の学会

        Returns:
            サポートする場合はTrue
        """
        return conference.type in self.SUPPORTED_CONFERENCES
