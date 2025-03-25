from fastapi import FastAPI, HTTPException, Depends, status
from datetime import datetime, timedelta, timezone
from typing import Annotated
import models
import jwt
import os
from dotenv import load_dotenv
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import quiz_generator
from schemas import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

# Root Endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI-Powered E-Learning Platform"}

@app.get("/courses")
def get_courses(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
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

@app.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, updated_course: CourseCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.title = updated_course.title
    course.description = updated_course.description
    db.commit()
    db.refresh(course)
    return course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}

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

@app.get("/lessons/{lesson_id}", response_model=LessonResponse)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@app.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(lesson_id: int, updated_lesson: LessonCreate, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.title = updated_lesson.title
    lesson.content = updated_lesson.content
    db.commit()
    db.refresh(lesson)
    return lesson

@app.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}

@app.post("/courses/{course_id}/lessonsquiz", response_model=LessonResponse)
def create_lesson(course_id: int, lesson_data: LessonCreate, db: Session = Depends(get_db)):
    """Create a new lesson and generate a quiz for it"""

    # Create lesson
    lesson = models.Lesson(**lesson_data.dict(), course_id=course_id)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

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

    return {"id": quiz.id, "lesson_id": quiz.lesson_id, "questions": quiz.questions}



