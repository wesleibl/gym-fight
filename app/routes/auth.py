from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import create_access_token, verify_password, credentials_exception
from app.models.user import User
from app.models.auth import LoginRequest, TokenResponse

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/auth/login")
async def login(login_request: LoginRequest, session: SessionDep):
    user = select(User).where(User.email == login_request.email)
    user = session.exec(user).first()

    if user is None:
        raise credentials_exception
    
    if not verify_password(login_request.password, user.hashed_password):
        raise credentials_exception
    
    token = create_access_token(data={
        "sub": user.email,
        "is_instructor": user.is_instructor,
    })
    return TokenResponse(access_token=token, token_type="bearer")