from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)

    lessons = relationship("Lesson", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    questions = Column(JSON, nullable=False)

    lesson = relationship("Lesson", back_populates="quizzes")
