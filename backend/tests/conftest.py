"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_state():
    """Sample onboarding state for testing."""
    return {
        "new_hire_id": "test-001",
        "new_hire_name": "Test User",
        "role": "Engineer",
        "start_date": "2026-02-01",
    }
