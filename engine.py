import os
import pdfplumber
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_CACHE = "trained_vocabulary.pkl"

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def train_vocabulary(corpus_folder):
    if os.path.exists(MODEL_CACHE):
        with open(MODEL_CACHE, 'rb') as f:
            return pickle.load(f)

    corpus_texts = []
    if os.path.exists(corpus_folder):
        files = [f for f in os.listdir(corpus_folder) if f.lower().endswith('.pdf')]
        for filename in files:
            try:
                with pdfplumber.open(os.path.join(corpus_folder, filename)) as pdf:
                    content = " ".join([p.extract_text() or "" for p in pdf.pages])
                    if content.strip():
                        corpus_texts.append(clean_text(content))
            except:
                continue

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3), min_df=2)
    if corpus_texts:
        vectorizer.fit(corpus_texts)
    else:
        vectorizer.fit(["placeholder text for empty corpus"])

    with open(MODEL_CACHE, 'wb') as f:
        pickle.dump(vectorizer, f)
    return vectorizer

def rank_candidates(job_desc, uploaded_files, corpus_folder):
    vectorizer = train_vocabulary(corpus_folder)
    candidate_texts = []
    candidate_names = []
    
    for file in uploaded_files:
        try:
            with pdfplumber.open(file) as pdf:
                content = " ".join([p.extract_text() or "" for p in pdf.pages])
                candidate_texts.append(clean_text(content))
                candidate_names.append(file.name)
        except:
            continue

    if not candidate_texts:
        return []

    jd_vector = vectorizer.transform([clean_text(job_desc)])
    candidate_vectors = vectorizer.transform(candidate_texts)
    scores = cosine_similarity(jd_vector, candidate_vectors).flatten()
    return sorted(zip(candidate_names, scores), key=lambda x: x[1], reverse=True)