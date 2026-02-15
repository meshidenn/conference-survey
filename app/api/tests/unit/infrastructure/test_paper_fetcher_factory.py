"""PaperFetcherFactoryのテスト."""


from src.domain.models.value_objects import Conference, ConferenceType
from src.infrastructure.paper_fetchers.acl_anthology_fetcher import AclAnthologyFetcher
from src.infrastructure.paper_fetchers.factory import PaperFetcherFactory


class TestPaperFetcherFactory:
    """PaperFetcherFactoryのテスト."""

    def test_get_fetcher_for_acl(self):
        """ACL学会用のFetcherを取得できる."""
        factory = PaperFetcherFactory()
        conference = Conference(type=ConferenceType.ACL, year=2024)
        fetcher = factory.get_fetcher(conference)
        assert isinstance(fetcher, AclAnthologyFetcher)

    def test_get_fetcher_for_naacl(self):
        """NAACL学会用のFetcherを取得できる."""
        factory = PaperFetcherFactory()
        conference = Conference(type=ConferenceType.NAACL, year=2024)
        fetcher = factory.get_fetcher(conference)
        assert isinstance(fetcher, AclAnthologyFetcher)

    def test_get_fetcher_for_emnlp(self):
        """EMNLP学会用のFetcherを取得できる."""
        factory = PaperFetcherFactory()
        conference = Conference(type=ConferenceType.EMNLP, year=2024)
        fetcher = factory.get_fetcher(conference)
        assert isinstance(fetcher, AclAnthologyFetcher)

    def test_get_fetcher_for_eacl(self):
        """EACL学会用のFetcherを取得できる."""
        factory = PaperFetcherFactory()
        conference = Conference(type=ConferenceType.EACL, year=2024)
        fetcher = factory.get_fetcher(conference)
        assert isinstance(fetcher, AclAnthologyFetcher)
