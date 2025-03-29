from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from db.database import get_db
from service import quiz_generator
import json
router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=schemas.QuizResponse)
def generate_quiz(lesson_id: int, db: Session = Depends(get_db)):
    """Generate a new quiz dynamically from lesson content"""

    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson_content = lesson.content

    questions_json = quiz_generator.generate_quiz(lesson_content)
    questions = json.loads(questions_json)
    # print(questions_json)

    new_quiz = models.Quiz(lesson_id=lesson_id, questions=questions)
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return new_quiz


@router.get("/{quiz_id}", response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if isinstance(quiz.questions, str):
        quiz.questions = json.loads(quiz.questions)

    return quiz


@router.delete("/{lesson_id}", response_model=dict)
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

