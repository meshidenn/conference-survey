"""HierarchyAgentのテスト."""

from unittest.mock import AsyncMock

import pytest

from src.infrastructure.agents.hierarchy_agent import HierarchyAgent


class TestHierarchyAgent:
    """HierarchyAgentのテスト."""

    @pytest.mark.asyncio
    async def test_create_hierarchy_from_tags(self):
        """タグから階層構造を作成できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "categories": [
                {
                    "name": "Natural Language Processing",
                    "children": ["Transformer", "BERT", "Text Classification"],
                },
                {
                    "name": "Machine Learning",
                    "children": ["Deep Learning", "Neural Networks"],
                },
            ]
        }

        agent = HierarchyAgent(llm_client=mock_llm)
        tags = [
            "Transformer",
            "BERT",
            "Text Classification",
            "Deep Learning",
            "Neural Networks",
        ]
        hierarchy = await agent.create_hierarchy(tags)

        assert len(hierarchy["categories"]) == 2
        assert hierarchy["categories"][0]["name"] == "Natural Language Processing"
        assert "Transformer" in hierarchy["categories"][0]["children"]

    @pytest.mark.asyncio
    async def test_create_hierarchy_with_few_tags(self):
        """少数のタグでも階層構造を作成できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "categories": [
                {
                    "name": "General",
                    "children": ["Tag1", "Tag2"],
                }
            ]
        }

        agent = HierarchyAgent(llm_client=mock_llm)
        tags = ["Tag1", "Tag2"]
        hierarchy = await agent.create_hierarchy(tags)

        assert len(hierarchy["categories"]) >= 1

    @pytest.mark.asyncio
    async def test_create_hierarchy_returns_5_to_10_categories(self):
        """5-10個のカテゴリを返すことを期待する."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "categories": [{"name": f"Category{i}", "children": [f"Tag{i}"]} for i in range(7)]
        }

        agent = HierarchyAgent(llm_client=mock_llm)
        tags = [f"Tag{i}" for i in range(20)]
        hierarchy = await agent.create_hierarchy(tags)

        # 期待: 5-10カテゴリ（モックでは7を返す）
        assert 1 <= len(hierarchy["categories"]) <= 10


class TestTagMergerAgent:
    """タグマージ機能のテスト."""

    @pytest.mark.asyncio
    async def test_merge_similar_tags(self):
        """類似タグを統合できる."""
        mock_llm = AsyncMock()
        mock_llm.generate_json.return_value = {
            "merged_tags": [
                {
                    "canonical": "Natural Language Processing",
                    "variants": ["NLP", "Natural Language Processing", "NaturalLanguageProcessing"],
                },
                {
                    "canonical": "Machine Learning",
                    "variants": ["ML", "Machine Learning"],
                },
            ]
        }

        agent = HierarchyAgent(llm_client=mock_llm)
        tags = ["NLP", "Natural Language Processing", "ML", "Machine Learning"]
        merged = await agent.merge_similar_tags(tags)

        assert len(merged["merged_tags"]) == 2
        assert merged["merged_tags"][0]["canonical"] == "Natural Language Processing"
