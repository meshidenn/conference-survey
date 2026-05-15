"""Survey集約ルート."""

from dataclasses import dataclass, field
from enum import Enum

from src.domain.models.paper import Paper
from src.domain.models.tag_hierarchy import TagHierarchy
from src.domain.models.value_objects import Conference, PaperId, SurveyId


class SurveyStatus(Enum):
    """サーベイのステータス."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Survey:
    """サーベイ集約ルート.

    学会の論文サーベイを表す。論文リスト、タグ階層構造、処理状態を管理する。

    Attributes:
        id: サーベイID
        conference: 対象の学会
        status: 処理ステータス
        papers: サーベイ対象の論文リスト
        tag_hierarchy: タグの階層構造
    """

    id: SurveyId
    conference: Conference
    status: SurveyStatus = SurveyStatus.PENDING
    papers: list[Paper] = field(default_factory=list)
    tag_hierarchy: TagHierarchy = field(default_factory=TagHierarchy)
    progress_message: str = ""
    progress_current: int = 0
    progress_total: int = 0
    error_message: str = ""

    def update_progress(self, message: str, current: int = 0, total: int = 0) -> None:
        """進捗を更新する.

        Args:
            message: 現在のステップの説明
            current: 現在の進捗数
            total: 合計数
        """
        self.progress_message = message
        self.progress_current = current
        self.progress_total = total

    def add_paper(self, paper: Paper) -> None:
        """論文を追加する.

        Args:
            paper: 追加する論文
        """
        self.papers.append(paper)

    def get_paper(self, paper_id: PaperId) -> Paper | None:
        """IDで論文を取得する.

        Args:
            paper_id: 取得する論文のID

        Returns:
            見つかった論文、またはNone
        """
        for paper in self.papers:
            if paper.id == paper_id:
                return paper
        return None

    def start_processing(self) -> None:
        """処理を開始する（初回または再試行）.

        Raises:
            ValueError: 既に処理中または完了している場合
        """
        if self.status not in (SurveyStatus.PENDING, SurveyStatus.FAILED):
            raise ValueError(f"Cannot start processing from status: {self.status}")
        self.status = SurveyStatus.PROCESSING

    def complete(self) -> None:
        """処理を完了する.

        Raises:
            ValueError: 処理中でない場合
        """
        if self.status != SurveyStatus.PROCESSING:
            raise ValueError(f"Cannot complete from status: {self.status}")
        self.status = SurveyStatus.COMPLETED

    def fail(self, message: str = "") -> None:
        """処理を失敗とする.

        Args:
            message: エラーメッセージ

        Raises:
            ValueError: 処理中でない場合
        """
        if self.status != SurveyStatus.PROCESSING:
            raise ValueError(f"Cannot fail from status: {self.status}")
        self.status = SurveyStatus.FAILED
        if message:
            self.error_message = message
