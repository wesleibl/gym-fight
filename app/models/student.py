from pydantic import EmailStr
from enum import Enum
from sqlmodel import Field, SQLModel
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

class Role(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"

class StudentBase(SQLModel):
    name: str
    email: EmailStr
    gender: Gender
    birth_date: dt.date
    phone: str


class Student(StudentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    role: Role = Role.STUDENT
    level: Level = Level.BEGINNER
    is_athletic: bool = False
    status: Status = Status.ACTIVE
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class StudentCreate(StudentBase):
    password: str

class StudentUpdate(SQLModel):
    name: str
    email: EmailStr
    phone: str

class StudentResponse(StudentBase):
    id: int | None
    role: Role
    level: Level
    is_athletic: bool
    status: Status
    created_at: dt.datetime

    model_config = {"from_attributes": True}