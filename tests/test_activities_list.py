"""
BDD tests for activities listing behavior.

Feature: Get all activities
  In order to see what's available
  As a student
  I want to retrieve all activities with their details and participant lists
"""

import pytest


def test_given_activities_exist_when_fetching_then_returns_all_activities(client, fresh_activities):
    """
    Scenario: Fetch all activities successfully
    
    GIVEN: The app has activities in memory
    WHEN: A GET request is sent to /activities
    THEN: Response status is 200 and contains all activity names
    """
    # GIVEN: activities exist (provided by fresh_activities fixture)
    
    # WHEN: GET request to /activities
    response = client.get("/activities")
    
    # THEN: success response with all activities
    assert response.status_code == 200
    activities_data = response.json()
    
    # Verify all expected activities are present
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class",
        "Basketball Team", "Soccer Club", "Art Club",
        "Drama Club", "Math Club", "Science Olympiad"
    ]
    for activity_name in expected_activities:
        assert activity_name in activities_data, f"Missing activity: {activity_name}"


def test_given_activity_with_participants_when_fetching_then_includes_participant_list(
    client, fresh_activities
):
    """
    Scenario: Activity response includes participants list
    
    GIVEN: An activity exists with registered participants
    WHEN: A GET request is sent to /activities
    THEN: Response includes participants list for that activity
    """
    # GIVEN: Chess Club exists with participants michael@mergington.edu and daniel@mergington.edu
    
    # WHEN: GET request to /activities
    response = client.get("/activities")
    
    # THEN: Chess Club includes the participants
    assert response.status_code == 200
    activities_data = response.json()
    chess_club = activities_data["Chess Club"]
    
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


@pytest.mark.parametrize("activity_name,expected_key", [
    ("Chess Club", "description"),
    ("Programming Class", "schedule"),
    ("Gym Class", "max_participants"),
])
def test_given_any_activity_when_fetching_then_includes_required_fields(
    client, fresh_activities, activity_name, expected_key
):
    """
    Scenario: All activities have required structure
    
    GIVEN: Activities exist
    WHEN: A GET request is sent to /activities
    THEN: Each activity has required fields (description, schedule, max_participants, participants)
    """
    # GIVEN: activities exist
    
    # WHEN: GET request to /activities
    response = client.get("/activities")
    
    # THEN: specified activity has all required fields
    assert response.status_code == 200
    activities_data = response.json()
    activity = activities_data[activity_name]
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    for field in required_fields:
        assert field in activity, f"{activity_name} missing field: {field}"
        assert activity[field] is not None


def test_given_any_activity_when_fetching_then_participants_is_list(client, fresh_activities):
    """
    Scenario: Participants field is always a list
    
    GIVEN: Activities exist
    WHEN: A GET request is sent to /activities
    THEN: participants field for each activity is a list
    """
    # GIVEN: activities exist
    
    # WHEN: GET request to /activities
    response = client.get("/activities")
    
    # THEN: all participants fields are lists
    assert response.status_code == 200
    activities_data = response.json()
    
    for activity_name, activity_data in activities_data.items():
        assert isinstance(activity_data["participants"], list), \
            f"{activity_name} participants is not a list: {type(activity_data['participants'])}"
        # Verify all participants are strings (email addresses)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str), \
                f"{activity_name} contains non-string participant: {participant}"
