import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

@st.cache_data
def create_bar_chart(df):
    """Create a bar chart of total revenue by inventory item"""
    # Sort by revenue descending
    df_sorted = df.sort_values("TOTAL_REVENUE", ascending=False).head(15)
    
    return px.bar(
        df_sorted, 
        x="INVENTORY", 
        y="TOTAL_REVENUE", 
        title="Total Revenue by Inventory (Top 15)",
        labels={"INVENTORY": "Inventory Item", "TOTAL_REVENUE": "Total Revenue"}
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
        st.metric(label="💰 Segment Revenue [Local Currency]", value=f"{segment_revenue:,.2f}")

    with col2:
        st.metric(label="🏦 Overall Revenue [Local Currency]", value=f"{overall_revenue:,.2f}")

    with col3:
        st.metric(label="📊 Revenue Share [Percentage]", value=f"{revenue_share:.1f}%")

@st.cache_data
def create_date_distribution_chart(df):
    """Create a chart showing data distribution by month"""
    # Extract month and year and count records
    df['month_year'] = df['DN_DELIVERY_DT'].dt.strftime('%Y-%m')
    monthly_counts = df.groupby('month_year').size().reset_index(name='count')
    
    # Sort by date
    monthly_counts = monthly_counts.sort_values('month_year')
    
    # Create the chart
    fig = px.bar(
        monthly_counts,
        x='month_year',
        y='count',
        title='Data Distribution by Month',
        labels={'month_year': 'Month-Year', 'count': 'Record Count'}
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    
    return fig