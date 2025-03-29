from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from schemas import LessonCreate, LessonResponse
from typing import List

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("/", response_model=List[LessonResponse])
def get_all_lessons(db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).all()
    if not lessons:
        raise HTTPException(status_code=404, detail="No lessons found")
    return lessons

@router.get("/{lesson_id}", response_model=LessonResponse)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(lesson_id: int, updated_lesson: LessonCreate, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.title = updated_lesson.title
    lesson.content = updated_lesson.content
    db.commit()
    db.refresh(lesson)
    return lesson

@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}



