from pydantic import BaseModel, EmailStr, ConfigDict
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

class Role(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    password : str
    gender: Gender
    birth_date: dt.date
    phone: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jones",
                    "email": "jones@email.com",
                    "password" : "strongPass",
                    "gender": "male",
                    "birth_date": "1998-11-02",
                    "phone": "5551991234567"
                }
            ]
        }
    }

class StudentUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jones",
                    "email": "jones@email.com",
                    "phone": "5551991234567"
                }
            ]
        }
    }

class StudentResponse(BaseModel):
    id: int
    role: Role
    name: str
    email: EmailStr
    gender: Gender
    birth_date: dt.date
    phone: str
    level: Level
    is_athletic: bool
    status: Status
    created_at: dt.datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                    {
                        "id": 1,
                        "role": "student",
                        "name": "Jones",
                        "email": "jones@email.com",
                        "gender": "male",
                        "birth_date": "1998-11-02",
                        "phone": "5551991234567",
                        "is_athletic": False,
                        "level": "intermediate",
                        "status": "active",
                        "created_at": "2025-06-12"
                    }
            ]
        }
    )