from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def extract_pdf_text(uploaded_file):
    return extract_text(uploaded_file)

def calculate_similarity(text1, text2):
    embeddings1 = model.encode([text1])
    embeddings2 = model.encode([text2])
    return cosine_similarity(embeddings1, embeddings2)[0][0]

def find_missing_keywords(resume, job_desc):
    resume_words = set(re.findall(r'\b\w+\b', resume.lower()))
    jd_words = set(re.findall(r'\b\w+\b', job_desc.lower()))
    missing = list(jd_words - resume_words)
    return missing[:20]
