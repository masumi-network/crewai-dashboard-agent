from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import os
import logging
from typing import Dict, List, Any, Optional
import uuid

from . import utils
from .dashboard_builder import DashboardBuilder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize dashboard builder
dashboard_builder = DashboardBuilder(dashboards_dir="dashboards")

# In-memory storage for dashboard info (in a real app, use a database)
dashboard_registry = {}

# Pydantic models for request validation
class Chart(BaseModel):
    type: str
    title: str
    x: str
    y: str
    color: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None

class Metric(BaseModel):
    column: str
    label: Optional[str] = None
    aggregation: Optional[str] = "sum"

class Filter(BaseModel):
    type: str
    column: str
    label: Optional[str] = None

class StyleConfig(BaseModel):
    theme: Optional[str] = "default"  # default, dark, light, colorful
    layout: Optional[str] = "standard"  # standard, compact, expanded, grid
    columns: Optional[int] = 2  # Number of columns for grid layout
    color_scheme: Optional[str] = "default"  # Color scheme for charts

class DashboardConfig(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = ""
    metrics: List[Metric] = Field(default_factory=list)
    charts: List[Chart] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    style: Optional[StyleConfig] = None
    auto_configure: Optional[bool] = True

class CreateDashboardRequest(BaseModel):
    data_url: str
    config: Optional[DashboardConfig] = None
    download_package: Optional[bool] = False
    
class DashboardResponse(BaseModel):
    dashboard_id: str
    dashboard_url: str
    download_url: Optional[str] = None
    status: str = "success"
    message: str = "Dashboard created successfully"

@router.post("/create-dashboard", response_model=DashboardResponse)
async def create_dashboard(
    request: CreateDashboardRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new dashboard from configuration and data URL.
    
    Args:
        request: CreateDashboardRequest containing data_url and dashboard configuration
        background_tasks: BackgroundTasks for handling background processing
        
    Returns:
        DashboardResponse with dashboard_id, URL, and status
    """
    try:
        # Validate the data URL
        if not utils.validate_data_url(request.data_url):
            raise HTTPException(status_code=400, detail="Invalid data URL")
            
        # Convert Pydantic model to dict if provided
        config_dict = {} if request.config is None else request.config.dict()
        
        # Generate a unique ID for the dashboard
        dashboard_id = utils.generate_dashboard_id()
        
        # Create the dashboard
        try:
            _, dashboard_path = dashboard_builder.create_dashboard(
                data_url=request.data_url,
                dashboard_config=config_dict
            )
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating dashboard: {str(e)}")
            
        # Deploy the dashboard (in a real app, this would be handled by a separate process)
        try:
            dashboard_url, port = dashboard_builder.deploy_dashboard(dashboard_path)
        except Exception as e:
            logger.error(f"Error deploying dashboard: {str(e)}")
            # Even if deployment fails, we can still provide the download link
            dashboard_url = f"/dashboards/{dashboard_id}"
            port = None
            
        # Store dashboard info in registry
        dashboard_registry[dashboard_id] = {
            'id': dashboard_id,
            'path': dashboard_path,
            'url': dashboard_url,
            'port': port,
            'config': config_dict
        }
        
        # Create download package if requested
        download_url = None
        if request.download_package:
            try:
                package_path = dashboard_builder.package_dashboard(dashboard_path)
                # Use absolute URL for download_url
                download_url = f"/api/download/{os.path.basename(package_path)}"
                
                # Add package path to registry
                dashboard_registry[dashboard_id]['package_path'] = package_path
                
                logger.info(f"Created download package at {package_path}")
            except Exception as e:
                logger.error(f"Error packaging dashboard: {str(e)}")
                # Failure to package shouldn't fail the whole request
                
        return DashboardResponse(
            dashboard_id=dashboard_id,
            dashboard_url=dashboard_url,
            download_url=download_url
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as is
        raise
    except Exception as e:
        logger.exception("Unexpected error creating dashboard")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/dashboards", response_model=List[Dict[str, Any]])
async def list_dashboards():
    """
    List all created dashboards.
    
    Returns:
        List of dashboard information
    """
    return [
        {
            'id': info['id'],
            'url': info['url'],
            'title': info['config'].get('title', 'Untitled Dashboard'),
        }
        for info in dashboard_registry.values()
    ]

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """
    Get information about a specific dashboard.
    
    Args:
        dashboard_id: ID of the dashboard
        
    Returns:
        Dashboard information
    """
    if dashboard_id not in dashboard_registry:
        raise HTTPException(status_code=404, detail="Dashboard not found")
        
    info = dashboard_registry[dashboard_id]
    
    return {
        'id': info['id'],
        'url': info['url'],
        'title': info['config'].get('title', 'Untitled Dashboard'),
        'config': info['config']
    }

@router.get("/download/{filename}")
async def download_dashboard(filename: str):
    """
    Download a packaged dashboard.
    
    Args:
        filename: Name of the file to download
        
    Returns:
        FileResponse with the dashboard package
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/zip"
    )

@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """
    Delete a dashboard.
    
    Args:
        dashboard_id: ID of the dashboard to delete
        
    Returns:
        Confirmation message
    """
    if dashboard_id not in dashboard_registry:
        raise HTTPException(status_code=404, detail="Dashboard not found")
        
    info = dashboard_registry[dashboard_id]
    
    # Delete the dashboard file
    try:
        if os.path.exists(info['path']):
            os.remove(info['path'])
            
        # Delete the package if it exists
        if 'package_path' in info and os.path.exists(info['package_path']):
            os.remove(info['package_path'])
    except Exception as e:
        logger.error(f"Error deleting dashboard files: {str(e)}")
        
    # Remove from registry
    del dashboard_registry[dashboard_id]
    
    return {"status": "success", "message": f"Dashboard {dashboard_id} deleted successfully"} 