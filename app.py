import streamlit as st
import pandas as pd
import pdfplumber
from engine import rank_candidates, clean_text

CORPUS_PATH = "sample_resumes"

st.set_page_config(page_title="AI resume reader", layout="wide", page_icon="🎯")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stTextArea textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Automated Resume Ranker")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Job Requirements")
    jd_input = st.text_area("Paste Job Description", height=250, placeholder="Enter required skills and role details...", label_visibility="collapsed")

with col2:
    st.markdown("### Candidate Pool")
    uploaded_resumes = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True, label_visibility="collapsed")

def get_candidate_status(jd, resume_file):
    jd_words = set(clean_text(jd).split())
    try:
        with pdfplumber.open(resume_file) as pdf:
            text = " ".join([p.extract_text() or "" for p in pdf.pages])
            resume_words = set(clean_text(text).split())
        
        common = jd_words.intersection(resume_words)
        skills = [word.upper() for word in common if len(word) > 3]
        
        count = len(skills)
        if count > 18:
            return ", ".join(skills[:10]), "Overqualified", "#9C27B0" # Purple
        elif 10 <= count <= 18:
            return ", ".join(skills[:10]), "Qualified", "#2E7D32"    # Green
        elif 5 <= count < 10:
            return ", ".join(skills[:10]), "Mediocre", "#F9A825"     # Yellow
        else:
            return ", ".join(skills[:10]), "Non-Qualified", "#C62828" # Red
    except:
        return "N/A", "Error", "#000000"

st.divider()

if st.button("🚀 Analyze & Rank"):
    if not jd_input.strip() or not uploaded_resumes:
        st.warning("Please provide both a Job Description and Resumes.")
    else:
        with st.spinner("Analyzing candidate relevance..."):
            rankings = rank_candidates(jd_input, uploaded_resumes, CORPUS_PATH)
            
            if rankings:
                results_list = []
                status_colors = {}

                for i, (name, score) in enumerate(rankings):
                    match_file = next(f for f in uploaded_resumes if f.name == name)
                    skills, status, color = get_candidate_status(jd_input, match_file)
                    
                    rank = i + 1
                    results_list.append({
                        "Rank": rank,
                        "Candidate Name": name,
                        "Status": status,
                        "Key Skills Found": skills
                    })
                    status_colors[rank] = color

                df = pd.DataFrame(results_list).set_index("Rank")

                def apply_text_color(row):
                    colors = [''] * len(row)
                    # Status is the second column (index 1)
                    colors[1] = f"color: {status_colors[row.name]}; font-weight: bold;"
                    return colors

                st.info(f"🏆 **Top Match identified:** {df.iloc[0]['Candidate Name']}")
                
                st.dataframe(
                    df.style.apply(apply_text_color, axis=1),
                    use_container_width=True,
                    height=450
                )
                
                csv = df.to_csv().encode('utf-8')
                st.download_button("📥 Download Report", csv, "hiring_report.csv", "text/csv")
            else:
                st.error("Processing failed. Please check the uploaded files.")