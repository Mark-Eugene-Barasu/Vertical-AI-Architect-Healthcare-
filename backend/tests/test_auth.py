"""Tests for authentication and tenant context."""

import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


class TestTenantContext:
    """Test tenant/org context extraction from JWT claims."""

    def test_valid_org_context(self, mock_claims):
        from auth.tenant import get_org_context
        # Simulate Depends injection by calling directly with claims
        with patch("auth.tenant.verify_token", return_value=mock_claims):
            ctx = get_org_context(mock_claims)
            assert ctx["org_id"] == "org-456"
            assert ctx["clinician_id"] == "clinician-123"
            assert ctx["role"] == "clinician"
            assert ctx["email"] == "doctor@test.com"

    def test_missing_org_id_raises(self):
        from auth.tenant import get_org_context
        claims = {"sub": "user-1", "email": "test@test.com"}
        with pytest.raises(HTTPException) as exc_info:
            get_org_context(claims)
        assert exc_info.value.status_code == 403

    def test_require_admin_allows_admin(self, mock_admin_claims):
        from auth.tenant import require_admin
        ctx = {
            "org_id": "org-456",
            "clinician_id": "admin-789",
            "role": "admin",
            "email": "admin@test.com",
        }
        result = require_admin(ctx)
        assert result["role"] == "admin"

    def test_require_admin_blocks_clinician(self):
        from auth.tenant import require_admin
        ctx = {
            "org_id": "org-456",
            "clinician_id": "user-1",
            "role": "clinician",
            "email": "user@test.com",
        }
        with pytest.raises(HTTPException) as exc_info:
            require_admin(ctx)
        assert exc_info.value.status_code == 403

    def test_require_super_admin_blocks_admin(self, mock_admin_claims):
        from auth.tenant import require_super_admin
        with pytest.raises(HTTPException) as exc_info:
            require_super_admin(mock_admin_claims)
        assert exc_info.value.status_code == 403
