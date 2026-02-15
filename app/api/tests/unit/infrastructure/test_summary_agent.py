"""SummaryAgentのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.infrastructure.agents.summary_agent import SummaryAgent


class TestSummaryAgent:
    """SummaryAgentのテスト."""

    @pytest.mark.asyncio
    async def test_generate_summary_from_texts(self):
        """複数のテキストから要約を生成できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "summary": "This category covers research on transformer architectures...",
            "key_themes": ["attention mechanisms", "efficiency", "pretraining"],
        }

        agent = SummaryAgent(llm_client=mock_llm)
        texts = [
            "Paper 1 discusses attention mechanisms in transformers...",
            "Paper 2 proposes an efficient transformer variant...",
            "Paper 3 explores pretraining strategies...",
        ]
        result = await agent.generate_summary(texts, category_name="Transformers")

        assert "summary" in result
        assert "key_themes" in result
        assert len(result["key_themes"]) > 0

    @pytest.mark.asyncio
    async def test_generate_summary_with_single_text(self):
        """単一のテキストから要約を生成できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "summary": "This paper introduces a novel approach...",
            "key_themes": ["novelty"],
        }

        agent = SummaryAgent(llm_client=mock_llm)
        texts = ["A single paper abstract about neural networks..."]
        result = await agent.generate_summary(texts, category_name="Neural Networks")

        assert "summary" in result

    @pytest.mark.asyncio
    async def test_generate_summary_includes_category_in_prompt(self):
        """プロンプトにカテゴリ名が含まれる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "summary": "Summary text",
            "key_themes": [],
        }

        agent = SummaryAgent(llm_client=mock_llm)
        await agent.generate_summary(["text"], category_name="Deep Learning")

        call_args = mock_llm.generate_json.call_args
        prompt = call_args.kwargs["prompt"]
        assert "Deep Learning" in prompt
