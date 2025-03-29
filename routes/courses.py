from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from routes.auth import get_current_active_user
from db.schemas import CourseCreate, CourseResponse, LessonCreate, LessonResponse, User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/")
def get_courses(db: Session = Depends(get_db)):
    return list(db.query(models.Course).all())

@router.post("/", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(title=course.title, description=course.description)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/{course_id}")
def read_course(current_user: Annotated[User, Depends(get_current_active_user)], course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, updated_course: CourseCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.title = updated_course.title
    course.description = updated_course.description
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}

@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
def get_lessons_by_course(course_id: int, db: Session = Depends(get_db)):
    lessons = db.query(models.Lesson).filter(models.Lesson.course_id == course_id).all()
    return lessons

@router.post("/{course_id}/lessons", response_model=LessonResponse)
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

