from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from enum import Enum
import datetime as dt

class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class ScheduleType(str, Enum):
    COMMON = "common"
    KIDS = "kids"
    FEMALE = "female"
    ATHLETE = "athlete"

class ScheduleBase(SQLModel):
    time: dt.time
    day_of_week: DayOfWeek
    type: ScheduleType

class Schedule(ScheduleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleDelete(SQLModel):
    id: int

class ScheduleResponse(ScheduleBase):
    id: int | None
    created_at: dt.datetime

    model_config = {"from_attributes": True}