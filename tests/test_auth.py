from tests.conftest import make_user


def test_login_success(client, regular_user):
    response = client.post("/auth/login", json={"email": "user@test.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, regular_user):
    response = client.post("/auth/login", json={"email": "user@test.com", "password": "errada"})
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post("/auth/login", json={"email": "ninguem@test.com", "password": "password123"})
    assert response.status_code == 401


def test_login_instructor_token_contains_flag(client, instructor):
    response = client.post("/auth/login", json={"email": "instructor@test.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
