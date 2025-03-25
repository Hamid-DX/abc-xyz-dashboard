import streamlit as st
import pandas as pd
from datetime import datetime

def handle_data_upload():
    """Handle data file upload or use session state data"""
    # Check if data is already in session state
    if "raw_df" in st.session_state and st.session_state["raw_df"] is not None:
        # Option to clear uploaded data
        if st.sidebar.button("Clear Uploaded Data"):
            st.session_state["raw_df"] = None
            st.session_state["upload_time"] = None
            # Also clear transformed data if exists
            if "transformed_data" in st.session_state:
                st.session_state["transformed_data"] = None
            st.rerun()
        
        # Show upload info
        if "upload_time" in st.session_state and st.session_state["upload_time"]:
            st.sidebar.success(f"✅ Using uploaded data from: {st.session_state['upload_time']}")
        else:
            st.sidebar.success("✅ Using uploaded data")
            
        return st.session_state["raw_df"]
    
    # Show upload widget when no data is present
    uploaded_file = st.sidebar.file_uploader("📁 Upload Raw Data", type=["parquet"])
    
    if uploaded_file is not None:
        try:
            # Read the parquet file
            df = pd.read_parquet(uploaded_file)
            
            # Validate that required columns exist
            required_columns = ['DN_DELIVERY_DT', 'DELIVERY_NO', 'COUNTRY', 'TERRITORY', 'ITEM_GROUP', 
                               'INVENTORY', 'CATALOG', 'REVENUE_VAT_EXCL', 'AD_AVG_COST', 
                               'AD_FR_MARGIN', 'AD_FR_MARGIN%']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.sidebar.error(f"⚠️ Required columns missing: {', '.join(missing_columns)}")
                return None
            
            # Ensure date column is in datetime format
            if not pd.api.types.is_datetime64_dtype(df['DN_DELIVERY_DT']):
                try:
                    df['DN_DELIVERY_DT'] = pd.to_datetime(df['DN_DELIVERY_DT'])
                except Exception as e:
                    st.sidebar.error(f"⚠️ Error converting date column: {e}")
                    return None
            
            # Store in session state
            st.session_state["raw_df"] = df
            st.session_state["upload_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Clear any previously transformed data
            if "transformed_data" in st.session_state:
                st.session_state["transformed_data"] = None
                
            st.rerun()
            
            return df
        except Exception as e:
            st.sidebar.error(f"⚠️ Error loading data: {e}")
            return None
    
    # When no data is available
    st.warning("⚠️ Please upload your raw data parquet file using the sidebar uploader.")
    return None

def initialize_data_state():
    """Initialize data state variables"""
    if "raw_df" not in st.session_state:
        st.session_state["raw_df"] = None
    if "upload_time" not in st.session_state:
        st.session_state["upload_time"] = None
    if "transformed_data" not in st.session_state:
        st.session_state["transformed_data"] = None

@st.cache_data
def create_pivot_table(df_territory):
    """Create ABC-XYZ pivot table from filtered data"""
    pivot_df = df_territory.pivot_table(
        index="ABC(REV-MAR)", 
        columns="TERRITORY_XYZ", 
        values="INVENTORY", 
        aggfunc="count", 
        fill_value=0
    )
    
    # Add Row and Column Totals
    pivot_df["Total"] = pivot_df.sum(axis=1)
    pivot_df.loc["Total"] = pivot_df.sum()
    
    return pivot_df.reset_index()

@st.cache_data
def apply_filters(df, abc_value, xyz_value):
    """Apply user-selected filters to data"""
    filtered = df.copy()
    if abc_value != "All":
        filtered = filtered[filtered["ABC(REV-MAR)"] == abc_value]
    if xyz_value != "All":
        filtered = filtered[filtered["TERRITORY_XYZ"] == xyz_value]
    return filtered

@st.cache_data
def create_summary_table(df):
    """Create summary table of inventory details"""
    summary = df.groupby("INVENTORY").agg(
        Total_revenue=("TOTAL_REVENUE", "sum"),
        Avg_Product_Margin=("PRODUCT_MARGIN", "mean")
    ).reset_index()
    
    # Round for better display
    summary["Total_revenue"] = summary["Total_revenue"].round(2)
    summary["Avg_Product_Margin"] = summary["Avg_Product_Margin"].round(3)
    
    return summary