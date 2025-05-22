from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_interview_questions(resume, job_desc, num_questions=5):
    prompt = f"""
You are a technical interviewer preparing a candidate for an AI/ML or software engineering role.

Based on the following RESUME and JOB DESCRIPTION, generate {num_questions} personalized and realistic interview questions.

Guidelines:
- Questions should be relevant to candidate’s experience and job requirements.
- Do NOT label as Technical/Behavioral.
- Do NOT number the questions.
- Ask only clear, natural-sounding questions.

RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Output:
Only return the questions, each on a new line.
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content.strip()
def evaluate_interview_answers(questions, answers):
    prompt = f"""
You are an expert interview coach.

Given the interview QUESTIONS and CANDIDATE'S ANSWERS, evaluate each answer.

For each question, return:
- A score out of 10
- A 1-2 sentence evaluation
- One suggestion for improvement

Return the output in this exact format:

Question 1: [question text]
Score: X/10
Feedback: ...
Suggestion: ...

Repeat for all questions.

QUESTIONS:
{questions}

ANSWERS:
{answers}
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content.strip()
