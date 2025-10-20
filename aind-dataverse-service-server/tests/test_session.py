"""Tests session module"""

import pytest

from aind_dataverse_service_server.session import get_session


class TestSession:
    """Test methods in Session Class"""

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Tests get_session method"""
        session = await get_session().__anext__()
        base_url = str(session.base_url)
        assert "http://example.com/" == base_url


if __name__ == "__main__":
    pytest.main([__file__])
