"""
BDD tests for activity signup behavior.

Feature: Sign up for activities
  In order to register for extracurricular activities
  As a student
  I want to sign up for an activity I'm interested in
"""

import pytest
from tests.conftest import (
    VALID_ACTIVITY_NAME,
    VALID_PARTICIPANT_EMAIL,
    EXISTING_PARTICIPANT_EMAIL,
    INVALID_ACTIVITY_NAME,
    assert_success_response,
    assert_error_response,
)


def test_given_valid_activity_and_email_when_signing_up_then_success(client, fresh_activities):
    """
    Scenario: Successfully sign up for an activity
    
    GIVEN: A valid activity exists and the student's email is not yet registered
    WHEN: POST /activities/{activity_name}/signup?email=... is sent
    THEN: Response status is 200, message indicates success, and participant is added
    """
    # GIVEN: Chess Club exists and test_student@mergington.edu is not registered
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[VALID_ACTIVITY_NAME]["participants"]
    assert VALID_PARTICIPANT_EMAIL not in initial_participants
    
    # WHEN: POST request to signup
    response = client.post(
        f"/activities/{VALID_ACTIVITY_NAME}/signup",
        params={"email": VALID_PARTICIPANT_EMAIL}
    )
    
    # THEN: success response
    result = assert_success_response(response, 200)
    assert "message" in result
    assert VALID_PARTICIPANT_EMAIL in result["message"]
    assert VALID_ACTIVITY_NAME in result["message"]


def test_given_valid_signup_when_fetching_activities_then_participant_appears(client, fresh_activities):
    """
    Scenario: Newly signed up participant appears in activity list
    
    GIVEN: A successful signup was completed
    WHEN: GET /activities is requested
    THEN: New participant appears in the activity's participants list
    """
    # GIVEN: successfully signed up
    signup_response = client.post(
        f"/activities/{VALID_ACTIVITY_NAME}/signup",
        params={"email": VALID_PARTICIPANT_EMAIL}
    )
    assert signup_response.status_code == 200
    
    # WHEN: fetch activities
    response = client.get("/activities")
    
    # THEN: new participant is visible in the list
    assert response.status_code == 200
    activities_data = response.json()
    participants = activities_data[VALID_ACTIVITY_NAME]["participants"]
    assert VALID_PARTICIPANT_EMAIL in participants


@pytest.mark.parametrize("invalid_activity", [
    "Underwater Basket Weaving",
    "Nonexistent Activity",
    "Invalid-Activity-Name",
])
def test_given_activity_not_found_when_signing_up_then_returns_404(
    client, fresh_activities, invalid_activity
):
    """
    Scenario: Signup for nonexistent activity fails with 404
    
    GIVEN: Activity name does not exist
    WHEN: POST /activities/{invalid_name}/signup?email=... is sent
    THEN: Response status is 404 with "Activity not found" message
    """
    # GIVEN: invalid activity name
    
    # WHEN: POST request to signup for nonexistent activity
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": VALID_PARTICIPANT_EMAIL}
    )
    
    # THEN: 404 not found
    result = assert_error_response(response, 404, "Activity not found")


def test_given_student_already_registered_when_signing_up_again_then_returns_error(
    client, fresh_activities
):
    """
    Scenario: Cannot signup for activity twice
    
    GIVEN: Student "michael@mergington.edu" is already registered in Chess Club
    WHEN: POST /activities/Chess Club/signup?email=michael@mergington.edu is sent again
    THEN: Response status is 409 (or 400), returns "already registered" message
    """
    # GIVEN: michael@mergington.edu already in Chess Club participants
    initial_response = client.get("/activities")
    assert EXISTING_PARTICIPANT_EMAIL in initial_response.json()[VALID_ACTIVITY_NAME]["participants"]
    
    # WHEN: POST request to signup again with same email
    response = client.post(
        f"/activities/{VALID_ACTIVITY_NAME}/signup",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    
    # THEN: error response (409 Conflict or 400 Bad Request)
    assert response.status_code in [409, 400, 409]
    result = response.json()
    assert "detail" in result
    # The message should indicate the student is already registered
    assert ("already" in result["detail"].lower() or 
            "signed up" in result["detail"].lower() or
            "registered" in result["detail"].lower())


def test_given_valid_email_when_signing_up_for_different_activities_then_succeeds_for_each(
    client, fresh_activities
):
    """
    Scenario: Same student can sign up for multiple different activities
    
    GIVEN: A student email and multiple activities exist
    WHEN: POST signup is sent for different activities with same email
    THEN: Student successfully signs up for each activity
    """
    # GIVEN: test_student@mergington.edu can sign up for multiple activities
    test_email = "multi_activity_student@mergington.edu"
    activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
    
    # WHEN: POST request to signup for multiple activities
    for activity_name in activities_to_join:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # THEN: each signup succeeds
        assert response.status_code == 200, \
            f"Failed to signup for {activity_name}: {response.text}"
    
    # THEN: verify participant appears in all activities
    final_response = client.get("/activities")
    activities_data = final_response.json()
    
    for activity_name in activities_to_join:
        participants = activities_data[activity_name]["participants"]
        assert test_email in participants, \
            f"Expected {test_email} in {activity_name} participants"
