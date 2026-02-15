"""論文取得器ファクトリ."""

from src.domain.models.value_objects import Conference
from src.domain.services.paper_fetcher import PaperFetcher
from src.infrastructure.paper_fetchers.acl_anthology_fetcher import AclAnthologyFetcher


class PaperFetcherFactory:
    """論文取得器のファクトリ.

    学会に応じた適切な論文取得器を生成する。
    """

    def __init__(self):
        """初期化."""
        # 利用可能なFetcherを登録
        self._fetchers: list[PaperFetcher] = [
            AclAnthologyFetcher(),
        ]

    def get_fetcher(self, conference: Conference) -> PaperFetcher:
        """学会に応じた論文取得器を取得する.

        Args:
            conference: 対象の学会

        Returns:
            適切な論文取得器

        Raises:
            ValueError: サポートされていない学会の場合
        """
        for fetcher in self._fetchers:
            if fetcher.supports(conference):
                return fetcher

        raise ValueError(f"No fetcher available for conference: {conference}")
