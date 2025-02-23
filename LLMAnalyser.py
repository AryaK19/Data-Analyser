import streamlit as st
import pandas as pd
import numpy as np
from utils.code_generator import generate_pandas_code
from LLMAnalyser.config import AVAILABLE_MODULES
from LLMAnalyser.test_case_parser import parse_test_cases_from_json
from LLMAnalyser.syntax_analyser import is_valid_compile
from LLMAnalyser.logical_analyser import is_valid_logic
from LLMAnalyser.efficiency_analyser import is_efficient
import time
from styles.main import get_css
import json

from LLMAnalyser.PDFGenerator import generate_pdf_report
import base64

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
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}

def init_test_cases():
    """Initialize test cases in session state if not present"""
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = [{
            "query": "",
            "expected_code": "",
            "expected_output": ""
        }]

def get_pdf_download_link(pdf_path):
    """Generate a download link for the PDF file"""
    with open(pdf_path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        filename = os.path.basename(pdf_path)
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download PDF Report</a>'


def run_test_cases():
    """Run all test cases and save results"""
    if not st.session_state.df is not None:
        st.error("Please upload a CSV file first")
        return

    results = []
    st.session_state.analysis_results = {}

    for idx, test_case in enumerate(st.session_state.test_cases):
        test_id = f"test_{idx}"
        st.session_state.analysis_results[test_id] = {}
        
        with st.spinner(f"Processing query: {test_case['query']}"):
            try:
                # Generate code from query
                generated_code = generate_pandas_code(
                    test_case['query'], 
                    st.session_state.df,
                    context={"df": st.session_state.df}
                )
                try:
                
                    if generated_code:
                        namespace = {
                            'df': st.session_state.df,
                            'pd': pd,
                            'np': np,
                            'result': None
                        }
                        
                        clean_code = '\n'.join(
                            line for line in generated_code.split('\n')
                            if line.strip() and not line.strip().startswith('#')
                        )
                        exec(clean_code, namespace)
                        actual_output = namespace.get('result')

                        
                        # Run each active module's analysis
                        for module in st.session_state.active_modules:
                            with st.spinner(f"Running {module['name']} analysis..."):
                                try:
                                    if module['id'] == 'syntax':
                                        analysis_result = is_valid_compile(generated_code,test_case["expected_code"])
                                        st.session_state.analysis_results[test_id][module['id']] = {
                                            'name': module['name'],
                                            'result': analysis_result,
                                            'timestamp': time.time()
                                        }
                                        
                                        # If syntax check fails, stop further analysis
                                        if analysis_result['status'] == 'Invalid ❌':
                                            results.append({
                                                "query": test_case["query"],
                                                "expected_code": test_case["expected_code"],
                                                "generated_code": generated_code,
                                                "expected_output": test_case["expected_output"],
                                                "actual_output": "Syntax validation failed",
                                                "status": "error",
                                                "analysis_results": {
                                                    'syntax': {
                                                        'name': module['name'],
                                                        'result': analysis_result,
                                                        'timestamp': time.time()
                                                    }
                                                }
                                            })
                                            break  # Skip other modules
                                        
                                    elif module['id'] == 'logical':
                                        # Only proceed if syntax check passed
                                        if 'syntax' in st.session_state.analysis_results[test_id] and \
                                        st.session_state.analysis_results[test_id]['syntax']['result']['status'] == 'Valid ✅':
                                            analysis_result = is_valid_logic(
                                                generated_code,
                                                test_case["expected_code"] if test_case["expected_code"].strip() else None,
                                                test_case["expected_output"],
                                                actual_output,
                                                st.session_state.df
                                            )
                                            st.session_state.analysis_results[test_id][module['id']] = {
                                                'name': module['name'],
                                                'result': analysis_result,
                                                'timestamp': time.time()
                                            }
                                        
                                    elif module['id'] == 'efficiency':
                                        # Only proceed if syntax check passed
                                        if 'syntax' in st.session_state.analysis_results[test_id] and \
                                        st.session_state.analysis_results[test_id]['syntax']['result']['status'] == 'Valid ✅':
                                            analysis_result = is_efficient(
                                                generated_code,
                                                test_case["expected_code"] if test_case["expected_code"].strip() else None,
                                                st.session_state.df
                                            )
                                            st.session_state.analysis_results[test_id][module['id']] = {
                                                'name': module['name'],
                                                'result': analysis_result,
                                                'timestamp': time.time()
                                            }
                                            
                                except Exception as e:
                                    st.session_state.analysis_results[test_id][module['id']] = {
                                        'name': module['name'],
                                        'error': str(e),
                                        'timestamp': time.time()
                                    }
                    
                    # Execute generated code
                    
                        
                        # Save results
                        results.append({
                            "query": test_case["query"],
                            "expected_code": test_case["expected_code"],
                            "generated_code": generated_code,
                            "expected_output": test_case["expected_output"],
                            "actual_output": actual_output,
                            "status": "success",
                            "analysis_results": st.session_state.analysis_results[test_id]
                        })
                        
                except Exception as e:
                    results.append({
                        "query": test_case["query"],
                        "expected_code": test_case["expected_code"],
                        "generated_code": generated_code,
                        "expected_output": test_case["expected_output"],
                        "actual_output": f"Error: {str(e)}",
                        "status": "error",
                        "analysis_results": st.session_state.analysis_results[test_id]
                    })
                
            except Exception as e:
                results.append({
                    "query": test_case["query"],
                    "expected_code": test_case["expected_code"],
                    "generated_code": "Failed to generate code",
                    "expected_output": test_case["expected_output"],
                    "actual_output": f"Error: {str(e)}",
                    "status": "error",
                    "analysis_results": st.session_state.analysis_results[test_id]
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


def calculate_overall_score(analysis_results: dict) -> dict:
    """
    Calculate overall test case score based on all analysis module results,
    with output validation as a critical factor
    """


    if 'syntax' not in analysis_results or \
       analysis_results['syntax']['result']['status'] == 'Invalid ❌':
        return {
            "passed": False,
            "score": 0.0,
            "module_scores": {'syntax': 0},
            "grade": "F"
        }
    total_score = 0
    max_score = 0
    
    # Updated weights to include output validation importance
    analysis_weights = {
        'syntax': 0.3,
        'logical': 0.4,
        'efficiency': 0.3, 
    }
    
    module_scores = {}
    
    for module_id, analysis in analysis_results.items():
        if 'error' in analysis:
            module_scores[module_id] = 0
            continue
            
        result = analysis['result']
        weight = analysis_weights.get(module_id, 0)
        max_score += weight * 100
        
        if module_id == 'syntax':
            # Syntax score: Valid = 100, Invalid = 0
            score = 100 if result['status'] == 'Valid ✅' else 0
            module_scores[module_id] = score * weight
            
        elif module_id == 'logical':
            # Get output validation result
            print("ajsdhkajshdjlkasd",result)
            output_validation = result['analysis'].get('output_validation', 'N/A')
            output_score = 100 if output_validation == 'Correct ✅' else 0
            module_scores['output'] = output_score 
            
            # Calculate logical score based on similarity and status
            base_score = float(result['analysis']['similarity_analysis']['overall_similarity'].rstrip('%'))
            status_multiplier = 1.0 if result['status'] == 'Valid ✅' else (
                0.7 if result['status'] == 'Warning ⚠️' else 0.3
            )
            score = base_score * status_multiplier
            module_scores[module_id] = score * weight
            
        elif module_id == 'efficiency':
            # Efficiency score based on comparison results
            score = 100 if result['comparison']['is_efficient'] else (
                50 if len(result['comparison']['notes']) <= 1 else 30
            )
            module_scores[module_id] = score * weight
        
        total_score += module_scores[module_id]
    
    # Add output score to total if present
    if 'output' in module_scores:
        total_score += module_scores['output']
    
    # Calculate final percentage
    final_score = (total_score / max_score * 100) if max_score > 0 else 0

    if final_score >100:
        final_score = 100
    
    # Determine if passed based on both final score and output validation
    passed = final_score >= 70 and module_scores.get('output', 0) > 0
    
    return {
        "passed": passed,  # Must have both good overall score AND correct output
        "score": round(final_score, 2),
        "module_scores": module_scores,
        "grade": get_grade(final_score)
    }

def get_grade(score: float) -> str:
    """Convert numerical score to letter grade"""
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"


def display_output(output, key_prefix=""):
    """Helper function to display different types of outputs with unique keys"""
    if output is None:
        st.write("No output")
        return
        
    if isinstance(output, str):
        st.code(output)
    elif str(type(output)).startswith("<class 'pandas"):
        st.dataframe(output, key=f"{key_prefix}_df")
    elif isinstance(output, dict) and 'figure' in output:
        st.plotly_chart(output['figure'], use_container_width=True, key=f"{key_prefix}_plot")
    else:
        st.write(output)
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
                
                return
            elif not has_modules:
                st.warning("⚠️ Please add at least one analysis module")
                
                return
            

            results = run_test_cases()

            print(results)

            if results:
                # Calculate summary statistics
                total_tests = len(results)
                passed_tests = sum(1 for r in results if (
                    "analysis_results" in r and 
                    calculate_overall_score(r["analysis_results"])["passed"]
                ))
                
                # Create summary box
                summary_color = "#00ff00" if passed_tests == total_tests else "#ff0000"
                st.markdown(f"""
                    <div style="
                        padding: 15px;
                        border-radius: 8px;
                        background-color: {summary_color}11;
                        border: 1px solid {summary_color};
                        text-align: center;
                        margin-bottom: 20px;
                    ">
                        <div style="font-size: 1.4em; font-weight: bold; margin-bottom: 5px;">
                            Test Cases Summary
                        </div>
                        <div style="font-size: 1.2em;">
                            {passed_tests} / {total_tests} Test Cases Passed
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.8;">
                            {round(passed_tests/total_tests * 100)}% Success Rate
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### Download Report")
                if st.button("Generate PDF Report"):
                    
                    with st.spinner("Generating PDF report..."):
                        pdf_path = generate_pdf_report(results)
                        if pdf_path:
                            st.markdown(get_pdf_download_link(pdf_path), unsafe_allow_html=True)
                            st.success("Report generated successfully!")
                        else:
                            st.error("Failed to generate PDF report")
                st.markdown("---")


                st.markdown("### Test Results")
                for idx, result in enumerate(results):
                    with st.expander(f"Test Case {idx + 1}: {result['query']}", expanded=False):
                    
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
                        
                        # Module Analysis Results
                        if "analysis_results" in result:

                            overall_score = calculate_overall_score(result["analysis_results"])
    
                            # Display overall score with appropriate color
                            score_color = "#00ff00" if overall_score["passed"] else "#ff0000"
                            grade_color = {
                                "A": "#00ff00",
                                "B": "#80ff00",
                                "C": "#ffff00",
                                "D": "#ffa500",
                                "F": "#ff0000"
                            }.get(overall_score["grade"], "#ff0000")
                            
                            st.markdown("##### Overall Test Case Results")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                    <div style="
                                        padding: 10px;
                                        border-radius: 5px;
                                        background-color: {score_color}22;
                                        border: 1px solid {score_color};
                                        text-align: center;
                                    ">
                                        <div style="font-size: 1.2em; font-weight: bold;">
                                            {overall_score["score"]}%
                                        </div>
                                        <div>Overall Score</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                    <div style="
                                        padding: 10px;
                                        border-radius: 5px;
                                        background-color: {grade_color}22;
                                        border: 1px solid {grade_color};
                                        text-align: center;
                                    ">
                                        <div style="font-size: 1.2em; font-weight: bold;">
                                            Grade {overall_score["grade"]}
                                        </div>
                                        <div>Performance Grade</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown(f"""
                                    <div style="
                                        padding: 10px;
                                        border-radius: 5px;
                                        background-color: {score_color}22;
                                        border: 1px solid {score_color};
                                        text-align: center;
                                    ">
                                        <div style="font-size: 1.2em; font-weight: bold;">
                                            {"PASSED" if overall_score["passed"] else "FAILED"}
                                        </div>
                                        <div>Test Status</div>
                                    </div>
                                """, unsafe_allow_html=True)

                            st.markdown("##### Module Analysis Results")
                            tabs = st.tabs([analysis['name'] for analysis in result["analysis_results"].values()])
                            
                            for tab, (module_id, analysis) in zip(tabs, result["analysis_results"].items()):
                                with tab:
                                    if "error" in analysis:
                                        st.error(f"Error: {analysis['error']}")



                                    elif module_id == 'syntax':
                                        # Get the result values
                                        status = analysis["result"]["status"]
                                        message = analysis["result"]["message"]
                                        suggestion = analysis["result"]["suggestion"]
                                        
                                        # Determine status color
                                        status_color = "#00ff00" if status == "Valid ✅" else "#ff0000"
                                        
                                        # Display in a clean UI format
                                        st.markdown(f"""
                                            <div style="
                                                padding: 15px;
                                                border-radius: 8px;
                                                background-color: {status_color}11;
                                                border: 1px solid {status_color};
                                                margin-bottom: 15px;
                                            ">
                                                <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 8px;">
                                                    {status}
                                                </div>
                                                <div style="margin-bottom: 5px;">
                                                    {message}
                                                </div>
                                                <div style="font-size: 0.9em; opacity: 0.8;">
                                                    {suggestion}
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)



                                    elif module_id == 'logical':
                                        logical_result = analysis["result"]
                                        
                                        # Display overall status with appropriate color
                                        status_color = "#00ff00" if logical_result["status"] == "Valid ✅" else (
                                            "#ffa500" if logical_result["status"] == "Warning ⚠️" else "#ff0000"
                                        )
                                        st.markdown(f"""
                                            <div style="
                                                padding: 10px;
                                                border-radius: 5px;
                                                border-left: 5px solid {status_color};
                                                background-color: {status_color}11;
                                                margin-bottom: 15px;
                                            ">
                                                <strong>Status:</strong> {logical_result["status"]}
                                            </div>
                                        """, unsafe_allow_html=True)



                                        # Output Validation Results
                                        st.markdown("##### Output Validation")
                                        st.markdown(f"""
                                            <div style="
                                                padding: 10px;
                                                border-radius: 5px;
                                                margin-bottom: 10px;
                                            ">
                                                <strong>Result:</strong> {logical_result["analysis"].get("output_validation", "N/A")}
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # AI Validation Results
                                        st.markdown("##### AI Validation")
                                        ai_validation = logical_result["analysis"]["ai_validation"]
                                        message_color = "#00ff00" if ai_validation["message"].startswith("Correct") else "#ff0000"
                                        st.markdown(f"""
                                            <div style="
                                                padding: 10px;
                                                border-radius: 5px;
                                                background-color: {message_color}11;
                                                margin-bottom: 10px;
                                            ">
                                                <strong>{ai_validation["message"]}</strong><br>
                                                {ai_validation["reason"]}
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Similarity Analysis
                                        st.markdown("##### Similarity Analysis")
                                        similarity = logical_result["analysis"]["similarity_analysis"]
                                        
                                        # Display overall similarity
                                        st.info(f"Overall Similarity: {similarity['overall_similarity']}")
                                        
                                        # Display metrics in columns
                                        metric_cols = st.columns(3)
                                        metrics = similarity["metrics"]
                                        
                                        with metric_cols[0]:
                                            st.metric(
                                                "Levenshtein Distance",
                                                f"{metrics['Levenshtein Distance']:.2f}",
                                                help="Edit distance between codes (lower is better)"
                                            )
                                        
                                        with metric_cols[1]:
                                            st.metric(
                                                "BLEU Score",
                                                f"{metrics['BLEU Score (spaCy)']:.2f}",
                                                help="Text similarity score (higher is better)"
                                            )
                                        
                                        with metric_cols[2]:
                                            st.metric(
                                                "Cosine Similarity",
                                                f"{metrics['Cosine Similarity']:.2f}",
                                                help="Vector similarity (higher is better)"
                                            )
                                        
                                        # Display suggestions
                                        if logical_result["suggestions"]:
                                            st.markdown("##### Suggestions")
                                            for suggestion in logical_result["suggestions"]:
                                                if suggestion == "Code logic appears correct":
                                                    st.success(suggestion)
                                                else:
                                                    st.warning(suggestion)
                                    elif module_id == 'efficiency':
                                        efficiency_result = analysis["result"]
                                        
                    
                                        # Display time complexity
                                        st.markdown("**Time Complexity Analysis:**")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.info(f"Generated Code: {efficiency_result['generated_code']['time_complexity']}")
                                        with col2:
                                            if 'test_code' in efficiency_result:
                                                st.info(f"Expected Code: {efficiency_result['test_code']['time_complexity']}")
                                        
                                        # Display execution metrics
                                        st.markdown("**Performance Metrics:**")
                                        metrics = st.columns(3)
                                        with metrics[0]:
                                            st.metric(
                                                "Operation Count", 
                                                efficiency_result['generated_code']['operation_count']
                                            )
                                        with metrics[1]:
                                            st.metric(
                                                "Execution Time", 
                                                efficiency_result['generated_code']['execution_time']
                                            )
                                        with metrics[2]:
                                            st.metric(
                                                "Memory Usage", 
                                                efficiency_result['generated_code']['memory_usage']
                                            )
                                        
                                        # Display comparison notes
                                        if efficiency_result["comparison"]["notes"]:
                                            st.markdown("**Optimization Notes:**")
                                            for note in efficiency_result["comparison"]["notes"]:
                                                st.warning(note)
                        
                        # Code comparison in tabs
                        st.markdown("##### Code & Output")
                        code_tab1, code_tab2 = st.columns([2, 2])

                        with code_tab1:
                            st.markdown("**Generated Code:**")
                            st.code(result["generated_code"], language="python")
                            st.markdown("**Actual Output:**")
                            if result["expected_output"] != "{}":
                                display_output(str(result["actual_output"]), key_prefix=f"gen_{idx}")
                            else:
                                display_output(result["actual_output"], key_prefix=f"gen_{idx}")

                        with code_tab2:
                            st.markdown("**Expected Code:**")
                            st.code(result["expected_code"], language="python")
                            st.markdown("**Expected Output:**")
                            if result["expected_output"] != "{}":
                                display_output(result["expected_output"], key_prefix=f"exp_{idx}")
                            else:
                                actual_output = logical_result['analysis']['actual_output']
                                display_output(actual_output, key_prefix=f"exp_{idx}")
                        
                    

if __name__ == "__main__":
    main()