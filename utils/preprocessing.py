import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def fill_null_values(df, method='mean', columns=None):
    """Fill null values in the DataFrame using specified method."""
    df_copy = df.copy()
    if columns is None:
        columns = df.columns
    
    for col in columns:
        if df[col].dtype.kind in 'iuf':  # numeric columns
            if method == 'mean':
                df_copy[col] = df[col].fillna(df[col].mean())
            elif method == 'median':
                df_copy[col] = df[col].fillna(df[col].median())
            elif method == 'zero':
                df_copy[col] = df[col].fillna(0)
        else:  # non-numeric columns
            df_copy[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
    
    return df_copy

def remove_null_rows(df, threshold=None):
    """Remove rows with null values based on threshold."""
    if threshold is None:
        return df.dropna()
    return df.dropna(thresh=int((1 - threshold) * len(df.columns)))

def normalize_columns(df, method='minmax', columns=None):
    """Normalize specified columns using the given method."""
    df_copy = df.copy()
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    for col in columns:
        if df[col].dtype.kind in 'iuf':  # numeric columns
            if method == 'minmax':
                scaler = MinMaxScaler()
                df_copy[col] = scaler.fit_transform(df[col].values.reshape(-1, 1))
            elif method == 'standard':
                scaler = StandardScaler()
                df_copy[col] = scaler.fit_transform(df[col].values.reshape(-1, 1))
            elif method == 'log':
                df_copy[col] = np.log1p(df[col] - df[col].min() + 1)
    
    return df_copy

def detect_patterns(df):
    """Detect basic patterns in the data."""
    patterns = {
        'missing_percentages': df.isnull().mean() * 100,
        'unique_counts': df.nunique(),
        'data_types': df.dtypes,
        'numeric_correlations': df.select_dtypes(include=[np.number]).corr()
    }
    return patterns
