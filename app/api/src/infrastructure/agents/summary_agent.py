"""要約生成エージェント."""

from src.domain.services.llm_client import LLMClient


class SummaryAgent:
    """カテゴリの要約を生成するエージェント.

    関連する論文群から、カテゴリの要約とキーテーマを抽出する。
    """

    SYSTEM_PROMPT = """You are an expert at summarizing academic research trends.

Guidelines:
- Create a concise summary (2-3 sentences) capturing the main research themes
- Identify 3-5 key themes or trends
- Use clear, accessible language
- Focus on the overall direction rather than specific papers
- Return the result in JSON format"""

    def __init__(self, llm_client: LLMClient):
        """初期化.

        Args:
            llm_client: LLMクライアント
        """
        self._llm_client = llm_client

    async def generate_summary(self, texts: list[str], category_name: str) -> dict:
        """複数のテキストからカテゴリの要約を生成する.

        Args:
            texts: 論文のabstractまたは特徴のリスト
            category_name: カテゴリ名

        Returns:
            要約結果を表す辞書
            {
                "summary": "カテゴリの要約文",
                "key_themes": ["theme1", "theme2", "theme3"]
            }
        """
        texts_str = "\n\n---\n\n".join(texts)
        prompt = f"""Summarize the following research papers in the category "{category_name}".

Papers:
{texts_str}

Return the result in the following JSON format:
{{
    "summary": "A 2-3 sentence summary of the research trends in this category",
    "key_themes": ["theme1", "theme2", "theme3"]
}}"""

        return await self._llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )
