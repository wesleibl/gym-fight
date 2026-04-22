import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.attendence import Attendence
from app.models.schedule import DayOfWeek, Schedule, ScheduleType
from app.models.user import Gender, User


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# --- Helpers ---

def make_user(
    session: Session,
    email: str,
    is_instructor: bool = False,
    gender: Gender = Gender.MALE,
    birth_date: dt.date = dt.date(1990, 1, 1),
    is_athletic: bool = False,
) -> User:
    user = User(
        name="Test User",
        email=email,
        gender=gender,
        birth_date=birth_date,
        phone="11999999999",
        hashed_password=get_password_hash("password123"),
        is_instructor=is_instructor,
        is_athletic=is_athletic,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def make_schedule(
    session: Session,
    day: DayOfWeek = DayOfWeek.MONDAY,
    time: dt.time = dt.time(10, 0),
    type: ScheduleType = ScheduleType.COMMON,
) -> Schedule:
    schedule = Schedule(day_of_week=day, time=time, type=type)
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


def make_attendance(session: Session, user_id: int, schedule_id: int) -> Attendence:
    attendance = Attendence(user_id=user_id, schedule_id=schedule_id)
    session.add(attendance)
    session.commit()
    session.refresh(attendance)
    return attendance


def token_for(user: User) -> str:
    return create_access_token({"sub": user.email, "is_instructor": user.is_instructor})


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --- Fixtures ---

@pytest.fixture(name="regular_user")
def regular_user_fixture(session):
    return make_user(session, "user@test.com")


@pytest.fixture(name="other_user")
def other_user_fixture(session):
    return make_user(session, "other@test.com")


@pytest.fixture(name="instructor")
def instructor_fixture(session):
    return make_user(session, "instructor@test.com", is_instructor=True)


@pytest.fixture(name="user_token")
def user_token_fixture(regular_user):
    return token_for(regular_user)


@pytest.fixture(name="other_token")
def other_token_fixture(other_user):
    return token_for(other_user)


@pytest.fixture(name="instructor_token")
def instructor_token_fixture(instructor):
    return token_for(instructor)
