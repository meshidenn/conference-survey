"""TagHierarchyのテスト."""

from src.domain.models.tag_hierarchy import TagHierarchy
from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import TagId


class TestTagHierarchy:
    """TagHierarchyのテスト."""

    def test_empty_hierarchy(self):
        """空の階層構造を作成できる."""
        hierarchy = TagHierarchy()
        assert len(hierarchy.nodes) == 0

    def test_add_node(self):
        """ノードを追加できる."""
        hierarchy = TagHierarchy()
        node = TagNode(id=TagId.generate(), name="NLP")
        hierarchy.add_node(node)
        assert len(hierarchy.nodes) == 1
        assert node.id in hierarchy.nodes

    def test_get_node(self):
        """IDでノードを取得できる."""
        hierarchy = TagHierarchy()
        node = TagNode(id=TagId.generate(), name="NLP")
        hierarchy.add_node(node)
        retrieved = hierarchy.get_node(node.id)
        assert retrieved == node

    def test_get_root_nodes(self):
        """ルートノードを取得できる."""
        hierarchy = TagHierarchy()
        root1 = TagNode(id=TagId.generate(), name="NLP")
        root2 = TagNode(id=TagId.generate(), name="Computer Vision")
        child = TagNode(id=TagId.generate(), name="Transformer", parent_id=root1.id)

        hierarchy.add_node(root1)
        hierarchy.add_node(root2)
        hierarchy.add_node(child)

        roots = hierarchy.get_root_nodes()
        assert len(roots) == 2
        assert root1 in roots
        assert root2 in roots
        assert child not in roots

    def test_get_leaf_nodes(self):
        """葉ノードを取得できる."""
        hierarchy = TagHierarchy()
        root = TagNode(id=TagId.generate(), name="NLP")
        child1 = TagNode(id=TagId.generate(), name="Transformer", parent_id=root.id)
        child2 = TagNode(id=TagId.generate(), name="BERT", parent_id=root.id)
        root.add_child(child1.id)
        root.add_child(child2.id)

        hierarchy.add_node(root)
        hierarchy.add_node(child1)
        hierarchy.add_node(child2)

        leaves = hierarchy.get_leaf_nodes()
        assert len(leaves) == 2
        assert child1 in leaves
        assert child2 in leaves
        assert root not in leaves

    def test_get_bottom_up_order(self):
        """ボトムアップ順でノードを取得できる."""
        hierarchy = TagHierarchy()

        # 3階層の構造を作成
        # root
        #   ├── child1
        #   │     └── grandchild1
        #   └── child2
        root = TagNode(id=TagId.generate(), name="Root")
        child1 = TagNode(id=TagId.generate(), name="Child1", parent_id=root.id)
        child2 = TagNode(id=TagId.generate(), name="Child2", parent_id=root.id)
        grandchild1 = TagNode(id=TagId.generate(), name="GrandChild1", parent_id=child1.id)

        root.add_child(child1.id)
        root.add_child(child2.id)
        child1.add_child(grandchild1.id)

        hierarchy.add_node(root)
        hierarchy.add_node(child1)
        hierarchy.add_node(child2)
        hierarchy.add_node(grandchild1)

        order = hierarchy.get_bottom_up_order()

        # grandchild1 は最初に来るべき（最も深い）
        # root は最後に来るべき
        grandchild_idx = order.index(grandchild1)
        child1_idx = order.index(child1)
        child2_idx = order.index(child2)
        root_idx = order.index(root)

        assert grandchild_idx < child1_idx  # grandchild1 は child1 より前
        assert child1_idx < root_idx  # child1 は root より前
        assert child2_idx < root_idx  # child2 は root より前

    def test_single_node_is_both_root_and_leaf(self):
        """単一ノードはルートかつ葉."""
        hierarchy = TagHierarchy()
        node = TagNode(id=TagId.generate(), name="Single")
        hierarchy.add_node(node)

        roots = hierarchy.get_root_nodes()
        leaves = hierarchy.get_leaf_nodes()

        assert len(roots) == 1
        assert len(leaves) == 1
        assert roots[0] == leaves[0] == node
