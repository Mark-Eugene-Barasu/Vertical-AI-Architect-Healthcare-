"""Tests for the health check endpoints."""

import sys
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a test client with mocked AWS services."""
    # Mock boto3 globally before importing the app
    mock_resource = MagicMock()
    mock_client = MagicMock()
    mock_session = MagicMock()

    with patch.dict(sys.modules, {}), \
         patch("boto3.resource", return_value=mock_resource), \
         patch("boto3.client", return_value=mock_client), \
         patch("boto3.Session", return_value=mock_session):
        # Need to reimport since mocks are now active
        from importlib import reload
        import main as main_mod
        reload(main_mod)
        from fastapi.testclient import TestClient
        return TestClient(main_mod.app)


class TestHealthEndpoints:
    def test_basic_health_check(self):
        """Test that /health returns expected shape regardless of deps."""
        with patch("boto3.resource"), patch("boto3.client"), patch("boto3.Session"):
            from fastapi.testclient import TestClient
            # Import with mocked boto3
            import main
            client = TestClient(main.app)
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "MediMind AI"
            assert "version" in data
