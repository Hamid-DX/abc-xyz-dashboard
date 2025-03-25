import streamlit as st
import pandas as pd

def validate_data(df, required_columns):
    """Validate that DataFrame contains required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"⚠️ Required columns missing from data: {', '.join(missing_columns)}")
        return False
    
    return True

def filter_by_territory(df, territory):
    """Filter DataFrame to show only data for selected territory"""
    return df[df["TERRITORY"] == territory]

def initialize_page():
    """Initialize page configuration"""
    st.set_page_config(
        page_title="ABC-XYZ Analysis Dashboard",
        page_icon="📊",
        layout="wide",
    )
    
def check_parquet_file(uploaded_file):
    """Check if the uploaded file is a valid parquet file"""
    try:
        # Try to read the first few rows
        df = pd.read_parquet(uploaded_file)
        # If it succeeds and returns a DataFrame, it's likely a valid parquet file
        return True, df
    except Exception as e:
        # If an error occurs, it's not a valid parquet file
        return False, str(e)