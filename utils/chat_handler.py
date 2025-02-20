import streamlit as st
from typing import List, Dict
import time

def init_chat_history():
    """Initialize chat history in session state if not present."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "context" not in st.session_state:
        st.session_state.context = {
            "last_operation": None,
            "last_columns_used": [],
            "data_insights": {}
        }

def add_message(role: str, content: str, code: str = None, result: str = None):
    """Add a message to the chat history."""
    message = {
        "role": role,
        "content": content,
        "timestamp": time.time(),
        "code": code,
        "result": result
    }
    st.session_state.messages.append(message)

def update_context(operation: str = None, columns: List[str] = None, insight: Dict = None):
    """Update the conversation context."""
    if operation:
        st.session_state.context["last_operation"] = operation
    if columns:
        st.session_state.context["last_columns_used"] = columns
    if insight:
        st.session_state.context["data_insights"].update(insight)

def get_chat_context():
    """Get the current chat context as a string."""
    context = st.session_state.context
    last_messages = st.session_state.messages[-3:] if len(st.session_state.messages) > 0 else []
    
    context_str = "Previous context:\n"
    
    if context["last_operation"]:
        context_str += f"Last operation: {context['last_operation']}\n"
    
    if context["last_columns_used"]:
        context_str += f"Last used columns: {', '.join(context['last_columns_used'])}\n"
    
    if last_messages:
        context_str += "\nRecent conversation:\n"
        for msg in last_messages:
            if msg["role"] == "user":
                context_str += f"User asked: {msg['content']}\n"
            else:
                if msg["code"]:
                    context_str += f"Assistant generated code: {msg['code']}\n"
    
    return context_str

def render_chat_message(message: Dict):
    """Render a single chat message."""
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"You: {message['content']}")
        else:
            if message.get("result") is not None :
                if isinstance(message["result"], dict) and "figure" in message["result"]:
                    # Display the figure
                    fig = message["result"]["figure"]
                    if isinstance(fig, str):  # Base64 encoded image
                        st.markdown(f"<img src='data:image/png;base64,{fig}'/>", unsafe_allow_html=True)
                    else:  # Plotly figure
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Display the data if available
                    if "data" in message["result"]:
                        st.markdown("**Data Summary:**")
                        st.dataframe(message["result"]["data"], use_container_width=True)
                
                # Handle string results
                elif isinstance(message["result"], str):
                    st.markdown(message["result"])
                
                # Handle DataFrame results
                elif str(type(message["result"])).startswith("<class 'pandas"):
                    st.markdown("**Data Preview:**")
                    st.dataframe(message["result"], use_container_width=True)
                
                # Handle other types of results
                else:
                    st.write(message["result"])
            else:
                st.markdown(message["content"])
        
        if message.get("code"):
            with st.expander("🔍 View Code"):
                st.code(message["code"], language="python")

def render_chat_interface():
    """Render the chat interface with message history."""
    # Create a container for chat messages
    chat_container = st.container()
    
    # Display messages in the container
    with chat_container:
       
        for message in st.session_state.messages:
            render_chat_message(message)

        
