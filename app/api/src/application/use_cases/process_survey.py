"""サーベイ処理ユースケース."""

from src.domain.models.tag_hierarchy import TagHierarchy
from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import SurveyId, TagId
from src.domain.repositories.survey_repository import SurveyRepository
from src.infrastructure.agents.characteristic_agent import CharacteristicAgent
from src.infrastructure.agents.hierarchy_agent import HierarchyAgent
from src.infrastructure.agents.summary_agent import SummaryAgent
from src.infrastructure.agents.tag_generator_agent import TagGeneratorAgent


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

        # 処理開始
        survey.start_processing()
        await self._survey_repository.save(survey)

        try:
            # Step 1: 各論文にタグを生成
            all_tags: list[str] = []
            paper_tags: dict[str, list[str]] = {}

            for paper in survey.papers:
                tags = await self._tag_generator.generate_tags(paper.abstract)
                paper_tags[str(paper.id)] = tags
                all_tags.extend(tags)

            # Step 2: 類似タグを統合
            unique_tags = list(set(all_tags))
            merged_result = await self._hierarchy_agent.merge_similar_tags(unique_tags)

            # 統合マッピングを作成
            tag_mapping: dict[str, str] = {}
            for merge_group in merged_result.get("merged_tags", []):
                canonical = merge_group["canonical"]
                for variant in merge_group.get("variants", []):
                    tag_mapping[variant] = canonical

            # Step 3: タグを階層化
            canonical_tags = list(
                set(tag_mapping.get(tag, tag) for tag in unique_tags)
            )
            hierarchy_result = await self._hierarchy_agent.create_hierarchy(
                canonical_tags
            )

            # Step 4: TagHierarchyを構築
            tag_hierarchy = TagHierarchy()
            tag_name_to_id: dict[str, TagId] = {}

            for category in hierarchy_result.get("categories", []):
                category_name = category["name"]
                category_id = TagId.generate()
                category_node = TagNode(id=category_id, name=category_name)

                for child_name in category.get("children", []):
                    child_id = TagId.generate()
                    child_node = TagNode(
                        id=child_id,
                        name=child_name,
                        parent_id=category_id,
                    )
                    category_node.add_child(child_id)
                    tag_hierarchy.add_node(child_node)
                    tag_name_to_id[child_name] = child_id

                tag_hierarchy.add_node(category_node)
                tag_name_to_id[category_name] = category_id

            # Step 5: 論文とタグを関連付け
            for paper in survey.papers:
                paper_tag_names = paper_tags[str(paper.id)]
                for tag_name in paper_tag_names:
                    canonical_name = tag_mapping.get(tag_name, tag_name)
                    if canonical_name in tag_name_to_id:
                        tag_id = tag_name_to_id[canonical_name]
                        paper.add_tag(tag_id)
                        node = tag_hierarchy.get_node(tag_id)
                        if node:
                            node.add_paper(paper.id)

            survey.tag_hierarchy = tag_hierarchy

            # Step 6: ボトムアップで要約を生成
            for node in tag_hierarchy.get_bottom_up_order():
                if node.paper_ids:
                    # 関連論文のabstractを収集
                    texts = []
                    for paper_id in node.paper_ids:
                        paper = survey.get_paper(paper_id)
                        if paper:
                            texts.append(paper.abstract)

                    if texts:
                        summary_result = await self._summary_agent.generate_summary(
                            texts, category_name=node.name
                        )
                        node.set_summary(summary_result.get("summary", ""))

            # Step 7: 各論文の特徴を抽出
            for paper in survey.papers:
                result = await self._characteristic_agent.extract_characteristics(
                    paper.abstract
                )
                paper.set_characteristics(result.get("characteristics", ""))

            # 完了
            survey.complete()
            await self._survey_repository.save(survey)

        except Exception:
            # エラー時は失敗ステータスに
            survey.fail()
            await self._survey_repository.save(survey)
            raise
