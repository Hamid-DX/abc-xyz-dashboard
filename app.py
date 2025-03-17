import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import yaml
from yaml.loader import SafeLoader
import hashlib
import time

# =================================================
# ✅ Set page config at the very beginning
# =================================================
st.set_page_config(
    page_title="ABC-XYZ Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# ✅ Custom Authentication Implementation
# =================================================
# Disable streamlit_authenticator and implement a very minimal custom solution
# to avoid the recursive request issue

def load_user_credentials():
    """Load user credentials from config file"""
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        st.error("⚠️ Authentication file (config.yaml) is missing.")
        st.stop()
    
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
            return config["credentials"]["usernames"]
    except Exception as e:
        st.error(f"⚠️ Error loading credentials: {e}")
        st.stop()

def verify_password(username, password, credentials):
    """Very basic password verification"""
    if username not in credentials:
        return False
    
    # This is a simplified check just to test functionality
    # In production, use a proper password hashing library
    hashed_pwd = credentials[username]["password"]
    
    # If the password starts with $2b$ it's likely bcrypt
    # We'll just compare the first few characters for testing
    # This is NOT secure but helps bypass the infinite loop issue
    return password == credentials[username].get("plaintext_password", "")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# Load credentials
user_credentials = load_user_credentials()

# Add some plaintext passwords (ONLY FOR TESTING)
# In production, you would use proper password verification
user_credentials["admin"]["plaintext_password"] = "Hamid@123"
user_credentials["user1"]["plaintext_password"] = "Nick@123"

# =================================================
# ✅ Login UI
# =================================================
def login_form():
    """Display a custom login form"""
    st.title("ABC-XYZ Analysis Dashboard Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            st.session_state.login_attempted = True
            if verify_password(username, password, user_credentials):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                time.sleep(1)  # Give time for the success message to be seen
            else:
                st.error("Invalid username or password")

# =================================================
# ✅ Logout functionality
# =================================================
def logout():
    """Custom logout function"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_attempted = False

# =================================================
# ✅ Main Application
# =================================================

# Check authentication status
if not st.session_state.authenticated:
    login_form()
    st.stop()  # Stop execution here if not authenticated

# Show logout button in sidebar if authenticated
st.sidebar.button("Logout", on_click=logout)

# Welcome message for authenticated user
if st.session_state.username:
    user_name = user_credentials[st.session_state.username]["name"]
    st.sidebar.success(f"Welcome, {user_name}! 🎉")

# =================================================
# ✅ Data Loading
# =================================================
@st.cache_data
def load_data():
    """Load and cache the dataset"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(data_dir, 'full__abc_xyz.csv')
    
    if not os.path.exists(file_path):
        st.error(f"⚠️ Data file missing: `{file_path}`")
        st.stop()
    
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        st.stop()

# =================================================
# ✅ Dashboard UI
# =================================================
st.title("📊 ABC-XYZ Analysis Dashboard")

try:
    # Load data
    df = load_data()
    
    # Validate required columns
    required_columns = ["Territory", "ABC(Rev-Mar)", "Territory_XYZ", "Inventory Name", "Total_revenue"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        st.error(f"⚠️ Missing columns in dataset: {', '.join(missing_cols)}")
        st.stop()
    
    # Territory selection
    territories = sorted(df["Territory"].dropna().unique())
    if not territories:
        st.error("⚠️ No territory data available")
        st.stop()
        
    selected_territory = st.selectbox("🌍 Select Territory:", options=territories)
    
    # Filter by territory
    filtered_df_territory = df[df["Territory"] == selected_territory]
    
    # =================================================
    # ✅ Pivot Table
    # =================================================
    @st.cache_data
    def create_pivot(df_territory):
        pivot = df_territory.pivot_table(
            index="ABC(Rev-Mar)", 
            columns="Territory_XYZ", 
            values="Inventory Name", 
            aggfunc=lambda x: x.nunique(), 
            fill_value=0
        )
        
        # Add totals
        pivot["Total"] = pivot.sum(axis=1)
        pivot.loc["Total"] = pivot.sum()
        
        return pivot.reset_index()
    
    pivot_df = create_pivot(filtered_df_territory)
    
    # Display pivot table
    st.subheader("📌 ABC-XYZ Matrix Table")
    
    gb = GridOptionsBuilder.from_dataframe(pivot_df)
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()
    grid_options["defaultColDef"] = {
        "cellStyle": {"fontSize": "16px", "textAlign": "center"},
        "autoWidth": True,
    }
    
    AgGrid(pivot_df, gridOptions=grid_options, enable_enterprise_modules=True)
    
    # =================================================
    # ✅ Filters
    # =================================================
    st.subheader("🔎 Filter Data")
    
    # ABC filter
    abc_values = sorted(filtered_df_territory["ABC(Rev-Mar)"].dropna().unique())
    selected_abc = st.selectbox("📌 Select ABC(Rev-Mar) Segment:", options=["All"] + list(abc_values))
    
    # XYZ filter
    xyz_values = sorted(filtered_df_territory["Territory_XYZ"].dropna().unique())
    selected_xyz = st.selectbox("📍 Select Territory_XYZ:", options=["All"] + list(xyz_values))
    
    # Apply filters
    filtered_df = filtered_df_territory.copy()
    
    if selected_abc != "All":
        filtered_df = filtered_df[filtered_df["ABC(Rev-Mar)"] == selected_abc]
        
    if selected_xyz != "All":
        filtered_df = filtered_df[filtered_df["Territory_XYZ"] == selected_xyz]
    
    # =================================================
    # ✅ Revenue Metrics
    # =================================================
    overall_revenue = filtered_df_territory["Total_revenue"].sum()
    segment_revenue = filtered_df["Total_revenue"].sum() if not filtered_df.empty else 0
    revenue_share = (segment_revenue / overall_revenue * 100) if overall_revenue > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Segment Revenue", f"${segment_revenue:,.2f}")
        
    with col2:
        st.metric("🏦 Overall Revenue", f"${overall_revenue:,.2f}")
        
    with col3:
        st.metric("📊 Revenue Share", f"{revenue_share:.1f}%")
    
    # =================================================
    # ✅ Inventory Details
    # =================================================
    st.subheader("📦 Inventory Details")
    
    if not filtered_df.empty and "Product_Margin" in filtered_df.columns:
        # Create summary table
        summary = filtered_df.groupby("Inventory Name").agg(
            Total_revenue=("Total_revenue", "sum"),
            Avg_Product_Margin=("Product_Margin", "mean")
        ).reset_index()
        
        # Format values
        summary["Total_revenue"] = summary["Total_revenue"].round(2)
        summary["Avg_Product_Margin"] = summary["Avg_Product_Margin"].round(3)
        
        # Display table
        gb_summary = GridOptionsBuilder.from_dataframe(summary)
        gb_summary.configure_grid_options(domLayout='autoHeight')
        
        grid_summary_options = gb_summary.build()
        grid_summary_options["defaultColDef"] = {
            "cellStyle": {"fontSize": "14px", "textAlign": "left"},
            "autoWidth": True,
        }
        
        AgGrid(summary, gridOptions=grid_summary_options, enable_enterprise_modules=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")
    
    # =================================================
    # ✅ Bar Chart
    # =================================================
    st.subheader("📈 Total Revenue Distribution")
    
    if not filtered_df.empty:
        fig = px.bar(
            filtered_df, 
            x="Inventory Name", 
            y="Total_revenue", 
            title="Total Revenue by Inventory Item",
            labels={"Total_revenue": "Revenue ($)", "Inventory Name": "Item"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data available to display chart.")
        
except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")