"""サーベイAPIエンドポイントのE2Eテスト."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.domain.models.paper import Paper
from src.domain.models.survey import Survey, SurveyStatus
from src.domain.models.tag_hierarchy import TagHierarchy
from src.domain.models.tag_node import TagNode
from src.domain.models.value_objects import (
    Conference,
    ConferenceType,
    PaperId,
    SurveyId,
    TagId,
)
from src.entrypoint.main import app
from src.infrastructure.repositories.in_memory_survey_repository import (
    InMemorySurveyRepository,
)

# ルートモジュールでimportされた関数をパッチするためのパス
_ROUTES = "src.presentation.routes.surveys"


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ."""
    return InMemorySurveyRepository()


@pytest.fixture
def mock_paper_fetcher():
    """論文取得のモック."""
    fetcher = AsyncMock()
    fetcher.fetch.return_value = [
        Paper(
            id=PaperId("paper-001"),
            title="Attention Is All You Need",
            authors=["Author A", "Author B"],
            abstract="We propose a new architecture based on attention mechanisms.",
        ),
        Paper(
            id=PaperId("paper-002"),
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Author C"],
            abstract="We introduce BERT, a language representation model.",
        ),
    ]
    return fetcher


@pytest.fixture
def client(repository):
    """テスト用HTTPクライアント（リポジトリをモック注入）."""
    with patch(f"{_ROUTES}.get_survey_repository", return_value=repository):
        transport = httpx.ASGITransport(app=app)
        yield httpx.AsyncClient(transport=transport, base_url="http://test")


class TestCreateSurvey:
    """POST /surveys のテスト."""

    async def test_サーベイを作成できる(self, client, repository, mock_paper_fetcher):
        """正常系: サーベイが作成され201が返る."""
        with patch(f"{_ROUTES}.get_create_survey_use_case") as mock_uc_fn:
            from src.application.use_cases.create_survey import CreateSurveyUseCase

            use_case = CreateSurveyUseCase(
                paper_fetcher=mock_paper_fetcher,
                survey_repository=repository,
            )
            mock_uc_fn.return_value = use_case

            response = await client.post(
                "/surveys",
                json={"conference_type": "ACL", "year": 2024},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["conferenceType"] == "ACL"
        assert data["year"] == 2024
        assert data["status"] == "pending"
        assert data["paperCount"] == 2
        assert "id" in data

    async def test_無効な学会種別で400エラー(self, client):
        """異常系: 無効な学会種別で400が返る."""
        response = await client.post(
            "/surveys",
            json={"conference_type": "INVALID", "year": 2024},
        )

        assert response.status_code == 400

    async def test_年度が範囲外で422エラー(self, client):
        """異常系: 年度がバリデーション範囲外で422が返る."""
        response = await client.post(
            "/surveys",
            json={"conference_type": "ACL", "year": 9999},
        )

        assert response.status_code == 422


class TestGetSurvey:
    """GET /surveys/{id} のテスト."""

    async def test_サーベイ詳細を取得できる(self, client, repository):
        """正常系: 存在するサーベイの詳細が返る."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.add_paper(
            Paper(
                id=PaperId("paper-001"),
                title="Test Paper",
                authors=["Author A"],
                abstract="Test abstract.",
            )
        )
        await repository.save(survey)

        response = await client.get(f"/surveys/{survey.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(survey.id)
        assert data["conferenceType"] == "ACL"
        assert data["year"] == 2024
        assert data["status"] == "pending"
        assert len(data["papers"]) == 1
        assert data["papers"][0]["title"] == "Test Paper"
        assert data["papers"][0]["authors"] == ["Author A"]
        assert data["papers"][0]["abstract"] == "Test abstract."

    async def test_存在しないサーベイで404エラー(self, client):
        """異常系: 存在しないIDで404が返る."""
        fake_id = SurveyId.generate()
        response = await client.get(f"/surveys/{fake_id}")

        assert response.status_code == 404

    async def test_無効なIDフォーマットで400エラー(self, client):
        """異常系: UUID形式でないIDで400が返る."""
        response = await client.get("/surveys/not-a-uuid")

        assert response.status_code == 400


class TestListSurveys:
    """GET /surveys のテスト."""

    async def test_空の一覧を取得できる(self, client):
        """正常系: サーベイがない場合は空リストが返る."""
        response = await client.get("/surveys")

        assert response.status_code == 200
        assert response.json() == []

    async def test_複数のサーベイ一覧を取得できる(self, client, repository):
        """正常系: 複数のサーベイが一覧で返る."""
        for conf_type in [ConferenceType.ACL, ConferenceType.EMNLP]:
            survey = Survey(
                id=SurveyId.generate(),
                conference=Conference(type=conf_type, year=2024),
            )
            await repository.save(survey)

        response = await client.get("/surveys")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestProcessSurvey:
    """POST /surveys/{id}/process のテスト."""

    async def test_処理を開始できる(self, client, repository):
        """正常系: 処理開始で202が返る."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        survey.add_paper(
            Paper(
                id=PaperId("paper-001"),
                title="Test Paper",
                authors=["Author A"],
                abstract="Test abstract.",
            )
        )
        await repository.save(survey)

        with patch(f"{_ROUTES}.get_process_survey_use_case") as mock_uc:
            mock_uc.return_value = AsyncMock()
            response = await client.post(f"/surveys/{survey.id}/process")

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "processing"
        assert data["id"] == str(survey.id)

    async def test_存在しないサーベイで404エラー(self, client):
        """異常系: 存在しないIDで404が返る."""
        fake_id = SurveyId.generate()
        response = await client.post(f"/surveys/{fake_id}/process")

        assert response.status_code == 404

    async def test_無効なIDフォーマットで400エラー(self, client):
        """異常系: UUID形式でないIDで400が返る."""
        response = await client.post("/surveys/not-a-uuid/process")

        assert response.status_code == 400


class TestGetMindmap:
    """GET /surveys/{id}/mindmap のテスト."""

    async def test_空のマインドマップを取得できる(self, client, repository):
        """正常系: タグ階層が空の場合、空のルートノードが返る."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        await repository.save(survey)

        response = await client.get(f"/surveys/{survey.id}/mindmap")

        assert response.status_code == 200
        data = response.json()
        assert data["surveyId"] == str(survey.id)
        assert data["conferenceType"] == "ACL"
        assert data["year"] == 2024
        assert data["rootNodes"] == []

    async def test_階層構造のあるマインドマップを取得できる(self, client, repository):
        """正常系: タグ階層がある場合、ツリー構造のマインドマップが返る."""
        survey = Survey(
            id=SurveyId.generate(),
            conference=Conference(type=ConferenceType.ACL, year=2024),
        )
        paper = Paper(
            id=PaperId("paper-001"),
            title="Test Paper",
            authors=["Author A"],
            abstract="Test abstract.",
        )
        survey.add_paper(paper)

        # タグ階層を構築
        parent_id = TagId.generate()
        child_id = TagId.generate()
        parent_node = TagNode(id=parent_id, name="NLP")
        child_node = TagNode(id=child_id, name="Transformer", parent_id=parent_id)
        child_node.add_paper(paper.id)
        child_node.set_summary("Transformerに関する研究")
        parent_node.add_child(child_id)

        hierarchy = TagHierarchy()
        hierarchy.add_node(parent_node)
        hierarchy.add_node(child_node)
        survey.tag_hierarchy = hierarchy

        await repository.save(survey)

        response = await client.get(f"/surveys/{survey.id}/mindmap")

        assert response.status_code == 200
        data = response.json()
        assert len(data["rootNodes"]) == 1

        root = data["rootNodes"][0]
        assert root["name"] == "NLP"
        assert len(root["children"]) == 1

        child = root["children"][0]
        assert child["name"] == "Transformer"
        assert child["paperCount"] == 1
        assert child["summary"] == "Transformerに関する研究"

    async def test_存在しないサーベイで404エラー(self, client):
        """異常系: 存在しないIDで404が返る."""
        fake_id = SurveyId.generate()
        response = await client.get(f"/surveys/{fake_id}/mindmap")

        assert response.status_code == 404

    async def test_無効なIDフォーマットで400エラー(self, client):
        """異常系: UUID形式でないIDで400が返る."""
        response = await client.get("/surveys/not-a-uuid/mindmap")

        assert response.status_code == 400
