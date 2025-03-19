import requests
import json
import time
import argparse

def test_create_dashboard(base_url, data_url):
    """
    Test creating a dashboard through the API.
    
    Args:
        base_url (str): Base URL of the API (e.g., http://localhost:8001)
        data_url (str): URL to a CSV data file
    """
    print("Testing dashboard creation API...")
    
    # Dashboard configuration
    config = {
        "title": "Sales Performance Dashboard",
        "description": "Overview of sales performance by region and product category",
        "metrics": [
            {"column": "Sales", "label": "Total Sales", "aggregation": "sum"},
            {"column": "Profit", "label": "Total Profit", "aggregation": "sum"},
            {"column": "Quantity", "label": "Units Sold", "aggregation": "sum"}
        ],
        "charts": [
            {
                "type": "bar",
                "title": "Sales by Region",
                "x": "Region",
                "y": "Sales"
            },
            {
                "type": "line",
                "title": "Monthly Sales Trend",
                "x": "Date",
                "y": "Sales"
            },
            {
                "type": "pie",
                "title": "Sales Distribution by Category",
                "x": "Category",
                "y": "Sales"
            }
        ],
        "filters": [
            {"type": "date_range", "column": "Date"},
            {"type": "categorical", "column": "Region"},
            {"type": "categorical", "column": "Category"}
        ]
    }
    
    # Create request payload
    payload = {
        "data_url": data_url,
        "config": config,
        "download_package": True  # Set to True explicitly
    }
    
    print(f"Sending request to {base_url}/api/create-dashboard")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Send request to create dashboard
    response = requests.post(
        f"{base_url}/api/create-dashboard",
        json=payload
    )
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("Dashboard created successfully!")
        print(f"Full response: {json.dumps(result, indent=2)}")
        print(f"Dashboard ID: {result['dashboard_id']}")
        print(f"Dashboard URL: {result['dashboard_url']}")
        if result.get('download_url'):
            print(f"Download URL: {result['download_url']}")
            
            # Try to download the package
            download_url = f"{base_url}{result['download_url']}"
            print(f"Attempting to download package from {download_url}")
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                print(f"Package download successful: {len(download_response.content)} bytes")
            else:
                print(f"Package download failed: {download_response.status_code}")
                print(download_response.text)
        
        # Get the list of dashboards
        list_response = requests.get(f"{base_url}/api/dashboards")
        if list_response.status_code == 200:
            dashboards = list_response.json()
            print("\nAll Dashboards:")
            for dashboard in dashboards:
                print(f"- {dashboard.get('title', 'Untitled')} (ID: {dashboard.get('id')})")
        
        return result['dashboard_id']
    else:
        print(f"Error creating dashboard: {response.status_code}")
        print(response.text)
        return None

def main():
    parser = argparse.ArgumentParser(description='Test CrewAI Dashboard Generator API')
    parser.add_argument('--url', default='http://localhost:8001', help='API base URL')
    parser.add_argument('--data', required=True, help='URL to CSV data file')
    
    args = parser.parse_args()
    
    dashboard_id = test_create_dashboard(args.url, args.data)
    
    if dashboard_id:
        print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 