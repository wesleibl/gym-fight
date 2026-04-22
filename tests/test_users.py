from tests.conftest import auth, make_attendance, make_schedule, make_user


# --- POST /users/ ---

def test_create_user(client):
    payload = {
        "name": "Novo Aluno",
        "email": "novo@test.com",
        "gender": "male",
        "birth_date": "1995-05-10",
        "phone": "11988887777",
        "password": "senha123",
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "novo@test.com"
    assert "hashed_password" not in data


def test_create_user_duplicate_email(client, regular_user):
    payload = {
        "name": "Duplicado",
        "email": "user@test.com",
        "gender": "male",
        "birth_date": "1995-05-10",
        "phone": "11988887777",
        "password": "senha123",
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 400


# --- GET /users/ ---

def test_list_users_as_instructor(client, instructor, instructor_token):
    response = client.get("/users/", headers=auth(instructor_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_as_regular_user(client, regular_user, user_token):
    response = client.get("/users/", headers=auth(user_token))
    assert response.status_code == 403


def test_list_users_unauthenticated(client):
    response = client.get("/users/")
    assert response.status_code == 401


# --- GET /users/{id} ---

def test_get_user_as_instructor(client, regular_user, instructor, instructor_token):
    response = client.get(f"/users/{regular_user.id}", headers=auth(instructor_token))
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email


def test_get_own_user(client, regular_user, user_token):
    response = client.get(f"/users/{regular_user.id}", headers=auth(user_token))
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email


def test_get_other_user_as_regular(client, regular_user, other_user, user_token):
    response = client.get(f"/users/{other_user.id}", headers=auth(user_token))
    # retorna os dados do próprio usuário (ignora o id)
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email


# --- PUT /users/{id} ---

def test_update_own_user(client, regular_user, user_token):
    response = client.put(
        f"/users/{regular_user.id}",
        json={"name": "Nome Atualizado"},
        headers=auth(user_token),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nome Atualizado"


def test_update_user_as_instructor(client, regular_user, instructor, instructor_token):
    response = client.put(
        f"/users/{regular_user.id}",
        json={"phone": "11000000000"},
        headers=auth(instructor_token),
    )
    assert response.status_code == 200
    assert response.json()["phone"] == "11000000000"


def test_update_user_not_found(client, instructor, instructor_token):
    response = client.put(
        "/users/9999",
        json={"name": "X"},
        headers=auth(instructor_token),
    )
    assert response.status_code == 404


# --- DELETE /users/{id} ---

def test_delete_user_as_instructor(client, regular_user, instructor, instructor_token):
    response = client.delete(f"/users/{regular_user.id}", headers=auth(instructor_token))
    assert response.status_code == 204


def test_delete_user_as_regular(client, regular_user, user_token):
    response = client.delete(f"/users/{regular_user.id}", headers=auth(user_token))
    assert response.status_code == 403


def test_delete_user_not_found(client, instructor, instructor_token):
    response = client.delete("/users/9999", headers=auth(instructor_token))
    assert response.status_code == 404


# --- PATCH /users/{id}/level ---

def test_update_level_as_instructor(client, regular_user, instructor, instructor_token):
    response = client.patch(
        f"/users/{regular_user.id}/level",
        json={"level": "advanced"},
        headers=auth(instructor_token),
    )
    assert response.status_code == 200
    assert response.json()["level"] == "advanced"


def test_update_level_as_regular(client, regular_user, user_token):
    response = client.patch(
        f"/users/{regular_user.id}/level",
        json={"level": "advanced"},
        headers=auth(user_token),
    )
    assert response.status_code == 403


# --- PATCH /users/{id}/instructor ---

def test_change_instructor_status(client, regular_user, instructor, instructor_token):
    response = client.patch(
        f"/users/{regular_user.id}/instructor",
        json={"is_instructor": True},
        headers=auth(instructor_token),
    )
    assert response.status_code == 200
    assert response.json()["is_instructor"] is True


def test_change_instructor_status_as_regular(client, regular_user, user_token):
    response = client.patch(
        f"/users/{regular_user.id}/instructor",
        json={"is_instructor": True},
        headers=auth(user_token),
    )
    assert response.status_code == 403


# --- PATCH /users/{id}/status ---

def test_update_status_as_instructor(client, regular_user, instructor, instructor_token):
    response = client.patch(
        f"/users/{regular_user.id}/status",
        json={"status": "blocked"},
        headers=auth(instructor_token),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"


def test_update_status_as_regular(client, regular_user, user_token):
    response = client.patch(
        f"/users/{regular_user.id}/status",
        json={"status": "blocked"},
        headers=auth(user_token),
    )
    assert response.status_code == 403


# --- GET /users/{id}/attendances ---

def test_get_own_attendances(client, session, regular_user, user_token):
    schedule = make_schedule(session)
    make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)

    response = client.get(f"/users/{regular_user.id}/attendances", headers=auth(user_token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_attendances_of_other_user_as_regular(client, regular_user, other_user, user_token):
    response = client.get(f"/users/{other_user.id}/attendances", headers=auth(user_token))
    assert response.status_code == 403


def test_get_attendances_as_instructor(client, session, regular_user, instructor, instructor_token):
    schedule = make_schedule(session)
    make_attendance(session, user_id=regular_user.id, schedule_id=schedule.id)

    response = client.get(f"/users/{regular_user.id}/attendances", headers=auth(instructor_token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_attendances_user_not_found(client, instructor, instructor_token):
    response = client.get("/users/9999/attendances", headers=auth(instructor_token))
    assert response.status_code == 404
