from app.models.user import Level, UserCreate, UserResponse, UserUpdate, LevelUpdate, InstructorUpdate, StatusUpdate
from app.models.attendence import Attendence, AttendenceResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user, get_password_hash, require_instructor
from app.models.user import User

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/users/")
async def create_user(user: UserCreate, session: SessionDep):
    email_already_exists = session.exec(select(User).where(User.email == user.email)).first()

    if email_already_exists:
        raise HTTPException(status_code=400, detail="Unable to create account")

    new_user = User(
        **user.model_dump(),
        hashed_password=get_password_hash(user.password)
        )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserResponse.model_validate(new_user)

@router.get("/users/")
async def list_users(current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep):
    users = session.exec(select(User)).all()

    if not users:
        return []

    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/{id}")
async def get_user_by_id(id: int, current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    if not current_user['is_instructor']:
        user = session.exec(select(User).where(current_user["email"] == User.email)).first()
    else:
        user = session.exec(select(User).where(id == User.id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)

@router.put("/users/{id}")
async def update_user(id: int, current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep, userUpdate: UserUpdate):
    if not current_user['is_instructor']:
        user = session.exec(select(User).where(current_user["email"] == User.email)).first()
    else:
        user = session.exec(select(User).where(User.id == id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = userUpdate.model_dump(exclude_unset=True)

    for key, value in user_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)

@router.delete("/users/{id}")
async def delete_user(id: int, current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep):
    user = session.exec(select(User).where(User.id == id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()

    return Response(status_code=204)

@router.patch("/users/{id}/level")
async def update_user_level(id: int, current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep, levelUpdate: LevelUpdate):
    user = session.exec(select(User).where(User.id == id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.level = levelUpdate.level

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)

@router.patch("/users/{id}/instructor")
async def change_instructor_status(id: int, current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep, instructorUpdate: InstructorUpdate):
    user = session.exec(select(User).where(User.id == id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_instructor = instructorUpdate.is_instructor

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)

@router.patch("/users/{id}/status")
async def update_user_status(id: int, current_user: Annotated[dict, Depends(require_instructor)], session: SessionDep, statusUpdate: StatusUpdate):
    user = session.exec(select(User).where(User.id == id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = statusUpdate.status

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse.model_validate(user)

@router.get("/users/{id}/attendances")
async def get_user_attendances(id: int, current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    if not current_user['is_instructor']:
        user = session.exec(select(User).where(current_user["email"] == User.email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.id != id:
            raise HTTPException(status_code=403, detail="Access Denied")
        target_id = user.id
    else:
        user = session.exec(select(User).where(User.id == id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        target_id = id

    attendances = session.exec(select(Attendence).where(Attendence.user_id == target_id)).all()
    return [AttendenceResponse.model_validate(a) for a in attendances]
