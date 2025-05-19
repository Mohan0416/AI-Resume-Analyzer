from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_interview_questions(resume, job_desc, num_questions=5):
    prompt = f"""
    Based on the following resume and job description, generate {num_questions} personalized interview questions.
    Include a mix of technical and behavioral questions.

    **Resume**:
    {resume}

    **Job Description**:
    {job_desc}
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content

def evaluate_interview_answers(questions, answers):
    prompt = f"""
    Evaluate the following candidate's answers to the interview questions. 
    Give a score out of 10 for each answer and a short constructive feedback.

    Questions:
    {questions}

    Answers:
    {answers}
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content
