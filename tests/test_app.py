import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import app as main_app
from fastapi.testclient import TestClient
import pytest

client = TestClient(main_app.app)
original_activities = deepcopy(main_app.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities store before each test."""
    main_app.activities.clear()
    main_app.activities.update(deepcopy(original_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    body = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in body
    assert isinstance(body["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_student():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"
    url = f"/activities/{activity}/signup"
    assert email not in main_app.activities[activity]["participants"]

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in main_app.activities[activity]["participants"]


def test_signup_for_existing_student_returns_400():
    # Arrange
    activity = "Chess Club"
    email = main_app.activities[activity]["participants"][0]
    url = f"/activities/{activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_student():
    # Arrange
    activity = "Basketball"
    email = "newplayer@example.com"
    if email not in main_app.activities[activity]["participants"]:
        main_app.activities[activity]["participants"].append(email)
    url = f"/activities/{activity}/unregister"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in main_app.activities[activity]["participants"]


def test_unregister_non_signed_student_returns_400():
    # Arrange
    activity = "Basketball"
    email = "notregistered@example.com"
    url = f"/activities/{activity}/unregister"
    assert email not in main_app.activities[activity]["participants"]

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
