"""TagGeneratorAgentのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.infrastructure.agents.tag_generator_agent import TagGeneratorAgent


class TestTagGeneratorAgent:
    """TagGeneratorAgentのテスト."""

    @pytest.mark.asyncio
    async def test_generate_tags_from_abstract(self):
        """abstractからタグを生成できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "tags": [
                "Natural Language Processing",
                "Transformer",
                "Machine Learning",
            ]
        }

        agent = TagGeneratorAgent(llm_client=mock_llm)
        abstract = (
            "We propose a new transformer-based model for natural language "
            "understanding. Our approach uses self-attention mechanisms..."
        )
        tags = await agent.generate_tags(abstract)

        assert len(tags) == 3
        assert "Natural Language Processing" in tags
        assert "Transformer" in tags
        assert "Machine Learning" in tags

    @pytest.mark.asyncio
    async def test_generate_tags_returns_3_to_5_tags(self):
        """3-5個のタグを返す."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"]
        }

        agent = TagGeneratorAgent(llm_client=mock_llm)
        tags = await agent.generate_tags("Some abstract text")

        assert 3 <= len(tags) <= 5

    @pytest.mark.asyncio
    async def test_generate_tags_handles_empty_response(self):
        """空のレスポンスを処理できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {"tags": []}

        agent = TagGeneratorAgent(llm_client=mock_llm)
        tags = await agent.generate_tags("Some abstract text")

        assert tags == []

    @pytest.mark.asyncio
    async def test_generate_tags_uses_correct_prompt(self):
        """正しいプロンプトを使用する."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {"tags": ["Tag1", "Tag2", "Tag3"]}

        agent = TagGeneratorAgent(llm_client=mock_llm)
        abstract = "Test abstract"
        await agent.generate_tags(abstract)

        # プロンプトにabstractが含まれていることを確認
        call_args = mock_llm.generate_json.call_args
        prompt = call_args.kwargs["prompt"]
        assert abstract in prompt
