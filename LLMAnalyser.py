import streamlit as st
import pandas as pd
import numpy as np
from utils.code_generator import generate_pandas_code
from LLMAnalyser.config import AVAILABLE_MODULES
from LLMAnalyser.test_case_parser import parse_test_cases_from_json
import time
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
    if "clear_uploader" not in st.session_state:
        st.session_state.clear_uploader = False

def init_test_cases():
    """Initialize test cases in session state if not present"""
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = [{
            "query": "",
            "expected_code": "",
            "expected_output": ""
        }]

def run_test_cases(has_test_cases, has_modules,uploaded_file ):
    if not has_test_cases or not has_modules:
        return
    """Run all test cases and save results"""
    if not st.session_state.df is not None:
        st.error("Please upload a CSV file first")
        return

    results = []
    for test_case in st.session_state.test_cases:
        with st.spinner(f"Processing query: {test_case['query']}"):
            try:
                # Generate code from query
                generated_code = generate_pandas_code(
                    test_case['query'], 
                    st.session_state.df,
                    context={"df": st.session_state.df}
                )
                
                if generated_code:
                    # Create namespace with required imports
                    namespace = {
                        'df': st.session_state.df,
                        'pd': pd,
                        'np': np,
                        'result': None
                    }
                    
                    # Execute generated code
                    try:
                        clean_code = '\n'.join(
                            line for line in generated_code.split('\n')
                            if line.strip() and not line.strip().startswith('#')
                        )
                        exec(clean_code, namespace)
                        actual_output = str(namespace.get('result'))
                        
                        # Save results
                        results.append({
                            "query": test_case["query"],
                            "expected_code": test_case["expected_code"],
                            "generated_code": generated_code,
                            "expected_output": test_case["expected_output"],
                            "actual_output": actual_output,
                            "status": "success"
                        })
                        
                    except Exception as e:
                        results.append({
                            "query": test_case["query"],
                            "expected_code": test_case["expected_code"],
                            "generated_code": generated_code,
                            "expected_output": test_case["expected_output"],
                            "actual_output": f"Error: {str(e)}",
                            "status": "error"
                        })
                
            except Exception as e:
                results.append({
                    "query": test_case["query"],
                    "expected_code": test_case["expected_code"],
                    "generated_code": "Failed to generate code",
                    "expected_output": test_case["expected_output"],
                    "actual_output": f"Error: {str(e)}",
                    "status": "error"
                })
    
    return results

def render_test_cases():
    """Render test cases input section"""
    
    st.markdown("### Test Cases Configuration")
    # Add JSON upload section
    col1, col2 = st.columns([3, 1])
    with col1:
        # Check if we should clear the uploader
        if st.session_state.get("clear_uploader", False):
            st.session_state.clear_uploader = False
            st.rerun()
            
        uploaded_file = st.file_uploader(
            "Upload test cases from JSON",
            type=["json"],
            key="test_cases_upload"
        )
        
    with col2:
        st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
        if uploaded_file is not None:
            # Initialize message placeholder if not exists
            if "message_timestamp" not in st.session_state:
                st.session_state.message_timestamp = None
            
            success, message = parse_test_cases_from_json(uploaded_file)
            current_time = time.time()
            
            # Show message only if within 2 seconds
            if st.session_state.message_timestamp is None or \
                current_time - st.session_state.message_timestamp < 2:
                if success:
                    st.success(message)
                    # Set flag to clear uploader on next rerun
                    st.session_state.clear_uploader = True
                else:
                    st.error(message)
                # Update timestamp on first show
                if st.session_state.message_timestamp is None:
                    st.session_state.message_timestamp = current_time
                    time.sleep(2)
                    st.rerun()
            else:
                # Reset timestamp after message expires
                st.session_state.message_timestamp = None
    
    # Render each test case
    for idx, test_case in enumerate(st.session_state.test_cases):
        st.markdown(f"###### Test Case {idx + 1}")
        
        # Input fields for test case
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style="
                    padding: 10px 0;
                    color: #E0E0E0;
                    font-size: 0.95em;
                    font-weight: 500;
                ">Query:</div>
            """, unsafe_allow_html=True)
        with col2:
            test_case["query"] = st.text_input(
                "",
                value=test_case["query"],
                key=f"query_{idx}",
                label_visibility="collapsed"
            )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style="
                    padding: 10px 0;
                    color: #E0E0E0;
                    font-size: 0.95em;
                    font-weight: 500;
                ">Expected Code:</div>
            """, unsafe_allow_html=True)
        with col2:
            test_case["expected_code"] = st.text_area(
                "",
                value=test_case["expected_code"],
                key=f"expected_code_{idx}",
                height=80,
                label_visibility="collapsed"
            )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
                <div style="
                    padding: 10px 0;
                    color: #E0E0E0;
                    font-size: 0.95em;
                    font-weight: 500;
                ">Expected Output:</div>
            """, unsafe_allow_html=True)
        with col2:
            test_case["expected_output"] = st.text_input(
                "",
                value=test_case["expected_output"],
                key=f"expected_output_{idx}",
                label_visibility="collapsed"
            )
        
        if len(st.session_state.test_cases) > 1:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Remove", key=f"remove_test_{idx}", use_container_width=True):
                    st.session_state.test_cases.pop(idx)
                    st.rerun()
        
        st.markdown("<hr style='margin: 20px 0; opacity: 0.8;'>", unsafe_allow_html=True)
    
    # Add new test case button with styling
    st.markdown("""
        <div style="display: flex; justify-content: center; margin: 20px 0 10px 0;">
    """, unsafe_allow_html=True)
    if st.button("Add Test Case", use_container_width=True):
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
            with st.expander(f"### Data Preview (Top 5)", expanded=False):
                st.dataframe(df.head())


        with st.expander("Test Cases", expanded=False):
            render_test_cases()    

        with st.expander("Analysis Modules", expanded=False):
            render_module_selection()

    with col2:

        # Active modules section
        if st.session_state.active_modules:
            render_active_modules()
        
        # Container for run test cases button and validations
        st.markdown("""<h3 style="color: #E0E0E0; margin: 0 0 15px 0;">Run Test Cases</h3>""", unsafe_allow_html=True)
        
        # Show validation messages if needed
        has_test_cases = any(test_case["query"].strip() for test_case in st.session_state.test_cases)
        has_modules = len(st.session_state.active_modules) > 0
        
        # Run Test Cases button
        if st.button(
            "🚀 Run All Test Cases", 
            use_container_width=True,
            # disabled=not (has_test_cases and has_modules),
            type="primary"
        ):
            

            if not has_test_cases:
                st.warning("⚠️ Please add at least one test case with a query")
                print("excited with")
                return
            elif not has_modules:
                st.warning("⚠️ Please add at least one analysis module")
                print("excited")
                return
            

            results = run_test_cases(has_test_cases, has_modules,uploaded_file)

            if results:
                st.markdown("### Test Results")
                for idx, result in enumerate(results):
                    with st.expander(f"Test Case {idx + 1}: {result['query']}", expanded=True):
                        # Status indicator
                        status_color = "#00ff00" if result["status"] == "success" else "#ff0000"
                        st.markdown(f"""
                            <div style="
                                padding: 10px;
                                border-radius: 5px;
                                border-left: 5px solid {status_color};
                                background-color: {status_color}11;
                                margin-bottom: 10px;
                            ">
                                Status: {result["status"].upper()}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Code comparison
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("##### Generated Code")
                            st.code(result["generated_code"], language="python")
                            st.markdown("##### Actual Output")
                            st.code(result["actual_output"])
                        with col2:
                            st.markdown("##### Expected Code")
                            st.code(result["expected_code"], language="python")
                            st.markdown("##### Expected Output")
                            st.code(result["expected_output"])

if __name__ == "__main__":
    main()