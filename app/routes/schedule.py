from app.models.schedule import Schedule, ScheduleCreate, ScheduleResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, col, select
from app.core.database import get_session
from app.core.security import get_current_user, require_instructor
from app.models.user import User
from app.services.schedule import allowed_types

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/schedules/")
async def create_schedule(current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep, schedule_create: ScheduleCreate):
    schedule_already_exists = session.exec(
        select(Schedule)
        .where(Schedule.day_of_week == schedule_create.day_of_week)
        .where(Schedule.time == schedule_create.time)
    ).first()

    if schedule_already_exists:
        raise HTTPException(status_code=400, detail="Unable to create schedule")

    new_schedule = Schedule.model_validate(schedule_create)
    session.add(new_schedule)
    session.commit()
    session.refresh(new_schedule)
    return ScheduleResponse.model_validate(new_schedule)

@router.get("/schedules/")
async def list_schedules(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    schedules = session.exec(select(Schedule)).all()

    if not schedules:
        return []
    
    return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

@router.get("/schedules/available")
async def list_schedules_available(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    user = session.exec(select(User).where(current_user["email"] == User.email)).first()

    if not user:
        raise HTTPException(status_code=400, detail="Unable to find schedules")

    schedules = session.exec(select(Schedule).where(Schedule.type.in_(allowed_types(user)))) # type: ignore[union-attr]

    if not schedules:
        return []
    
    return [ScheduleResponse.model_validate(schedule) for schedule in schedules]

@router.delete("/schedules/{id}")
async def delete_schedule(current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep, id: int):
    schedule_already_exists = session.exec(select(Schedule).where(Schedule.id == id)).first()

    if not schedule_already_exists:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    session.delete(schedule_already_exists)
    session.commit()

    return Response(status_code=204)