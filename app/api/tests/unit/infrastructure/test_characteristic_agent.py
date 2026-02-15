"""CharacteristicAgentのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.infrastructure.agents.characteristic_agent import CharacteristicAgent


class TestCharacteristicAgent:
    """CharacteristicAgentのテスト."""

    @pytest.mark.asyncio
    async def test_extract_characteristics(self):
        """論文の特徴を抽出できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "characteristics": (
                "This paper proposes a novel attention mechanism that achieves "
                "state-of-the-art results on multiple NLP benchmarks."
            )
        }

        agent = CharacteristicAgent(llm_client=mock_llm)
        abstract = (
            "We propose a new attention mechanism for transformer models. "
            "Our approach improves efficiency while maintaining accuracy..."
        )
        context = "This paper belongs to the Transformer Architectures category."

        result = await agent.extract_characteristics(abstract, context)

        assert "characteristics" in result
        assert len(result["characteristics"]) > 0

    @pytest.mark.asyncio
    async def test_extract_characteristics_without_context(self):
        """コンテキストなしでも特徴を抽出できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "characteristics": "A paper about machine learning methods."
        }

        agent = CharacteristicAgent(llm_client=mock_llm)
        abstract = "This paper discusses machine learning approaches..."

        result = await agent.extract_characteristics(abstract)

        assert "characteristics" in result

    @pytest.mark.asyncio
    async def test_extract_characteristics_includes_abstract_in_prompt(self):
        """プロンプトにabstractが含まれる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {"characteristics": "test"}

        agent = CharacteristicAgent(llm_client=mock_llm)
        abstract = "Unique abstract text for testing"
        await agent.extract_characteristics(abstract)

        call_args = mock_llm.generate_json.call_args
        prompt = call_args.kwargs["prompt"]
        assert abstract in prompt
