"""ACL Anthology論文取得器."""

import xml.etree.ElementTree as ET

import httpx

from src.domain.models.paper import Paper
from src.domain.models.value_objects import Conference, ConferenceType, PaperId
from src.domain.services.paper_fetcher import PaperFetcher


class AclAnthologyFetcher(PaperFetcher):
    """ACL Anthology GitHub XMLから論文を取得する.

    ACL, NAACL, EMNLP, EACLの論文を取得する。
    データソースはACL AnthologyのGitHubリポジトリにあるXMLメタデータファイル。
    """

    # サポートする学会
    SUPPORTED_CONFERENCES = {
        ConferenceType.ACL,
        ConferenceType.NAACL,
        ConferenceType.EMNLP,
        ConferenceType.EACL,
    }

    # 学会名のマッピング（ACL Anthology XMLファイルで使用される名前）
    CONFERENCE_MAPPING = {
        ConferenceType.ACL: "acl",
        ConferenceType.NAACL: "naacl",
        ConferenceType.EMNLP: "emnlp",
        ConferenceType.EACL: "eacl",
    }

    BASE_URL = (
        "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml"
    )

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
        collection_id = f"{conference.year}.{conf_name}"

        # HTTPクライアントを取得または作成
        client = self._client or httpx.AsyncClient(timeout=60.0)
        should_close = self._client is None

        try:
            papers = await self._fetch_papers_from_xml(client, collection_id)
            return papers
        finally:
            if should_close:
                await client.aclose()

    async def _fetch_papers_from_xml(
        self, client: httpx.AsyncClient, collection_id: str
    ) -> list[Paper]:
        """GitHub上のXMLファイルから論文を取得する.

        Args:
            client: HTTPクライアント
            collection_id: コレクションID（例: "2024.acl"）

        Returns:
            論文のリスト
        """
        url = f"{self.BASE_URL}/{collection_id}.xml"
        response = await client.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        papers = []

        for volume in root.findall("volume"):
            volume_id = volume.get("id", "")
            for paper_elem in volume.findall("paper"):
                paper_id = paper_elem.get("id", "")
                full_id = f"{collection_id}-{volume_id}.{paper_id}"

                title = self._extract_text(paper_elem.find("title"))
                authors = self._extract_authors(paper_elem)
                abstract = self._extract_text(paper_elem.find("abstract"))

                paper = Paper(
                    id=PaperId(full_id),
                    title=title,
                    authors=authors,
                    abstract=abstract,
                )
                papers.append(paper)

        return papers

    @staticmethod
    def _extract_text(element: ET.Element | None) -> str:
        """XML要素からテキストを抽出する（子要素のテキストも含む）.

        fixed-caseタグなどの子要素内のテキストも連結して返す。

        Args:
            element: XML要素

        Returns:
            抽出されたテキスト
        """
        if element is None:
            return ""
        return "".join(element.itertext()).strip()

    @staticmethod
    def _extract_authors(paper_elem: ET.Element) -> list[str]:
        """論文要素から著者リストを抽出する.

        Args:
            paper_elem: 論文のXML要素

        Returns:
            著者名のリスト
        """
        authors = []
        for author_elem in paper_elem.findall("author"):
            first = author_elem.findtext("first", "")
            last = author_elem.findtext("last", "")
            name = f"{first} {last}".strip()
            if name:
                authors.append(name)
        return authors

    def supports(self, conference: Conference) -> bool:
        """この取得器が指定された学会をサポートするかどうか.

        Args:
            conference: 対象の学会

        Returns:
            サポートする場合はTrue
        """
        return conference.type in self.SUPPORTED_CONFERENCES
