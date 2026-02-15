"""TagNodeエンティティ."""

from dataclasses import dataclass, field

from src.domain.models.value_objects import PaperId, TagId


@dataclass
class TagNode:
    """タグノードエンティティ.

    タグ階層構造のノードを表す。親子関係と関連論文を持つ。

    Attributes:
        id: タグID
        name: タグ名
        parent_id: 親ノードのID（ルートノードの場合はNone）
        child_ids: 子ノードのIDリスト
        paper_ids: このタグに関連付けられた論文のIDリスト
        summary: LLMによって生成されたこのカテゴリの要約
    """

    id: TagId
    name: str
    parent_id: TagId | None = None
    child_ids: list[TagId] = field(default_factory=list)
    paper_ids: list[PaperId] = field(default_factory=list)
    summary: str | None = None

    @property
    def paper_count(self) -> int:
        """関連付けられた論文の数を返す."""
        return len(self.paper_ids)

    @property
    def is_root(self) -> bool:
        """ルートノードかどうかを返す."""
        return self.parent_id is None

    def add_child(self, child_id: TagId) -> None:
        """子ノードを追加する.

        Args:
            child_id: 追加する子ノードのID
        """
        self.child_ids.append(child_id)

    def add_paper(self, paper_id: PaperId) -> None:
        """論文を関連付ける.

        Args:
            paper_id: 関連付ける論文のID
        """
        self.paper_ids.append(paper_id)

    def set_summary(self, summary: str) -> None:
        """要約を設定する.

        Args:
            summary: LLMによって生成された要約
        """
        self.summary = summary

    def set_parent(self, parent_id: TagId) -> None:
        """親ノードを設定する.

        Args:
            parent_id: 親ノードのID
        """
        self.parent_id = parent_id
