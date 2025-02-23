import streamlit as st
import pandas as pd
import numpy as np
from utils.code_generator import generate_pandas_code

def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "df" not in st.session_state:
        st.session_state.df = None

def render_chat_message(message):
    """Render a single chat message"""
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            if message.get("result") is not None:
                if isinstance(message["result"], pd.DataFrame):
                    st.dataframe(message["result"])
                else:
                    st.write(message["result"])
            
            if message.get("code"):
                with st.expander("🔍 View Generated Code"):
                    st.code(message["code"], language="python")

def main():
    st.set_page_config(
        page_title="LLM Code Generator",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state
    init_session_state()

    # App header
    st.title("🤖 LLM Code Generator")
    st.markdown("Upload your CSV file and generate Python code using natural language!")

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Load the data
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df

            # Display data preview
            st.subheader("📊 Data Preview")
            st.dataframe(df.head())

            # Chat interface
            st.subheader("💬 Ask Questions")
            
            # Display chat history
            for message in st.session_state.messages:
                render_chat_message(message)

            # Chat input
            if question := st.chat_input("What would you like to know about your data?"):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": question
                })

                # Generate code
                with st.spinner("Generating code..."):
                    generated_code = generate_pandas_code(
                        question=question,
                        columns=list(df.columns),
                        context=None
                    )

                    if generated_code:
                        try:
                            # Execute the generated code
                            namespace = {
                                'df': df,
                                'pd': pd,
                                'np': np,
                                'result': None
                            }
                            exec(generated_code, namespace)
                            result = namespace.get('result')

                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "Here's what I found:",
                                "code": generated_code,
                                "result": result
                            })

                            st.rerun()

                        except Exception as e:
                            st.error(f"Error executing code: {str(e)}")

        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
    else:
        st.info("👆 Upload a CSV file to get started!")

if __name__ == "__main__":
    main()