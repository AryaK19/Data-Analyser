import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import pandas as pd

load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', ''))

def clean_code(code):
    """Clean up the generated code and ensure proper imports."""
    # Remove markdown formatting
    if code.startswith('```python'):
        code = code.replace('```python', '').replace('```', '')
    if code.startswith('Here'):
        code = code.split('\n', 1)[1]
    
    code = code.strip()
    
    # Remove any attempts to read CSV files
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines with read_csv
        if 'read_csv' in line:
            continue
        # Replace direct DataFrame boolean comparisons
        if 'if df ==' in line or 'if df !=' in line:
            continue
        # Add proper DataFrame boolean checks
        if 'if df' in line:
            line = line.replace('if df', 'if df.empty')
        cleaned_lines.append(line)
    
    code = '\n'.join(cleaned_lines)
    
    # Add necessary imports
    imports = []
    if 'create_plot' in code and 'from utils.visualization import create_plot' not in code:
        imports.append('from utils.visualization import create_plot')
    if ('pd.' in code or 'DataFrame' in code) and 'import pandas as pd' not in code:
        imports.append('import pandas as pd')
    if 'np.' in code and 'import numpy as np' not in code:
        imports.append('import numpy as np')
    
    if imports:
        code = '\n'.join(imports) + '\n\n' + code
    
    return code

def generate_pandas_code(question, df, include_viz=True, context=None):
    """Generate pandas code using Google's Gemini API based on user question and available columns."""
    
    columns = list(df.columns)


    viz_hint = """
    For visualization requests:
    - Always include 'from utils.visualization import create_plot' when using create_plot
    - Available plot types: line, scatter, bar, histogram, boxplot, heatmap, pie
    - For pie charts: result = create_plot('pie', data=df, x='column_name', title='Title')
    - For other plots: result = create_plot('plot_type', data=df, x='column1', y='column2', title='Title')
    - The DataFrame 'df' is already loaded and available
    - Always use data=df parameter, not just df
    """
    
    context_info = f"\n{context}" if context else ""
    
    prompt = f"""Your Are a Data Science Analysis and Python Expert. Generate ONLY Python code (no explanations) to analyze this dataset with columns: {', '.join(columns)}
    Question: "{question}"{context_info}
    
    Example responses for visualization:
    1. For pie chart of categories:
    ```python
    from utils.visualization import create_plot
    result = create_plot('pie', data=df, x='column_name', title='Distribution of Categories')
    ```
    
    2. For comparing two columns:
    ```python
    from utils.visualization import create_plot
    result = create_plot('bar', data=df, x='column1', y='column2', title='Comparison')
    ```

    3. for data preprocessing (that is the result is to me a dataframe type), result = df.(any operation) , result variable must have the dataframe type.
    
    CRITICAL RULES:
    1. ALWAYS include required imports at the top (pandas, numpy, create_plot)
    2. The DataFrame 'df' is already loaded - DO NOT use read_csv
    3. Consider the conversation context when generating code
    4. If referring to previous operations, make it clear in variable names
    5. Format numbers with f-strings and commas
    6. NO comments or markdown
    7. Keep code concise
    8. The code should be directly executable - No samples or examples
    9. If user asks general questions , reply with correct general output. (for example - user:"hi how are you", python_code(ouput): result = "am fine how are you ")
    10. THE END RESULTS IF IS A STRING MUST BE FORMATED NICELY .IF RESULT IS A DATAFRAME MUST BE FORMATED AS result = df.(any operation)
    {viz_hint if include_viz else ''}
    """
    
    # Configure generation parameters
    generation_config = GenerationConfig(
        temperature=0.2,  # Lower temperature for more consistent outputs
        top_p=0.7,       # Nucleus sampling parameter
        max_output_tokens=500,  # Maximum length of response
        candidate_count=1  # Number of completion choices to generate
    )
    
    # Generate code using Gemini with configuration
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )

    print(response.text)
    
    # Clean up the generated code
    return clean_code(response.text.strip())
