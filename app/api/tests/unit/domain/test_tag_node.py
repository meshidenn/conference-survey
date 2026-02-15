"""TagNodeエンティティのテスト."""

from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import PaperId, TagId


class TestTagNode:
    """TagNodeエンティティのテスト."""

    def test_create_with_required_fields(self):
        """必須フィールドでTagNodeを生成できる."""
        tag_id = TagId.generate()
        node = TagNode(id=tag_id, name="Machine Learning")
        assert node.id == tag_id
        assert node.name == "Machine Learning"

    def test_parent_id_default_none(self):
        """parent_idはデフォルトでNone."""
        node = TagNode(id=TagId.generate(), name="NLP")
        assert node.parent_id is None

    def test_child_ids_initialized_as_empty_list(self):
        """child_idsは空リストで初期化される."""
        node = TagNode(id=TagId.generate(), name="NLP")
        assert node.child_ids == []

    def test_paper_ids_initialized_as_empty_list(self):
        """paper_idsは空リストで初期化される."""
        node = TagNode(id=TagId.generate(), name="NLP")
        assert node.paper_ids == []

    def test_summary_default_none(self):
        """summaryはデフォルトでNone."""
        node = TagNode(id=TagId.generate(), name="NLP")
        assert node.summary is None

    def test_add_child(self):
        """子ノードを追加できる."""
        parent = TagNode(id=TagId.generate(), name="NLP")
        child_id = TagId.generate()
        parent.add_child(child_id)
        assert child_id in parent.child_ids

    def test_add_multiple_children(self):
        """複数の子ノードを追加できる."""
        parent = TagNode(id=TagId.generate(), name="NLP")
        child_id1 = TagId.generate()
        child_id2 = TagId.generate()
        parent.add_child(child_id1)
        parent.add_child(child_id2)
        assert len(parent.child_ids) == 2

    def test_add_paper(self):
        """論文を関連付けできる."""
        node = TagNode(id=TagId.generate(), name="Transformer")
        paper_id = PaperId("acl-2024-001")
        node.add_paper(paper_id)
        assert paper_id in node.paper_ids

    def test_paper_count_returns_paper_ids_length(self):
        """paper_countはpaper_idsの数を返す."""
        node = TagNode(id=TagId.generate(), name="Transformer")
        assert node.paper_count == 0
        node.add_paper(PaperId("acl-2024-001"))
        assert node.paper_count == 1
        node.add_paper(PaperId("acl-2024-002"))
        assert node.paper_count == 2

    def test_is_root_when_no_parent(self):
        """parent_idがNoneの場合はルートノード."""
        node = TagNode(id=TagId.generate(), name="Root")
        assert node.is_root is True

    def test_is_not_root_when_has_parent(self):
        """parent_idがある場合はルートノードではない."""
        parent_id = TagId.generate()
        node = TagNode(id=TagId.generate(), name="Child", parent_id=parent_id)
        assert node.is_root is False

    def test_set_summary(self):
        """要約を設定できる."""
        node = TagNode(id=TagId.generate(), name="NLP")
        node.set_summary("This category covers NLP research...")
        assert node.summary == "This category covers NLP research..."

    def test_set_parent(self):
        """親ノードを設定できる."""
        node = TagNode(id=TagId.generate(), name="Transformer")
        parent_id = TagId.generate()
        node.set_parent(parent_id)
        assert node.parent_id == parent_id
