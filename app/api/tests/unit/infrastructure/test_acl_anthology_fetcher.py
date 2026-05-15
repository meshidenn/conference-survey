"""AclAnthologyFetcherのテスト."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.models.value_objects import Conference, ConferenceType
from src.infrastructure.paper_fetchers.acl_anthology_fetcher import AclAnthologyFetcher


class TestAclAnthologyFetcher:
    """AclAnthologyFetcherのテスト."""

    def test_supports_acl_conferences(self):
        """ACL系学会をサポートする."""
        fetcher = AclAnthologyFetcher()

        assert fetcher.supports(Conference(type=ConferenceType.ACL, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.NAACL, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.EMNLP, year=2024))
        assert fetcher.supports(Conference(type=ConferenceType.EACL, year=2024))

    @pytest.mark.asyncio
    async def test_fetch_papers_from_xml(self):
        """XMLから論文を取得できる."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2024.acl">
          <volume id="long" type="proceedings">
            <meta><title>Proceedings</title></meta>
            <paper id="1">
              <title>Test Paper 1</title>
              <author><first>Author</first><last>A</last></author>
              <author><first>Author</first><last>B</last></author>
              <abstract>This is a test abstract.</abstract>
            </paper>
            <paper id="2">
              <title>Test Paper 2</title>
              <author><first>Author</first><last>C</last></author>
              <abstract>Another test abstract.</abstract>
            </paper>
          </volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 2
        assert papers[0].id.value == "2024.acl-long.1"
        assert papers[0].title == "Test Paper 1"
        assert papers[0].authors == ["Author A", "Author B"]
        assert papers[0].abstract == "This is a test abstract."

        # 正しいURLが呼ばれたことを確認
        mock_client.get.assert_called_once_with(
            "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.acl.xml"
        )

    @pytest.mark.asyncio
    async def test_fetch_handles_fixed_case_in_title(self):
        """タイトル内のfixed-caseタグを正しく処理する."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2024.acl">
          <volume id="long" type="proceedings">
            <paper id="1">
              <title>Pre-training of <fixed-case>BERT</fixed-case> Models</title>
              <abstract>An abstract about <fixed-case>BERT</fixed-case>.</abstract>
            </paper>
          </volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 1
        assert papers[0].title == "Pre-training of BERT Models"
        assert papers[0].abstract == "An abstract about BERT."

    @pytest.mark.asyncio
    async def test_fetch_naacl_papers(self):
        """NAACL論文を取得できる."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2024.naacl">
          <volume id="main" type="proceedings"></volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.NAACL, year=2024)
        await fetcher.fetch(conference)

        mock_client.get.assert_called_once_with(
            "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.naacl.xml"
        )

    @pytest.mark.asyncio
    async def test_fetch_empty_response(self):
        """論文がない場合は空リストを返す."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2024.acl">
          <volume id="main" type="proceedings"></volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert papers == []

    @pytest.mark.asyncio
    async def test_fetch_handles_missing_fields(self):
        """フィールドが欠けている場合もエラーにならない."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2024.acl">
          <volume id="long" type="proceedings">
            <paper id="1">
            </paper>
          </volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.ACL, year=2024)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 1
        assert papers[0].title == ""
        assert papers[0].authors == []
        assert papers[0].abstract == ""

    @pytest.mark.asyncio
    async def test_fetch_multiple_volumes(self):
        """複数のボリュームから論文を取得できる."""
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
        <collection id="2025.emnlp">
          <volume id="main" type="proceedings">
            <paper id="1">
              <title>Main Paper</title>
              <author><first>Main</first><last>Author</last></author>
              <abstract>Main abstract.</abstract>
            </paper>
          </volume>
          <volume id="demos" type="proceedings">
            <paper id="1">
              <title>Demo Paper</title>
              <author><first>Demo</first><last>Author</last></author>
              <abstract>Demo abstract.</abstract>
            </paper>
          </volume>
        </collection>"""

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = xml_content

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        fetcher = AclAnthologyFetcher(client=mock_client)
        conference = Conference(type=ConferenceType.EMNLP, year=2025)
        papers = await fetcher.fetch(conference)

        assert len(papers) == 2
        assert papers[0].id.value == "2025.emnlp-main.1"
        assert papers[0].title == "Main Paper"
        assert papers[1].id.value == "2025.emnlp-demos.1"
        assert papers[1].title == "Demo Paper"
