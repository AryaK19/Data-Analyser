import google.generativeai as genai
import json
import os
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# Set your Gemini API key
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
    model = genai.GenerativeModel("gemini-flash-2.0")
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
