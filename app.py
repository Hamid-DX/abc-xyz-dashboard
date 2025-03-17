import streamlit as st

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

# Load data from file upload
df = handle_data_upload()

# Stop execution if no data is available
if df is None:
    st.stop()

# ===================================
# ✅ Territory Selection
# ===================================
if not validate_data(df, ["Territory"]):
    st.stop()

territories = df["Territory"].dropna().unique()
if len(territories) == 0:
    st.error("⚠️ No territory data available.")
    st.stop()

selected_territory = st.selectbox("🌍 Select Territory:", options=territories)

# Filter Data Based on Selected Territory
filtered_df_territory = filter_by_territory(df, selected_territory)

# ===================================
# ✅ Pivot Table Creation
# ===================================
required_columns = ["ABC(Rev-Mar)", "Territory_XYZ", "Inventory Name"]
if not validate_data(df, required_columns):
    st.stop()

# Create and display pivot table
pivot_df_reset = create_pivot_table(filtered_df_territory)
display_pivot_table(pivot_df_reset)

# ===================================
# ✅ Filters
# ===================================
st.subheader("🔎 Filter Data")

abc_values = sorted(filtered_df_territory["ABC(Rev-Mar)"].dropna().unique())
selected_abc = st.selectbox("📌 Select ABC(Rev-Mar) Segment:", options=["All"] + abc_values, index=0)

territory_xyz_values = sorted(filtered_df_territory["Territory_XYZ"].dropna().unique())
selected_territory_xyz = st.selectbox("📍 Select Territory_XYZ:", options=["All"] + territory_xyz_values, index=0)

# Apply filters
filtered_df = apply_filters(filtered_df_territory, selected_abc, selected_territory_xyz)

# ===================================
# ✅ Revenue Calculation
# ===================================
if not validate_data(df, ["Total_revenue"]):
    st.stop()

# Calculate metrics
overall_revenue = filtered_df_territory["Total_revenue"].sum() if not filtered_df_territory.empty else 0
segment_revenue = filtered_df["Total_revenue"].sum() if not filtered_df.empty else 0
revenue_share = (segment_revenue / overall_revenue * 100) if overall_revenue > 0 else 0

# Display Revenue Metrics
display_revenue_metrics(overall_revenue, segment_revenue, revenue_share)

# ===================================
# ✅ Inventory Details Table
# ===================================
st.subheader("📦 Inventory Details")

if not filtered_df.empty and "Product_Margin" in filtered_df.columns:
    summary_table = create_summary_table(filtered_df)
    display_summary_table(summary_table)
else:
    st.warning("⚠️ No data available for the selected filters or missing Product_Margin column.")

# ===================================
# ✅ Revenue Bar Chart
# ===================================
st.subheader("📈 Total Revenue Distribution")

if not filtered_df.empty:
    fig = create_bar_chart(filtered_df)
    st.plotly_chart(fig)
else:
    st.warning("⚠️ No data available for the selected filters to display the chart.")