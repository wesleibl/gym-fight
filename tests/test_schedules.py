import datetime as dt

from tests.conftest import auth, make_schedule, make_user
from app.models.schedule import DayOfWeek, ScheduleType
from app.models.user import Gender


SCHEDULE_PAYLOAD = {
    "time": "10:00:00",
    "day_of_week": "monday",
    "type": "common",
}


# --- POST /schedules/ ---

def test_create_schedule_as_instructor(client, instructor, instructor_token):
    response = client.post("/schedules/", json=SCHEDULE_PAYLOAD, headers=auth(instructor_token))
    assert response.status_code == 200
    data = response.json()
    assert data["day_of_week"] == "monday"
    assert data["type"] == "common"


def test_create_schedule_as_regular_user(client, regular_user, user_token):
    response = client.post("/schedules/", json=SCHEDULE_PAYLOAD, headers=auth(user_token))
    assert response.status_code == 403


def test_create_duplicate_schedule(client, session, instructor, instructor_token):
    make_schedule(session)
    response = client.post("/schedules/", json=SCHEDULE_PAYLOAD, headers=auth(instructor_token))
    assert response.status_code == 400


# --- GET /schedules/ ---

def test_list_schedules(client, session, regular_user, user_token):
    make_schedule(session)
    make_schedule(session, day=DayOfWeek.TUESDAY, time=dt.time(18, 0))

    response = client.get("/schedules/", headers=auth(user_token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_schedules_unauthenticated(client):
    response = client.get("/schedules/")
    assert response.status_code == 401


# --- GET /schedules/available ---

def test_list_available_schedules_common_only(client, session, regular_user, user_token):
    make_schedule(session, type=ScheduleType.COMMON)
    make_schedule(session, day=DayOfWeek.TUESDAY, time=dt.time(18, 0), type=ScheduleType.ATHLETE)

    response = client.get("/schedules/available", headers=auth(user_token))
    assert response.status_code == 200
    types = [s["type"] for s in response.json()]
    assert "common" in types
    assert "athlete" not in types


def test_list_available_schedules_female(client, session, engine):
    from app.models.user import User, Status, Level
    from app.core.security import get_password_hash, create_access_token
    from sqlmodel import Session

    with Session(engine) as s:
        female = User(
            name="Female",
            email="female@test.com",
            gender=Gender.FEMALE,
            birth_date=dt.date(1995, 1, 1),
            phone="11999999999",
            hashed_password=get_password_hash("password123"),
        )
        s.add(female)
        s.commit()
        s.refresh(female)
        female_token = create_access_token({"sub": female.email, "is_instructor": False})

    make_schedule(session, type=ScheduleType.COMMON)
    make_schedule(session, day=DayOfWeek.TUESDAY, time=dt.time(18, 0), type=ScheduleType.FEMALE)

    response = client.get("/schedules/available", headers=auth(female_token))
    assert response.status_code == 200
    types = [s["type"] for s in response.json()]
    assert "female" in types


# --- DELETE /schedules/{id} ---

def test_delete_schedule_as_instructor(client, session, instructor, instructor_token):
    schedule = make_schedule(session)
    response = client.delete(f"/schedules/{schedule.id}", headers=auth(instructor_token))
    assert response.status_code == 204


def test_delete_schedule_as_regular(client, session, regular_user, user_token):
    schedule = make_schedule(session)
    response = client.delete(f"/schedules/{schedule.id}", headers=auth(user_token))
    assert response.status_code == 403


def test_delete_schedule_not_found(client, instructor, instructor_token):
    response = client.delete("/schedules/9999", headers=auth(instructor_token))
    assert response.status_code == 404
