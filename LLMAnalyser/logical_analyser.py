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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


warnings.filterwarnings('ignore', message='numpy.dtype size changed')
warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', ''))

def validate_output(expected_output, generated_output, expected_code, generated_code, df):
    """
    Validate output correctness by comparing expected and generated output.
    Returns tuple of (validation_result, actual_output)
    """
    if expected_output != "{}":
        # Simple string-based validation
        return ("Correct ✅" if str(expected_output) == str(generated_output) else "Incorrect ❌", 
                generated_output)
    
    elif str(type(generated_output)).startswith("<class 'pandas"):
        # Execute expected_code to get the expected DataFrame
        namespace = {
            'df': df,
            'pd': pd,
            'np': np,
            'result': None
        }
        
        # Clean and execute code
        clean_code = '\n'.join(
            line for line in expected_code.split('\n')
            if line.strip() and not line.strip().startswith('#')
        )
        try:
            exec(clean_code, namespace)
            expected_df = namespace.get('result')
            if expected_df is None:
                return ("Error: Expected dataframe not produced", None)
            if generated_output is None:
                return ("Error: Generated output is None", None)
            # Compare DataFrames
            return ("Correct ✅" if expected_df.equals(generated_output) else "Incorrect ❌",
                    generated_output)
        except Exception as e:
            return (f"Error: {str(e)}", generated_output)
    
    elif isinstance(generated_output, dict) and 'figure' in generated_output:
        # Handle Plotly figure comparison when output is in dict format
        try:
            namespace = {
                'df': df,
                'pd': pd,
                'np': np,
                'result': None,
                'px': px,
                'go': go
            }
            
            exec(expected_code, namespace)
            expected_output = namespace.get('result')
            
            if expected_output is None:
                return ("Error: Expected figure not produced", None)
            if generated_output is None:
                return ("Error: Generated figure is None", None)

            # Extract figure objects for comparison
            generated_fig = generated_output['figure']
            expected_fig = expected_output.get('figure') if isinstance(expected_output, dict) else expected_output

            # Compare essential figure attributes
            is_matching = (
                generated_fig.layout.title.text == expected_fig.layout.title.text and
                generated_fig.data[0].type == expected_fig.data[0].type and
                len(generated_fig.data) == len(expected_fig.data) and
                all(
                    len(t1.x) == len(t2.x) and len(t1.y) == len(t2.y)
                    for t1, t2 in zip(generated_fig.data, expected_fig.data)
                )
            )
            
            # Return just the figure for display
            return ("Correct ✅" if is_matching else "Incorrect ❌", generated_output)
            
        except Exception as e:
            print(f"Error comparing figures: {str(e)}")
            return (f"Error comparing figures: {str(e)}", generated_output.get('figure'))
    
    else:
        print(f"Unsupported output type: {type(generated_output)}")
        return ("Unsupported output format", generated_output)

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
        Return ONLY THE BELOW JSON response:
        {{
            "message": "Correct ✅" or "Incorrect ❌",
            "reason": "Explanation of differences"
        }}
    """

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,      
            "top_k": 40,      
            "max_output_tokens": 1024
        },
        safety_settings={"HARM_CATEGORY_DANGEROUS": "BLOCK_NONE"}
    )

    if not response.text:
        return {
            "message": "Error ❌",
            "reason": "Gemini AI returned an empty response."
        }

    # Clean and parse the response
    try:
        # Remove any leading/trailing whitespace and markdown formatting
        cleaned_text = response.text.strip()
        
        # If response is wrapped in ```json ... ```, extract just the JSON part
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:].strip()
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()
            
        # Remove any potential markdown formatting
        cleaned_text = cleaned_text.replace("```", "").strip()
        
        # Parse the cleaned JSON
        result = json.loads(cleaned_text)
        
        # Validate required fields
        if not all(key in result for key in ["message", "reason"]):
            raise ValueError("Missing required fields in JSON response")
            
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}\nRaw Response: {response.text}")
        return {
            "message": "Error ❌",
            "reason": "Failed to parse Gemini AI response as JSON"
        }
    except Exception as e:
        print(f"Unexpected Error: {str(e)}\nRaw Response: {response.text}")
        return {
            "message": "Error ❌",
            "reason": f"Error processing Gemini AI response: {str(e)}"
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

def is_valid_logic(generated_code: str, 
                   expected_code: str = None, 
                   expected_output: str = "{}", 
                   generated_output: str = None, 
                   df: pd.DataFrame = None) -> dict:
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


        # 3.3 Output validation using validate_output
        out_val, actual_output = validate_output(expected_output, generated_output, expected_code, generated_code, df)
        results["output_validation"] = out_val
        results["actual_output"] = actual_output

        # 4. Determine status and suggestions
        if ai_validation.get("message", "").startswith("Incorrect"):
            results["status"] = "Invalid ❌"
            results["suggestions"].append(ai_validation.get("reason", "Check code logic"))
        
        # Add similarity-based suggestions
        if overall_similarity < 0.6:  # Less than 70% similar
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
                },
                "output_validation": results["output_validation"],
                "actual_output": results["actual_output"]

            },
            "suggestions": results["suggestions"] if results["suggestions"] else ["Code logic appears correct"]
        }
    except Exception as e:
        return {
            "status": "Error ❌",
            "message": f"Analysis failed: {str(e)}",
            "error": True
        }