import difflib
import numpy as np
import spacy
import Levenshtein
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine
import google.generativeai as genai
import json
nlp = spacy.load("en_core_web_sm")

genai.configure(api_key="AIzaSyCeh14GWGwxSk6yw3Cx9I3Nl4dFJ7f29Fw")

def validate_text_output(expected_output, generated_output):
    """
    Validate text/table-based output using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
        You are a validation system. Compare the expected and generated outputs.

        **Expected Output:** 
        {expected_output}

        **Generated Output:** 
        {generated_output}

        **Instructions:** 
        - If both outputs match, return "Correct ✅".
        - If they are different, return "Incorrect ❌" and explain why.
        - If the format differs but content is similar, mention formatting issues.

        Return JSON response:
        {{
            "message": "Correct ✅" or "Incorrect ❌",
            "reason": "Explanation"
        }}
    """

    response = model.generate_content(prompt)

    # 🛑 Debug: Print raw response
    print("Gemini AI Response:", response.text)

    if not response.text:
        return {
            "message": "Error ❌",
            "reason": "Gemini AI returned an empty response."
        }

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        return {
            "message": "Error ❌",
            "reason": f"Invalid JSON response from Gemini AI. Error: {str(e)}"
        }


def validate_code(expected_code, generated_code):
    """
    Validate code correctness by comparing expected and generated code using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
        You are a code validation system. Compare the expected and generated code snippets.

        **Expected Code:** 
        ```python
        {expected_code}
        ```

        **Generated Code:** 
        ```python
        {generated_code}
        ```

        **Instructions:** 
        - If both code snippets match exactly, return "Correct ✅".
        - If they are different, return "Incorrect ❌" and explain why.
        - If there are minor differences (like variable names, formatting, or comments), mention them separately.
        - If the logic differs, specify the exact issues and suggest corrections.

        Return JSON response:
        {{
            "message": "Correct ✅" or "Incorrect ❌",
            "reason": "Explanation of differences"
        }}
    """

    response = model.generate_content(prompt)

    # 🛑 Debug: Print raw response
    print("Gemini AI Response:", response.text)

    if not response.text:
        return {
            "message": "Error ❌",
            "reason": "Gemini AI returned an empty response."
        }

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        return {
            "message": "Error ❌",
            "reason": f"Invalid JSON response from Gemini AI. Error: {str(e)}"
        }


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

def is_valid_logic():
    pass