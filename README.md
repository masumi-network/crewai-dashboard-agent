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

## Using the Dashboard Generator

### 1. Simple Auto-Generated Dashboard

For a quick start, let the system automatically generate a dashboard based on your data:

```python
import requests

# Minimal configuration with auto-generation
payload = {
    "data_url": "http://example.com/data.csv",
    "config": {
        "auto_configure": true,
        "style": {
            "theme": "default"
        }
    }
}

response = requests.post("http://localhost:8001/api/create-dashboard", json=payload)
print(f"Dashboard created at: {response.json()['dashboard_url']}")
```

### 2. Sales Performance Dashboard

Create a sales dashboard with specific metrics and visualizations:

```python
payload = {
    "data_url": "http://example.com/sales_data.csv",
    "config": {
        "title": "Sales Performance Dashboard",
        "description": "Monthly sales analysis by region and product",
        "metrics": [
            {
                "column": "Revenue",
                "label": "Total Revenue",
                "aggregation": "sum"
            },
            {
                "column": "Orders",
                "label": "Total Orders",
                "aggregation": "count"
            },
            {
                "column": "Revenue",
                "label": "Average Order Value",
                "aggregation": "mean"
            }
        ],
        "charts": [
            {
                "type": "line",
                "title": "Monthly Revenue Trend",
                "x": "Date",
                "y": "Revenue",
                "color": "Region"
            },
            {
                "type": "bar",
                "title": "Sales by Product Category",
                "x": "Category",
                "y": "Revenue"
            },
            {
                "type": "pie",
                "title": "Revenue Distribution by Region",
                "x": "Region",
                "y": "Revenue"
            }
        ],
        "filters": [
            {
                "type": "date_range",
                "column": "Date",
                "label": "Select Period"
            },
            {
                "type": "categorical",
                "column": "Region",
                "label": "Filter by Region"
            }
        ],
        "style": {
            "theme": "light",
            "layout": "standard"
        }
    }
}
```

### 3. Product Analytics Dashboard

Create a dashboard focused on product performance and customer behavior:

```python
payload = {
    "data_url": "http://example.com/product_data.csv",
    "config": {
        "title": "Product Analytics Dashboard",
        "description": "Product performance and customer behavior analysis",
        "metrics": [
            {
                "column": "Rating",
                "label": "Average Rating",
                "aggregation": "mean"
            },
            {
                "column": "Reviews",
                "label": "Total Reviews",
                "aggregation": "sum"
            },
            {
                "column": "Returns",
                "label": "Return Rate",
                "aggregation": "mean"
            }
        ],
        "charts": [
            {
                "type": "scatter",
                "title": "Price vs Rating Distribution",
                "x": "Price",
                "y": "Rating",
                "color": "Category"
            },
            {
                "type": "bar",
                "title": "Reviews by Product Category",
                "x": "Category",
                "y": "Reviews"
            }
        ],
        "filters": [
            {
                "type": "numeric_range",
                "column": "Price",
                "label": "Price Range"
            },
            {
                "type": "categorical",
                "column": "Category",
                "label": "Product Category"
            }
        ],
        "style": {
            "theme": "dark",
            "layout": "grid",
            "columns": 2
        }
    }
}
```

### 4. Custom Themed Dashboard

Create a dashboard with custom styling and layout:

```python
payload = {
    "data_url": "http://example.com/data.csv",
    "config": {
        "title": "Custom Themed Dashboard",
        "description": "Dashboard with custom styling",
        "auto_configure": true,  # Let the system suggest charts and metrics
        "style": {
            "theme": "colorful",
            "layout": "expanded",
            "color_scheme": "custom",
            "custom_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"]
        }
    }
}
```

### 5. Compact KPI Dashboard

Create a compact dashboard focused on key metrics:

```python
payload = {
    "data_url": "http://example.com/kpi_data.csv",
    "config": {
        "title": "KPI Overview",
        "description": "Key performance indicators at a glance",
        "metrics": [
            {
                "column": "Revenue",
                "label": "Revenue",
                "aggregation": "sum",
                "format": "currency"
            },
            {
                "column": "Profit",
                "label": "Profit",
                "aggregation": "sum",
                "format": "currency"
            },
            {
                "column": "ROI",
                "label": "ROI",
                "aggregation": "mean",
                "format": "percentage"
            }
        ],
        "charts": [
            {
                "type": "line",
                "title": "Metrics Over Time",
                "x": "Date",
                "y": ["Revenue", "Profit"],
                "display": "small"
            }
        ],
        "style": {
            "theme": "light",
            "layout": "compact"
        }
    }
}
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
    "aggregation": "sum",  // Options: sum, mean/average, count, min, max
    "format": "currency"   // Options: currency, percentage, number, decimal
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
    "y_label": "Sales Amount",  // Optional: custom axis label
    "orientation": "vertical",  // Optional: vertical or horizontal
    "display": "normal"   // Optional: normal, small, large
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
    "y_label": "Sales Amount",
    "interpolation": "linear",  // Optional: linear, spline
    "display": "normal"
}
```

#### Pie Chart

```json
{
    "type": "pie",
    "title": "Revenue Distribution",
    "x": "Category",  // Categories for pie segments
    "y": "Revenue",   // Values to determine segment size
    "donut": false,   // Optional: true for donut chart
    "display": "normal"
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
    "y_label": "Customer Rating",
    "size": "Sales",     // Optional: vary point size
    "display": "normal"
}
```

#### Area Chart

```json
{
    "type": "area",
    "title": "Market Share Over Time",
    "x": "Date",
    "y": "Share",
    "color": "Company",  // Optional: stack areas by category
    "x_label": "Time Period",
    "y_label": "Market Share (%)",
    "stacked": true,    // Optional: stack areas
    "display": "normal"
}
```

### Filters Configuration

Filters allow users to interact with the dashboard:

#### Date Range Filter

```json
{
    "type": "date_range",
    "column": "Date",
    "label": "Select Date Range",
    "default": {  // Optional
        "start": "2024-01-01",
        "end": "2024-12-31"
    }
}
```

#### Categorical Filter

```json
{
    "type": "categorical",
    "column": "Category",
    "label": "Filter by Category",
    "multiple": true,  // Optional: allow multiple selections
    "default": ["Electronics", "Clothing"]  // Optional
}
```

#### Numeric Range Filter

```json
{
    "type": "numeric_range",
    "column": "Price",
    "label": "Price Range",
    "default": {  // Optional
        "min": 0,
        "max": 1000
    }
}
```

### Style and Layout Configuration

Customize the dashboard appearance:

```json
"style": {
    "theme": "default",    // Options: default, dark, light, colorful
    "layout": "standard",  // Options: standard, compact, expanded, grid
    "columns": 2,         // Number of columns for grid layout
    "color_scheme": "default",  // Color scheme for charts
    "custom_colors": ["#FF6B6B", "#4ECDC4"],  // Optional: custom color palette
    "font_family": "Inter",  // Optional: custom font
    "chart_height": "normal"  // Options: small, normal, large
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