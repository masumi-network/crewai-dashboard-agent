# CrewAI Dashboard Generator

A versatile dashboard generation tool that creates interactive data visualizations from various data sources. This tool is designed to be used with CrewAI agents to automate dashboard creation based on natural language requests.

## Features

- **Data Source Flexibility**: Connect to various data sources including CSV, JSON, databases
- **Auto-Configuration**: Automatically generates appropriate visualizations based on data characteristics
- **Interactive Filtering**: Apply filters to explore data from different angles
- **Multiple Chart Types**: Support for bar charts, line charts, pie charts, scatter plots, and more
- **Customizable Metrics**: Display key performance indicators with flexible aggregation options
- **Style Customization**: Choose from different themes and layouts to personalize your dashboards
- **Export Capability**: Download dashboards as standalone packages

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Required packages: FastAPI, Streamlit, Pandas, Plotly

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crewai-dashboard-agent.git
cd crewai-dashboard-agent

# Install dependencies
pip install -r requirements.txt
```

### Running the API Server

```bash
# Start the API server
uvicorn app.main:app --reload --port 8001
```

### Using the API

Create a dashboard by sending a POST request to the `/api/create-dashboard` endpoint:

```python
import requests
import json

# Dashboard configuration
payload = {
    "data_url": "http://example.com/data.csv",
    "config": {
        "title": "Sales Dashboard",
        "description": "Overview of sales performance",
        "metrics": [
            {"column": "Revenue", "label": "Total Revenue", "aggregation": "sum"}
        ],
        "charts": [
            {
                "type": "bar",
                "title": "Sales by Region",
                "x": "Region",
                "y": "Sales"
            }
        ],
        "filters": [
            {"type": "date_range", "column": "Date"}
        ],
        "style": {
            "theme": "default",
            "layout": "standard"
        }
    }
}

# Send request
response = requests.post("http://localhost:8001/api/create-dashboard", json=payload)
result = response.json()

print(f"Dashboard created at: {result['dashboard_url']}")
```

## Dashboard Configuration

### Basic Structure

```json
{
    "title": "Dashboard Title",
    "description": "Dashboard description",
    "metrics": [...],
    "charts": [...],
    "filters": [...],
    "style": {...},
    "auto_configure": true
}
```

### Metrics Configuration

Metrics display key values from your data:

```json
{
    "column": "Revenue",
    "label": "Total Revenue",
    "aggregation": "sum"  // Options: sum, mean/average, count, min, max
}
```

### Charts Configuration

The dashboard supports several chart types:

#### Bar Chart

```json
{
    "type": "bar",
    "title": "Sales by Region",
    "x": "Region",
    "y": "Sales",
    "color": "Category",  // Optional: color bars by a category
    "x_label": "Region Name",  // Optional: custom axis label
    "y_label": "Sales Amount"  // Optional: custom axis label
}
```

#### Line Chart

```json
{
    "type": "line",
    "title": "Monthly Sales Trend",
    "x": "Date",
    "y": "Sales",
    "color": "Product",  // Optional: create multiple lines by category
    "x_label": "Month",
    "y_label": "Sales Amount"
}
```

#### Pie Chart

```json
{
    "type": "pie",
    "title": "Revenue Distribution",
    "x": "Category",  // Categories for pie segments
    "y": "Revenue"    // Values to determine segment size
}
```

#### Scatter Plot

```json
{
    "type": "scatter",
    "title": "Price vs Rating",
    "x": "Price",
    "y": "Rating",
    "color": "Category",  // Optional: color points by category
    "x_label": "Price ($)",
    "y_label": "Customer Rating"
}
```

### Filters Configuration

Filters allow users to interact with the dashboard:

```json
{
    "type": "date_range",  // Options: date_range, categorical, numeric_range
    "column": "Date",
    "label": "Select Date Range"  // Optional: custom filter label
}
```

### Style and Layout Configuration

Customize the dashboard appearance:

```json
"style": {
    "theme": "default",    // Options: default, dark, light, colorful
    "layout": "standard",  // Options: standard, compact, expanded, grid
    "columns": 2,          // Number of columns for grid layout
    "color_scheme": "default"  // Color scheme for charts
}
```

#### Theme Options

- **default**: Clean, professional look with blue accent colors
- **dark**: Dark background with light text and vibrant chart colors
- **light**: Light background with subtle shadows and blue accent colors
- **colorful**: Gradients and vibrant colors for a more playful appearance

#### Layout Options

- **standard**: Metrics in sidebar, charts in main area (traditional dashboard)
- **compact**: Metrics as small inline boxes, charts stacked below
- **expanded**: Full-width sections for both metrics and charts
- **grid**: Arranges all elements in a grid with configurable columns

### Auto-Configuration

Enable automatic dashboard configuration based on data characteristics:

```json
"auto_configure": true
```

When enabled, the system will:
- Suggest appropriate metrics based on numeric columns
- Choose chart types that best represent the data
- Add relevant filters based on date and categorical columns
- Apply default styling

## Testing

Use the included test script to verify the API functionality:

```bash
python test_api.py --url http://localhost:8001 --data http://example.com/data.csv --test all
```

Test options:
- `basic`: Tests basic dashboard creation
- `styles`: Tests different style and layout combinations
- `auto`: Tests auto-configuration functionality
- `all`: Runs all tests

## License

[MIT License](LICENSE)