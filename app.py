import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt  # For debugging password hashes

# ===================================
# ✅ Authentication Setup
# ===================================
# Check if config.yaml exists
config_path = "config.yaml"
if not os.path.exists(config_path):
    st.error("⚠️ Authentication file (config.yaml) is missing. Please add it.")
    st.stop()

# Load credentials from YAML file
with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# ✅ Correct Authenticate class instantiation for v0.1.5
authenticator = stauth.Authenticate(
    config["credentials"], 
    config["cookie"]["name"], 
    config["cookie"]["key"], 
    config["cookie"]["expiry_days"], 
    config["preauthorized"]  # ✅ Ensure this exists in config.yaml
)

# ✅ Fix login function for v0.1.5
name, authentication_status, username = authenticator.login('main')

# ✅ Debugging: Check password hash matching
if authentication_status is False:
    entered_password = "Hamid@123"  # Change this to the password you're testing
    hashed_stored_password = config["credentials"]["usernames"]["admin"]["password"]

    if bcrypt.checkpw(entered_password.encode(), hashed_stored_password.encode()):
        st.write("✅ Password matches the stored hash!")
    else:
        st.write("❌ Password does NOT match!")

# ✅ Handle authentication
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}! 🎉")
    
    # ✅ Proceed with the app only after login
    st.title("📊 ABC-XYZ Analysis Dashboard")

elif authentication_status is False:
    st.sidebar.error("❌ Incorrect username or password. Try again.")
    st.stop()

elif authentication_status is None:
    st.sidebar.warning("⚠️ Please enter your username and password.")
    st.stop()

# ===================================
# ✅ Data Loading & Validation
# ===================================
# Define data path
data_dir = os.path.join(os.path.dirname(__file__), 'data')
file_path = os.path.join(data_dir, 'full__abc_xyz.csv')

# Check if CSV file exists
if not os.path.exists(file_path):
    st.error(f"⚠️ Data file missing: `{file_path}`. Please upload it.")
    st.stop()

# Load data
df = pd.read_csv(file_path)

# ✅ Continue with app UI
st.title("📊 ABC-XYZ Analysis Dashboard")

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
if "ABC(Rev-Mar)" not in df.columns or "Territory_XYZ" not in df.columns or "Inventory Name" not in df.columns:
    st.error("⚠️ Required columns missing from data.")
    st.stop()

pivot_df = filtered_df_territory.pivot_table(
    index="ABC(Rev-Mar)", 
    columns="Territory_XYZ", 
    values="Inventory Name", 
    aggfunc=lambda x: x.nunique(), 
    fill_value=0
)

# Add Row and Column Totals
pivot_df["Total"] = pivot_df.sum(axis=1)
pivot_df.loc["Total"] = pivot_df.sum()

# Convert Pivot Table to DataFrame
pivot_df_reset = pivot_df.reset_index()

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
filtered_df = filtered_df_territory.copy()
if selected_abc != "All":
    filtered_df = filtered_df[filtered_df["ABC(Rev-Mar)"] == selected_abc]

if selected_territory_xyz != "All":
    filtered_df = filtered_df[filtered_df["Territory_XYZ"] == selected_territory_xyz]

# ===================================
# ✅ Revenue Calculation
# ===================================
if "Total_revenue" not in df.columns:
    st.error("⚠️ 'Total_revenue' column missing from data.")
    st.stop()

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

if not filtered_df.empty:
    summary_table = filtered_df.groupby("Inventory Name").agg(
        Total_revenue=("Total_revenue", "sum"),
        Avg_Product_Margin=("Product_Margin", "mean")
    ).reset_index()

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
    st.warning("⚠️ No data available for the selected filters.")

# ===================================
# ✅ Revenue Bar Chart
# ===================================
st.subheader("📈 Total Revenue Distribution")

if not filtered_df.empty:
    fig = px.bar(filtered_df, x="Inventory Name", y="Total_revenue", title="Total Revenue of Selected Category")
    st.plotly_chart(fig)
else:
    st.warning("⚠️ No data available for the selected filters to display the chart.")
