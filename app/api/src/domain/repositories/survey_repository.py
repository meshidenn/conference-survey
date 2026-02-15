"""サーベイリポジトリインターフェース."""

from abc import ABC, abstractmethod

from src.domain.models.survey import Survey
from src.domain.models.value_objects import SurveyId


class SurveyRepository(ABC):
    """サーベイリポジトリの抽象インターフェース.

    サーベイの永続化を担当する。
    """

    @abstractmethod
    async def save(self, survey: Survey) -> None:
        """サーベイを保存する.

        Args:
            survey: 保存するサーベイ
        """
        pass

    @abstractmethod
    async def find_by_id(self, survey_id: SurveyId) -> Survey | None:
        """IDでサーベイを取得する.

        Args:
            survey_id: 取得するサーベイのID

        Returns:
            見つかったサーベイ、またはNone
        """
        pass

    @abstractmethod
    async def find_all(self) -> list[Survey]:
        """全てのサーベイを取得する.

        Returns:
            サーベイのリスト
        """
        pass
