import re
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_analysis_report(resume, job_desc):
    prompt = f"""
    You are a professional career consultant with expertise in technical hiring. Your task is to analyze the candidate's resume based on the given job description.
**Instructions:**
1. For each requirement or skill in the job description, evaluate whether it is:
   - Fully met ✅ (Score: 5/5)
   - Partially met ⚠️ (Score: 3/5)
   - Not met ❌ (Score: 1/5)
2. Format each point like this:  
   - [Skill/Requirement Name]: Score: X/5 (✅/⚠️/❌) - [Short justification]

3. End with:
   - Summary of strengths
   - Summary of weaknesses or gaps
   - Top 10 missing or weak keywords
   - Overall suggestions for improvement

**Job Description**:
{job_desc}

**Resume**:
{resume}
"""
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def extract_scores(text):
    pattern = r'(\d+(?:\.\d+)?)/5'
    return [float(m) for m in re.findall(pattern, text)]
