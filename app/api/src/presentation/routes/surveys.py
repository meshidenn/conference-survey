"""サーベイ関連のAPIルート."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import Conference, SurveyId
from src.presentation.deps import (
    get_create_survey_use_case,
    get_process_survey_use_case,
    get_survey_repository,
    parse_conference_type,
)
from src.presentation.schemas.survey import (
    CreateSurveyRequest,
    MindmapNode,
    MindmapResponse,
    PaperResponse,
    SurveyDetailResponse,
    SurveyResponse,
    TagNodeResponse,
)

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.post("", response_model=SurveyResponse, status_code=201)
async def create_survey(request: CreateSurveyRequest) -> SurveyResponse:
    """サーベイを作成する.

    指定された学会の論文を取得し、新しいサーベイを作成する。
    """
    try:
        conference_type = parse_conference_type(request.conference_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    conference = Conference(type=conference_type, year=request.year)
    use_case = get_create_survey_use_case(conference)

    try:
        survey = await use_case.execute(conference)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create survey: {e}")

    return SurveyResponse(
        id=str(survey.id),
        conference_type=survey.conference.type.value,
        year=survey.conference.year,
        status=survey.status.value,
        paper_count=len(survey.papers),
        progress_message=survey.progress_message,
        progress_current=survey.progress_current,
        progress_total=survey.progress_total,
        error_message=survey.error_message,
    )


@router.get("/{survey_id}", response_model=SurveyDetailResponse)
async def get_survey(survey_id: str) -> SurveyDetailResponse:
    """サーベイ詳細を取得する."""
    try:
        uuid_id = UUID(survey_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid survey ID format")

    repository = get_survey_repository()
    survey = await repository.find_by_id(SurveyId(uuid_id))

    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    papers = [
        PaperResponse(
            id=str(paper.id),
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            characteristics=paper.characteristics,
        )
        for paper in survey.papers
    ]

    tag_nodes = [
        TagNodeResponse(
            id=str(node.id),
            name=node.name,
            parent_id=str(node.parent_id) if node.parent_id else None,
            child_ids=[str(cid) for cid in node.child_ids],
            paper_ids=[str(pid) for pid in node.paper_ids],
            paper_count=survey.tag_hierarchy.get_total_paper_count(node.id),
            summary=node.summary,
        )
        for node in survey.tag_hierarchy.nodes.values()
    ]

    return SurveyDetailResponse(
        id=str(survey.id),
        conference_type=survey.conference.type.value,
        year=survey.conference.year,
        status=survey.status.value,
        papers=papers,
        tag_hierarchy=tag_nodes,
        progress_message=survey.progress_message,
        progress_current=survey.progress_current,
        progress_total=survey.progress_total,
        error_message=survey.error_message,
    )


@router.get("", response_model=list[SurveyResponse])
async def list_surveys() -> list[SurveyResponse]:
    """サーベイ一覧を取得する."""
    repository = get_survey_repository()
    surveys = await repository.find_all()

    return [
        SurveyResponse(
            id=str(survey.id),
            conference_type=survey.conference.type.value,
            year=survey.conference.year,
            status=survey.status.value,
            paper_count=len(survey.papers),
            progress_message=survey.progress_message,
            progress_current=survey.progress_current,
            progress_total=survey.progress_total,
            error_message=survey.error_message,
        )
        for survey in surveys
    ]


@router.post("/{survey_id}/process", response_model=SurveyResponse, status_code=202)
async def process_survey(
    survey_id: str, background_tasks: BackgroundTasks
) -> SurveyResponse:
    """サーベイ処理を開始する（非同期）.

    タグ生成、階層化、要約生成、特徴抽出を非同期で実行する。
    """
    try:
        uuid_id = UUID(survey_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid survey ID format")

    repository = get_survey_repository()
    survey = await repository.find_by_id(SurveyId(uuid_id))

    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    if survey.status.value == "processing":
        raise HTTPException(
            status_code=409,
            detail="Processing already in progress",
        )

    if survey.status.value not in ("pending", "failed"):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start processing from status: {survey.status.value}",
        )

    # バックグラウンドで処理を実行
    use_case = get_process_survey_use_case()
    background_tasks.add_task(use_case.execute, survey.id)

    return SurveyResponse(
        id=str(survey.id),
        conference_type=survey.conference.type.value,
        year=survey.conference.year,
        status="processing",  # 処理開始を示す
        paper_count=len(survey.papers),
        progress_message=survey.progress_message,
        progress_current=survey.progress_current,
        progress_total=survey.progress_total,
        error_message=survey.error_message,
    )


def _build_mindmap_node(node: TagNode, hierarchy_nodes: dict, tag_hierarchy) -> MindmapNode:
    """TagNodeからMindmapNodeを構築する."""
    children = []
    for child_id in node.child_ids:
        child_node = hierarchy_nodes.get(child_id)
        if child_node:
            children.append(_build_mindmap_node(child_node, hierarchy_nodes, tag_hierarchy))

    return MindmapNode(
        id=str(node.id),
        name=node.name,
        summary=node.summary,
        paper_count=tag_hierarchy.get_total_paper_count(node.id),
        children=children,
    )


@router.get("/{survey_id}/status", response_model=SurveyResponse)
async def get_survey_status(survey_id: str) -> SurveyResponse:
    """サーベイのステータスと進捗を取得する（軽量）."""
    try:
        uuid_id = UUID(survey_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid survey ID format")

    repository = get_survey_repository()
    survey = await repository.find_by_id(SurveyId(uuid_id))

    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    return SurveyResponse(
        id=str(survey.id),
        conference_type=survey.conference.type.value,
        year=survey.conference.year,
        status=survey.status.value,
        paper_count=len(survey.papers),
        progress_message=survey.progress_message,
        progress_current=survey.progress_current,
        progress_total=survey.progress_total,
        error_message=survey.error_message,
    )


@router.get("/{survey_id}/mindmap", response_model=MindmapResponse)
async def get_mindmap(survey_id: str) -> MindmapResponse:
    """マインドマップ用データを取得する."""
    try:
        uuid_id = UUID(survey_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid survey ID format")

    repository = get_survey_repository()
    survey = await repository.find_by_id(SurveyId(uuid_id))

    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    # ルートノードからマインドマップを構築
    hierarchy_nodes = {node.id: node for node in survey.tag_hierarchy.nodes.values()}
    root_nodes = [
        _build_mindmap_node(node, hierarchy_nodes, survey.tag_hierarchy)
        for node in survey.tag_hierarchy.get_root_nodes()
    ]

    return MindmapResponse(
        survey_id=str(survey.id),
        conference_type=survey.conference.type.value,
        year=survey.conference.year,
        root_nodes=root_nodes,
    )
