"""サーベイ処理ユースケース."""

import asyncio
import logging

from src.core.config import settings
from src.domain.models.tag_hierarchy import TagHierarchy
from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import PaperId, SurveyId, TagId
from src.domain.repositories.survey_repository import SurveyRepository
from src.infrastructure.agents.characteristic_agent import CharacteristicAgent
from src.infrastructure.agents.hierarchy_agent import HierarchyAgent
from src.infrastructure.agents.summary_agent import SummaryAgent
from src.infrastructure.agents.tag_generator_agent import TagGeneratorAgent

logger = logging.getLogger(__name__)


class ProcessSurveyUseCase:
    """サーベイ処理ユースケース.

    サーベイ内の論文に対してタグ生成、階層化、要約生成、特徴抽出を行う。
    """

    def __init__(
        self,
        survey_repository: SurveyRepository,
        tag_generator: TagGeneratorAgent,
        hierarchy_agent: HierarchyAgent,
        summary_agent: SummaryAgent,
        characteristic_agent: CharacteristicAgent,
    ):
        """初期化.

        Args:
            survey_repository: サーベイリポジトリ
            tag_generator: タグ生成エージェント
            hierarchy_agent: 階層化エージェント
            summary_agent: 要約エージェント
            characteristic_agent: 特徴抽出エージェント
        """
        self._survey_repository = survey_repository
        self._tag_generator = tag_generator
        self._hierarchy_agent = hierarchy_agent
        self._summary_agent = summary_agent
        self._characteristic_agent = characteristic_agent

    async def execute(self, survey_id: SurveyId) -> None:
        """サーベイを処理する.

        Args:
            survey_id: 処理するサーベイのID

        Raises:
            ValueError: サーベイが見つからない場合
        """
        # サーベイを取得
        survey = await self._survey_repository.find_by_id(survey_id)
        if survey is None:
            raise ValueError(f"Survey not found: {survey_id}")

        # 処理開始（再処理時は既存タグ情報を初期化）
        survey.start_processing()
        survey.tag_hierarchy = TagHierarchy()
        survey.progress_message = ""
        survey.progress_current = 0
        survey.progress_total = 0
        survey.error_message = ""
        for paper in survey.papers:
            paper.tags = []
        await self._survey_repository.save(survey)

        skip_counts: dict[str, int] = {}
        semaphore = asyncio.Semaphore(settings.llm_max_concurrent)

        try:
            # Step 1: 各論文にタグを生成（並行処理）
            all_tags: list[str] = []
            paper_tags: dict[str, list[str]] = {}
            total_papers = len(survey.papers)
            completed_count = 0
            skip_counts["タグ生成"] = 0

            async def generate_tags_for_paper(paper):
                nonlocal completed_count
                async with semaphore:
                    try:
                        tags = await self._tag_generator.generate_tags(paper.abstract)
                        paper_tags[str(paper.id)] = tags
                        all_tags.extend(tags)
                    except Exception as e:
                        logger.warning(f"タグ生成スキップ (論文: {paper.title[:50]}): {e}")
                        paper_tags[str(paper.id)] = []
                        skip_counts["タグ生成"] += 1
                    finally:
                        completed_count += 1
                        survey.update_progress(
                            f"タグ生成中 (スキップ: {skip_counts['タグ生成']}件)"
                            if skip_counts["タグ生成"] > 0
                            else "タグ生成中",
                            completed_count,
                            total_papers,
                        )
                        if completed_count % 10 == 0:
                            await self._survey_repository.save(survey)

            await asyncio.gather(*[generate_tags_for_paper(p) for p in survey.papers])
            await self._survey_repository.save(survey)

            # Step 2: 類似タグを統合
            unique_tags = list(set(all_tags))
            survey.update_progress("類似タグを統合中", 0, 0)
            await self._survey_repository.save(survey)
            merged_result = await self._hierarchy_agent.merge_similar_tags(unique_tags)

            # 統合マッピングを作成
            tag_mapping: dict[str, str] = {}
            for merge_group in merged_result.get("merged_tags", []):
                canonical = merge_group["canonical"]
                for variant in merge_group.get("variants", []):
                    tag_mapping[variant] = canonical

            # Step 3: タグを階層化
            canonical_tags = list(set(tag_mapping.get(tag, tag) for tag in unique_tags))
            survey.update_progress("タグを階層化中", 0, 0)
            await self._survey_repository.save(survey)
            hierarchy_result = await self._hierarchy_agent.create_hierarchy(canonical_tags)

            # canonical_tag → paper_idsのマッピングを構築
            canonical_tag_to_papers: dict[str, list[str]] = {}
            for paper in survey.papers:
                for tag_name in paper_tags[str(paper.id)]:
                    canonical_name = tag_mapping.get(tag_name, tag_name)
                    canonical_tag_to_papers.setdefault(canonical_name, []).append(str(paper.id))

            # Step 4: TagHierarchyを構築
            tag_hierarchy = TagHierarchy()
            # original_tag（canonical_tag）→ child_idのマッピング
            original_tag_to_child_id: dict[str, TagId] = {}

            for category in hierarchy_result.get("categories", []):
                category_name = category["name"]
                category_id = TagId.generate()
                category_node = TagNode(id=category_id, name=category_name)

                for child in category.get("children", []):
                    # childは {"name": "...", "original_tags": [...]} 形式
                    if isinstance(child, str):
                        # フォールバック: 旧形式（文字列リスト）
                        child_name = child
                        child_original_tags = [child]
                    else:
                        child_name = child["name"]
                        child_original_tags = child.get("original_tags", [])

                    child_id = TagId.generate()
                    child_node = TagNode(
                        id=child_id,
                        name=child_name,
                        parent_id=category_id,
                    )
                    category_node.add_child(child_id)
                    tag_hierarchy.add_node(child_node)

                    # original_tagsからchild_idへのマッピングを記録
                    for orig_tag in child_original_tags:
                        original_tag_to_child_id[orig_tag] = child_id

                tag_hierarchy.add_node(category_node)

            # Step 5: 論文とタグを関連付け（original_tagsマッピング経由）
            for orig_tag, paper_id_strs in canonical_tag_to_papers.items():
                child_id = original_tag_to_child_id.get(orig_tag)
                if not child_id:
                    continue
                node = tag_hierarchy.get_node(child_id)
                if not node:
                    continue
                for pid_str in paper_id_strs:
                    paper = survey.get_paper(PaperId(pid_str))
                    if paper:
                        paper.add_tag(child_id)
                        node.add_paper(paper.id)

            survey.tag_hierarchy = tag_hierarchy

            # Step 6: ボトムアップで要約を生成
            nodes_with_papers = [n for n in tag_hierarchy.get_bottom_up_order() if n.paper_ids]
            total_nodes = len(nodes_with_papers)
            skip_counts["要約生成"] = 0
            for node_i, node in enumerate(nodes_with_papers):
                survey.update_progress("要約生成中", node_i, total_nodes)
                if node_i % 5 == 0:
                    await self._survey_repository.save(survey)
                if node.paper_ids:
                    # 関連論文のabstractを収集
                    texts = []
                    for paper_id in node.paper_ids:
                        paper = survey.get_paper(paper_id)
                        if paper:
                            texts.append(paper.abstract)

                    if texts:
                        try:
                            summary_result = await self._summary_agent.generate_summary(
                                texts, category_name=node.name
                            )
                            node.set_summary(summary_result.get("summary", ""))
                        except Exception as e:
                            logger.warning(f"要約生成スキップ (ノード: {node.name}): {e}")
                            skip_counts["要約生成"] += 1

            # Step 7: 各論文の特徴を抽出（並行処理）
            completed_count = 0
            skip_counts["特徴抽出"] = 0

            async def extract_characteristics_for_paper(paper):
                nonlocal completed_count
                async with semaphore:
                    try:
                        result = await self._characteristic_agent.extract_characteristics(
                            paper.abstract
                        )
                        paper.set_characteristics(result.get("characteristics", ""))
                    except Exception as e:
                        logger.warning(f"特徴抽出スキップ (論文: {paper.title[:50]}): {e}")
                        skip_counts["特徴抽出"] += 1
                    finally:
                        completed_count += 1
                        survey.update_progress("論文の特徴抽出中", completed_count, total_papers)
                        if completed_count % 10 == 0:
                            await self._survey_repository.save(survey)

            await asyncio.gather(*[extract_characteristics_for_paper(p) for p in survey.papers])
            await self._survey_repository.save(survey)

            # スキップ情報をまとめる
            skipped_parts = [
                f"{step}: {count}件" for step, count in skip_counts.items() if count > 0
            ]
            if skipped_parts:
                survey.error_message = f"一部スキップあり ({', '.join(skipped_parts)})"
                logger.info(f"サーベイ処理完了（{survey.error_message}）")

            # 完了
            survey.complete()
            await self._survey_repository.save(survey)

        except Exception as e:
            # エラー時は失敗ステータスに
            survey.fail(str(e))
            await self._survey_repository.save(survey)
            raise
