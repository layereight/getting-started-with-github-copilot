"""
BDD tests for participant removal behavior.

Feature: Remove participant from activity
  In order to unregister from an activity
  As a student
  I want to be able to remove myself from the participants list
"""

import pytest
from tests.conftest import (
    VALID_ACTIVITY_NAME,
    EXISTING_PARTICIPANT_EMAIL,
    INVALID_ACTIVITY_NAME,
    NONEXISTENT_PARTICIPANT_EMAIL,
    assert_error_response,
)


def test_given_participant_exists_when_removing_then_success(client, fresh_activities):
    """
    Scenario: Successfully remove registered participant
    
    GIVEN: A participant is registered in an activity
    WHEN: DELETE /activities/{activity}/participants?email=... is sent
    THEN: Response status is 200, message indicates success, participant removed
    """
    # GIVEN: michael@mergington.edu is in Chess Club participants
    initial_response = client.get("/activities")
    assert EXISTING_PARTICIPANT_EMAIL in initial_response.json()[VALID_ACTIVITY_NAME]["participants"]
    
    # WHEN: DELETE request to remove participant
    response = client.delete(
        f"/activities/{VALID_ACTIVITY_NAME}/participants",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    
    # THEN: success response
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert EXISTING_PARTICIPANT_EMAIL in result["message"]
    assert VALID_ACTIVITY_NAME in result["message"]


def test_given_participant_removed_when_fetching_activities_then_no_longer_visible(
    client, fresh_activities
):
    """
    Scenario: Removed participant disappears from activity list
    
    GIVEN: A participant was successfully removed from an activity
    WHEN: GET /activities is requested
    THEN: Participant no longer appears in the activity's participants list
    """
    # GIVEN: michael@mergington.edu removed from Chess Club
    delete_response = client.delete(
        f"/activities/{VALID_ACTIVITY_NAME}/participants",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    assert delete_response.status_code == 200
    
    # WHEN: fetch activities
    response = client.get("/activities")
    
    # THEN: participant not in list anymore
    assert response.status_code == 200
    activities_data = response.json()
    participants = activities_data[VALID_ACTIVITY_NAME]["participants"]
    assert EXISTING_PARTICIPANT_EMAIL not in participants


@pytest.mark.parametrize("invalid_activity", [
    "Underwater Basket Weaving",
    "Nonexistent Activity",
    "Invalid-Activity-Name",
])
def test_given_activity_not_found_when_removing_then_returns_404(
    client, fresh_activities, invalid_activity
):
    """
    Scenario: Remove from nonexistent activity fails with 404
    
    GIVEN: Activity name does not exist
    WHEN: DELETE /activities/{invalid_name}/participants?email=... is sent
    THEN: Response status is 404 with "Activity not found" message
    """
    # GIVEN: invalid activity name
    
    # WHEN: DELETE request for nonexistent activity
    response = client.delete(
        f"/activities/{invalid_activity}/participants",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    
    # THEN: 404 not found
    result = assert_error_response(response, 404, "Activity not found")


def test_given_participant_not_in_activity_when_removing_then_returns_404(
    client, fresh_activities
):
    """
    Scenario: Remove nonexistent participant fails with 404
    
    GIVEN: Email is not registered in the activity
    WHEN: DELETE /activities/{activity}/participants?email=unregistered@... is sent
    THEN: Response status is 404 with "Participant not found" message
    """
    # GIVEN: NONEXISTENT_PARTICIPANT_EMAIL is not in Chess Club
    initial_response = client.get("/activities")
    assert NONEXISTENT_PARTICIPANT_EMAIL not in initial_response.json()[VALID_ACTIVITY_NAME]["participants"]
    
    # WHEN: DELETE request for participant not in activity
    response = client.delete(
        f"/activities/{VALID_ACTIVITY_NAME}/participants",
        params={"email": NONEXISTENT_PARTICIPANT_EMAIL}
    )
    
    # THEN: 404 not found
    result = assert_error_response(response, 404, "Participant not found")


def test_given_multiple_participants_when_removing_one_then_others_remain(client, fresh_activities):
    """
    Scenario: Removing one participant doesn't affect others
    
    GIVEN: An activity has multiple participants
    WHEN: DELETE request removes one participant
    THEN: Other participants remain in the list
    """
    # GIVEN: Chess Club has michael@mergington.edu and daniel@mergington.edu
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[VALID_ACTIVITY_NAME]["participants"]
    assert "michael@mergington.edu" in initial_participants
    assert "daniel@mergington.edu" in initial_participants
    assert len(initial_participants) >= 2
    
    # WHEN: remove michael@mergington.edu
    response = client.delete(
        f"/activities/{VALID_ACTIVITY_NAME}/participants",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    
    # THEN: daniel@mergington.edu still in list
    final_response = client.get("/activities")
    final_participants = final_response.json()[VALID_ACTIVITY_NAME]["participants"]
    assert "daniel@mergington.edu" in final_participants
    assert "michael@mergington.edu" not in final_participants
    assert len(final_participants) == len(initial_participants) - 1


def test_given_participant_removed_when_signup_again_then_succeeds(
    client, fresh_activities
):
    """
    Scenario: Previously removed participant can sign up again
    
    GIVEN: A participant was removed from an activity
    WHEN: Same participant signs up again
    THEN: Signup succeeds and participant reappears
    """
    # GIVEN: michael@mergington.edu removed from Chess Club
    delete_response = client.delete(
        f"/activities/{VALID_ACTIVITY_NAME}/participants",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    assert delete_response.status_code == 200
    
    verify_response = client.get("/activities")
    assert EXISTING_PARTICIPANT_EMAIL not in verify_response.json()[VALID_ACTIVITY_NAME]["participants"]
    
    # WHEN: same participant signs up again
    signup_response = client.post(
        f"/activities/{VALID_ACTIVITY_NAME}/signup",
        params={"email": EXISTING_PARTICIPANT_EMAIL}
    )
    
    # THEN: signup succeeds and participant reappears
    assert signup_response.status_code == 200
    
    final_response = client.get("/activities")
    participants = final_response.json()[VALID_ACTIVITY_NAME]["participants"]
    assert EXISTING_PARTICIPANT_EMAIL in participants
