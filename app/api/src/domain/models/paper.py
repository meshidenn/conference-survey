"""Paperエンティティ."""

from dataclasses import dataclass, field

from src.domain.models.value_objects import PaperId, TagId


@dataclass
class Paper:
    """論文エンティティ.

    学会で発表された論文を表す。タグ付けと特徴抽出の対象となる。

    Attributes:
        id: 論文ID
        title: タイトル
        authors: 著者リスト
        abstract: 概要
        tags: 付与されたタグのIDリスト
        characteristics: LLMによって抽出された論文の特徴
    """

    id: PaperId
    title: str
    authors: list[str]
    abstract: str
    tags: list[TagId] = field(default_factory=list)
    characteristics: str | None = None

    def add_tag(self, tag_id: TagId) -> None:
        """タグを追加する.

        Args:
            tag_id: 追加するタグのID
        """
        self.tags.append(tag_id)

    def set_characteristics(self, characteristics: str) -> None:
        """論文の特徴を設定する.

        Args:
            characteristics: LLMによって抽出された特徴の説明
        """
        self.characteristics = characteristics
