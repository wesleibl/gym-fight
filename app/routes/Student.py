from fastapi import APIRouter
from app.models.Student import StudentCreate

router = APIRouter()

@router.post("/students/")
async def create_student(student: StudentCreate):
    results = {"student": student}
    return results