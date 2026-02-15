"""論文取得サービスインターフェース."""

from abc import ABC, abstractmethod

from src.domain.models.paper import Paper
from src.domain.models.value_objects import Conference


class PaperFetcher(ABC):
    """論文取得の抽象インターフェース.

    外部ソースから論文情報を取得する。
    """

    @abstractmethod
    async def fetch(self, conference: Conference) -> list[Paper]:
        """指定された学会の論文を取得する.

        Args:
            conference: 対象の学会

        Returns:
            論文のリスト
        """
        pass

    @abstractmethod
    def supports(self, conference: Conference) -> bool:
        """この取得器が指定された学会をサポートするかどうか.

        Args:
            conference: 対象の学会

        Returns:
            サポートする場合はTrue
        """
        pass
