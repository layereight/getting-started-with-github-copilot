"""
Fixtures and configuration for BDD-style FastAPI tests.

This module provides shared test infrastructure including:
- TestClient connected to the FastAPI app
- Fresh activities data per test (deep copy for isolation)
- Helper assertions for common response patterns
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing TestClient connected to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Fixture providing fresh, isolated activities data for each test.
    
    Uses deep copy to ensure modifications in one test don't affect others.
    Each test gets a clean state with the original participants list.
    """
    # Deep copy the original activities
    original_activities = copy.deepcopy(activities)
    
    # Replace the app's activities with the fresh copy
    monkeypatch.setitem(app.__dict__, 'activities', original_activities)
    
    # Also patch the module-level activities
    monkeypatch.setattr('src.app.activities', original_activities, raising=False)
    
    return original_activities


# Test data constants for common scenarios
VALID_ACTIVITY_NAME = "Chess Club"
VALID_PARTICIPANT_EMAIL = "test_student@mergington.edu"
EXISTING_PARTICIPANT_EMAIL = "michael@mergington.edu"  # Already in Chess Club
INVALID_ACTIVITY_NAME = "Underwater Basket Weaving"
NONEXISTENT_PARTICIPANT_EMAIL = "nobody@mergington.edu"


def assert_success_response(response, expected_status=200):
    """Helper to assert successful API response."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    return response.json()


def assert_error_response(response, expected_status, expected_detail_substring=None):
    """Helper to assert error API response."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    result = response.json()
    if expected_detail_substring:
        assert expected_detail_substring.lower() in result.get("detail", "").lower(), \
            f"Expected '{expected_detail_substring}' in error detail: {result.get('detail')}"
    return result
