def get_css():
    return """
        <style>
        /* Reset default Streamlit padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        .main {
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: 100vh !important;
        }
        /* App container */
        .stApp {
            margin: 0 auto;
            width: 100% !important;
            max-width: 100% !important;
            background-color: #0e1117;
        }
        .column-list-container {
            background-color: #0e1117;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 1rem;
            color: #fafafa;
            height: calc(100vh - 200px);
            display: flex;
            flex-direction: column;
            position: sticky;
            top: 1rem;
        }
        .column-list-header {
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
            font-size: 1.25rem;
            font-weight: 600;
            color: #00a4e4;
        }
        .column-list {
            flex: 1;
            overflow-y: auto;
            padding-right: 10px;
            background-color: #0e1117;
            margin-bottom: 5px;
        }
        .column-list::-webkit-scrollbar {
            width: 6px;
        }
        .column-list::-webkit-scrollbar-track {
            background: #1e1e1e;
            border-radius: 3px;
        }
        .column-list::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 3px;
        }
        .column-list ul {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }
        .column-list li {
            padding: 8px 10px;
            border-bottom: 1px solid #333;
            font-size: 14px;
            color: #a8d4f2;
            transition: all 0.2s ease;
        }
        .column-list li:hover {
            background-color: #1e1e1e;
            color: #00a4e4;
        }
        .column-list li:last-child {
            border-bottom: none;
        }
        .info-box {
            background-color: #0e1117;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 1rem;
            color: #a8d4f2;
        }
        .info-box h4 {
            margin-top: 0;
            color: #00a4e4;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        /* Make dataframes use full width and add spacing */
        .stDataFrame {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
        .dataframe {
            width: 100% !important;
        }
        /* Style markdown elements */
        .stMarkdown p {
            color: #a8d4f2 !important;
            margin-bottom: 0.5rem !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #00a4e4 !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        /* Style tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #0e1117;
            margin-bottom: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #1e1e1e;
            border-radius: 4px 4px 0 0;
            color: #a8d4f2;
            border: 1px solid #333;
            border-bottom: none;
            font-size: 1rem;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0e1117;
            color: #00a4e4;
        }
        /* Style text inputs */
        .stTextInput {
            margin-top: 1rem !important;
            margin-bottom: 1rem !important;
        }
        .stTextInput input {
            background-color: #1e1e1e;
            border: 1px solid #333;
            color: #fafafa;
            padding: 10px 12px;
            font-size: 1rem;
            border-radius: 4px;
        }
        .stTextInput input:focus {
            border-color: #00a4e4;
            box-shadow: 0 0 0 1px #00a4e4;
        }
        /* Style horizontal rule */
        hr {
            margin: 1rem 0 !important;
            border-color: #333 !important;
        }
        /* Style spinners and progress */
        .stSpinner {
            margin: 1rem 0;
        }
        /* Style expander */
        .streamlit-expanderHeader {
            background-color: #1e1e1e !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            margin-top: 1rem !important;
        }
        .streamlit-expanderContent {
            background-color: #0e1117 !important;
            border: 1px solid #333 !important;
            border-top: none !important;
            padding: 0.75rem !important;
        }
        /* Reduce spacing between sections */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        .stHeadingContainer {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
    .chat-message-container {
        height: 600px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
    }
    
    .element-container {
        margin-bottom: 10px;
    }
    
    .stChatMessage {
        margin-bottom: 15px;
    }
        .chat-container {
            background-color: #0e1117;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 1rem;
            color: #fafafa;
            height: calc(100vh - 200px);
            display: flex;
            flex-direction: column;
            position: sticky;
    }
    
        
        </style>
    """
