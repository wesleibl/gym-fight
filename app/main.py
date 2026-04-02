from fastapi import FastAPI
from app.core.database import create_db
from contextlib import asynccontextmanager
from app.routes.auth import router as auth_router
from app.routes.student import router as students_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(students_router)