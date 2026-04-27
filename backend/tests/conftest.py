"""Shared test fixtures and mocks for the MediMind test suite."""

import os
import pytest
from unittest.mock import MagicMock, patch

# Set test environment variables before any imports
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("COGNITO_USER_POOL_ID", "us-east-1_TestPool")
os.environ.setdefault("COGNITO_CLIENT_ID", "test-client-id")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("SNS_ALERT_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789:test-topic")
os.environ.setdefault("HEALTHLAKE_ENDPOINT", "https://healthlake.test.endpoint")
os.environ.setdefault("TRANSCRIBE_BUCKET", "test-transcribe-bucket")


@pytest.fixture
def mock_claims():
    """Standard JWT claims for a test clinician."""
    return {
        "sub": "clinician-123",
        "email": "doctor@test.com",
        "custom:org_id": "org-456",
        "custom:role": "clinician",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TestPool",
        "aud": "test-client-id",
        "token_use": "id",
        "exp": 9999999999,
    }


@pytest.fixture
def mock_admin_claims():
    """JWT claims for an admin user."""
    return {
        "sub": "admin-789",
        "email": "admin@test.com",
        "custom:org_id": "org-456",
        "custom:role": "admin",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_TestPool",
        "aud": "test-client-id",
        "token_use": "id",
        "exp": 9999999999,
    }


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table."""
    table = MagicMock()
    table.put_item = MagicMock(return_value={})
    table.get_item = MagicMock(return_value={})
    table.query = MagicMock(return_value={"Items": []})
    table.update_item = MagicMock(return_value={})
    table.scan = MagicMock(return_value={"Items": []})
    return table
