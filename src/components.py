import streamlit as st
import pandas as pd
from utils.visualization import suggest_plots, create_plot

def render_column_list(df):
    """Render the available columns list."""
    column_items = '\n'.join([f'<li>{col}</li>' for col in df.columns])
    st.markdown(f"""
        <div class="column-list-container">
            <div class="column-list-header">Available Columns</div>
            <div class="column-list">
                <ul>
                    {column_items}
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_dataset_info(df):
    """Render the dataset information box."""
    st.markdown(f"""
        <div class="info-box">
            <h4>Dataset Info</h4>
            <p>Total rows: {len(df):,}</p>
            <p>Total columns: {len(df.columns)}</p>
            <p>Memory usage: {df.memory_usage().sum() / 1024 / 1024:.2f} MB</p>
        </div>
    """, unsafe_allow_html=True)

def render_dataset_preview(df):
    """Render the dataset preview."""
    st.markdown("### Dataset Preview (Top 5 Rows)")
    st.dataframe(df.head(5), use_container_width=True)

def render_plot_suggestions(df):
    """Render plot suggestions based on data types."""
    suggestions = suggest_plots(df)
    suggestions = False
    if suggestions:
        st.markdown("### Suggested Visualizations")
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion['description'], key=f"viz_{i}"):
                    with st.spinner("Creating visualization..."):
                        try:
                            x = suggestion.get('x')
                            y = suggestion.get('y')
                            plot_type = suggestion['type']
                            
                            image = create_plot(
                                plot_type=plot_type,
                                data=df,
                                x=x,
                                y=y,
                                title=suggestion['description']
                            )
                            
                            st.markdown(f"""
                                <img src="data:image/png;base64,{image}" 
                                style="width: 100%; border-radius: 5px; margin: 10px 0;">
                                """, 
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(f"Error creating visualization: {str(e)}")

def display_result(result):
    """Display the analysis result in appropriate format."""
    st.markdown("### Results")
    
    if isinstance(result, str):
        # Check if result is a base64 encoded image
        if result.startswith('/9j/') or result.startswith('iVBORw0KGgo'):
            st.markdown(f"""
                <img src="data:image/png;base64,{result}" 
                style="width: 100%; border-radius: 5px; margin: 10px 0;">
                """, 
                unsafe_allow_html=True
            )
        else:
            st.info(result)
    elif isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    elif isinstance(result, pd.Series):
        st.write(result.to_frame())
    elif result is not None:
        st.write(result)
    else:
        st.warning("No result was generated. Please try rephrasing your question.")
