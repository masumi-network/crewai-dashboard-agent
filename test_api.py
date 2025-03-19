#!/usr/bin/env python3
import argparse
import requests
import json
import time
import pandas as pd

def test_create_dashboard(url, data_url):
    """Test the create dashboard API by creating a sample dashboard."""
    endpoint = f"{url}/api/create-dashboard"
    
    # Example dashboard config - sales dashboard
    payload = {
        "data_url": data_url,
        "config": {
            "title": "Sales Performance Dashboard",
            "description": "Overview of sales performance by region and product category",
            "metrics": [
                {"column": "Sales", "label": "Total Sales", "aggregation": "sum"},
                {"column": "Profit", "label": "Total Profit", "aggregation": "sum"},
                {"column": "Units", "label": "Units Sold", "aggregation": "sum"}
            ],
            "charts": [
                {
                    "type": "bar",
                    "title": "Sales by Region",
                    "x": "Region",
                    "y": "Sales",
                    "x_label": "Region",
                    "y_label": "Sales ($)"
                },
                {
                    "type": "line",
                    "title": "Monthly Sales Trend",
                    "x": "Date",
                    "y": "Sales",
                    "x_label": "Month",
                    "y_label": "Sales ($)"
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
            ],
            "style": {
                "theme": "default",
                "layout": "standard"
            }
        },
        "download_package": True
    }
    
    print(f"Sending request to {endpoint}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("\nResponse:")
        print(json.dumps(result, indent=2))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def test_styled_dashboards(url, data_url):
    """Test creating multiple dashboards with different styles."""
    
    # Base configuration for all dashboards
    base_config = {
        "metrics": [
            {"column": "Sales", "label": "Total Sales", "aggregation": "sum"},
            {"column": "Profit", "label": "Total Profit", "aggregation": "sum"},
            {"column": "Units", "label": "Units Sold", "aggregation": "sum"}
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
    
    # Style variations to test
    style_variations = [
        {
            "title": "Dark Theme Dashboard",
            "description": "Sales dashboard with dark theme and standard layout",
            "style": {
                "theme": "dark",
                "layout": "standard"
            }
        },
        {
            "title": "Light Theme Compact Dashboard",
            "description": "Sales dashboard with light theme and compact layout",
            "style": {
                "theme": "light",
                "layout": "compact"
            }
        },
        {
            "title": "Colorful Grid Dashboard",
            "description": "Sales dashboard with colorful theme and grid layout",
            "style": {
                "theme": "colorful",
                "layout": "grid",
                "columns": 3
            }
        },
        {
            "title": "Expanded Dashboard",
            "description": "Sales dashboard with default theme and expanded layout",
            "style": {
                "theme": "default",
                "layout": "expanded"
            }
        }
    ]
    
    results = []
    
    for style_config in style_variations:
        # Create a complete config by merging the base config with style variation
        complete_config = base_config.copy()
        for key, value in style_config.items():
            complete_config[key] = value
        
        payload = {
            "data_url": data_url,
            "config": complete_config,
            "download_package": False
        }
        
        endpoint = f"{url}/api/create-dashboard"
        
        print(f"\nCreating dashboard: {style_config['title']}")
        print(f"Style: {style_config['style']}")
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"Dashboard created successfully: {result['dashboard_url']}")
            results.append(result)
            
            # Add a small delay between requests
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    return results

def test_auto_configured_dashboard(url, data_url):
    """Test creating a dashboard with auto-configuration."""
    endpoint = f"{url}/api/create-dashboard"
    
    # Minimal config with auto-configure enabled
    payload = {
        "data_url": data_url,
        "config": {
            "auto_configure": True,
            "style": {
                "theme": "colorful",
                "layout": "standard"
            }
        }
    }
    
    print(f"\nTesting auto-configured dashboard...")
    print(f"Sending request to {endpoint} with minimal configuration...")
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("Auto-configured dashboard created successfully!")
        print(f"Dashboard URL: {result['dashboard_url']}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Test dashboard generation API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--data", default="https://example.com/data.csv", help="Data URL")
    parser.add_argument("--test", default="all", choices=["basic", "styles", "auto", "all"], 
                        help="Test to run: basic, styles, auto, or all")
    
    args = parser.parse_args()
    
    # Run tests based on the selected option
    if args.test == "basic" or args.test == "all":
        print("\n=== Testing Basic Dashboard Creation ===")
        result = test_create_dashboard(args.url, args.data)
        if result:
            print(f"\nSuccess! Dashboard created at: {result['dashboard_url']}")
    
    if args.test == "styles" or args.test == "all":
        print("\n=== Testing Styled Dashboards ===")
        results = test_styled_dashboards(args.url, args.data)
        if results:
            print(f"\nSuccess! Created {len(results)} styled dashboards.")
    
    if args.test == "auto" or args.test == "all":
        print("\n=== Testing Auto-Configured Dashboard ===")
        result = test_auto_configured_dashboard(args.url, args.data)
        if result:
            print(f"\nSuccess! Auto-configured dashboard created at: {result['dashboard_url']}") 