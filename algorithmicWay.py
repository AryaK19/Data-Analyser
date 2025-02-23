import difflib
import numpy as np
import spacy
import Levenshtein
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine

nlp = spacy.load("en_core_web_sm")
   
def tokenize_text(text):
    """Tokenize text using spaCy."""
    doc = nlp(text)
    return [token.text for token in doc if not token.is_punct]  # Exclude punctuation

def calculate_levenshtein_distance(expected_code, generated_code):
    """Calculate Levenshtein Distance (edit distance) between two code strings."""
    return Levenshtein.distance(expected_code, generated_code)

def calculate_bleu_score(expected_code, generated_code):
    """Calculate BLEU Score alternative using spaCy tokenization."""
    reference_tokens = tokenize_text(expected_code)
    candidate_tokens = tokenize_text(generated_code)

    # Compute simple overlap score (alternative to BLEU)
    common_tokens = set(reference_tokens) & set(candidate_tokens)
    bleu_like_score = len(common_tokens) / len(reference_tokens) if reference_tokens else 0

    return bleu_like_score

def calculate_cosine_similarity(expected_code, generated_code):
    """Calculate Cosine Similarity between expected and generated code using TF-IDF."""
    vectorizer = TfidfVectorizer().fit_transform([expected_code, generated_code])
    vectors = vectorizer.toarray()
    
    if np.any(vectors[0]) and np.any(vectors[1]):  # Avoid division by zero
        return 1 - cosine(vectors[0], vectors[1])  # Cosine Similarity
    return 0.0

def calculate_similarity_metrics(expected_code, generated_code):
    """Calculate similarity scores using different algorithms."""
    levenshtein_dist = calculate_levenshtein_distance(expected_code, generated_code)
    bleu_score = calculate_bleu_score(expected_code, generated_code)
    cosine_sim = calculate_cosine_similarity(expected_code, generated_code)

    return {
        "Levenshtein Distance": levenshtein_dist,
        "BLEU Score (spaCy)": bleu_score,
        "Cosine Similarity": cosine_sim
    }
