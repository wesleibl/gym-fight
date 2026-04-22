from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from enum import Enum
import datetime as dt

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Status(str, Enum):
    ACTIVE = "active"
    PASTDUE = "pastdue"
    BLOCKED = "blocked"

class UserBase(SQLModel):
    name: str
    email: EmailStr
    gender: Gender
    birth_date: dt.date
    phone: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    level: Level = Level.BEGINNER
    is_athletic: bool = False
    is_instructor: bool = False
    status: Status = Status.ACTIVE
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

class UserResponse(UserBase):
    id: int | None
    is_instructor: bool
    level: Level
    is_athletic: bool
    status: Status
    created_at: dt.datetime

    model_config = {"from_attributes": True}

class LevelUpdate(SQLModel):
    level: Level

class InstructorUpdate(SQLModel):
    is_instructor: bool

class StatusUpdate(SQLModel):
    status: Status