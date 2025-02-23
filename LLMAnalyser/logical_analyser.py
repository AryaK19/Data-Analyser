import difflib
import numpy as np
import spacy
import Levenshtein
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine
import google.generativeai as genai
import json
import warnings
nlp = spacy.load("en_core_web_sm")
from dotenv import load_dotenv
import os

warnings.filterwarnings('ignore', message='numpy.dtype size changed')
warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', ''))

def validate_text_output(expected_output, generated_output):
    """
    Validate text/table-based output using Gemini AI.
    """
    model = genai.GenerativeModel("gemini-pro")
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
        - always provide your response in below format only

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
    model = genai.GenerativeModel("gemini-pro")
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
        - If there final result is same but they use different approach then return "Correct ✅" and explain the both codes
        - If they provide different outputs, return "Incorrect ❌" and explain why.
        - If there are minor differences (like variable names, formatting, or comments), mention them separately.
        - reason should not not be more than two lines because if it exceeds then json structute corrupts
        - always provide your response in below json format only
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

def is_valid_logic(generated_code: str, expected_code: str = None) -> dict:
    """
    Analyze logical correctness of generated code by comparing with expected code
    using multiple validation approaches.
    
    Args:
        generated_code (str): The code generated by the system
        expected_code (str, optional): Expected correct code for comparison
        
    Returns:
        dict: Analysis results including AI validation and similarity metrics
    """
    try:
        results = {
            "status": "Valid ✅",
            "ai_validation": None,
            "similarity_metrics": None,
            "overall_similarity": 0.0,
            "suggestions": []
        }

        if not expected_code:
            results.update({
                "status": "Warning ⚠️",
                "message": "No expected code provided for comparison",
                "suggestion": "Provide expected code for comprehensive analysis"
            })
            return results

        # 1. AI-based validation using Gemini
        ai_validation = validate_code(expected_code, generated_code)
        results["ai_validation"] = ai_validation

        # 2. Calculate similarity metrics
        similarity_metrics = calculate_similarity_metrics(expected_code, generated_code)
        results["similarity_metrics"] = similarity_metrics

        # 3. Calculate overall similarity score
        # Weight each metric based on importance
        weights = {
            "Levenshtein Distance": 0.2,
            "BLEU Score (spaCy)": 0.3,
            "Cosine Similarity": 0.5
        }

        # Normalize Levenshtein distance (lower is better)
        max_len = max(len(expected_code), len(generated_code))
        normalized_levenshtein = 1 - (similarity_metrics["Levenshtein Distance"] / max_len)

        overall_similarity = (
            normalized_levenshtein * weights["Levenshtein Distance"] +
            similarity_metrics["BLEU Score (spaCy)"] * weights["BLEU Score (spaCy)"] +
            similarity_metrics["Cosine Similarity"] * weights["Cosine Similarity"]
        )
        results["overall_similarity"] = round(overall_similarity * 100, 2)  # Convert to percentage

        # 4. Determine status and suggestions
        if ai_validation.get("message", "").startswith("Incorrect"):
            results["status"] = "Invalid ❌"
            results["suggestions"].append(ai_validation.get("reason", "Check code logic"))
        
        # Add similarity-based suggestions
        if overall_similarity < 0.7:  # Less than 70% similar
            results["status"] = "Invalid ❌"
            results["suggestions"].append("Code structure differs significantly from expected")
        elif overall_similarity < 0.9:  # Less than 90% similar
            if results["status"] == "Valid ✅":
                results["status"] = "Warning ⚠️"
            results["suggestions"].append("Minor differences detected in code structure")

        # Format final response
        return {
            "status": results["status"],
            "analysis": {
                "ai_validation": results["ai_validation"],
                "similarity_analysis": {
                    "metrics": results["similarity_metrics"],
                    "overall_similarity": f"{results['overall_similarity']}%"
                }
            },
            "suggestions": results["suggestions"] if results["suggestions"] else ["Code logic appears correct"]
        }

    except Exception as e:
        return {
            "status": "Error ❌",
            "message": f"Analysis failed: {str(e)}",
            "error": True
        }