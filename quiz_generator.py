import google.generativeai as genai

# Configure API key
genai.configure(api_key="AIzaSyA53JF_Q2FgfbAg0Lur4--eBkq_tscBJDY")

def generate_quiz(lesson_content):
    """Generate a quiz using Gemini AI"""

    # Use the correct model name
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    prompt = f"""
    Generate a quiz in JSON format with 3 multiple-choice questions from the given lesson content.
    Each question should have 4 answer choices and 1 correct answer.

    Lesson Content:
    {lesson_content}

    Ensure the output is a valid JSON array of objects.

    JSON Format:
    [
      {{
        "question": "<question>",
        "options": ["A) <option>", "B) <option>", "C) <option>", "D) <option>"],
        "answer": "<correct_option>"
      }}
    ]
    """

    response = model.generate_content(prompt)
    return response.text  # Extract text from the response

# Example usage
lesson_text = "Python is a popular programming language known for its readability and versatility."
quiz = generate_quiz(lesson_text)
print(quiz)
