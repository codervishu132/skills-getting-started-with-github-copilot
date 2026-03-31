def test_get_activities_returns_expected_structure(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data
    for details in data.values():
        assert expected_keys.issubset(details.keys())


def test_signup_new_student_returns_success_and_updates_participants(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_existing_student_returns_success_and_updates_participants(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_registered_student_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_signup_when_activity_is_at_capacity_is_rejected(client):
    # Arrange
    activity_name = "Chess Club"
    email = "capacity.test@mergington.edu"

    # Fill participants up to capacity first.
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    max_participants = activity["max_participants"]
    current_participants = len(activity["participants"])

    for idx in range(max_participants - current_participants):
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"filler{idx}@mergington.edu"},
        )

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_signup_with_invalid_email_is_rejected(client):
    # Arrange
    activity_name = "Chess Club"
    invalid_email = "not-an-email"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": invalid_email},
    )

    # Assert
    assert response.status_code == 422
