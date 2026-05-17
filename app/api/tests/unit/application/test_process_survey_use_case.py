"""ProcessSurveyUseCaseのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.process_survey import ProcessSurveyUseCase
from src.domain.models.paper import Paper
from src.domain.models.survey import Survey, SurveyStatus
from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import Conference, ConferenceType, PaperId, SurveyId, TagId


class TestProcessSurveyUseCase:
    """ProcessSurveyUseCaseのテスト."""

    def _create_survey_with_papers(self) -> Survey:
        """テスト用のサーベイを作成."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.add_paper(
            Paper(
                id=PaperId("paper-1"),
                title="Paper 1",
                authors=["Author 1"],
                abstract="Abstract about transformers and NLP.",
            )
        )
        survey.add_paper(
            Paper(
                id=PaperId("paper-2"),
                title="Paper 2",
                authors=["Author 2"],
                abstract="Abstract about machine learning.",
            )
        )
        return survey

    @pytest.mark.asyncio
    async def test_process_survey_updates_status_to_processing(self):
        """処理開始時にステータスがprocessingになる."""
        survey = self._create_survey_with_papers()

        mock_repository = AsyncMock()
        mock_repository.find_by_id.return_value = survey

        mock_tag_generator = AsyncMock()
        mock_tag_generator.generate_tags.return_value = ["Tag1", "Tag2"]

        mock_hierarchy_agent = AsyncMock()
        mock_hierarchy_agent.merge_similar_tags.return_value = {"merged_tags": []}
        mock_hierarchy_agent.create_hierarchy.return_value = {
            "categories": [
                {
                    "name": "Category1",
                    "children": [
                        {"name": "Tag1", "original_tags": ["Tag1"]},
                        {"name": "Tag2", "original_tags": ["Tag2"]},
                    ],
                }
            ]
        }

        mock_summary_agent = AsyncMock()
        mock_summary_agent.generate_summary.return_value = {
            "summary": "Summary",
            "key_themes": [],
        }

        mock_characteristic_agent = AsyncMock()
        mock_characteristic_agent.extract_characteristics.return_value = {
            "characteristics": "Characteristic"
        }

        use_case = ProcessSurveyUseCase(
            survey_repository=mock_repository,
            tag_generator=mock_tag_generator,
            hierarchy_agent=mock_hierarchy_agent,
            summary_agent=mock_summary_agent,
            characteristic_agent=mock_characteristic_agent,
        )

        await use_case.execute(survey.id)

        # 処理中にステータスが更新されたことを確認
        assert survey.status == SurveyStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_process_survey_generates_tags_for_each_paper(self):
        """各論文に対してタグが生成される."""
        survey = self._create_survey_with_papers()

        mock_repository = AsyncMock()
        mock_repository.find_by_id.return_value = survey

        mock_tag_generator = AsyncMock()
        mock_tag_generator.generate_tags.return_value = ["Tag1", "Tag2"]

        mock_hierarchy_agent = AsyncMock()
        mock_hierarchy_agent.merge_similar_tags.return_value = {"merged_tags": []}
        mock_hierarchy_agent.create_hierarchy.return_value = {
            "categories": [
                {
                    "name": "Category1",
                    "children": [
                        {"name": "Tag1", "original_tags": ["Tag1"]},
                        {"name": "Tag2", "original_tags": ["Tag2"]},
                    ],
                }
            ]
        }

        mock_summary_agent = AsyncMock()
        mock_summary_agent.generate_summary.return_value = {
            "summary": "Summary",
            "key_themes": [],
        }

        mock_characteristic_agent = AsyncMock()
        mock_characteristic_agent.extract_characteristics.return_value = {
            "characteristics": "Characteristic"
        }

        use_case = ProcessSurveyUseCase(
            survey_repository=mock_repository,
            tag_generator=mock_tag_generator,
            hierarchy_agent=mock_hierarchy_agent,
            summary_agent=mock_summary_agent,
            characteristic_agent=mock_characteristic_agent,
        )

        await use_case.execute(survey.id)

        # 各論文に対してタグ生成が呼ばれたことを確認
        assert mock_tag_generator.generate_tags.call_count == 2

    @pytest.mark.asyncio
    async def test_reprocess_clears_existing_tags_and_hierarchy(self):
        """再処理時は既存タグと階層を初期化して再生成する."""
        survey = self._create_survey_with_papers()
        survey.status = SurveyStatus.COMPLETED

        # 既存のタグと階層を持たせる
        old_tag_id = TagId.generate()
        survey.papers[0].tags = [old_tag_id]
        survey.tag_hierarchy.add_node(TagNode(id=old_tag_id, name="OldTag"))
        survey.progress_message = "完了済み"
        survey.progress_current = 10
        survey.progress_total = 10
        survey.papers[0].characteristics = "Old characteristic"

        mock_repository = AsyncMock()
        mock_repository.find_by_id.return_value = survey

        mock_tag_generator = AsyncMock()
        mock_tag_generator.generate_tags.return_value = ["Tag1"]

        mock_hierarchy_agent = AsyncMock()
        mock_hierarchy_agent.merge_similar_tags.return_value = {"merged_tags": []}
        mock_hierarchy_agent.create_hierarchy.return_value = {
            "categories": [
                {"name": "Category1", "children": [{"name": "Tag1", "original_tags": ["Tag1"]}]}
            ]
        }

        mock_summary_agent = AsyncMock()
        mock_summary_agent.generate_summary.return_value = {"summary": "Summary", "key_themes": []}

        mock_characteristic_agent = AsyncMock()
        mock_characteristic_agent.extract_characteristics.return_value = {
            "characteristics": "Characteristic"
        }

        use_case = ProcessSurveyUseCase(
            survey_repository=mock_repository,
            tag_generator=mock_tag_generator,
            hierarchy_agent=mock_hierarchy_agent,
            summary_agent=mock_summary_agent,
            characteristic_agent=mock_characteristic_agent,
        )

        await use_case.execute(survey.id)

        assert all(len(p.tags) > 0 for p in survey.papers)
        assert old_tag_id not in survey.papers[0].tags
        assert old_tag_id not in survey.tag_hierarchy.nodes
        assert survey.progress_message != "完了済み"
        assert survey.progress_current != 10
        assert survey.progress_total != 10
        assert survey.papers[0].characteristics == "Characteristic"

    @pytest.mark.asyncio
    async def test_process_survey_not_found(self):
        """サーベイが見つからない場合はエラー."""
        mock_repository = AsyncMock()
        mock_repository.find_by_id.return_value = None

        use_case = ProcessSurveyUseCase(
            survey_repository=mock_repository,
            tag_generator=AsyncMock(),
            hierarchy_agent=AsyncMock(),
            summary_agent=AsyncMock(),
            characteristic_agent=AsyncMock(),
        )

        with pytest.raises(ValueError, match="Survey not found"):
            await use_case.execute(SurveyId.generate())

    @pytest.mark.asyncio
    async def test_process_survey_sets_characteristics(self):
        """各論文に特徴が設定される."""
        survey = self._create_survey_with_papers()

        mock_repository = AsyncMock()
        mock_repository.find_by_id.return_value = survey

        mock_tag_generator = AsyncMock()
        mock_tag_generator.generate_tags.return_value = ["Tag1"]

        mock_hierarchy_agent = AsyncMock()
        mock_hierarchy_agent.merge_similar_tags.return_value = {"merged_tags": []}
        mock_hierarchy_agent.create_hierarchy.return_value = {
            "categories": [
                {"name": "Category1", "children": [{"name": "Tag1", "original_tags": ["Tag1"]}]}
            ]
        }

        mock_summary_agent = AsyncMock()
        mock_summary_agent.generate_summary.return_value = {
            "summary": "Summary",
            "key_themes": [],
        }

        mock_characteristic_agent = AsyncMock()
        mock_characteristic_agent.extract_characteristics.return_value = {
            "characteristics": "Paper characteristic"
        }

        use_case = ProcessSurveyUseCase(
            survey_repository=mock_repository,
            tag_generator=mock_tag_generator,
            hierarchy_agent=mock_hierarchy_agent,
            summary_agent=mock_summary_agent,
            characteristic_agent=mock_characteristic_agent,
        )

        await use_case.execute(survey.id)

        # 各論文に特徴が設定されたことを確認
        for paper in survey.papers:
            assert paper.characteristics == "Paper characteristic"
