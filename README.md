# AI Integrated Quiz App Backend

## Overview
FastAPI-based backend for an AI-powered quiz application. It allows users to create lessons, generate quizzes using AI (Gemini API), and retrieve quizzes for lessons. The project utilizes PostgreSQL as the database and SQLAlchemy as the ORM.

## Features
- User authentication (registration, login, JWT-based authentication)
- Create, read, update, and delete (CRUD) operations for courses and lessons
- Generate quizzes dynamically from lesson content using AI
- Store and retrieve quizzes from the database
- Serve quizzes via a REST API

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (hosted on Railway)
- **ORM**: SQLAlchemy
- **AI Integration**: Google Gemini API
- **Authentication**: OAuth2 with JWT


## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- PostgreSQL
- Git
- Virtual environment (optional but recommended)

### Clone the Repository
```sh
git clone https://github.com/pokonti/ai-quiz-app-backend.git
cd ai-quiz-app-backend
```

### Create and Activate a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate
```

## Configuration
### Database Setup
Create a `.env` file in the project root with the following environment variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
GEMINI_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_secret_key
```
Update the `DATABASE_URL` with your PostgreSQL credentials.

## Running the Application
```sh
fastapi dev main.py
```
The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Endpoints

### Authentication
- **POST `auth/register/`** - Register a new user
- **POST `auth/login/`** - Login and get an access token

### Courses
- **POST `/courses/`** - Create a new course
- **GET `/courses/`** - Retrieve all courses
- **PUT `/courses/{course_id}`** - Update a course 
- **DELETE `/courses/{course_id}`** - Delete a course

### Lessons
- **POST `/courses/{course_id}/lessonsquiz`** - Create a lesson and generate a quiz
- **GET `/lessons/{lesson_id}`** - Retrieve a lesson

### Quizzes
- **GET `/lessons/{lesson_id}/quiz`** - Retrieve quiz for a lesson

