# CrewAI Dashboard Generator

A backend service that dynamically generates and deploys interactive Streamlit dashboards from API requests.

## Features

- 📊 Generate interactive dashboards with Streamlit
- 🚀 Deploy dashboards dynamically
- 📦 Package dashboards for download
- 🔄 Custom metrics, charts, and filters
- 🌐 RESTful API for dashboard creation

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crewai-dashboard-agent.git
   cd crewai-dashboard-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### Docker Deployment

Build and run with Docker:

```bash
docker build -t crewai-dashboard-generator .
docker run -p 8000:8000 -p 8501:8501 crewai-dashboard-generator
```

## API Usage

### Create a Dashboard

```bash
curl -X POST "http://localhost:8000/api/create-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "data_url": "https://example.com/data.csv",
    "config": {
      "title": "Sales Dashboard",
      "description": "Overview of sales performance",
      "metrics": [
        {"column": "revenue", "label": "Total Revenue", "aggregation": "sum"},
        {"column": "orders", "label": "Order Count", "aggregation": "count"}
      ],
      "charts": [
        {
          "type": "bar",
          "title": "Revenue by Category",
          "x": "category",
          "y": "revenue"
        },
        {
          "type": "line",
          "title": "Sales Over Time",
          "x": "date",
          "y": "revenue"
        }
      ],
      "filters": [
        {"type": "date_range", "column": "date"},
        {"type": "categorical", "column": "category"}
      ]
    },
    "download_package": true
  }'
```

### List Dashboards

```bash
curl -X GET "http://localhost:8000/api/dashboards"
```

### Get Dashboard Details

```bash
curl -X GET "http://localhost:8000/api/dashboards/{dashboard_id}"
```

### Delete Dashboard

```bash
curl -X DELETE "http://localhost:8000/api/dashboards/{dashboard_id}"
```

## Dashboard Configuration

A dashboard configuration consists of:

- `title`: Dashboard title
- `description`: Dashboard description
- `metrics`: Key performance indicators to display
- `charts`: Data visualizations (bar, line, scatter, pie)
- `filters`: Interactive filters for the data

### Example Configuration

```json
{
  "title": "Sales Dashboard",
  "description": "Monthly sales performance by region",
  "metrics": [
    {"column": "revenue", "label": "Total Revenue", "aggregation": "sum"},
    {"column": "profit", "label": "Total Profit", "aggregation": "sum"},
    {"column": "units_sold", "label": "Units Sold", "aggregation": "sum"}
  ],
  "charts": [
    {
      "type": "bar",
      "title": "Revenue by Region",
      "x": "region",
      "y": "revenue"
    },
    {
      "type": "line",
      "title": "Monthly Sales Trend",
      "x": "month",
      "y": "revenue"
    },
    {
      "type": "pie",
      "title": "Revenue Distribution by Product",
      "x": "product",
      "y": "revenue"
    }
  ],
  "filters": [
    {"type": "date_range", "column": "date"},
    {"type": "categorical", "column": "region"},
    {"type": "categorical", "column": "product_category"}
  ]
}
```

## Deployment to DigitalOcean

1. Push your code to GitHub
2. On DigitalOcean App Platform:
   - Connect to your GitHub repository
   - Select the Dockerfile deployment type
   - Configure environment variables if needed
   - Set up networking to expose ports 8000 (API) and 8501 (Streamlit)

## License

This project is licensed under the MIT License - see the LICENSE file for details.