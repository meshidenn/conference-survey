"""Surveyエンティティ（集約ルート）のテスト."""

import pytest

from src.domain.models.paper import Paper
from src.domain.models.survey import Survey, SurveyStatus
from src.domain.models.value_objects import Conference, ConferenceType, PaperId, SurveyId


class TestSurveyStatus:
    """SurveyStatusのテスト."""

    def test_status_values(self):
        """ステータス値が正しい."""
        assert SurveyStatus.PENDING.value == "pending"
        assert SurveyStatus.PROCESSING.value == "processing"
        assert SurveyStatus.COMPLETED.value == "completed"
        assert SurveyStatus.FAILED.value == "failed"


class TestSurvey:
    """Surveyエンティティのテスト."""

    def test_create_with_required_fields(self):
        """必須フィールドでSurveyを生成できる."""
        survey_id = SurveyId.generate()
        conference = Conference(type=ConferenceType.ACL, year=2024)
        survey = Survey(id=survey_id, conference=conference)
        assert survey.id == survey_id
        assert survey.conference == conference

    def test_initial_status_is_pending(self):
        """初期ステータスはpending."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        assert survey.status == SurveyStatus.PENDING

    def test_papers_initialized_as_empty_list(self):
        """papersは空リストで初期化される."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        assert survey.papers == []

    def test_tag_hierarchy_initialized_empty(self):
        """tag_hierarchyは空で初期化される."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        assert len(survey.tag_hierarchy.nodes) == 0

    def test_add_paper(self):
        """論文を追加できる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        survey.add_paper(paper)
        assert len(survey.papers) == 1
        assert survey.papers[0] == paper

    def test_add_multiple_papers(self):
        """複数の論文を追加できる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        paper1 = Paper(
            id=PaperId("acl-2024-001"),
            title="Paper 1",
            authors=["Author 1"],
            abstract="Abstract 1",
        )
        paper2 = Paper(
            id=PaperId("acl-2024-002"),
            title="Paper 2",
            authors=["Author 2"],
            abstract="Abstract 2",
        )
        survey.add_paper(paper1)
        survey.add_paper(paper2)
        assert len(survey.papers) == 2

    def test_start_processing(self):
        """処理中にできる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.start_processing()
        assert survey.status == SurveyStatus.PROCESSING

    def test_complete(self):
        """完了にできる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.start_processing()
        survey.complete()
        assert survey.status == SurveyStatus.COMPLETED

    def test_fail(self):
        """失敗にできる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.start_processing()
        survey.fail()
        assert survey.status == SurveyStatus.FAILED

    def test_cannot_start_processing_if_already_processing(self):
        """処理中から再度処理開始はできない."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.start_processing()
        with pytest.raises(ValueError):
            survey.start_processing()

    def test_cannot_complete_if_not_processing(self):
        """処理中でない場合は完了にできない."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        with pytest.raises(ValueError):
            survey.complete()

    def test_get_paper_by_id(self):
        """IDで論文を取得できる."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        survey.add_paper(paper)
        retrieved = survey.get_paper(PaperId("acl-2024-001"))
        assert retrieved == paper

    def test_get_paper_by_id_not_found(self):
        """存在しないIDの場合はNoneを返す."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        retrieved = survey.get_paper(PaperId("nonexistent"))
        assert retrieved is None
