import google.generativeai as genai
import json
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# Set your Gemini API key
genai.configure(api_key="AIzaSyCeh14GWGwxSk6yw3Cx9I3Nl4dFJ7f29Fw")

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

