import streamlit as st
import pandas as pd
import numpy as np
from utils.code_generator import generate_pandas_code
from LLMAnalyser.config import AVAILABLE_MODULES
from styles.main import get_css
import json

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "df" not in st.session_state:
        st.session_state.df = None
    if "active_modules" not in st.session_state:
        st.session_state.active_modules = []
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = None
    if "dragging" not in st.session_state:
        st.session_state.dragging = None

def init_test_cases():
    """Initialize test cases in session state if not present"""
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = [{
            "query": "",
            "expected_code": "",
            "expected_output": ""
        }]

def render_test_cases():
    """Render test cases input section"""
    with st.expander("Test Cases", expanded=False):
        st.markdown("### Test Cases Configuration")
        
        # Render each test case
        for idx, test_case in enumerate(st.session_state.test_cases):
            st.markdown(f"###### Test Case {idx + 1}")
            
            # Input fields for test case
            test_case["query"] = st.text_area(
                "Query",
                test_case["query"],
                key=f"query_{idx}",
                height=100
            )
            
            test_case["expected_code"] = st.text_area(
                "Expected Code",
                test_case["expected_code"],
                key=f"expected_code_{idx}",
                height=150
            )
            
            test_case["expected_output"] = st.text_area(
                "Expected Output",
                test_case["expected_output"],
                key=f"expected_output_{idx}",
                height=100
            )
            
            # Remove button for test case
            if len(st.session_state.test_cases) > 1:
                if st.button("Remove Test Case", key=f"remove_test_{idx}"):
                    st.session_state.test_cases.pop(idx)
                    st.rerun()
            
            st.markdown("---")
        
        # Add new test case button
        if st.button("Add Test Case"):
            st.session_state.test_cases.append({
                "query": "",
                "expected_code": "",
                "expected_output": ""
            })
            st.rerun()

def render_module_selection():
    """Render available modules in a grid layout"""
    st.markdown("### Analysis Modules")
    st.markdown("Select modules to analyze your generated code")
    
    # Create a grid layout for modules with smaller width
    cols = st.columns(4)  # Changed from 3 to 4 columns to make modules smaller
    for idx, (name, module) in enumerate(AVAILABLE_MODULES.items()):
        with cols[idx % 4]:  # Changed from 3 to 4
            # Create a module card with custom styling and smaller size
            st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, {module['color']}22, {module['color']}11);
                    border: 1px solid {module['color']};
                    border-radius: 8px;
                    padding: 10px;
                    margin: 4px 0;
                    cursor: pointer;
                    transition: all 0.3s;
                    position: relative;
                    font-size: 0.9em;
                ">
                    <div style="font-size: 20px; margin-bottom: 4px;">{module['icon']}</div>
                    <h4 style="margin: 0; color: {module['color']}; font-size: 0.95em;">{name}</h4>
                    <p style="font-size: 0.8em; margin: 3px 0;">{module['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Add module button
            if module["id"] not in [m["id"] for m in st.session_state.active_modules]:
                if st.button("Add", key=f"add_{module['id']}", use_container_width=True):
                    st.session_state.active_modules.append({
                        "id": module["id"],
                        "name": name,
                        "icon": module["icon"],
                        "color": module["color"]
                    })
                    st.rerun()

def render_active_modules():
    """Render active modules pipeline vertically"""
    if not st.session_state.active_modules:
        return

    st.markdown("### Analysis Pipeline")
    
    # Create container for vertical layout
    for idx, module in enumerate(st.session_state.active_modules):
        # Module container with updated styling
        col1, col2 = st.columns([0.92, 0.08])  # Adjusted column ratio
        with col1:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, {module['color']}22, {module['color']}11);
                    border: 1px solid {module['color']};
                    border-radius: 10px;
                    padding: 10px;
                    display: flex;
                    align-items: center;
                ">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 18px;">{module['icon']}</span>
                        <span style="color: {module['color']}; font-weight: bold; margin-left: 10px;">{module['name']}</span>
                    </div>
                
            """, unsafe_allow_html=True)
        
        with col2:



            # Hidden button for actual functionality
            if st.button("x", key=f"remove_{idx}", help="Remove module", 
                        use_container_width=True):
                remove_module(idx)

            st.markdown("</div></div>", unsafe_allow_html=True)

           
        
        # Add arrow between modules
        if idx < len(st.session_state.active_modules) - 1:
            st.markdown("""
                <div style="
                    text-align: center;
                    margin: 8px 0;
                    color: #666;
                ">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 5v14M6 13l6 6 6-6" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            """, unsafe_allow_html=True)
        
        # Run analysis if code is generated
        if st.session_state.generated_code:
            try:
                module_path = f"LLMAnalyser.{module['id']}_analyser"
                module_obj = __import__(module_path, fromlist=['analyze'])
                analysis_result = module_obj.analyze(st.session_state.generated_code)
                
                with st.expander(f"View Analysis", expanded=True):
                    st.markdown(analysis_result)
            except Exception as e:
                st.error(f"Error in {module['name']}: {str(e)}")



def remove_module(index):
    """Remove module from active modules"""
    if 0 <= index < len(st.session_state.active_modules):
        st.session_state.active_modules.pop(index)
        st.rerun()
def main():
    st.set_page_config(
        page_title="Code Analyzer",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(get_css(), unsafe_allow_html=True)
    init_session_state()
    init_test_cases()

    st.title("Code Analysis Pipeline")
    st.markdown("Generate and analyze code through customizable analysis modules")

    # Main content area with gap
    col1, _, col2 = st.columns([2, 0.2, 3])  # Added gap column

    with col1:
        # File upload section with clean styling
        st.markdown("""<h3 style="color: #E0E0E0; margin: 0;">📁 Upload Data""", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Select CSV file", type="csv")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            
            # Clean data preview
            st.markdown("### Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Clean dataset info
            st.markdown("""
                <div style="
                    background: #1E1E1E;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 16px 0;
                ">
                    <h4 style="color: #E0E0E0; margin: 0 0 12px 0;">Dataset Information</h4>
                    <table style="width: 100%; color: #E0E0E0;">
                        <tr><td>Rows:</td><td>{:,}</td></tr>
                        <tr><td>Columns:</td><td>{:,}</td></tr>
                        <tr><td>Memory:</td><td>{:.2f} MB</td></tr>
                    </table>
                </div>
            """.format(
                len(df), 
                len(df.columns), 
                df.memory_usage().sum() / 1024 / 1024
            ), unsafe_allow_html=True)
            pass

  
        render_test_cases()    

        with st.expander("Analysis Modules", expanded=False):
            render_module_selection()

    with col2:
        # Query interface with clean design
        if st.session_state.df is not None:
            st.markdown("""
                <div style="
                    background: #1E1E1E;
                    border-radius: 8px;
                    padding: 20px;
                ">
                    <h3 style="color: #E0E0E0; margin: 0;">Query Data</h3>
                </div>
            """, unsafe_allow_html=True)
            
            question = st.text_input("Enter your query")
            
            # if question:
            #     with st.spinner("Generating code..."):
            #         # ... rest of the code generation logic ...

        # Active modules section
        if st.session_state.active_modules:
            render_active_modules()

if __name__ == "__main__":
    main()