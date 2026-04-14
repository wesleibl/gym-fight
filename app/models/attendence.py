from sqlmodel import Field, SQLModel
import datetime as dt

class AttendenceBase(SQLModel):
    schedule_id: int = Field(foreign_key="schedule.id")

class Attendence(AttendenceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class AttendenceCreate(AttendenceBase):
    pass

class AttendenceResponse(AttendenceBase):
    id: int | None
    user_id: int
    created_at: dt.datetime

    model_config = {"from_attributes": True}