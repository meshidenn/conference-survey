"""Paperエンティティのテスト."""

from src.domain.models.paper import Paper
from src.domain.models.value_objects import PaperId, TagId


class TestPaper:
    """Paperエンティティのテスト."""

    def test_create_with_required_fields(self):
        """必須フィールドでPaperを生成できる."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Attention Is All You Need",
            authors=["Author A", "Author B"],
            abstract="We propose a new architecture...",
        )
        assert paper.id == PaperId("acl-2024-001")
        assert paper.title == "Attention Is All You Need"
        assert paper.authors == ["Author A", "Author B"]
        assert paper.abstract == "We propose a new architecture..."

    def test_tags_initialized_as_empty_list(self):
        """tagsは空リストで初期化される."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        assert paper.tags == []

    def test_characteristics_initialized_as_none(self):
        """characteristicsはNoneで初期化される."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        assert paper.characteristics is None

    def test_add_tag(self):
        """タグを追加できる."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        tag_id = TagId.generate()
        paper.add_tag(tag_id)
        assert tag_id in paper.tags

    def test_add_multiple_tags(self):
        """複数のタグを追加できる."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        tag_id1 = TagId.generate()
        tag_id2 = TagId.generate()
        paper.add_tag(tag_id1)
        paper.add_tag(tag_id2)
        assert len(paper.tags) == 2
        assert tag_id1 in paper.tags
        assert tag_id2 in paper.tags

    def test_set_characteristics(self):
        """特徴を設定できる."""
        paper = Paper(
            id=PaperId("acl-2024-001"),
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
        )
        paper.set_characteristics("This paper introduces a novel approach...")
        assert paper.characteristics == "This paper introduces a novel approach..."
