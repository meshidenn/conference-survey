"""LLMクライアントインターフェース."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLMレスポンス.

    Attributes:
        content: レスポンスの内容
        model: 使用したモデル名
    """

    content: str
    model: str


class LLMClient(ABC):
    """LLMクライアントの抽象インターフェース.

    LLMとの通信を担当する。
    """

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
        """テキストを生成する.

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）

        Returns:
            LLMレスポンス
        """
        pass

    @abstractmethod
    async def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict:
        """JSON形式でテキストを生成する.

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）

        Returns:
            パースされたJSON辞書
        """
        pass
