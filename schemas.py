from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None



class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None

class CourseResponse(CourseCreate):
    id: int
    lessons: List[int] = []

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
    questions: str

