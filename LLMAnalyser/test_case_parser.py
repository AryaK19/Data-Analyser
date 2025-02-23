import json
import streamlit as st

def parse_test_cases_from_json(uploaded_file):
    """
    Parse test cases from an uploaded JSON file and store them in session state
    
    Expected JSON format:
    {
        "test_cases": [
            {
                "query": "...",
                "expected_code": "...",
                "expected_output": "..."
            },
            ...
        ]
    }
    """
    try:
        content = uploaded_file.read()
        data = json.loads(content)
        
        if not isinstance(data, dict) or "test_cases" not in data:
            raise ValueError("JSON must contain a 'test_cases' array")
            
        test_cases = data["test_cases"]
        
        # Validate test cases format
        required_fields = ["query", "expected_code", "expected_output"]
        for test_case in test_cases:
            if not all(field in test_case for field in required_fields):
                raise ValueError("Each test case must contain query, expected_code, and expected_output")
        
        # Update session state
        st.session_state.test_cases = test_cases
        return True, "Test cases loaded successfully"
        
    except json.JSONDecodeError:
        return False, "Invalid JSON format"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error processing file: {str(e)}"