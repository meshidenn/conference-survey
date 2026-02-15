"""インメモリサーベイリポジトリ."""

from src.domain.models.survey import Survey
from src.domain.models.value_objects import SurveyId
from src.domain.repositories.survey_repository import SurveyRepository


class InMemorySurveyRepository(SurveyRepository):
    """インメモリサーベイリポジトリ.

    開発・テスト用のシンプルなリポジトリ実装。
    """

    def __init__(self):
        """初期化."""
        self._surveys: dict[SurveyId, Survey] = {}

    async def save(self, survey: Survey) -> None:
        """サーベイを保存する.

        Args:
            survey: 保存するサーベイ
        """
        self._surveys[survey.id] = survey

    async def find_by_id(self, survey_id: SurveyId) -> Survey | None:
        """IDでサーベイを取得する.

        Args:
            survey_id: 取得するサーベイのID

        Returns:
            見つかったサーベイ、またはNone
        """
        return self._surveys.get(survey_id)

    async def find_all(self) -> list[Survey]:
        """全てのサーベイを取得する.

        Returns:
            サーベイのリスト
        """
        return list(self._surveys.values())
