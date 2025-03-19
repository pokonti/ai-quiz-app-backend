from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import quiz_generator
import json

app = FastAPI()
# models.Base.metadata.drop_all(engine)
models.Base.metadata.create_all(bind=engine)

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None

class CourseResponse(CourseCreate):
    id: int
    lessons: List[int] = []  # List of Lesson IDs

    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    title: str
    content: str

class LessonResponse(LessonCreate):
    id: int
    quiz_id: Optional[int] = None

    class Config:
        from_attributes = True

class QuizResponse(BaseModel):
    id: int
    lesson_id: int
    questions: str  # JSON format



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-Powered E-Learning Platform"}

@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return list(db.query(models.Course).all())

@app.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(title=course.title, description=course.description)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/courses/{course_id}")
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.get("/courses/{course_id}/lessons", response_model=List[LessonResponse])
def get_lessons_by_course(course_id: int, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).filter(models.Lesson.course_id == course_id).all()
    return lessons

@app.post("/courses/{course_id}/lessons", response_model=LessonResponse)
def create_lesson(course_id: int, lesson: LessonCreate, db: Session = Depends(get_db)):
    # Check if the course exists
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Create the new lesson (without a quiz)
    new_lesson = models.Lesson(
        title=lesson.title,
        content=lesson.content,
        course_id=course_id,
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson


@app.post("/courses/{course_id}/lessonsquiz", response_model=LessonResponse)
def create_lesson(course_id: int, lesson_data: LessonCreate, db: Session = Depends(get_db)):
    """Create a new lesson and generate a quiz for it"""

    # Create lesson
    lesson = models.Lesson(**lesson_data.dict(), course_id=course_id)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    # Generate quiz (You can store it in DB)
    try:
        quiz_questions = quiz_generator.generate_quiz(lesson_data.content)

        # Save quiz in database
        quiz = models.Quiz(lesson_id=lesson.id, questions=quiz_questions)
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        # print("Generated Quiz:", quiz_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

    return {"id": lesson.id, "title": lesson.title, "content": lesson.content, "course_id": lesson.course_id, "quiz_id": quiz.id}



@app.get("/lessons/{lesson_id}/quiz", response_model=QuizResponse)
def get_quiz(lesson_id: int, db: Session = Depends(get_db)):
    """Retrieve quiz for a specific lesson"""
    quiz = db.query(models.Quiz).filter(models.Quiz.lesson_id == lesson_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {"id": quiz.id, "lesson_id": quiz.lesson_id, "questions": quiz.questions}  # Directly return JSON



