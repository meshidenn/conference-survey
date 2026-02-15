"""タグ生成エージェント."""

from src.domain.services.llm_client import LLMClient


class TagGeneratorAgent:
    """論文のabstractからタグを生成するエージェント.

    各論文に対して3-5個の研究トピックタグを生成する。
    """

    SYSTEM_PROMPT = (
        "You are a research paper tagging expert. "
        "Your task is to analyze academic paper abstracts "
        "and generate relevant topic tags.\n\n"
        "Guidelines:\n"
        "- Generate 3-5 concise, specific research topic tags\n"
        "- Use standard academic terminology\n"
        "- Tags should capture the main research areas, methods, and applications\n"
        "- Avoid overly broad or generic tags\n"
        "- Return tags in JSON format"
    )

    def __init__(self, llm_client: LLMClient):
        """初期化.

        Args:
            llm_client: LLMクライアント
        """
        self._llm_client = llm_client

    async def generate_tags(self, abstract: str) -> list[str]:
        """abstractからタグを生成する.

        Args:
            abstract: 論文の概要

        Returns:
            生成されたタグのリスト（3-5個）
        """
        prompt = (
            "Analyze the following academic paper abstract "
            "and generate 3-5 research topic tags.\n\n"
            f"Abstract:\n{abstract}\n\n"
            "Return the tags in the following JSON format:\n"
            '{"tags": ["tag1", "tag2", "tag3"]}'
        )

        result = await self._llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )

        return result.get("tags", [])
