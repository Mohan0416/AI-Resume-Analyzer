import streamlit as st
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import matplotlib.pyplot as plt
import re
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")

st.title("AI Resume Analyzer")
client = Groq(api_key=api_key)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def extract_pdf_text(uploaded_file):
    return extract_text(uploaded_file)

def calculate_similarity(text1, text2):
    embeddings1 = model.encode([text1])
    embeddings2 = model.encode([text2])
    return cosine_similarity(embeddings1, embeddings2)[0][0]

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

def find_missing_keywords(resume, job_desc):
    resume_words = set(re.findall(r'\b\w+\b', resume.lower()))
    jd_words = set(re.findall(r'\b\w+\b', job_desc.lower()))
    missing = list(jd_words - resume_words)
    return missing[:20]

def send_email_report(to_email, report, filename):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_email
    msg['Subject'] = 'Your AI Resume Analysis Report'

    body = "Please find attached your resume analysis report."
    msg.attach(MIMEText(body, 'plain'))

    attachment = MIMEApplication(report.encode('utf-8'))
    attachment['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(email_user, email_pass)
        server.send_message(msg)

def plot_scores(scores, labels=None, filename="score_chart.png"):
    chart_dir = "charts"
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, filename)

    fig, ax = plt.subplots(figsize=(10, 5))

    if not labels:
        labels = [f"Point {i+1}" for i in range(len(scores))]

    bars = ax.bar(labels, scores, color='mediumseagreen', edgecolor='black')

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9, color='black')

    ax.set_ylim(0, 5.5)
    ax.set_title("Resume Evaluation per Job Requirement", fontsize=14, fontweight='bold')
    ax.set_ylabel("Score (out of 5)", fontsize=12)
    ax.set_xlabel("Evaluation Points", fontsize=12)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=30, ha='right')
    fig.tight_layout()

    fig.savefig(chart_path)
    plt.close(fig)
    return chart_path

job_desc = st.text_area("Enter Job Description")
email = st.text_input("Enter your email to receive the report")
resumes = st.file_uploader("Upload Resume PDFs", type="pdf", accept_multiple_files=True)

if st.button("Analyze"):
    if job_desc and resumes:
        for resume_file in resumes:
            resume_text = extract_pdf_text(resume_file)
            similarity = calculate_similarity(resume_text, job_desc)
            report = get_analysis_report(resume_text, job_desc)
            scores = extract_scores(report)
            avg_score = sum(scores) / (5 * len(scores)) if scores else 0
            missing_keywords = find_missing_keywords(resume_text, job_desc)
            chart_path = plot_scores(scores, filename=f"{resume_file.name}_chart.png")

            st.subheader(f"Report for: {resume_file.name}")
            st.write(f"**Similarity Score:** {similarity:.2f}")
            st.write(f"**Average Evaluation Score:** {avg_score:.2f}")
            st.image(chart_path, caption="Score Chart")

            st.markdown("### AI Feedback Report")
            st.markdown(report, unsafe_allow_html=True)

            st.download_button("Download Report", report, file_name=f"{resume_file.name}_report.txt")

            if email:
                send_email_report(email, report, f"{resume_file.name}_report.txt")
                st.success(f"Report emailed to {email}")
    else:
        st.warning("Please enter a job description and upload at least one resume.")
