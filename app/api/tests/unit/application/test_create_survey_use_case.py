"""CreateSurveyUseCaseのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.create_survey import CreateSurveyUseCase
from src.domain.models.paper import Paper
from src.domain.models.survey import SurveyStatus
from src.domain.models.value_objects import Conference, ConferenceType, PaperId


class TestCreateSurveyUseCase:
    """CreateSurveyUseCaseのテスト."""

    @pytest.mark.asyncio
    async def test_creates_survey_with_papers(self):
        """論文を含むサーベイを作成できる."""
        # モックを作成
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = [
            Paper(
                id=PaperId("acl-2024-001"),
                title="Paper 1",
                authors=["Author A"],
                abstract="Abstract 1",
            ),
            Paper(
                id=PaperId("acl-2024-002"),
                title="Paper 2",
                authors=["Author B"],
                abstract="Abstract 2",
            ),
        ]

        mock_repository = AsyncMock()

        # ユースケースを実行
        use_case = CreateSurveyUseCase(
            paper_fetcher=mock_fetcher,
            survey_repository=mock_repository,
        )
        conference = Conference(type=ConferenceType.ACL, year=2024)
        survey = await use_case.execute(conference)

        # 検証
        assert survey.conference == conference
        assert survey.status == SurveyStatus.PENDING
        assert len(survey.papers) == 2
        assert survey.papers[0].id.value == "acl-2024-001"

        # リポジトリに保存されたことを確認
        mock_repository.save.assert_called_once_with(survey)

    @pytest.mark.asyncio
    async def test_creates_survey_with_no_papers(self):
        """論文がなくてもサーベイを作成できる."""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = []

        mock_repository = AsyncMock()

        use_case = CreateSurveyUseCase(
            paper_fetcher=mock_fetcher,
            survey_repository=mock_repository,
        )
        conference = Conference(type=ConferenceType.NAACL, year=2024)
        survey = await use_case.execute(conference)

        assert survey.conference == conference
        assert len(survey.papers) == 0

    @pytest.mark.asyncio
    async def test_assigns_unique_survey_id(self):
        """一意のサーベイIDが割り当てられる."""
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = []
        mock_repository = AsyncMock()

        use_case = CreateSurveyUseCase(
            paper_fetcher=mock_fetcher,
            survey_repository=mock_repository,
        )

        conference = Conference(type=ConferenceType.ACL, year=2024)
        survey1 = await use_case.execute(conference)
        survey2 = await use_case.execute(conference)

        assert survey1.id != survey2.id
