"""値オブジェクト定義."""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4


class ConferenceType(Enum):
    """学会種別.

    ACL系学会のみ初期対応。
    """

    ACL = "ACL"
    NAACL = "NAACL"
    EMNLP = "EMNLP"
    EACL = "EACL"


@dataclass(frozen=True)
class SurveyId:
    """サーベイID.

    UUIDを内部値として持つ値オブジェクト。
    """

    value: UUID

    @classmethod
    def generate(cls) -> "SurveyId":
        """新しいSurveyIdを生成する."""
        return cls(value=uuid4())

    def __str__(self) -> str:
        """文字列表現を返す."""
        return str(self.value)


@dataclass(frozen=True)
class PaperId:
    """論文ID.

    外部システムから付与される文字列IDを保持する。
    """

    value: str

    def __str__(self) -> str:
        """文字列表現を返す."""
        return self.value


@dataclass(frozen=True)
class TagId:
    """タグID.

    UUIDを内部値として持つ値オブジェクト。
    """

    value: UUID

    @classmethod
    def generate(cls) -> "TagId":
        """新しいTagIdを生成する."""
        return cls(value=uuid4())

    def __str__(self) -> str:
        """文字列表現を返す."""
        return str(self.value)


@dataclass(frozen=True)
class Conference:
    """学会情報.

    学会種別と開催年度を持つ値オブジェクト。

    Attributes:
        type: 学会種別
        year: 開催年度（1900-2100）
    """

    type: ConferenceType
    year: int

    def __post_init__(self):
        """バリデーションを実行する."""
        if self.year < 1900 or self.year > 2100:
            raise ValueError(f"year must be between 1900 and 2100, got {self.year}")

    def __str__(self) -> str:
        """文字列表現を返す（例: ACL 2024）."""
        return f"{self.type.value} {self.year}"
