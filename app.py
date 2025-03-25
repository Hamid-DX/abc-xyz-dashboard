import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import from our modules
from utils import initialize_page, validate_data, filter_by_territory
from authentication import initialize_auth_state, check_authentication, logout
from data_handler import (
    initialize_data_state, handle_data_upload, create_pivot_table, 
    apply_filters, create_summary_table
)
from visualizations import (
    display_pivot_table, display_revenue_metrics, 
    display_summary_table, create_bar_chart
)
from transformer import abc_analysis, xyz_analysis, merge_abc_xyz

# Initialize the app
initialize_page()

# Initialize session state
initialize_auth_state()
initialize_data_state()

# Check authentication
if not check_authentication():
    st.stop()

# Show welcome and logout in sidebar
st.sidebar.success(f"Welcome, {st.session_state.get('display_name', st.session_state['username'])}! 🎉")
logout()

# ===================================
# ✅ Main Dashboard
# ===================================
st.title("📊 ABC-XYZ Analysis Dashboard")

# Load raw data from file upload
raw_df = handle_data_upload()

# Stop execution if no data is available
if raw_df is None:
    st.stop()

# ===================================
# ✅ Data Preprocessing
# ===================================
st.subheader("🔄 Data Preprocessing")

# Validate required columns for raw data
required_raw_columns = ['DN_DELIVERY_DT', 'DELIVERY_NO', 'COUNTRY', 'TERRITORY', 'ITEM_GROUP', 
                         'INVENTORY', 'CATALOG', 'REVENUE_VAT_EXCL', 'AD_AVG_COST', 
                         'AD_FR_MARGIN', 'AD_FR_MARGIN%']

if not validate_data(raw_df, required_raw_columns):
    st.error("⚠️ Raw data is missing required columns.")
    st.stop()

# Ensure DN_DELIVERY_DT is in datetime format
try:
    if not pd.api.types.is_datetime64_dtype(raw_df['DN_DELIVERY_DT']):
        raw_df['DN_DELIVERY_DT'] = pd.to_datetime(raw_df['DN_DELIVERY_DT'])
except Exception as e:
    st.error(f"⚠️ Error converting date column: {e}")
    st.stop()

# Date range filter
min_date = raw_df['DN_DELIVERY_DT'].min().date()
max_date = raw_df['DN_DELIVERY_DT'].max().date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Convert to datetime for filtering
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Filter data by date range
date_filtered_df = raw_df[(raw_df['DN_DELIVERY_DT'] >= start_datetime) & 
                          (raw_df['DN_DELIVERY_DT'] <= end_datetime)]

# Display preview of filtered data
with st.expander("Preview Filtered Raw Data"):
    st.dataframe(date_filtered_df.head(5))

st.info(f"🔍 Filtered data contains {date_filtered_df.shape[0]} records from {start_date} to {end_date}")

# ===================================
# ✅ Transform Data
# ===================================
analyze_button = st.button("🔄 Analyze Data", type="primary")

if analyze_button or ("transformed_data" in st.session_state and st.session_state["transformed_data"] is not None):
    with st.spinner("Transforming data..."):
        if analyze_button or "transformed_data" not in st.session_state:
            # Run ABC analysis
            territory_abc_df = abc_analysis(date_filtered_df)
            
            # Run XYZ analysis
            xyz_df = xyz_analysis(date_filtered_df)
            
            # Merge ABC-XYZ results
            transformed_df = merge_abc_xyz(territory_abc_df, xyz_df)
            
            # Store transformed data in session state
            st.session_state["transformed_data"] = transformed_df
        else:
            # Use already transformed data
            transformed_df = st.session_state["transformed_data"]
    
    st.success("✅ Data transformation complete!")
    
    # Display preview of transformed data
    with st.expander("Preview Transformed Data"):
        st.dataframe(transformed_df.head(5))
    
    # ===================================
    # ✅ Territory Selection
    # ===================================
    territories = transformed_df["TERRITORY"].dropna().unique()
    if len(territories) == 0:
        st.error("⚠️ No territory data available.")
        st.stop()

    selected_territory = st.selectbox("🌍 Select Territory:", options=territories)

    # Filter Data Based on Selected Territory
    filtered_df_territory = filter_by_territory(transformed_df, selected_territory)

    # ===================================
    # ✅ Pivot Table Creation
    # ===================================
    required_columns = ["ABC(REV-MAR)", "TERRITORY_XYZ", "INVENTORY"]
    if not validate_data(transformed_df, required_columns):
        st.stop()

    # Create and display pivot table
    pivot_df_reset = create_pivot_table(filtered_df_territory)
    display_pivot_table(pivot_df_reset)

    # ===================================
    # ✅ Filters
    # ===================================
    st.subheader("🔎 Filter Data")

    abc_values = sorted(filtered_df_territory["ABC(REV-MAR)"].dropna().unique())
    selected_abc = st.selectbox("📌 Select ABC(REV-MAR) Segment:", options=["All"] + abc_values, index=0)

    territory_xyz_values = sorted(filtered_df_territory["TERRITORY_XYZ"].dropna().unique())
    selected_territory_xyz = st.selectbox("📍 Select TERRITORY_XYZ:", options=["All"] + territory_xyz_values, index=0)

    # Apply filters
    filtered_df = apply_filters(filtered_df_territory, selected_abc, selected_territory_xyz)

    # ===================================
    # ✅ Revenue Calculation
    # ===================================
    if not validate_data(transformed_df, ["TOTAL_REVENUE"]):
        st.stop()

    # Calculate metrics
    overall_revenue = filtered_df_territory["TOTAL_REVENUE"].sum() if not filtered_df_territory.empty else 0
    segment_revenue = filtered_df["TOTAL_REVENUE"].sum() if not filtered_df.empty else 0
    revenue_share = (segment_revenue / overall_revenue * 100) if overall_revenue > 0 else 0

    # Display Revenue Metrics
    display_revenue_metrics(overall_revenue, segment_revenue, revenue_share)

    # ===================================
    # ✅ Inventory Details Table
    # ===================================
    st.subheader("📦 Inventory Details")

    if not filtered_df.empty and "PRODUCT_MARGIN" in filtered_df.columns:
        summary_table = create_summary_table(filtered_df)
        display_summary_table(summary_table)
    else:
        st.warning("⚠️ No data available for the selected filters or missing PRODUCT_MARGIN column.")

    # ===================================
    # ✅ Revenue Bar Chart
    # ===================================
    st.subheader("📈 Total Revenue Distribution")

    if not filtered_df.empty:
        fig = create_bar_chart(filtered_df)
        st.plotly_chart(fig)
    else:
        st.warning("⚠️ No data available for the selected filters to display the chart.")
else:
    st.info("👆 Please click the 'Analyze Data' button to transform and analyze the filtered data.")