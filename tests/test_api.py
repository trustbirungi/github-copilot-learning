"""
Pytest suite for Mergington High School Activities API

Tests follow the Arrange-Act-Assert pattern and make use of a fixture that
resets the in-memory `activities` dictionary before each test so they are
isolated from one another.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the shared activities dictionary to its original state.

    Because the application stores everything in a global `activities` dict,
    tests can interfere with each other unless we reset it.  This fixture runs
    automatically for every test (via ``autouse=True``) and replaces the dict
    contents with the static data defined in `src/app.py`.
    """
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": [
                "michael@mergington.edu",
                "daniel@mergington.edu",
            ],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": [
                "emma@mergington.edu",
                "sophia@mergington.edu",
            ],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": [
                "john@mergington.edu",
                "olivia@mergington.edu",
            ],
        },
        "Basketball Team": {
            "description": "Compete in competitive basketball leagues and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"],
        },
        "Tennis Club": {
            "description": "Improve tennis skills and participate in matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": [
                "lucas@mergington.edu",
                "nina@mergington.edu",
            ],
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["bella@mergington.edu"],
        },
        "Art Studio": {
            "description": "Explore painting, sculpture, and digital art",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": [
                "mason@mergington.edu",
                "isabella@mergington.edu",
            ],
        },
        "Debate Team": {
            "description": "Develop argumentation skills and compete in debate competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"],
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM topics",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 22,
            "participants": [
                "victoria@mergington.edu",
                "jacob@mergington.edu",
            ],
        },
    }

    activities.clear()
    activities.update(original_activities)
    yield
    # nothing special after test


@pytest.fixture

def client():
    """Return a TestClient configured with the FastAPI app."""

    return TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities GET endpoint."""

    def test_get_activities(self, client):
        # Arrange: nothing special beyond a clean activities dict
        expected_keys = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_keys
        assert "description" in data["Chess Club"]
        assert "participants" in data["Chess Club"]


class TestSignupEndpoint:
    """Tests exercising the signup-for-activity POST interface."""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests exercising the unregister (delete) interface."""

    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # pre‑existing participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Successfully unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nobody@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent"
        email = "somebody@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
