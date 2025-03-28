from fastapi import FastAPI, Depends
from typing import Annotated
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from routes.courses import router as courses_router
from routes.auth import router as auth_router
from routes.lessons import router as lessons_router

app = FastAPI()
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]

# Root Endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI-Powered E-Learning Platform"}

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(lessons_router)








