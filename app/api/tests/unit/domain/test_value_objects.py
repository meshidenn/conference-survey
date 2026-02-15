"""値オブジェクトのテスト."""

import uuid

import pytest

from src.domain.models.value_objects import (
    Conference,
    ConferenceType,
    PaperId,
    SurveyId,
    TagId,
)


class TestSurveyId:
    """SurveyIdのテスト."""

    def test_generate_creates_uuid(self):
        """SurveyIdはUUIDとして生成される."""
        survey_id = SurveyId.generate()
        # UUIDとして解析可能であることを確認
        uuid.UUID(str(survey_id.value))

    def test_two_generated_ids_are_different(self):
        """生成されたIDは一意である."""
        id1 = SurveyId.generate()
        id2 = SurveyId.generate()
        assert id1 != id2


class TestPaperId:
    """PaperIdのテスト."""

    def test_create_with_string(self):
        """PaperIdは文字列から生成される."""
        paper_id = PaperId("acl-2024-001")
        assert paper_id.value == "acl-2024-001"

    def test_equality(self):
        """同じ値のPaperIdは等しい."""
        id1 = PaperId("acl-2024-001")
        id2 = PaperId("acl-2024-001")
        assert id1 == id2


class TestTagId:
    """TagIdのテスト."""

    def test_generate_creates_uuid(self):
        """TagIdはUUIDとして生成される."""
        tag_id = TagId.generate()
        uuid.UUID(str(tag_id.value))

    def test_two_generated_ids_are_different(self):
        """生成されたIDは一意である."""
        id1 = TagId.generate()
        id2 = TagId.generate()
        assert id1 != id2


class TestConferenceType:
    """ConferenceTypeのテスト."""

    def test_has_acl_conferences(self):
        """ACL系学会の種別を持つ."""
        assert ConferenceType.ACL.value == "ACL"
        assert ConferenceType.NAACL.value == "NAACL"
        assert ConferenceType.EMNLP.value == "EMNLP"
        assert ConferenceType.EACL.value == "EACL"


class TestConference:
    """Conferenceのテスト."""

    def test_create_with_type_and_year(self):
        """学会種別と年度で生成される."""
        conference = Conference(type=ConferenceType.ACL, year=2024)
        assert conference.type == ConferenceType.ACL
        assert conference.year == 2024

    def test_year_validation_minimum(self):
        """年度は1900以上."""
        with pytest.raises(ValueError):
            Conference(type=ConferenceType.ACL, year=1899)

    def test_year_validation_maximum(self):
        """年度は2100以下."""
        with pytest.raises(ValueError):
            Conference(type=ConferenceType.ACL, year=2101)

    def test_year_boundary_valid(self):
        """境界値は有効."""
        conf_min = Conference(type=ConferenceType.ACL, year=1900)
        conf_max = Conference(type=ConferenceType.ACL, year=2100)
        assert conf_min.year == 1900
        assert conf_max.year == 2100
