"""論文特徴抽出エージェント."""

from src.domain.services.llm_client import LLMClient


class CharacteristicAgent:
    """論文の特徴を抽出するエージェント.

    各論文の独自の貢献や特徴を簡潔に記述する。
    """

    SYSTEM_PROMPT = (
        "You are an expert at analyzing academic papers "
        "and extracting their key characteristics.\n\n"
        "Guidelines:\n"
        "- Focus on what makes this paper unique or important\n"
        "- Describe the main contribution in 1-2 sentences\n"
        "- Be concise and specific\n"
        "- Use technical but accessible language\n"
        "- Return the result in JSON format"
    )

    def __init__(self, llm_client: LLMClient):
        """初期化.

        Args:
            llm_client: LLMクライアント
        """
        self._llm_client = llm_client

    async def extract_characteristics(
        self, abstract: str, context: str | None = None
    ) -> dict:
        """論文の特徴を抽出する.

        Args:
            abstract: 論文の概要
            context: 追加のコンテキスト（カテゴリ情報など、オプション）

        Returns:
            特徴を表す辞書
            {
                "characteristics": "論文の特徴を説明する1-2文"
            }
        """
        context_str = f"\nContext: {context}" if context else ""
        prompt = (
            f"Extract the key characteristics of this academic paper.{context_str}\n\n"
            f"Abstract:\n{abstract}\n\n"
            "Return the result in the following JSON format:\n"
            '{\n    "characteristics": '
            '"A 1-2 sentence description of what makes this paper unique or important"\n}'
        )

        return await self._llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )
