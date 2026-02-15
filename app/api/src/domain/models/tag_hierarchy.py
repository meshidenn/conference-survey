"""TagHierarchy値オブジェクト."""

from dataclasses import dataclass, field

from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import TagId


@dataclass
class TagHierarchy:
    """タグ階層構造.

    タグノードの階層構造を管理する。ルートノードから葉ノードまでの
    木構造を表現し、ボトムアップでの走査をサポートする。

    Attributes:
        nodes: タグIDからTagNodeへのマッピング
    """

    nodes: dict[TagId, TagNode] = field(default_factory=dict)

    def add_node(self, node: TagNode) -> None:
        """ノードを追加する.

        Args:
            node: 追加するタグノード
        """
        self.nodes[node.id] = node

    def get_node(self, tag_id: TagId) -> TagNode | None:
        """IDでノードを取得する.

        Args:
            tag_id: 取得するノードのID

        Returns:
            見つかったノード、またはNone
        """
        return self.nodes.get(tag_id)

    def get_root_nodes(self) -> list[TagNode]:
        """ルートノード（親を持たないノード）を取得する.

        Returns:
            ルートノードのリスト
        """
        return [node for node in self.nodes.values() if node.is_root]

    def get_leaf_nodes(self) -> list[TagNode]:
        """葉ノード（子を持たないノード）を取得する.

        Returns:
            葉ノードのリスト
        """
        return [node for node in self.nodes.values() if len(node.child_ids) == 0]

    def get_bottom_up_order(self) -> list[TagNode]:
        """ボトムアップ順でノードを取得する.

        葉ノードから順にルートノードまで、深さの深いノードから
        浅いノードの順で返す。同じ深さのノードの順序は不定。

        Returns:
            ボトムアップ順に並んだノードのリスト
        """
        # 各ノードの深さを計算
        depths: dict[TagId, int] = {}
        for node in self.nodes.values():
            depths[node.id] = self._calculate_depth(node.id)

        # 深さの降順（深い方から）でソート
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: depths[n.id],
            reverse=True,
        )
        return sorted_nodes

    def _calculate_depth(self, tag_id: TagId) -> int:
        """ノードの深さを計算する.

        Args:
            tag_id: 計算対象のノードID

        Returns:
            ルートからの深さ（ルートノードは0）
        """
        node = self.nodes.get(tag_id)
        if node is None:
            return 0
        if node.parent_id is None:
            return 0
        return 1 + self._calculate_depth(node.parent_id)
