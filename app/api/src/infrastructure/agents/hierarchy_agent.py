"""タグ階層化エージェント."""

from src.domain.services.llm_client import LLMClient


class HierarchyAgent:
    """タグを階層構造に整理するエージェント.

    類似タグの統合と、カテゴリへの階層化を行う。
    """

    HIERARCHY_SYSTEM_PROMPT = (
        "You are an expert at organizing research topics "
        "into hierarchical categories.\n\n"
        "Guidelines:\n"
        "- Create 5-10 top-level categories\n"
        "- Group related research topics together\n"
        "- Use clear, descriptive category names\n"
        "- You may rename or rephrase child names for clarity\n"
        "- Each child must list the original input tags it covers "
        "in the 'original_tags' field using the EXACT original names\n"
        "- Every input tag must appear in exactly one child\n"
        "- Return the result in JSON format"
    )

    MERGE_SYSTEM_PROMPT = (
        "You are an expert at identifying and merging "
        "similar research topic tags.\n\n"
        "Guidelines:\n"
        "- Identify tags that refer to the same concept\n"
        "- Choose a canonical (standard) name for each group\n"
        "- List all variants that should be merged\n"
        "- Return the result in JSON format"
    )

    def __init__(self, llm_client: LLMClient):
        """初期化.

        Args:
            llm_client: LLMクライアント
        """
        self._llm_client = llm_client

    async def create_hierarchy(self, tags: list[str]) -> dict:
        """タグを階層構造に整理する.

        Args:
            tags: タグのリスト

        Returns:
            階層構造を表す辞書
            {
                "categories": [
                    {
                        "name": "Category Name",
                        "children": [
                            {"name": "Child Name", "original_tags": ["tag1", "tag2"]}
                        ]
                    },
                    ...
                ]
            }
        """
        tags_str = ", ".join(tags)
        prompt = (
            "Organize the following research topic tags "
            "into 5-10 hierarchical categories.\n\n"
            "You may rename or group tags into clearer child names, "
            "but each child must list which original input tags it covers.\n\n"
            f"Tags:\n{tags_str}\n\n"
            "Return the result in the following JSON format:\n"
            "{\n"
            '    "categories": [\n'
            "        {\n"
            '            "name": "Category Name",\n'
            '            "children": [\n'
            '                {"name": "Child Name", "original_tags": ["tag1", "tag2"]},\n'
            '                {"name": "Another Child", "original_tags": ["tag3"]}\n'
            "            ]\n"
            "        },\n"
            "        ...\n"
            "    ]\n"
            "}"
        )

        return await self._llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.HIERARCHY_SYSTEM_PROMPT,
        )

    async def merge_similar_tags(self, tags: list[str]) -> dict:
        """類似タグを統合する.

        Args:
            tags: タグのリスト

        Returns:
            統合結果を表す辞書
            {
                "merged_tags": [
                    {"canonical": "Standard Name", "variants": ["var1", "var2"]},
                    ...
                ]
            }
        """
        tags_str = ", ".join(tags)
        prompt = (
            "Identify and group similar research topic tags "
            "that refer to the same concept.\n\n"
            f"Tags:\n{tags_str}\n\n"
            "Return the result in the following JSON format:\n"
            "{\n"
            '    "merged_tags": [\n'
            '        {"canonical": "Standard Name", "variants": ["variant1", "variant2"]},\n'
            "        ...\n"
            "    ]\n"
            "}"
        )

        return await self._llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.MERGE_SYSTEM_PROMPT,
        )
