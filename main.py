from fastapi import FastAPI, Depends
from typing import Annotated
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from routes.courses import router as courses_router
from routes.auth import router as auth_router
from routes.lessons import router as lessons_router
from routes.quizzes import router as quizzes_router

app = FastAPI()
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(lessons_router)
app.include_router(quizzes_router)








