import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key
api_key = os.getenv("API_KEY")

# Configure API key
genai.configure(api_key=api_key)

def generate_quiz(lesson_content):
    """Generate a quiz using Gemini AI"""

    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    prompt = f"""
    Generate a quiz in JSON format based on the given lesson content.  
    The quiz should contain exactly 3 multiple-choice questions.  

    Quiz Format:
    - Each question should have 4 answer choices labeled A, B, C, and D.  
    - One of the choices should be the correct answer.  

    Lesson Content:
    {lesson_content}

    Output Format:
    Return a valid JSON array containing objects with the following structure:  

    [
      {{
        "question": "<question_text>",
        "options": [
          "A) <option_1>",
          "B) <option_2>",
          "C) <option_3>",
          "D) <option_4>"
        ],
        "answer": "<correct_option_text>"
      }}
    ]
    Important Instructions:
    1. Do not include any extra text or explanations—only return raw JSON.  
    2. Do not format the output with triple backticks (```json) or markdown.  
    3. The output must be valid JSON, directly parsable in Python or JavaScript.  
    """

    response = model.generate_content(prompt)
    return response.text

# lesson_text = "Python is a popular programming language known for its readability and versatility."
# quiz = generate_quiz(lesson_text)
# print(quiz)
