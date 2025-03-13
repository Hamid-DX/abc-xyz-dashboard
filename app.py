import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

# Set page configuration at the very beginning
st.set_page_config(
    page_title="ABC-XYZ Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

# ===================================
# ✅ Session State Management
# ===================================
# Initialize session state variables to prevent re-authentication
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# ===================================
# ✅ Authentication Setup
# ===================================
# Function to load config safely
def load_config():
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        st.error("⚠️ Authentication file (config.yaml) is missing. Please add it.")
        st.stop()
    
    try:
        with open(config_path) as file:
            return yaml.load(file, Loader=SafeLoader)
    except Exception as e:
        st.error(f"⚠️ Error loading config: {e}")
        st.stop()

# Load config only once
if "config" not in st.session_state:
    st.session_state["config"] = load_config()

config = st.session_state["config"]

# Create authenticator instance only once
if "authenticator" not in st.session_state:
    try:
        st.session_state["authenticator"] = stauth.Authenticate(
            config["credentials"], 
            config["cookie"]["name"], 
            config["cookie"]["key"], 
            config["cookie"]["expiry_days"],
            config.get("preauthorized", {"emails": []})
        )
    except Exception as e:
        st.error(f"⚠️ Authentication setup error: {e}")
        st.stop()

# Handle authentication
authenticator = st.session_state["authenticator"]

# Only show login if not authenticated
if st.session_state["authentication_status"] != True:
    with st.container():
        st.title("ABC-XYZ Analysis Dashboard Login")
        st.markdown("Please enter your credentials to access the dashboard.")
        
        # Login form
        name, authentication_status, username = authenticator.login("Login", "main")
        
        # Update session state
        st.session_state["authentication_status"] = authentication_status
        st.session_state["name"] = name
        st.session_state["username"] = username
        
        # Handle authentication status
        if authentication_status is False:
            st.error("❌ Incorrect username or password. Please try again.")
        elif authentication_status is None:
            st.warning("⚠️ Please enter your username and password.")
        
        # Stop execution if not authenticated
        if authentication_status is not True:
            st.stop()

# ===================================
# ✅ Main Dashboard (only shown if authenticated)
# ===================================
# Show logout button in sidebar
authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"Welcome, {st.session_state['name']}! 🎉")

# ===================================
# ✅ Data Loading & Validation
# ===================================
@st.cache_data
def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(data_dir, 'full__abc_xyz.csv')
    
    if not os.path.exists(file_path):
        st.error(f"⚠️ Data file missing: `{file_path}`. Please place it in the data directory.")
        st.stop()
    
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        st.stop()

# Main application
st.title("📊 ABC-XYZ Analysis Dashboard")

# Load data with caching
df = load_data()

# ===================================
# ✅ Territory Selection
# ===================================
if "Territory" not in df.columns:
    st.error("⚠️ Missing 'Territory' column in data.")
    st.stop()

territories = df["Territory"].dropna().unique()
if len(territories) == 0:
    st.error("⚠️ No territory data available.")
    st.stop()

selected_territory = st.selectbox("🌍 Select Territory:", options=territories)

# Filter Data Based on Selected Territory
filtered_df_territory = df[df["Territory"] == selected_territory]

# ===================================
# ✅ Pivot Table Creation
# ===================================
required_columns = ["ABC(Rev-Mar)", "Territory_XYZ", "Inventory Name"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"⚠️ Required columns missing from data: {', '.join(missing_columns)}")
    st.stop()

@st.cache_data
def create_pivot_table(df_territory):
    pivot_df = df_territory.pivot_table(
        index="ABC(Rev-Mar)", 
        columns="Territory_XYZ", 
        values="Inventory Name", 
        aggfunc=lambda x: x.nunique(), 
        fill_value=0
    )
    
    # Add Row and Column Totals
    pivot_df["Total"] = pivot_df.sum(axis=1)
    pivot_df.loc["Total"] = pivot_df.sum()
    
    return pivot_df.reset_index()

pivot_df_reset = create_pivot_table(filtered_df_territory)

# Display Pivot Table
st.subheader("📌 ABC-XYZ Matrix Table")

# Customize AgGrid for Better Readability
gb = GridOptionsBuilder.from_dataframe(pivot_df_reset)
gb.configure_grid_options(domLayout='autoHeight')

# Apply styling
grid_options = gb.build()
grid_options["defaultColDef"] = {
    "cellStyle": {"fontSize": "16px", "textAlign": "center"},
    "autoWidth": True,
}

AgGrid(pivot_df_reset, gridOptions=grid_options, enable_enterprise_modules=True)

# ===================================
# ✅ Filters
# ===================================
st.subheader("🔎 Filter Data")

abc_values = sorted(filtered_df_territory["ABC(Rev-Mar)"].dropna().unique())
selected_abc = st.selectbox("📌 Select ABC(Rev-Mar) Segment:", options=["All"] + abc_values, index=0)

territory_xyz_values = sorted(filtered_df_territory["Territory_XYZ"].dropna().unique())
selected_territory_xyz = st.selectbox("📍 Select Territory_XYZ:", options=["All"] + territory_xyz_values, index=0)

# Apply filters
@st.cache_data
def apply_filters(df, abc_value, xyz_value):
    filtered = df.copy()
    if abc_value != "All":
        filtered = filtered[filtered["ABC(Rev-Mar)"] == abc_value]
    if xyz_value != "All":
        filtered = filtered[filtered["Territory_XYZ"] == xyz_value]
    return filtered

filtered_df = apply_filters(filtered_df_territory, selected_abc, selected_territory_xyz)

# ===================================
# ✅ Revenue Calculation
# ===================================
if "Total_revenue" not in df.columns:
    st.error("⚠️ 'Total_revenue' column missing from data.")
    st.stop()

# Calculate metrics
overall_revenue = filtered_df_territory["Total_revenue"].sum() if not filtered_df_territory.empty else 0
segment_revenue = filtered_df["Total_revenue"].sum() if not filtered_df.empty else 0
revenue_share = (segment_revenue / overall_revenue * 100) if overall_revenue > 0 else 0

# Display Revenue Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💰 Segment Revenue", value=f"${segment_revenue:,.2f}")

with col2:
    st.metric(label="🏦 Overall Revenue", value=f"${overall_revenue:,.2f}")

with col3:
    st.metric(label="📊 Revenue Share", value=f"{revenue_share:.1f}%")

# ===================================
# ✅ Inventory Details Table
# ===================================
st.subheader("📦 Inventory Details")

if not filtered_df.empty and "Product_Margin" in filtered_df.columns:
    @st.cache_data
    def create_summary_table(df):
        summary = df.groupby("Inventory Name").agg(
            Total_revenue=("Total_revenue", "sum"),
            Avg_Product_Margin=("Product_Margin", "mean")
        ).reset_index()
        
        # Round for better display
        summary["Total_revenue"] = summary["Total_revenue"].round(2)
        summary["Avg_Product_Margin"] = summary["Avg_Product_Margin"].round(3)
        
        return summary

    summary_table = create_summary_table(filtered_df)

    # Display as AgGrid
    gb_summary = GridOptionsBuilder.from_dataframe(summary_table)
    gb_summary.configure_grid_options(domLayout='autoHeight')

    grid_summary_options = gb_summary.build()
    grid_summary_options["defaultColDef"] = {
        "cellStyle": {"fontSize": "14px", "textAlign": "left"},
        "autoWidth": True,
    }

    AgGrid(summary_table, gridOptions=grid_summary_options, enable_enterprise_modules=True)
else:
    st.warning("⚠️ No data available for the selected filters or missing Product_Margin column.")

# ===================================
# ✅ Revenue Bar Chart
# ===================================
st.subheader("📈 Total Revenue Distribution")

if not filtered_df.empty:
    @st.cache_data
    def create_bar_chart(df):
        return px.bar(
            df, 
            x="Inventory Name", 
            y="Total_revenue", 
            title="Total Revenue of Selected Category"
        )
    
    fig = create_bar_chart(filtered_df)
    st.plotly_chart(fig)
else:
    st.warning("⚠️ No data available for the selected filters to display the chart.")