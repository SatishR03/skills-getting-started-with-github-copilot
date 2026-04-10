"""
Tests for the Mergington High School Activity Management API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities state before each test to avoid test pollution."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants_backup in original_participants.items():
        activities[name]["participants"] = participants_backup


client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange / Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Arrange / Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        # Arrange / Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self):
        # Arrange / Act
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]

        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignupForActivity:
    def test_signup_returns_200(self):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_adds_student_to_activity(self):
        # Arrange
        email = "teststudent@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants

    def test_signup_returns_confirmation_message(self):
        # Arrange
        email = "another@mergington.edu"
        activity = "Programming Class"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "message" in response.json()

    def test_signup_for_nonexistent_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400

    def test_signup_duplicate_returns_error_detail(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "detail" in response.json()


class TestUnregisterFromActivity:
    def test_unregister_returns_200(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_student_from_activity(self):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_unregister_returns_confirmation_message(self):
        # Arrange
        email = "daniel@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "message" in response.json()

    def test_unregister_from_nonexistent_activity_returns_404(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_signed_up_returns_404(self):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
