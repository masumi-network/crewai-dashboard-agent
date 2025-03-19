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
    
    def download_data(self, url: str) -> pd.DataFrame:
        """
        Download data from URL and convert to pandas DataFrame.
        
        Args:
            url (str): URL to download data from (CSV, JSON, etc.)
            
        Returns:
            pd.DataFrame: DataFrame containing the data
        """
        logger.info(f"Downloading data from {url}")
        
        try:
            # Determine file type from URL
            file_extension = os.path.splitext(url)[1].lower()
            
            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file_path = tmp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
            
            # Read the file into a DataFrame based on file type
            if file_extension == '.csv':
                df = pd.read_csv(tmp_file_path)
            elif file_extension in ['.json', '.jsonl']:
                df = pd.read_json(tmp_file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(tmp_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading data: {str(e)}")
            raise
    
    def create_dashboard(self, 
                         data_url: str,
                         dashboard_config: Dict[str, Any]) -> Tuple[str, str]:
        """
        Create a Streamlit dashboard from a data URL and configuration.
        
        Args:
            data_url (str): URL to the data file (CSV, JSON, etc.)
            dashboard_config (dict): Configuration for the dashboard
                - title (str): Dashboard title
                - description (str): Dashboard description
                - metrics (list): List of metrics to display
                - charts (list): List of chart configurations
                - filters (list): List of filter configurations
                
        Returns:
            tuple: (dashboard_id, dashboard_path)
        """
        # Generate a unique ID for the dashboard
        dashboard_id = str(uuid.uuid4())[:8]
        dashboard_name = dashboard_config.get('title', 'dashboard').lower().replace(' ', '_')
        dashboard_filename = f"{dashboard_name}_{dashboard_id}.py"
        dashboard_path = os.path.join(self.dashboards_dir, dashboard_filename)
        
        logger.info(f"Creating dashboard {dashboard_id} at {dashboard_path}")
        
        try:
            # Download the data
            df = self.download_data(data_url)
            
            # Pre-process data if needed (convert date columns to datetime, etc.)
            df = self._preprocess_data(df, dashboard_config)
            
            # Generate the dashboard file from template
            self._generate_dashboard_file(dashboard_path, data_url, dashboard_config)
            
            return dashboard_id, dashboard_path
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise
    
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
            import socket
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