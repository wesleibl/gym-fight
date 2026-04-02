from fastapi import APIRouter
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.models.student import Student
from app.models.auth import LoginRequest, TokenResponse

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.post("/auth/login")
async def login(loginRequest: LoginRequest, session: SessionDep):
    student = select(Student).where(Student.email == loginRequest.email)
    student = session.exec(student).first()
    if student is None:
        raise credentials_exception
    if not verify_password(loginRequest.password, student.hashed_password):
        raise credentials_exception
    token = create_access_token(data={
        "sub": student.email,
        "role": student.role
    })
    return TokenResponse(access_token=token, token_type="bearer")

