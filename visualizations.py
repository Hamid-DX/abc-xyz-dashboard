import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data
def create_bar_chart(df):
    """Create a bar chart of total revenue by inventory item"""
    return px.bar(
        df, 
        x="Inventory Name", 
        y="Total_revenue", 
        title="Total Revenue of Selected Category"
    )

def display_pivot_table(pivot_df):
    """Display a pivot table using AgGrid"""
    st.subheader("📌 ABC-XYZ Matrix Table")

    # Customize AgGrid for Better Readability
    gb = GridOptionsBuilder.from_dataframe(pivot_df)
    gb.configure_grid_options(domLayout='autoHeight')

    # Apply styling
    grid_options = gb.build()
    grid_options["defaultColDef"] = {
        "cellStyle": {"fontSize": "16px", "textAlign": "center"},
        "autoWidth": True,
    }

    AgGrid(pivot_df, gridOptions=grid_options, enable_enterprise_modules=True)

def display_summary_table(summary_table):
    """Display a summary table using AgGrid"""
    # Display as AgGrid
    gb_summary = GridOptionsBuilder.from_dataframe(summary_table)
    gb_summary.configure_grid_options(domLayout='autoHeight')

    grid_summary_options = gb_summary.build()
    grid_summary_options["defaultColDef"] = {
        "cellStyle": {"fontSize": "14px", "textAlign": "left"},
        "autoWidth": True,
    }

    AgGrid(summary_table, gridOptions=grid_summary_options, enable_enterprise_modules=True)

def display_revenue_metrics(overall_revenue, segment_revenue, revenue_share):
    """Display revenue metrics in columns"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="💰 Segment Revenue", value=f"${segment_revenue:,.2f}")

    with col2:
        st.metric(label="🏦 Overall Revenue", value=f"${overall_revenue:,.2f}")

    with col3:
        st.metric(label="📊 Revenue Share", value=f"{revenue_share:.1f}%")