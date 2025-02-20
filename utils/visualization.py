import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def create_plot(plot_type, data, x=None, y=None, title=None, kind='line', figsize=(10, 6)):
    """Create various types of plots based on the input parameters."""
    
    if plot_type == 'pie':
        # Handle value_counts() for pie charts
        if isinstance(data, pd.Series):
            plot_data = data.reset_index()
            plot_data.columns = ['category', 'count']  # Explicit column naming
        else:
            value_counts = data[x].value_counts()
            plot_data = pd.DataFrame({
                'category': value_counts.index,
                'count': value_counts.values
            })
        
        fig = px.pie(
            plot_data,
            values='count',
            names='category',
            title=title
        )
        
        return {
            "figure": fig,
            "data": plot_data
        }
    
    elif plot_type == 'bar':
        if y:
            fig = px.bar(data, x=x, y=y, title=title or f'{y} by {x}')
            summary_data = data.groupby(x)[y].mean().reset_index()
        else:
            value_counts = data[x].value_counts()
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=title or f'Distribution of {x}'
            )
            summary_data = value_counts.reset_index().rename(columns={'index': x, x: 'count'})
        
        return {
            'figure': fig,
            'data': summary_data
        }
    
    elif plot_type == 'scatter':
        fig = px.scatter(data, x=x, y=y, title=title or f'{y} vs {x}')
        return {
            'figure': fig,
            'data': data[[x, y]].describe()
        }
    
    elif plot_type == 'line':
        fig = px.line(data, x=x, y=y, title=title or f'{y} over {x}')
        return {
            'figure': fig,
            'data': data[[x, y]].head(10)
        }
    
    elif plot_type == 'box':
        fig = px.box(data, x=x, y=y, title=title or f'Box Plot of {y} by {x}')
        return {
            'figure': fig,
            'data': data.groupby(x)[y].describe().reset_index()
        }
    
    elif plot_type == 'histogram':
        plt.hist(data[x], bins=30)
        plt.title(title or f'Distribution of {x}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, facecolor='#0e1117')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'figure': image_base64,
            'data': data[x].describe()
        }
    
    elif plot_type == 'heatmap':
        if isinstance(data, (pd.DataFrame, np.ndarray)):
            sns.heatmap(data, annot=True, cmap='coolwarm')
        else:
            sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
        plt.title(title or 'Correlation Heatmap')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, facecolor='#0e1117')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'figure': image_base64,
            'data': data.corr()
        }
    
    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")

def get_numeric_columns(df):
    """Get list of numeric columns from dataframe."""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df):
    """Get list of categorical columns from dataframe."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def suggest_plots(df):
    """Suggest suitable plots based on data types."""
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    suggestions = []
    
    if len(numeric_cols) >= 2:
        suggestions.append({
            'type': 'scatter',
            'description': f"Create a scatter plot between {numeric_cols[0]} and {numeric_cols[1]}",
            'x': numeric_cols[0],
            'y': numeric_cols[1]
        })
        
        suggestions.append({
            'type': 'line',
            'description': f"Show trend line for {numeric_cols[0]}",
            'x': df.index.name or 'index',
            'y': numeric_cols[0]
        })
    
    if len(numeric_cols) > 0:
        suggestions.append({
            'type': 'histogram',
            'description': f"Show distribution of {numeric_cols[0]}",
            'x': numeric_cols[0]
        })
        
        suggestions.append({
            'type': 'box',
            'description': f"Show boxplot for {numeric_cols[0]}",
            'x': numeric_cols[0]
        })
    
    if len(categorical_cols) > 0:
        suggestions.append({
            'type': 'bar',
            'description': f"Show counts for {categorical_cols[0]}",
            'x': categorical_cols[0]
        })
        
        suggestions.append({
            'type': 'pie',
            'description': f"Show percentage distribution of {categorical_cols[0]}",
            'x': categorical_cols[0]
        })
    
    if len(numeric_cols) > 3:
        suggestions.append({
            'type': 'heatmap',
            'description': "Show correlation heatmap for numeric columns"
        })
    
    return suggestions
