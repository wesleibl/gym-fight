from app.models.student import StudentCreate, StudentResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_password_hash
from app.models.student import Student

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/students/")
async def create_student(student: StudentCreate, session: SessionDep):
    email_already_exists = session.exec(select(Student).where(Student.email == student.email)).first()

    if email_already_exists is not None:
        raise HTTPException(status_code=400, detail="Unable to create account")
    
    new_student = Student(
        **student.model_dump(), 
        hashed_password=get_password_hash(student.password)
        )
    session.add(new_student)
    session.commit()
    session.refresh(new_student)
    return StudentResponse.model_validate(new_student)