import os
import json
import uuid
import pandas as pd
import requests
import tempfile
import shutil
import subprocess
import time
import logging
from pathlib import Path
import jinja2
from typing import Dict, List, Any, Optional, Tuple, Union
import re
import socket

from .templates.base_template import TemplateRenderer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardBuilder:
    """
    A class for building and deploying Streamlit dashboards dynamically.
    """
    
    def __init__(self, dashboards_dir: str = "dashboards"):
        """
        Initialize the dashboard builder.
        
        Args:
            dashboards_dir (str): Directory where dashboard files will be stored
        """
        self.dashboards_dir = dashboards_dir
        
        # Create dashboards directory if it doesn't exist
        os.makedirs(self.dashboards_dir, exist_ok=True)
        
        # Template environment for generating dashboard files
        template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), "templates"))
        self.template_env = jinja2.Environment(loader=template_loader)
        
        # Initialize template renderer
        self.template_renderer = TemplateRenderer()
    
    def _download_data(self, data_url):
        """
        Download data from a URL.
        
        Args:
            data_url (str): URL to the data file
            
        Returns:
            bytes: Raw data content
        """
        logger.info(f"Downloading data from {data_url}")
        
        try:
            response = requests.get(data_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading data: {str(e)}")
            raise Exception(f"Failed to download data from {data_url}: {str(e)}")
            
    def _load_data(self, data_content):
        """
        Load data content into a pandas DataFrame.
        
        Args:
            data_content (bytes): Raw data content
            
        Returns:
            pd.DataFrame: Loaded data frame
        """
        import io
        
        try:
            # Try to load as CSV
            return pd.read_csv(io.BytesIO(data_content))
        except Exception as csv_error:
            logger.warning(f"Could not load as CSV: {str(csv_error)}")
            
            try:
                # Try to load as JSON
                return pd.read_json(io.BytesIO(data_content))
            except Exception as json_error:
                logger.warning(f"Could not load as JSON: {str(json_error)}")
                
                # Try other formats if needed
                # ...
                
                raise Exception("Could not load data: unsupported format")
    
    def create_dashboard(self, data_url, dashboard_config=None):
        """
        Create a new dashboard based on data and configuration.
        
        Args:
            data_url (str): URL to the data source (CSV, JSON, etc.)
            dashboard_config (dict, optional): Dashboard configuration including title, charts, metrics, etc.
            
        Returns:
            tuple: (dashboard_id, dashboard_path)
        """
        # Default empty config if None provided
        if dashboard_config is None:
            dashboard_config = {}
            
        # Check for auto-configure flag
        auto_configure = dashboard_config.get('auto_configure', True)
            
        # Download and analyze data
        try:
            data = self._download_data(data_url)
            df = self._load_data(data)
            
            # Auto-generate dashboard elements if needed
            if auto_configure or 'title' not in dashboard_config or not dashboard_config['title']:
                # Generate title if not provided
                dashboard_config['title'] = dashboard_config.get('title') or f"Data Dashboard - {pd.Timestamp.now().strftime('%Y-%m-%d')}"
                
                # Generate description if not provided
                if 'description' not in dashboard_config or not dashboard_config['description']:
                    dashboard_config['description'] = f"Automatically generated dashboard for {data_url}"
                
                # Generate metrics if not provided
                if 'metrics' not in dashboard_config or not dashboard_config['metrics']:
                    dashboard_config['metrics'] = self._suggest_metrics(df)
                
                # Generate charts if not provided
                if 'charts' not in dashboard_config or not dashboard_config['charts']:
                    dashboard_config['charts'] = self._suggest_chart_types(df)
                
                # Generate filters if not provided
                if 'filters' not in dashboard_config or not dashboard_config['filters']:
                    dashboard_config['filters'] = self._suggest_filters(df)
                    
                # Set up style if not provided
                if 'style' not in dashboard_config:
                    dashboard_config['style'] = {
                        'theme': 'default',
                        'layout': 'standard',
                        'columns': 2,
                        'color_scheme': 'default'
                    }
            
            # Generate a unique dashboard ID
            dashboard_id = str(uuid.uuid4())[:8]
            
            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', dashboard_config['title']).strip().lower()
            clean_title = re.sub(r'[-\s]+', '-', clean_title)
            
            # Create a unique filename
            filename = f"{clean_title}-{dashboard_id}"
            
            # Generate dashboard HTML
            dashboard_html = self.template_renderer.render_dashboard(
                title=dashboard_config['title'],
                description=dashboard_config['description'],
                df=df,
                charts_config=dashboard_config.get('charts', []),
                metrics_config=dashboard_config.get('metrics', []),
                filters_config=dashboard_config.get('filters', []),
                style_config=dashboard_config.get('style', {})
            )
            
            # Create dashboard directory if it doesn't exist
            os.makedirs(self.dashboards_dir, exist_ok=True)
            
            # Save dashboard HTML
            dashboard_path = os.path.join(self.dashboards_dir, f"{filename}")
            os.makedirs(dashboard_path, exist_ok=True)
            
            # Save the data file
            data_path = os.path.join(dashboard_path, "data.csv")
            df.to_csv(data_path, index=False)
            
            # Save the dashboard file
            dashboard_file = os.path.join(dashboard_path, "index.html")
            with open(dashboard_file, "w") as f:
                f.write(dashboard_html)
                
            # Save dashboard config for later reference
            config_path = os.path.join(dashboard_path, "config.json")
            with open(config_path, "w") as f:
                json.dump(dashboard_config, f, indent=2)
                
            logger.info(f"Created dashboard at {dashboard_path}")
            
            return dashboard_id, dashboard_path
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise e
    
    def _preprocess_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocess the data before creating the dashboard.
        
        Args:
            df (pd.DataFrame): The data to preprocess
            config (dict): Dashboard configuration
            
        Returns:
            pd.DataFrame: Preprocessed DataFrame
        """
        # Convert date columns to datetime
        date_filters = [f for f in config.get('filters', []) if f.get('type') == 'date_range']
        for date_filter in date_filters:
            column = date_filter.get('column')
            if column and column in df.columns:
                try:
                    df[column] = pd.to_datetime(df[column])
                except Exception as e:
                    logger.warning(f"Could not convert column {column} to datetime: {str(e)}")
        
        return df
    
    def _generate_dashboard_file(self, 
                                dashboard_path: str, 
                                data_url: str, 
                                config: Dict[str, Any]) -> None:
        """
        Generate a Streamlit dashboard file.
        
        Args:
            dashboard_path (str): Path to save the dashboard file
            data_url (str): URL to the data
            config (dict): Dashboard configuration
        """
        # Convert config to JSON string and then replace JSON null with Python None
        config_json = json.dumps(config, indent=4)
        config_json = config_json.replace(': null', ': None')
        
        # Extract title for page_config
        title = config.get('title', 'CrewAI Dashboard')
        
        dashboard_code = f"""
import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="{title}",
    page_icon="📊",
    layout="wide"
)

# Add the parent directory to sys.path to import templates
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from app.templates.base_template import render_dashboard

# Configuration
CONFIG = {config_json}

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("{data_url}")
        
        # Convert date columns to datetime
        date_filters = [f for f in CONFIG.get('filters', []) if f.get('type') == 'date_range']
        for date_filter in date_filters:
            column = date_filter.get('column')
            if column and column in df.columns:
                df[column] = pd.to_datetime(df[column])
                
        return df
    except Exception as e:
        st.error(f"Error loading data: {{str(e)}}")
        return None

# Load the data
data = load_data()

# Render the dashboard if data is loaded
if data is not None:
    render_dashboard(data, CONFIG)
else:
    st.error("Failed to load data. Please check the data URL.")
"""
        
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_code)
            
        logger.info(f"Dashboard file generated at {dashboard_path}")
    
    def deploy_dashboard(self, dashboard_path: str, port: Optional[int] = None) -> Tuple[str, int]:
        """
        Deploy a Streamlit dashboard.
        
        Args:
            dashboard_path (str): Path to the dashboard file
            port (int, optional): Port to run the dashboard on (if None, a random port will be used)
            
        Returns:
            tuple: (url, port) where url is the URL to access the dashboard
        """
        # For local deployment, start a new Streamlit process
        if port is None:
            # Find an available port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 0))
            port = s.getsockname()[1]
            s.close()
        
        logger.info(f"Deploying dashboard at {dashboard_path} on port {port}")
        
        # In a production environment, you would need to manage these processes
        # or use a service like Docker or Kubernetes to manage the deployments.
        # For simplicity, we'll use a subprocess for local testing.
        
        # Run Streamlit in a separate process
        process = subprocess.Popen(
            ["streamlit", "run", dashboard_path, "--server.port", str(port), "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is not None:
            # Process has terminated, read stderr
            _, stderr = process.communicate()
            error_message = stderr.decode('utf-8')
            logger.error(f"Streamlit process failed to start: {error_message}")
            raise RuntimeError(f"Failed to start Streamlit: {error_message}")
        
        # For local testing, return localhost URL
        url = f"http://localhost:{port}"
        
        return url, port
    
    def package_dashboard(self, dashboard_path: str) -> str:
        """
        Package a dashboard for download.
        
        Args:
            dashboard_path (str): Path to the dashboard file
            
        Returns:
            str: Path to the ZIP file
        """
        dashboard_name = os.path.splitext(os.path.basename(dashboard_path))[0]
        temp_dir = tempfile.mkdtemp()
        zip_path = f"{dashboard_name}.zip"
        
        logger.info(f"Packaging dashboard {dashboard_path} to {zip_path}")
        
        try:
            # Create a directory structure for the package
            package_dir = os.path.join(temp_dir, dashboard_name)
            os.makedirs(package_dir, exist_ok=True)
            
            # Copy the dashboard file
            shutil.copy(dashboard_path, os.path.join(package_dir, os.path.basename(dashboard_path)))
            logger.info(f"Copied dashboard file to {os.path.join(package_dir, os.path.basename(dashboard_path))}")
            
            # Copy the template file
            template_path = os.path.join(os.path.dirname(__file__), "templates", "base_template.py")
            templates_dir = os.path.join(package_dir, "templates")
            os.makedirs(templates_dir, exist_ok=True)
            shutil.copy(template_path, os.path.join(templates_dir, "base_template.py"))
            logger.info(f"Copied template file to {os.path.join(templates_dir, 'base_template.py')}")
            
            # Create a README file
            readme_path = os.path.join(package_dir, "README.md")
            readme_content = f"""# {dashboard_name.replace('_', ' ').title()} Dashboard

This is a Streamlit dashboard generated by CrewAI Dashboard Generator.

## Running the Dashboard

1. Install the required dependencies:
   ```
   pip install streamlit pandas plotly
   ```

2. Run the dashboard:
   ```
   streamlit run {os.path.basename(dashboard_path)}
   ```
"""
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            logger.info(f"Created README file at {readme_path}")
            
            # Create a requirements.txt file
            req_path = os.path.join(package_dir, "requirements.txt")
            req_content = """streamlit==1.28.0
pandas==2.1.3
plotly==5.18.0
"""
            with open(req_path, 'w') as f:
                f.write(req_content)
            logger.info(f"Created requirements.txt file at {req_path}")
            
            # Create a ZIP file
            archive_path = shutil.make_archive(dashboard_name, 'zip', temp_dir, dashboard_name)
            logger.info(f"Created ZIP archive at {archive_path}")
            
            # Move the ZIP file to the current directory
            if os.path.exists(zip_path):
                os.remove(zip_path)
            shutil.move(archive_path, zip_path)
            logger.info(f"Moved ZIP archive to {zip_path}")
            
            # Verify the file exists
            if os.path.exists(zip_path):
                logger.info(f"ZIP file exists at {zip_path} with size {os.path.getsize(zip_path)} bytes")
            else:
                logger.error(f"ZIP file does not exist at {zip_path}")
            
            # Get the absolute path
            abs_path = os.path.abspath(zip_path)
            logger.info(f"Dashboard packaged at {abs_path}")
            
            return abs_path
            
        except Exception as e:
            logger.error(f"Error packaging dashboard: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up the temporary directory
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {str(e)}")
    
    def get_dashboard_url(self, dashboard_id: str, base_url: str = "http://localhost") -> str:
        """
        Get the URL for a deployed dashboard.
        
        Args:
            dashboard_id (str): ID of the dashboard
            base_url (str): Base URL for the dashboard
            
        Returns:
            str: URL to access the dashboard
        """
        # In a production environment, this would look up the dashboard in a database
        # and return the actual URL where it's deployed.
        # For local testing, we'll just return a constructed URL.
        return f"{base_url}/dashboards/{dashboard_id}"
    
    def _suggest_chart_types(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggests appropriate charts based on data characteristics.
        
        Args:
            df (pd.DataFrame): The data to analyze
            
        Returns:
            list: List of chart configurations
        """
        suggested_charts = []
        
        # Get column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        
        # If we have date columns and numeric columns, suggest time series charts
        if date_cols and numeric_cols:
            for date_col in date_cols[:1]:  # Limit to first date column
                for num_col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    suggested_charts.append({
                        'type': 'line',
                        'title': f'{num_col} Over Time',
                        'x': date_col,
                        'y': num_col
                    })
        
        # If we have categorical columns and numeric columns, suggest bar charts and pie charts
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols[:2]:  # Limit to first 2 categorical columns
                for num_col in numeric_cols[:2]:  # Limit to first 2 numeric columns
                    # Bar chart for comparison
                    suggested_charts.append({
                        'type': 'bar',
                        'title': f'{num_col} by {cat_col}',
                        'x': cat_col,
                        'y': num_col
                    })
                    
                    # Pie chart for distribution
                    if len(df[cat_col].unique()) <= 10:  # Only if not too many categories
                        suggested_charts.append({
                            'type': 'pie',
                            'title': f'{num_col} Distribution by {cat_col}',
                            'x': cat_col,
                            'y': num_col
                        })
        
        # If we have numeric columns only, suggest scatter plots for relationships
        if len(numeric_cols) >= 2:
            # Scatter plot for first two numeric columns
            suggested_charts.append({
                'type': 'scatter',
                'title': f'Relationship between {numeric_cols[0]} and {numeric_cols[1]}',
                'x': numeric_cols[0],
                'y': numeric_cols[1]
            })
        
        return suggested_charts

    def _suggest_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggests appropriate metrics based on data characteristics.
        
        Args:
            df (pd.DataFrame): The data to analyze
            
        Returns:
            list: List of metric configurations
        """
        suggested_metrics = []
        
        # Get numeric columns for metrics
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Create sum metrics for numeric columns
        for col in numeric_cols[:4]:  # Limit to first 4 numeric columns
            # Format column name for display
            display_name = col.replace('_', ' ').title()
            
            # Determine appropriate aggregation
            if 'count' in col.lower() or 'quantity' in col.lower() or 'units' in col.lower():
                agg = 'sum'
                label = f'Total {display_name}'
            elif 'price' in col.lower() or 'cost' in col.lower() or 'revenue' in col.lower() or 'sales' in col.lower():
                agg = 'sum'
                label = f'Total {display_name}'
            elif 'rate' in col.lower() or 'ratio' in col.lower() or 'percentage' in col.lower() or 'percent' in col.lower():
                agg = 'mean'
                label = f'Average {display_name}'
            else:
                # Default to sum for other numeric columns
                agg = 'sum'
                label = f'Total {display_name}'
            
            suggested_metrics.append({
                'column': col,
                'label': label,
                'aggregation': agg
            })
            
            # If it makes sense, also add average metric for some columns
            if agg == 'sum' and not ('ratio' in col.lower() or 'rate' in col.lower()):
                suggested_metrics.append({
                    'column': col,
                    'label': f'Average {display_name}',
                    'aggregation': 'mean'
                })
        
        return suggested_metrics

    def _suggest_filters(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggests appropriate filters based on data characteristics.
        
        Args:
            df (pd.DataFrame): The data to analyze
            
        Returns:
            list: List of filter configurations
        """
        suggested_filters = []
        
        # Get column types
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Add date filters - these are usually very useful
        for col in date_cols:
            suggested_filters.append({
                'type': 'date_range',
                'column': col
            })
        
        # Add categorical filters - limit to those with a reasonable number of unique values
        for col in categorical_cols:
            if len(df[col].unique()) <= 30:  # Avoid columns with too many unique values
                suggested_filters.append({
                    'type': 'categorical',
                    'column': col
                })
        
        # Add numeric range filters for select numeric columns (like price, age, etc.)
        for col in numeric_cols:
            # Only include numeric filters if the range makes sense (not binary values)
            if df[col].nunique() > 5 and any(keyword in col.lower() for keyword in ['price', 'cost', 'amount', 'age', 'time', 'duration', 'score']):
                suggested_filters.append({
                    'type': 'numeric_range',
                    'column': col
                })
        
        return suggested_filters