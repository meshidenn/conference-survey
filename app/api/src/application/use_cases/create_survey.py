"""サーベイ作成ユースケース."""

from src.domain.models.survey import Survey
from src.domain.models.value_objects import Conference, SurveyId
from src.domain.repositories.survey_repository import SurveyRepository
from src.domain.services.paper_fetcher import PaperFetcher


class CreateSurveyUseCase:
    """サーベイ作成ユースケース.

    指定された学会の論文を取得し、新しいサーベイを作成する。
    """

    def __init__(
        self,
        paper_fetcher: PaperFetcher,
        survey_repository: SurveyRepository,
    ):
        """初期化.

        Args:
            paper_fetcher: 論文取得サービス
            survey_repository: サーベイリポジトリ
        """
        self._paper_fetcher = paper_fetcher
        self._survey_repository = survey_repository

    async def execute(self, conference: Conference) -> Survey:
        """サーベイを作成する.

        Args:
            conference: 対象の学会

        Returns:
            作成されたサーベイ
        """
        # 論文を取得
        papers = await self._paper_fetcher.fetch(conference)

        # サーベイを作成
        survey = Survey(
            id=SurveyId.generate(),
            conference=conference,
        )

        # 論文を追加
        for paper in papers:
            survey.add_paper(paper)

        # 保存
        await self._survey_repository.save(survey)

        return survey
