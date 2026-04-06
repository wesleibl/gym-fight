from sqlalchemy import false

from app.models.token import Token
from app.models.user import Level, UserCreate, UserResponse, UserUpdate
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from app.core.database import get_session
from app.core.security import get_current_user, get_password_hash, require_instructor
from app.models.user import User

class LevelUpdate(SQLModel):
    level: Level

class InstructorUpdate(SQLModel):
    is_instructor: bool

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/users/")
async def create_user(user: UserCreate, session: SessionDep):
    email_already_exists = session.exec(select(User).where(User.email == user.email)).first()

    if email_already_exists is not None:
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

    return UserResponse.model_validate(user)

@router.put("/users/{id}")
async def update_user(id: int, current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep, userUpdate : UserUpdate):
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