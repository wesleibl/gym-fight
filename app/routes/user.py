from app.models.user import UserCreate, UserResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models.user import User

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