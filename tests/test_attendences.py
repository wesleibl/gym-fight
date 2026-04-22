from tests.conftest import auth, make_attendance, make_schedule


# --- POST /attendences/ ---

def test_create_attendence(client, session, regular_user, user_token):
    schedule = make_schedule(session)
    response = client.post(
        "/attendences/",
        json={"schedule_id": schedule.id},
        headers=auth(user_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["schedule_id"] == schedule.id
    assert data["user_id"] == regular_user.id


def test_create_attendence_invalid_schedule(client, regular_user, user_token):
    response = client.post(
        "/attendences/",
        json={"schedule_id": 9999},
        headers=auth(user_token),
    )
    assert response.status_code == 400


def test_create_attendence_unauthenticated(client, session):
    schedule = make_schedule(session)
    response = client.post("/attendences/", json={"schedule_id": schedule.id})
    assert response.status_code == 401


# --- GET /attendences/ ---

def test_list_attendences_as_instructor_sees_all(client, session, regular_user, other_user, instructor, instructor_token):
    schedule = make_schedule(session)
    make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)
    make_attendance(session, user_id=other_user.id, schedule_id=schedule.id)

    response = client.get("/attendences/", headers=auth(instructor_token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_attendences_as_user_sees_own_only(client, session, regular_user, other_user, user_token):
    schedule = make_schedule(session)
    make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)
    make_attendance(session, user_id=other_user.id, schedule_id=schedule.id)

    response = client.get("/attendences/", headers=auth(user_token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == regular_user.id


def test_list_attendences_unauthenticated(client):
    response = client.get("/attendences/")
    assert response.status_code == 401


# --- DELETE /attendences/{id} ---

def test_delete_own_attendence(client, session, regular_user, user_token):
    schedule = make_schedule(session)
    attendance = make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)

    response = client.delete(f"/attendences/{attendance.id}", headers=auth(user_token))
    assert response.status_code == 204


def test_delete_attendence_as_instructor(client, session, regular_user, instructor, instructor_token):
    schedule = make_schedule(session)
    attendance = make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)

    response = client.delete(f"/attendences/{attendance.id}", headers=auth(instructor_token))
    assert response.status_code == 204


def test_delete_other_users_attendence_as_regular(client, session, regular_user, other_user, user_token):
    schedule = make_schedule(session)
    attendance = make_attendance(session, user_id=other_user.id, schedule_id=schedule.id)

    response = client.delete(f"/attendences/{attendance.id}", headers=auth(user_token))
    assert response.status_code == 403


def test_delete_attendence_not_found(client, regular_user, user_token):
    response = client.delete("/attendences/9999", headers=auth(user_token))
    assert response.status_code == 404
