"""依存性注入."""

from functools import lru_cache

from src.application.use_cases.create_survey import CreateSurveyUseCase
from src.application.use_cases.process_survey import ProcessSurveyUseCase
from src.domain.models.value_objects import Conference, ConferenceType
from src.domain.repositories.survey_repository import SurveyRepository
from src.domain.services.llm_client import LLMClient
from src.infrastructure.agents.characteristic_agent import CharacteristicAgent
from src.infrastructure.agents.hierarchy_agent import HierarchyAgent
from src.infrastructure.agents.summary_agent import SummaryAgent
from src.infrastructure.agents.tag_generator_agent import TagGeneratorAgent
from src.infrastructure.llm.litellm_client import LiteLLMClient
from src.infrastructure.paper_fetchers.factory import PaperFetcherFactory
from src.infrastructure.repositories.in_memory_survey_repository import (
    InMemorySurveyRepository,
)


@lru_cache
def get_survey_repository() -> SurveyRepository:
    """サーベイリポジトリを取得する."""
    return InMemorySurveyRepository()


@lru_cache
def get_paper_fetcher_factory() -> PaperFetcherFactory:
    """論文取得ファクトリを取得する."""
    return PaperFetcherFactory()


def get_create_survey_use_case(conference: Conference) -> CreateSurveyUseCase:
    """サーベイ作成ユースケースを取得する.

    Args:
        conference: 対象の学会

    Returns:
        サーベイ作成ユースケース
    """
    factory = get_paper_fetcher_factory()
    fetcher = factory.get_fetcher(conference)
    repository = get_survey_repository()
    return CreateSurveyUseCase(
        paper_fetcher=fetcher,
        survey_repository=repository,
    )


def parse_conference_type(conference_type: str) -> ConferenceType:
    """文字列からConferenceTypeを解析する.

    Args:
        conference_type: 学会種別文字列

    Returns:
        ConferenceType

    Raises:
        ValueError: 無効な学会種別の場合
    """
    try:
        return ConferenceType(conference_type.upper())
    except ValueError:
        valid_types = [ct.value for ct in ConferenceType]
        raise ValueError(
            f"Invalid conference type: {conference_type}. Valid types are: {', '.join(valid_types)}"
        )


@lru_cache
def get_llm_client() -> LLMClient:
    """LLMクライアントを取得する."""
    return LiteLLMClient()


def get_process_survey_use_case() -> ProcessSurveyUseCase:
    """サーベイ処理ユースケースを取得する.

    Returns:
        サーベイ処理ユースケース
    """
    repository = get_survey_repository()
    llm_client = get_llm_client()

    return ProcessSurveyUseCase(
        survey_repository=repository,
        tag_generator=TagGeneratorAgent(llm_client),
        hierarchy_agent=HierarchyAgent(llm_client),
        summary_agent=SummaryAgent(llm_client),
        characteristic_agent=CharacteristicAgent(llm_client),
    )
