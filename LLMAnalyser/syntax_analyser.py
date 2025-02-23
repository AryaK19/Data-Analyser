
def is_valid_compile(code: str) -> bool:

    try:
        result = compile(code, "<string>", "exec") 
        print("The result is",result) # Attempt to compile the code
        explanation = {
            "status": "Valid ✅",
            "message": "The given Python code has correct syntax and can be executed without errors.",
            "suggestion": "Proceed with execution."
        }
    except SyntaxError as e:
        explanation = {
            "status": "Invalid ❌",
            "message": f"Syntax Error: {e.msg} at line {e.lineno}, column {e.offset}.",
            "suggestion": "Check the syntax error message and fix the incorrect part of your code."
        }
        print(f"Syntax Error: {e}")
    
    return explanation