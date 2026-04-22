from app.models.attendence import Attendence, AttendenceCreate, AttendenceResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.schedule import Schedule
from app.models.user import User

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/attendences/")
async def create_attendence(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep, attendence: AttendenceCreate):
    user = session.exec(select(User).where(User.email == current_user['email'])).first()

    if not user:
        raise HTTPException(status_code=400, detail="Unable to find user")

    schedule = session.exec(select(Schedule).where(Schedule.id == attendence.schedule_id)).first()

    if not schedule:
        raise HTTPException(status_code=400, detail="Unable to find schedule")

    assert user.id is not None

    new_attendence = Attendence(
        **attendence.model_dump(),
        user_id=user.id
    )
    session.add(new_attendence)
    session.commit()
    session.refresh(new_attendence)

    return AttendenceResponse.model_validate(new_attendence)

@router.get("/attendences/")
async def list_attendences(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    if current_user['is_instructor']:
        attendences = session.exec(select(Attendence)).all()
    else:
        user = session.exec(select(User).where(User.email == current_user['email'])).first()
        if not user:
            raise HTTPException(status_code=400, detail="Unable to find user")
        attendences = session.exec(select(Attendence).where(Attendence.user_id == user.id)).all()

    return [AttendenceResponse.model_validate(a) for a in attendences]

@router.delete("/attendences/{id}")
async def delete_attendence(id: int, current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    attendence = session.exec(select(Attendence).where(Attendence.id == id)).first()

    if not attendence:
        raise HTTPException(status_code=404, detail="Attendence not found")

    if not current_user['is_instructor']:
        user = session.exec(select(User).where(User.email == current_user['email'])).first()
        if not user or attendence.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access Denied")

    session.delete(attendence)
    session.commit()

    return Response(status_code=204)
