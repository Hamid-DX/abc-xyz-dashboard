import streamlit as st

def validate_data(df, required_columns):
    """Validate that DataFrame contains required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"⚠️ Required columns missing from data: {', '.join(missing_columns)}")
        return False
    
    return True

def filter_by_territory(df, territory):
    """Filter DataFrame to show only data for selected territory"""
    return df[df["Territory"] == territory]

def initialize_page():
    """Initialize page configuration"""
    st.set_page_config(
        page_title="ABC-XYZ Analysis Dashboard",
        page_icon="📊",
        layout="wide",
    )