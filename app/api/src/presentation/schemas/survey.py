"""サーベイ関連のAPIスキーマ."""

from pydantic import BaseModel, ConfigDict, Field


class CreateSurveyRequest(BaseModel):
    """サーベイ作成リクエスト."""

    conference_type: str = Field(
        ...,
        alias="conferenceType",
        description="学会種別 (ACL, NAACL, EMNLP, EACL)",
        examples=["ACL"],
    )
    year: int = Field(
        ...,
        description="開催年度",
        ge=1900,
        le=2100,
        examples=[2024],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conferenceType": "ACL",
                "year": 2024,
            }
        },
        populate_by_name=True,
    )


class PaperResponse(BaseModel):
    """論文レスポンス."""

    id: str = Field(..., description="論文ID")
    title: str = Field(..., description="タイトル")
    authors: list[str] = Field(..., description="著者リスト")
    abstract: str = Field(..., description="概要")
    characteristics: str | None = Field(None, description="論文の特徴")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TagNodeResponse(BaseModel):
    """タグノードレスポンス."""

    id: str = Field(..., description="タグID")
    name: str = Field(..., description="タグ名")
    parent_id: str | None = Field(None, alias="parentId", description="親ノードID")
    child_ids: list[str] = Field(
        default_factory=list, alias="childIds", description="子ノードIDリスト"
    )
    paper_ids: list[str] = Field(
        default_factory=list, alias="paperIds", description="関連論文IDリスト"
    )
    paper_count: int = Field(0, alias="paperCount", description="関連論文数")
    summary: str | None = Field(None, description="カテゴリ要約")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SurveyResponse(BaseModel):
    """サーベイレスポンス."""

    id: str = Field(..., description="サーベイID")
    conference_type: str = Field(..., alias="conferenceType", description="学会種別")
    year: int = Field(..., description="開催年度")
    status: str = Field(..., description="処理ステータス")
    paper_count: int = Field(0, alias="paperCount", description="論文数")
    progress_message: str = Field("", alias="progressMessage", description="進捗メッセージ")
    progress_current: int = Field(0, alias="progressCurrent", description="現在の進捗数")
    progress_total: int = Field(0, alias="progressTotal", description="合計数")
    error_message: str = Field("", alias="errorMessage", description="エラーメッセージ")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SurveyDetailResponse(BaseModel):
    """サーベイ詳細レスポンス."""

    id: str = Field(..., description="サーベイID")
    conference_type: str = Field(..., alias="conferenceType", description="学会種別")
    year: int = Field(..., description="開催年度")
    status: str = Field(..., description="処理ステータス")
    papers: list[PaperResponse] = Field(default_factory=list, description="論文リスト")
    tag_hierarchy: list[TagNodeResponse] = Field(
        default_factory=list, alias="tagHierarchy", description="タグ階層構造"
    )
    progress_message: str = Field("", alias="progressMessage", description="進捗メッセージ")
    progress_current: int = Field(0, alias="progressCurrent", description="現在の進捗数")
    progress_total: int = Field(0, alias="progressTotal", description="合計数")
    error_message: str = Field("", alias="errorMessage", description="エラーメッセージ")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MindmapNode(BaseModel):
    """マインドマップノード."""

    id: str = Field(..., description="ノードID")
    name: str = Field(..., description="ノード名")
    summary: str | None = Field(None, description="要約")
    paper_count: int = Field(0, alias="paperCount", description="関連論文数")
    children: list["MindmapNode"] = Field(default_factory=list, description="子ノード")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class MindmapResponse(BaseModel):
    """マインドマップレスポンス."""

    survey_id: str = Field(..., alias="surveyId", description="サーベイID")
    conference_type: str = Field(..., alias="conferenceType", description="学会種別")
    year: int = Field(..., description="開催年度")
    root_nodes: list[MindmapNode] = Field(
        default_factory=list, alias="rootNodes", description="ルートノード"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
