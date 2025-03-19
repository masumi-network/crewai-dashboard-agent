import os
import json
import uuid
import logging
import re
from typing import Dict, List, Any, Optional, Union
from fastapi import HTTPException
from pydantic import ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's safe for file system operations.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace spaces with underscores and remove invalid characters
    sanitized = re.sub(r'[^\w\-\.]', '_', filename.lower().replace(' ', '_'))
    return sanitized

def validate_dashboard_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and standardize dashboard configuration.
    
    Args:
        config (dict): Dashboard configuration to validate
        
    Returns:
        dict: Validated and standardized configuration
        
    Raises:
        HTTPException: If the configuration is invalid
    """
    try:
        # Check required fields
        if not config.get('title'):
            raise ValueError("Dashboard title is required")
            
        # Standardize metrics format
        metrics = config.get('metrics', [])
        if isinstance(metrics, list):
            for i, metric in enumerate(metrics):
                if isinstance(metric, str):
                    # Convert string metrics to dict format
                    metrics[i] = {'column': metric, 'label': metric, 'aggregation': 'sum'}
                elif not metric.get('column'):
                    raise ValueError(f"Metric at index {i} is missing 'column' field")
        else:
            raise ValueError("Metrics must be a list")
            
        # Standardize charts format
        charts = config.get('charts', [])
        if isinstance(charts, list):
            for i, chart in enumerate(charts):
                if not chart.get('type'):
                    chart['type'] = 'bar'  # Default chart type
                if not chart.get('x') or not chart.get('y'):
                    raise ValueError(f"Chart at index {i} is missing 'x' or 'y' field")
        else:
            raise ValueError("Charts must be a list")
            
        # Standardize filters format
        filters = config.get('filters', [])
        if isinstance(filters, list):
            for i, filter_config in enumerate(filters):
                if not filter_config.get('type'):
                    filter_config['type'] = 'categorical'  # Default filter type
                if not filter_config.get('column'):
                    raise ValueError(f"Filter at index {i} is missing 'column' field")
        else:
            raise ValueError("Filters must be a list")
            
        # Update the config with standardized values
        config['metrics'] = metrics
        config['charts'] = charts
        config['filters'] = filters
        
        return config
        
    except ValueError as e:
        logger.error(f"Invalid dashboard configuration: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Error validating dashboard configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

def get_file_extension_from_url(url: str) -> str:
    """
    Extract file extension from URL.
    
    Args:
        url (str): URL to extract extension from
        
    Returns:
        str: File extension (with dot)
    """
    # Extract the filename from the URL
    filename = os.path.basename(url.split('?')[0])
    
    # Get the extension
    _, extension = os.path.splitext(filename)
    
    return extension.lower()

def generate_dashboard_id() -> str:
    """
    Generate a unique dashboard ID.
    
    Returns:
        str: Unique dashboard ID
    """
    return str(uuid.uuid4())[:8]

def validate_data_url(url: str) -> bool:
    """
    Validate if a URL is suitable for data download.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # More flexible URL validation for development
    url_pattern = re.compile(
        r'^(http|https)://'  # http:// or https://
        r'([a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}|'  # domain.com
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP address
        r'(:\d+)?'  # optional port
        r'(/[-a-zA-Z0-9_%./]*)*'  # optional path
        r'(\?[;&a-zA-Z0-9%_.,/=:~-]*)?'  # optional query string
        r'(#[-a-zA-Z0-9_]*)?$'  # optional fragment
    )
    
    if not url_pattern.match(url):
        logger.warning(f"URL validation failed for: {url}")
        return False
        
    # Check file extension
    extension = get_file_extension_from_url(url)
    valid_extensions = ['.csv', '.json', '.jsonl', '.xlsx', '.xls']
    
    if extension not in valid_extensions:
        logger.warning(f"Unsupported file extension: {extension}")
        return False
        
    return True 