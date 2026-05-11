import streamlit as st
import pdfplumber
import docx
import re
import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# -------------------------------
# Custom CSS
# -------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #4CAF50;
}

.card {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
}

.skill-box {
    background-color: #4CAF50;
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    display: inline-block;
    margin: 5px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------

st.markdown('<p class="big-title">📄 AI Resume Analyzer Dashboard</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

# -------------------------------
# PDF Extraction
# -------------------------------

def extract_text_from_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# -------------------------------
# DOCX Extraction
# -------------------------------

def extract_text_from_docx(file):

    doc = docx.Document(file)

    text = []

    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)

# -------------------------------
# Extract Email
# -------------------------------

def extract_email(text):

    match = re.search(r'[\w\.-]+@[\w\.-]+', text)

    if match:
        return match.group(0)

    return "Not Found"

# -------------------------------
# Extract Phone
# -------------------------------

def extract_phone(text):

    match = re.search(r'\+?\d[\d\s\-]{8,15}', text)

    if match:
        return match.group(0)

    return "Not Found"

# -------------------------------
# Extract Name
# -------------------------------

def extract_name(text):

    doc = nlp(text)

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            return ent.text

    return "Not Found"

# -------------------------------
# Extract Skills
# -------------------------------

def extract_skills(text):

    skills_list = [

        "python",
        "java",
        "c",
        "c++",
        "html",
        "css",
        "javascript",
        "react",
        "nodejs",
        "mongodb",
        "mysql",
        "sql",
        "machine learning",
        "deep learning",
        "streamlit",
        "aws",
        "git",
        "github",
        "numpy",
        "pandas"
    ]

    found_skills = []

    lower_text = text.lower()

    for skill in skills_list:

        if skill in lower_text:
            found_skills.append(skill.title())

    return found_skills

# -------------------------------
# Extract Education
# -------------------------------

def extract_education(text):

    education_keywords = [
        "B.Tech",
        "Bachelor",
        "Master",
        "M.Tech",
        "Intermediate",
        "SSC"
    ]

    found = []

    for word in education_keywords:

        if word.lower() in text.lower():
            found.append(word)

    return found

# -------------------------------
# Experience Estimation
# -------------------------------

def estimate_experience(text):

    experience_keywords = [
        "intern",
        "experience",
        "project",
        "worked"
    ]

    score = 0

    for word in experience_keywords:

        if word.lower() in text.lower():
            score += 1

    return f"{score}+ Relevant Experiences"

# -------------------------------
# Main Logic
# -------------------------------

if uploaded_file:

    text = ""

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)

    elif uploaded_file.name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    education = extract_education(text)
    experience = estimate_experience(text)

    # -------------------------------
    # Candidate Overview
    # -------------------------------

    st.markdown("## 👤 Candidate Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidate Name", name)

    with col2:
        st.metric("Phone", phone)

    with col3:
        st.metric("Experience", experience)

    st.markdown("---")

    # -------------------------------
    # Professional Details Card
    # -------------------------------

    st.markdown("## 📌 Professional Details")

    st.markdown(f"""
    <div class="card">

    <h4>📧 Email</h4>
    <p>{email}</p>

    <h4>🎓 Education</h4>
    <p>{", ".join(education)}</p>

    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Skills Section
    # -------------------------------

    st.markdown("## 🚀 Technical Skills")

    if skills:

        for skill in skills:
            st.markdown(
                f'<span class="skill-box">{skill}</span>',
                unsafe_allow_html=True
            )

    else:
        st.warning("No Skills Found")

    st.markdown("---")

    # -------------------------------
    # Resume Text
    # -------------------------------

    with st.expander("📄 View Extracted Resume Text"):

        st.text_area(
            "",
            text,
            height=300
        )

    # -------------------------------
    # Final Data Table
    # -------------------------------

    st.markdown("## 📊 Parsed Resume Data")

    data = {

        "Name": [name],
        "Email": [email],
        "Phone": [phone],
        "Experience": [experience],
        "Education": [", ".join(education)],
        "Skills": [", ".join(skills)]
    }

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True
    )

    # -------------------------------
    # Download CSV
    # -------------------------------

    csv = df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Parsed Resume CSV",
        data=csv,
        file_name="parsed_resume.csv",
        mime="text/csv"
    )