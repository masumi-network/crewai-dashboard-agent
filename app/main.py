from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import uvicorn

from .api import router as api_router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CrewAI Dashboard Generator",
    description="API for generating interactive dashboards from data",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

# Mount static files (for development)
@app.on_event("startup")
async def startup_event():
    # Create directories if they don't exist
    os.makedirs("dashboards", exist_ok=True)
    
    # Log startup information
    logger.info("CrewAI Dashboard Generator API started")
    logger.info(f"Documentation available at http://localhost:8000/docs")

@app.get("/")
async def root():
    """
    Root endpoint returns API information.
    """
    return {
        "name": "CrewAI Dashboard Generator API",
        "version": "0.1.0",
        "docs_url": "/docs",
        "api_prefix": "/api",
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 