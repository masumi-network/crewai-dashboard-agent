
import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Add the parent directory to sys.path to import templates
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from app.templates.base_template import render_dashboard

# Configuration
CONFIG = {
    "title": "Sales Performance Dashboard",
    "description": "Overview of sales performance by region and product category",
    "metrics": [
        {
            "column": "Sales",
            "label": "Total Sales",
            "aggregation": "sum"
        },
        {
            "column": "Profit",
            "label": "Total Profit",
            "aggregation": "sum"
        },
        {
            "column": "Quantity",
            "label": "Units Sold",
            "aggregation": "sum"
        }
    ],
    "charts": [
        {
            "type": "bar",
            "title": "Sales by Region",
            "x": "Region",
            "y": "Sales",
            "color": None,
            "x_label": None,
            "y_label": None
        },
        {
            "type": "line",
            "title": "Monthly Sales Trend",
            "x": "Date",
            "y": "Sales",
            "color": None,
            "x_label": None,
            "y_label": None
        },
        {
            "type": "pie",
            "title": "Sales Distribution by Category",
            "x": "Category",
            "y": "Sales",
            "color": None,
            "x_label": None,
            "y_label": None
        }
    ],
    "filters": [
        {
            "type": "date_range",
            "column": "Date",
            "label": None
        },
        {
            "type": "categorical",
            "column": "Region",
            "label": None
        },
        {
            "type": "categorical",
            "column": "Category",
            "label": None
        }
    ]
}

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("http://localhost:8080/sample_data.csv")
        
        # Convert date columns to datetime
        date_filters = [f for f in CONFIG.get('filters', []) if f.get('type') == 'date_range']
        for date_filter in date_filters:
            column = date_filter.get('column')
            if column and column in df.columns:
                df[column] = pd.to_datetime(df[column])
                
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load the data
data = load_data()

# Render the dashboard if data is loaded
if data is not None:
    render_dashboard(data, CONFIG)
else:
    st.error("Failed to load data. Please check the data URL.")
