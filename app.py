import streamlit as st
from utils.extract import extract_pdf_text, calculate_similarity, find_missing_keywords
from utils.analysis import get_analysis_report, extract_scores
from utils.emailer import send_email_report
from dotenv import load_dotenv
import os

load_dotenv()
st.set_page_config(page_title="TalentIQ Analyzer", layout="wide", page_icon="📊")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h1>TalentIQ Analyzer</h1>
        <p>AI-powered recruitment intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📊 Resume Matching", use_container_width=True):
        st.session_state.page = "Resume Matching"

    if st.button("🎤 Smart Interview Prep", use_container_width=True):
        st.session_state.page = "Smart Interview Prep"

    st.markdown("---")

if 'page' not in st.session_state:
    st.session_state.page = "Resume Matching"

# ------------------ PAGE 1: RESUME MATCHING ------------------
if st.session_state.page == "Resume Matching":
    st.markdown("""
    <div class="gradient-header">
        <h1>Resume Matching System</h1>
        <p>Optimize your resume for any job opportunity</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns([3, 2])

        with col1:
            with st.expander("📋 Job Requirements", expanded=True):
                job_desc = st.text_area("", height=250, label_visibility="collapsed",
                                        placeholder="Paste the complete job description here...")

            with st.expander("📄 Upload Your Resume(s)", expanded=True):
                resumes = st.file_uploader("", type="pdf", accept_multiple_files=True,
                                           label_visibility="collapsed")

        with col2:
            with st.expander("📧 Report Delivery", expanded=True):
                email = st.text_input("", placeholder="Enter email for detailed report",
                                      label_visibility="collapsed")

            st.markdown("""
            <div class="info-box">
                <h3>How it works:</h3>
                <ol>
                    <li>Paste the job description</li>
                    <li>Upload your resume (PDF)</li>
                    <li>Get instant analysis</li>
                    <li>Receive detailed report</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔍 Analyze Compatibility", type="primary", use_container_width=True):

        if job_desc and resumes:
            for resume_file in resumes:
                resume_text = extract_pdf_text(resume_file)
                similarity = calculate_similarity(resume_text, job_desc)
                report = get_analysis_report(resume_text, job_desc)
                scores = extract_scores(report)
                avg_score = sum(scores) / (5 * len(scores)) if scores else 0
                missing_keywords = find_missing_keywords(resume_text, job_desc)

                # Display Results
                st.markdown("---")
                st.subheader(f"📁 Report for: `{resume_file.name}`")
                st.markdown(f"**🧮 Similarity Score:** `{similarity:.2f}`")
                st.markdown(f"**📊 Average Evaluation Score:** `{avg_score:.2f}`")

                st.markdown("### 🧠 AI Feedback Report")
                st.markdown(report, unsafe_allow_html=True)

                st.download_button("📥 Download Report", report, file_name=f"{resume_file.name}_report.txt")

                if email:
                    send_email_report(email, report, f"{resume_file.name}_report.txt")
                    st.success(f"📧 Report emailed to **{email}**")

        else:
            st.warning("⚠️ Please enter a job description and upload at least one resume.")

# -------------------- PAGE 2: SMART INTERVIEW PREP --------------------
elif st.session_state.page == "Smart Interview Prep":
    from utils.interview import generate_interview_questions, evaluate_interview_answers
    from utils.extract import extract_text_from_pdf

    st.markdown("""
    <div style="background: linear-gradient(to right, #5f72be, #9921e8); padding: 1.5rem; border-radius: 12px; color: white;">
        <h1>Smart Interview Preparation</h1>
        <p>Upload your resume and job description to get AI-generated questions & feedback</p>
    </div>
    """, unsafe_allow_html=True)

    col_prep1, col_prep2 = st.columns(2)

    with col_prep1:
        with st.expander("📄 Upload Resume", expanded=True):
            resume_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"], key="resume_upload")
            resume_text = ""
            if resume_file:
                resume_text = extract_text_from_pdf(resume_file)

    with col_prep2:
        with st.expander("🧾 Upload or Paste Job Description", expanded=True):
            job_desc_text = st.text_area("Or paste the Job Description here", height=200)

    if st.button("🎯 Generate Interview Questions", type="primary", use_container_width=True):
        if resume_text.strip() and job_desc_text.strip():
            with st.spinner("Generating tailored interview questions..."):
                questions = generate_interview_questions(resume_text, job_desc_text, num_questions=5)
                # Clean out any prefix like "1. Technical:" or "2. Behavioral:"
                cleaned_questions = [
                    q.split(":", 1)[-1].strip() if ":" in q else q
                    for q in questions.split('\n') if q.strip()
                ]
                st.session_state.questions = cleaned_questions
                st.session_state.answers = [""] * len(cleaned_questions)
        else:
            st.warning("Please upload or paste both resume and job description.")

    if 'questions' in st.session_state:
        st.markdown("### 🔍 Interview Questions")
        with st.form(key='interview_form'):
            for i, question in enumerate(st.session_state.questions):
                st.markdown(f"""
                <div style='background-color:#1e1e1e; padding:15px; border-radius:10px; margin-bottom:15px; color:#f5f5f5;'>
                    <strong style='color:#A78BFA;'>Question {i+1}:</strong><br>{question}
                </div>
                """, unsafe_allow_html=True)

                st.session_state.answers[i] = st.text_area(
                    f"Answer to Question {i+1}",
                    value=st.session_state.answers[i],
                    height=100,
                    key=f"answer_{i}",
                    label_visibility="collapsed"
                )

            if st.form_submit_button("📝 Submit Answers for Evaluation", use_container_width=True):
                with st.spinner("Evaluating your responses..."):
                    answers_text = "\n".join(
                        f"Question {i+1}: {q}\nAnswer: {a}\n"
                        for i, (q, a) in enumerate(zip(
                            st.session_state.questions,
                            st.session_state.answers
                        )) if q.strip()
                    )
                    feedback = evaluate_interview_answers("\n".join(st.session_state.questions), answers_text)
                    st.markdown("### 📝 AI Evaluation")
                    for block in feedback.split("Question")[1:]:  # Skip first empty split
                        block = "Question" + block.strip()
                        question_line = block.split("\n")[0]
                        score_line = next((line for line in block.split("\n") if line.startswith("Score:")), "")
                        feedback_line = next((line for line in block.split("\n") if line.startswith("Feedback:")), "")
                        suggestion_line = next((line for line in block.split("\n") if line.startswith("Suggestion:")), "")

                        st.markdown(f"""
                        <div style="background-color:#1e1e1e; padding:15px; border-radius:12px; margin-bottom:20px; color:#e0e0e0;">
        <h4 style="color:#A78BFA;">{question_line}</h4>
        <p><strong style="color:#7FFFD4;">{score_line}</strong></p>
        <p><span style="color:#FFA07A;"><strong>Feedback:</strong></span> {feedback_line.replace('Feedback:', '').strip()}</p>
        <p><span style="color:#87CEFA;"><strong>Suggestion:</strong></span> {suggestion_line.replace('Suggestion:', '').strip()}</p>
    </div>
    """, unsafe_allow_html=True)


