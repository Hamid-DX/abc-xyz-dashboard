import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px


# ===================================
# ✅ Data Loading & Validation
# ===================================

data_dir = os.path.join(os.path.dirname(__file__), 'data')
file_path = os.path.join(data_dir, 'full__abc_xyz.csv')
df = pd.read_csv(file_path)

# Streamlit UI
st.title("ABC-XYZ Analysis Dashboard")

# ===================================
# ✅ Territory Selection
# ===================================

territories = df["Territory"].unique()
selected_territory = st.selectbox("Select Territory:", options=territories)

# Filter Data Based on Selected Territory
filtered_df_territory = df[df["Territory"] == selected_territory]

# ===================================
# ✅ Pivot Table Creation
# ===================================

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

# Convert Pivot Table to DataFrame for Streamlit AgGrid
pivot_df_reset = pivot_df.reset_index()

# Display Matrix Table
st.subheader("ABC-XYZ Matrix Table")

# Customize AgGrid for Bigger Font & Better Readability
gb = GridOptionsBuilder.from_dataframe(pivot_df_reset)
gb.configure_grid_options(domLayout='autoHeight')

# Apply Styling for Bigger Font
grid_options = gb.build()
grid_options["defaultColDef"] = {
    "cellStyle": {
        "fontSize": "16px",  # Increased font size
        "textAlign": "center",
    },
    "autoWidth": True,
}

AgGrid(pivot_df_reset, gridOptions=grid_options, enable_enterprise_modules=True)

# ===================================
# ✅ Filters
# ===================================
# ABC(Rev-Mar) Segment Selection 
st.subheader("Filter Data")
abc_values = sorted(filtered_df_territory["ABC(Rev-Mar)"].dropna().unique())  # Sorting Alphabetically
selected_abc = st.selectbox("Select ABC(Rev-Mar) Segment:", options=["All"] + abc_values, index=0)

# Territory_XYZ Selection (Optional)
territory_xyz_values = sorted(filtered_df_territory["Territory_XYZ"].dropna().unique())  # Sorting Alphabetically
selected_territory_xyz = st.selectbox("Select Territory_XYZ:", options=["All"] + territory_xyz_values, index=0)

# Initialize Filtered DataFrame
filtered_df = filtered_df_territory.copy()

# Apply Filters if Selections Are Made
if selected_abc != "All":
    filtered_df = filtered_df[filtered_df["ABC(Rev-Mar)"] == selected_abc]

if selected_territory_xyz != "All":
    filtered_df = filtered_df[filtered_df["Territory_XYZ"] == selected_territory_xyz]
    
# ===================================
# ✅ Revenue Calculation
# ===================================

# Calculate Overall Revenue
overall_revenue = filtered_df_territory["Total_revenue"].sum()

# Calculate Segment Revenue (Filtered Data)
segment_revenue = filtered_df["Total_revenue"].sum() if not filtered_df.empty else 0

# Calculate Revenue Percentage Share
revenue_share = (segment_revenue / overall_revenue) * 100 if overall_revenue > 0 else 0

# Display Revenue Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Segment Revenue", value=f"{segment_revenue:,.2f}")

with col2:
    st.metric(label="Overall Revenue", value=f"{overall_revenue:,.2f}")

with col3:
    st.metric(label="Revenue Percentage Share", value=f"{revenue_share:.1f}%")

# ===================================
# ✅ Inventory Details Table
# ===================================

st.subheader("Inventory Details")

# Ensure that filtering doesn't break the table
if not filtered_df.empty:
    # Create Summary Table
    summary_table = filtered_df.groupby("Inventory Name").agg(
        Total_revenue=("Total_revenue", "sum"),
        Avg_Product_Margin=("Product_Margin", "mean")
    ).reset_index()

    # Round Values for Better Readability
    summary_table["Total_revenue"] = summary_table["Total_revenue"].round(2)
    summary_table["Avg_Product_Margin"] = summary_table["Avg_Product_Margin"].round(3)

    # Add a Total Row at the Bottom
    total_row = pd.DataFrame({
        "Inventory Name": ["Total"],
        "Total_revenue": [summary_table["Total_revenue"].sum()],
        "Avg_Product_Margin": [summary_table["Avg_Product_Margin"].mean()]
    }).round(2)

    summary_table = pd.concat([summary_table, total_row], ignore_index=True)

    # Display as AgGrid for better interactivity
    gb_summary = GridOptionsBuilder.from_dataframe(summary_table)
    gb_summary.configure_grid_options(domLayout='autoHeight')

    # Apply styling
    grid_summary_options = gb_summary.build()
    grid_summary_options["defaultColDef"] = {
        "cellStyle": {
            "fontSize": "14px",
            "textAlign": "left",
        },
        "autoWidth": True,
    }

    AgGrid(summary_table, gridOptions=grid_summary_options, enable_enterprise_modules=True)
else:
    st.warning("No data available for the selected filters.")

# Create a bar chart of Total Revenue for the selected ABC(Rev-Mar) segment
st.subheader("Total Revenue Distribution")

if not filtered_df.empty:
    fig = px.bar(filtered_df, x="Inventory Name", y="Total_revenue", title="Total Revenue of Selected Category")
    st.plotly_chart(fig)
else:
    st.warning("No data available for the selected filters to display the chart.")