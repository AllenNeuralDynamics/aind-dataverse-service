"""Tests for handler module"""

import pytest
from httpx import AsyncClient

from aind_dataverse_service_server.handler import SessionHandler


class TestHandler:
    """Test SessionHandler"""

    @pytest.mark.asyncio
    async def test_get_quick_search_info(
        self, mock_async_client_get_pvalb: AsyncClient
    ):
        """Tests get_quick_search_info."""
        session_handler = SessionHandler(mock_async_client_get_pvalb)
        quick_search_info = await session_handler.get_quick_search_info(
            allele_name="Parvalbumin-IRES-Cre"
        )
        assert len(quick_search_info) == 1

    @pytest.mark.asyncio
    async def test_get_quick_search_info_nothing(
        self, mock_async_client_get_nothing: AsyncClient
    ):
        """Tests get_quick_search_info."""
        session_handler = SessionHandler(mock_async_client_get_nothing)
        quick_search_info = await session_handler.get_quick_search_info(
            allele_name="NOTHING"
        )
        assert len(quick_search_info) == 0


if __name__ == "__main__":
    pytest.main([__file__])
