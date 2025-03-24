import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateRenderer:
    """Base template renderer for dashboards"""
    
    def render_dashboard(self, 
                        title: str, 
                        description: str, 
                        df: pd.DataFrame,
                        charts_config: List[Dict[str, Any]],
                        metrics_config: List[Dict[str, Any]],
                        filters_config: List[Dict[str, Any]],
                        style_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a full dashboard HTML using the provided configuration.
        
        Args:
            title: Dashboard title
            description: Dashboard description
            df: Pandas DataFrame with the data
            charts_config: List of chart configurations
            metrics_config: List of metric configurations
            filters_config: List of filter configurations
            style_config: Style and layout configuration (optional)
            
        Returns:
            str: Complete HTML for the dashboard
        """
        # Default style config if not provided
        if style_config is None:
            style_config = {
                'theme': 'default',
                'layout': 'standard',
                'columns': 2,
                'color_scheme': 'default'
            }
            
        # Apply the theme styling
        theme_styles = self.apply_styling(style_config.get('theme', 'default'))
        
        # Determine layout
        layout = style_config.get('layout', 'standard')
        grid_columns = style_config.get('columns', 2)
        color_scheme = style_config.get('color_scheme', 'default')
        
        # Generate dashboard timestamp
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Render filters section
        filters_html = self.render_filters(df, filters_config)
        
        # Render metrics and charts based on layout
        if layout == 'compact':
            # Compact layout: Metrics as inline small boxes, charts stacked
            metrics_html = self.display_metrics(df, metrics_config, is_sidebar=False, compact=True)
            charts_html = self.render_charts(df, charts_config, style_config)
            main_content = f"""
                <div class="dashboard-content">
                    <div class="metrics-container compact">{metrics_html}</div>
                    <div class="charts-container">{charts_html}</div>
                </div>
            """
        elif layout == 'expanded':
            # Expanded layout: Full-width sections for both metrics and charts
            metrics_html = self.display_metrics(df, metrics_config, is_sidebar=False, compact=False)
            charts_html = self.render_charts(df, charts_config, style_config)
            main_content = f"""
                <div class="dashboard-content">
                    <div class="metrics-container expanded">{metrics_html}</div>
                    <div class="charts-container expanded">{charts_html}</div>
                </div>
            """
        elif layout == 'grid':
            # Grid layout: Everything in a grid with specified columns
            metrics_html = self.display_metrics(df, metrics_config, is_sidebar=False, compact=False)
            charts_html = self.render_charts(df, charts_config, style_config)
            main_content = f"""
                <div class="dashboard-content grid-layout" style="grid-template-columns: repeat({grid_columns}, 1fr);">
                    {metrics_html}
                    {charts_html}
                </div>
            """
        else:  # standard layout
            # Standard layout: Metrics in sidebar, charts in main area
            metrics_html = self.display_metrics(df, metrics_config, is_sidebar=True)
            charts_html = self.render_charts(df, charts_config, style_config)
            main_content = f"""
                <div class="dashboard-layout">
                    <div class="sidebar">
                        <div class="metrics-container">{metrics_html}</div>
                    </div>
                    <div class="main-content">
                        <div class="charts-container">{charts_html}</div>
                    </div>
                </div>
            """
            
        # Create the full HTML document
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css">
            <style>
                {theme_styles}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <header>
                    <div class="header-content">
                        <h1><i class="bi bi-bar-chart-line-fill"></i> {title}</h1>
                        <p>{description}</p>
                    </div>
                </header>
                
                {filters_html}
                
                {main_content}
                
                <footer>
                    <div class="footer-content">
                        <p><i class="bi bi-clock"></i> Last updated: {timestamp}</p>
                        <p>Powered by CrewAI Dashboard Generator</p>
                    </div>
                </footer>
            </div>
            
            <script>
                // Dashboard initialization and filter handling
                $(document).ready(function() {{
                    // Add filter event handlers
                    $('.filter-input').on('change', function() {{
                        applyFilters();
                    }});
                    
                    // Setup toggle buttons for metrics if present
                    $('.metric-box').each(function() {{
                        $(this).append('<div class="metric-trend"><i class="bi bi-arrow-up-right"></i></div>');
                    }});
                    
                    // Function to apply filters
                    function applyFilters() {{
                        console.log('Applying filters...');
                        // In a real implementation, this would filter the data and update charts
                        // For this demo, we'll just log the selected filters
                        
                        $('.filter-input').each(function() {{
                            console.log($(this).attr('name') + ': ' + $(this).val());
                        }});
                        
                        // Show a notification
                        showNotification('Filters applied!');
                    }}
                    
                    // Notification function
                    function showNotification(message) {{
                        // Create notification element if it doesn't exist
                        if ($('#notification').length === 0) {{
                            $('body').append('<div id="notification"></div>');
                        }}
                        
                        // Set message and display notification
                        $('#notification').text(message);
                        $('#notification').addClass('show');
                        
                        // Hide notification after 3 seconds
                        setTimeout(function() {{
                            $('#notification').removeClass('show');
                        }}, 3000);
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        return html
    
    def apply_styling(self, theme):
        """Apply CSS styling based on the selected theme"""
        # Common styles shared across themes
        common_styles = """
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                padding: 0;
                margin: 0;
            }
            
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0;
            }
            
            header {
                padding: 30px;
                margin-bottom: 30px;
                border-radius: 0;
            }
            
            header h1 {
                font-weight: 600;
                margin-bottom: 10px;
                font-size: 28px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            header h1 i {
                font-size: 28px;
            }
            
            header p {
                font-size: 16px;
                opacity: 0.9;
            }
            
            .dashboard-layout {
                display: flex;
                gap: 25px;
                padding: 0 20px 30px 20px;
            }
            
            .sidebar {
                flex: 0 0 300px;
            }
            
            .main-content {
                flex: 1;
            }
            
            /* Grid layout */
            .grid-layout {
                display: grid;
                gap: 25px;
                padding: 0 20px 30px 20px;
            }
            
            /* Metric boxes */
            .metrics-container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .metrics-container.compact {
                display: flex;
                flex-direction: row;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
                padding: 0 20px;
            }
            
            .metrics-container.compact .metric-box {
                flex: 1 0 200px;
            }
            
            .metric-box {
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                position: relative;
                overflow: hidden;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
            }
            
            .metric-box:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.12);
            }
            
            .metric-icon {
                font-size: 24px;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
            }
            
            .metric-content {
                flex: 1;
            }
            
            .metric-label {
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
            
            .metric-value {
                font-size: 28px;
                font-weight: 700;
                line-height: 1.2;
                margin-bottom: 5px;
            }
            
            .metric-trend {
                font-size: 12px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .metric-trend.positive {
                color: #34a853;
            }
            
            .metric-trend.negative {
                color: #ea4335;
            }
            
            /* Charts */
            .charts-container {
                display: flex;
                flex-direction: column;
                gap: 30px;
            }
            
            .chart-container {
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .chart-container:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.12);
            }
            
            .chart-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            /* Filters */
            .filters-section {
                margin: 0 20px 30px 20px;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            
            .filters-section h3 {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .filters-container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .filter-columns {
                display: grid;
                gap: 20px;
            }
            
            .filter-group {
                margin-bottom: 10px;
            }
            
            .filter-label {
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .filter-input {
                width: 100%;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            
            .date-range-filter {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .date-inputs {
                display: flex;
                gap: 10px;
            }
            
            .date-input-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .date-input-group label {
                font-size: 12px;
                color: #888;
            }
            
            .numeric-range-filter {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .range-values {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
            }
            
            .range-sliders {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            input[type="range"].range-slider {
                width: 100%;
                height: 6px;
                -webkit-appearance: none;
                border-radius: 5px;
                outline: none;
            }
            
            input[type="range"].range-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                cursor: pointer;
            }
            
            .filter-actions {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                border: none;
                transition: all 0.2s ease;
            }
            
            /* Footer */
            footer {
                padding: 20px;
                font-size: 12px;
                text-align: center;
                margin-top: 30px;
            }
            
            footer p {
                margin: 5px 0;
            }
            
            /* Notification */
            #notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                background-color: #333;
                color: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(150%);
                transition: transform 0.3s ease;
                z-index: 1000;
                font-size: 14px;
            }
            
            #notification.show {
                transform: translateX(0);
            }
            
            @media (max-width: 768px) {
                .dashboard-layout {
                    flex-direction: column;
                }
                
                .sidebar {
                    flex: none;
                    width: 100%;
                }
                
                .filter-columns {
                    grid-template-columns: 1fr !important;
                }
                
                .metrics-container.compact .metric-box {
                    flex: 1 0 100%;
                }
            }
        """
        
        if theme == 'dark':
            return common_styles + """
                body {
                    background-color: #121212;
                    color: #e0e0e0;
                }
                
                header {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                }
                
                .metric-box {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                
                .metric-icon {
                    background-color: rgba(100, 181, 246, 0.2);
                    color: #64b5f6;
                }
                
                .metric-label {
                    color: #aaa;
                }
                
                .metric-value {
                    color: #64b5f6;
                }
                
                .chart-container {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                }
                
                .chart-title {
                    color: #e0e0e0;
                }
                
                .filters-section {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                }
                
                .filters-section h3 {
                    color: #e0e0e0;
                }
                
                .filter-label {
                    color: #aaa;
                }
                
                .filter-input {
                    background-color: #2c2c2c;
                    border: 1px solid #444;
                    color: #e0e0e0;
                }
                
                .filter-input:focus {
                    border-color: #64b5f6;
                    outline: none;
                }
                
                input[type="range"].range-slider {
                    background-color: #333;
                }
                
                input[type="range"].range-slider::-webkit-slider-thumb {
                    background-color: #64b5f6;
                }
                
                .btn.btn-primary {
                    background-color: #2a5298;
                    color: white;
                }
                
                .btn.btn-primary:hover {
                    background-color: #1e3c72;
                }
                
                .btn.btn-secondary {
                    background-color: #333;
                    color: #e0e0e0;
                }
                
                .btn.btn-secondary:hover {
                    background-color: #444;
                }
                
                date-input-group label {
                    color: #888;
                }
                
                footer {
                    color: #888;
                    border-top: 1px solid #333;
                }
                
                select.filter-input {
                    appearance: none;
                    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23e0e0e0%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
                    background-repeat: no-repeat;
                    background-position: right .7em top 50%;
                    background-size: .65em auto;
                    padding-right: 1.4em;
                }
            """
        elif theme == 'light':
            return common_styles + """
                body {
                    background-color: #f8f9fa;
                    color: #343a40;
                }
                
                header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                }
                
                .metric-box {
                    background-color: white;
                    border: 1px solid #e9ecef;
                }
                
                .metric-icon {
                    background-color: rgba(99, 102, 241, 0.1);
                    color: #6366f1;
                }
                
                .metric-label {
                    color: #6c757d;
                }
                
                .metric-value {
                    color: #6366f1;
                }
                
                .chart-container {
                    background-color: white;
                    border: 1px solid #e9ecef;
                }
                
                .filters-section {
                    background-color: white;
                    border: 1px solid #e9ecef;
                }
                
                .filter-label {
                    color: #495057;
                }
                
                .filter-input {
                    background-color: white;
                    border: 1px solid #ced4da;
                    color: #495057;
                }
                
                .filter-input:focus {
                    border-color: #6366f1;
                    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
                    outline: none;
                }
                
                input[type="range"].range-slider {
                    background-color: #e9ecef;
                }
                
                input[type="range"].range-slider::-webkit-slider-thumb {
                    background-color: #6366f1;
                }
                
                .btn.btn-primary {
                    background-color: #6366f1;
                    color: white;
                }
                
                .btn.btn-primary:hover {
                    background-color: #4f46e5;
                }
                
                .btn.btn-secondary {
                    background-color: #e9ecef;
                    color: #495057;
                }
                
                .btn.btn-secondary:hover {
                    background-color: #ced4da;
                }
                
                footer {
                    color: #6c757d;
                    border-top: 1px solid #e9ecef;
                }
                
                select.filter-input {
                    appearance: none;
                    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23343a40%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
                    background-repeat: no-repeat;
                    background-position: right .7em top 50%;
                    background-size: .65em auto;
                    padding-right: 1.4em;
                }
            """
        elif theme == 'colorful':
            return common_styles + """
                body {
                    background-color: #f0f8ff;
                    color: #333;
                }
                
                header {
                    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                    color: white;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                }
                
                .metric-box {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border: none;
                    position: relative;
                    transition: all 0.3s ease;
                }
                
                .metric-box::before {
                    content: '';
                    position: absolute;
                    top: -2px;
                    left: -2px;
                    right: -2px;
                    bottom: -2px;
                    background: linear-gradient(45deg, #ff00cc, #3333ff, #00ccff, #6a11cb);
                    border-radius: 14px;
                    z-index: -1;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }
                
                .metric-box:hover::before {
                    opacity: 1;
                }
                
                .metric-icon {
                    background: rgba(94, 53, 177, 0.15);
                    color: #5e35b1;
                }
                
                .metric-label {
                    color: #4a4a4a;
                    font-weight: 600;
                }
                
                .metric-value {
                    color: #5e35b1;
                    font-size: 36px;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }
                
                .chart-container {
                    background-color: #ffffff;
                    border: none;
                    border-radius: 16px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
                    position: relative;
                    overflow: hidden;
                }
                
                .chart-container::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 6px;
                    background: linear-gradient(90deg, #fc466b, #3f5efb);
                    z-index: 1;
                }
                
                .chart-title {
                    font-size: 20px;
                    font-weight: 700;
                    color: #4a4a4a;
                }
                
                .filters-section {
                    background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                    border: none;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                }
                
                .filters-section h3 {
                    color: #1a237e;
                    font-weight: 700;
                }
                
                .filter-label {
                    color: #455a64;
                }
                
                .filter-input {
                    background-color: rgba(255,255,255,0.8);
                    border: 1px solid #b2ebf2;
                    color: #333;
                    border-radius: 10px;
                    transition: all 0.2s ease;
                }
                
                .filter-input:focus {
                    background-color: white;
                    border-color: #3f5efb;
                    outline: none;
                    box-shadow: 0 0 0 3px rgba(63, 94, 251, 0.2);
                }
                
                input[type="range"].range-slider {
                    background: linear-gradient(90deg, #00c9ff, #92fe9d);
                }
                
                input[type="range"].range-slider::-webkit-slider-thumb {
                    background-color: #1a237e;
                    box-shadow: 0 0 4px rgba(0,0,0,0.3);
                }
                
                .btn.btn-primary {
                    background: linear-gradient(90deg, #fc466b, #3f5efb);
                    color: white;
                    border: none;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                }
                
                .btn.btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(0,0,0,0.25);
                }
                
                .btn.btn-secondary {
                    background-color: rgba(255,255,255,0.8);
                    color: #333;
                    border: 1px solid #b2ebf2;
                }
                
                .btn.btn-secondary:hover {
                    background-color: white;
                }
                
                footer {
                    color: #455a64;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 15px;
                    border-radius: 0 0 12px 12px;
                }
                
                select.filter-input {
                    appearance: none;
                    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23333%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
                    background-repeat: no-repeat;
                    background-position: right .7em top 50%;
                    background-size: .65em auto;
                    padding-right: 1.4em;
                }
            """
        else:  # default theme
            return common_styles + """
                body {
                    background-color: #ffffff;
                    color: #333333;
                }
                
                header {
                    background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                    color: white;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                }
                
                .metric-box {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    transition: all 0.3s ease;
                }
                
                .metric-icon {
                    background-color: rgba(66, 133, 244, 0.1);
                    color: #4285f4;
                }
                
                .metric-label {
                    color: #6c757d;
                }
                
                .metric-value {
                    color: #4285f4;
                }
                
                .chart-container {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                }
                
                .filters-section {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                }
                
                .filter-label {
                    color: #495057;
                }
                
                .filter-input {
                    background-color: white;
                    border: 1px solid #ced4da;
                    color: #495057;
                    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
                }
                
                .filter-input:focus {
                    border-color: #4285f4;
                    box-shadow: 0 0 0 0.2rem rgba(66, 133, 244, 0.25);
                    outline: 0;
                }
                
                input[type="range"].range-slider {
                    background-color: #e9ecef;
                }
                
                input[type="range"].range-slider::-webkit-slider-thumb {
                    background-color: #4285f4;
                }
                
                .btn.btn-primary {
                    background-color: #4285f4;
                    color: white;
                }
                
                .btn.btn-primary:hover {
                    background-color: #3367d6;
                }
                
                .btn.btn-secondary {
                    background-color: #f8f9fa;
                    color: #495057;
                    border: 1px solid #ced4da;
                }
                
                .btn.btn-secondary:hover {
                    background-color: #e9ecef;
                }
                
                footer {
                    color: #6c757d;
                    border-top: 1px solid #e9ecef;
                }
                
                select.filter-input {
                    appearance: none;
                    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23343a40%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
                    background-repeat: no-repeat;
                    background-position: right .7em top 50%;
                    background-size: .65em auto;
                    padding-right: 1.4em;
                }
            """
    
    def display_metrics(self, df, metrics_config, is_sidebar=True, compact=False):
        """
        Generate HTML for metrics display.
        
        Args:
            df: Pandas DataFrame with the data
            metrics_config: List of metric configurations
            is_sidebar: Whether metrics are displayed in sidebar (affects styling)
            compact: Whether to use compact display style
            
        Returns:
            str: HTML for metrics section
        """
        metrics_html = ""
        
        # Define icons for different metric types
        metric_icons = {
            "sales": "bi-currency-dollar",
            "revenue": "bi-currency-dollar",
            "profit": "bi-graph-up-arrow",
            "count": "bi-hash",
            "units": "bi-box",
            "quantity": "bi-box",
            "customers": "bi-people",
            "orders": "bi-cart",
            "average": "bi-calculator",
            "time": "bi-clock",
            "rate": "bi-percent",
            "views": "bi-eye",
            "clicks": "bi-mouse",
            "score": "bi-star",
            "rating": "bi-star"
        }
        
        for i, metric in enumerate(metrics_config):
            column = metric["column"]
            label = metric.get("label", column)
            aggregation = metric.get("aggregation", "sum")
            
            # Skip if column doesn't exist
            if column not in df.columns:
                continue
                
            # Choose an appropriate icon based on the metric name
            icon_class = "bi-graph-up"  # Default icon
            for key, icon in metric_icons.items():
                if key.lower() in column.lower() or key.lower() in label.lower():
                    icon_class = icon
                    break
                
            # Calculate the metric value
            if aggregation == "sum":
                value = df[column].sum()
            elif aggregation == "average" or aggregation == "mean":
                value = df[column].mean()
            elif aggregation == "min":
                value = df[column].min()
            elif aggregation == "max":
                value = df[column].max()
            elif aggregation == "count":
                value = df[column].count()
            else:
                value = df[column].sum()  # Default to sum
                
            # Format the value (improved formatting)
            if isinstance(value, (int, float)):
                if value > 1000000:
                    formatted_value = f"{value/1000000:.1f}M"
                elif value > 1000:
                    formatted_value = f"{value/1000:.1f}K"
                elif value % 1 == 0:
                    formatted_value = f"{int(value):,}"
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
                
            # Determine trend direction and color (randomly for demo purposes)
            # In a real implementation, this would be calculated from historical data
            trend_direction = random.choice(['up', 'down'])
            trend_percent = round(random.uniform(1.5, 15.5), 1)
            
            trend_icon = "bi-arrow-up-right" if trend_direction == 'up' else "bi-arrow-down-right"
            trend_color = "positive" if trend_direction == 'up' else "negative"
            
            if aggregation in ["min", "count"]:
                # For some metrics, "down" might not be negative
                trend_color = "" 
                
            # Create metric box HTML with icon and trend indicator
            class_suffix = " compact" if compact else ""
            metrics_html += f"""
                <div class="metric-box{class_suffix}">
                    <div class="metric-icon">
                        <i class="bi {icon_class}"></i>
                    </div>
                    <div class="metric-content">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{formatted_value}</div>
                        <div class="metric-trend {trend_color}">
                            <i class="bi {trend_icon}"></i> {trend_percent}%
                        </div>
                    </div>
                </div>
            """
            
        return metrics_html
        
    def render_filters(self, df, filters_config):
        """
        Generate HTML for filters section.
        
        Args:
            df: Pandas DataFrame with the data
            filters_config: List of filter configurations
            
        Returns:
            str: HTML for filters section
        """
        if not filters_config:
            return ""
            
        filters_html = '<div class="filters-section">'
        filters_html += '<h3><i class="bi bi-funnel"></i> Filters</h3>'
        filters_html += '<div class="filters-container">'
        
        # Group filters into columns for better layout
        filter_count = len(filters_config)
        columns_needed = min(3, filter_count)  # Max 3 columns
        
        # Create filter columns for responsive layout
        filters_html += f'<div class="filter-columns" style="grid-template-columns: repeat({columns_needed}, 1fr);">'
        
        for filter_config in filters_config:
            filter_type = filter_config["type"]
            column = filter_config["column"]
            label = filter_config.get("label", column.replace('_', ' ').title())
            
            # Skip if column doesn't exist
            if column not in df.columns:
                continue
                
            if filter_type == "date_range":
                # Date range filter - improved with better UI
                try:
                    min_date = pd.to_datetime(df[column].min()).strftime('%Y-%m-%d')
                    max_date = pd.to_datetime(df[column].max()).strftime('%Y-%m-%d')
                except:
                    # If conversion fails, use string values
                    min_date = str(df[column].min())
                    max_date = str(df[column].max())
                
                filters_html += f"""
                <div class="filter-group">
                    <div class="filter-label"><i class="bi bi-calendar3"></i> {label}</div>
                    <div class="date-range-filter">
                        <div class="date-inputs">
                            <div class="date-input-group">
                                <label>From</label>
                                <input type="date" name="filter_{column}_start" class="filter-input" 
                                       value="{min_date}" min="{min_date}" max="{max_date}">
                            </div>
                            <div class="date-input-group">
                                <label>To</label>
                                <input type="date" name="filter_{column}_end" class="filter-input" 
                                       value="{max_date}" min="{min_date}" max="{max_date}">
                            </div>
                        </div>
                    </div>
                </div>
                """
            elif filter_type == "categorical":
                # Categorical filter with search and multiple selection
                unique_values = df[column].dropna().unique()
                
                options_html = ""
                for value in unique_values:
                    options_html += f'<option value="{value}">{value}</option>'
                
                # Use enhanced select with search functionality
                filters_html += f"""
                <div class="filter-group">
                    <div class="filter-label"><i class="bi bi-tag"></i> {label}</div>
                    <select name="filter_{column}" class="filter-input" data-placeholder="Select {label}">
                        <option value="">All {label}</option>
                        {options_html}
                    </select>
                </div>
                """
            elif filter_type == "numeric_range":
                # Numeric range filter with slider
                try:
                    min_val = float(df[column].min())
                    max_val = float(df[column].max())
                    
                    # Round the values for better UI
                    step = 1 if max_val - min_val > 100 else 0.1
                    
                    filters_html += f"""
                    <div class="filter-group">
                        <div class="filter-label"><i class="bi bi-sliders"></i> {label} Range</div>
                        <div class="numeric-range-filter">
                            <div class="range-values">
                                <span id="{column}_min_value">{min_val:.1f}</span>
                                <span>to</span>
                                <span id="{column}_max_value">{max_val:.1f}</span>
                            </div>
                            <div class="range-sliders">
                                <input type="range" name="filter_{column}_min" class="filter-input range-slider" 
                                       value="{min_val}" min="{min_val}" max="{max_val}" step="{step}"
                                       oninput="document.getElementById('{column}_min_value').innerHTML = this.value">
                                <input type="range" name="filter_{column}_max" class="filter-input range-slider" 
                                       value="{max_val}" min="{min_val}" max="{max_val}" step="{step}"
                                       oninput="document.getElementById('{column}_max_value').innerHTML = this.value">
                            </div>
                        </div>
                    </div>
                    """
                except:
                    # Fallback to standard inputs if slider creation fails
                    filters_html += f"""
                    <div class="filter-group">
                        <div class="filter-label"><i class="bi bi-123"></i> {label} Range</div>
                        <div class="numeric-range-filter">
                            <input type="number" name="filter_{column}_min" class="filter-input" 
                                   placeholder="Min" step="any">
                            <span>to</span>
                            <input type="number" name="filter_{column}_max" class="filter-input" 
                                   placeholder="Max" step="any">
                        </div>
                    </div>
                    """
                    
        # Close filter columns
        filters_html += '</div>'
        
        # Add apply filters button
        filters_html += """
        <div class="filter-actions">
            <button id="apply-filters" class="btn btn-primary">
                <i class="bi bi-funnel-fill"></i> Apply Filters
            </button>
            <button id="reset-filters" class="btn btn-secondary">
                <i class="bi bi-arrow-counterclockwise"></i> Reset
            </button>
        </div>
        """
                
        filters_html += '</div></div>'
        return filters_html
        
    def render_charts(self, df, charts_config, style_config=None):
        """
        Generate HTML for charts section.
        
        Args:
            df: Pandas DataFrame with the data
            charts_config: List of chart configurations
            style_config: Style configuration
            
        Returns:
            str: HTML for charts section
        """
        if not charts_config:
            return "<div><p>No charts configured.</p></div>"
            
        # Get the color scheme
        color_scheme = style_config.get('color_scheme', 'default') if style_config else 'default'
        
        charts_html = ""
        
        for chart_config in charts_config:
            chart_type = chart_config["type"]
            title = chart_config["title"]
            
            # Skip if essential columns don't exist
            if "x" in chart_config and chart_config["x"] not in df.columns:
                charts_html += f"<div><p>Error: Column {chart_config['x']} not found for chart {title}</p></div>"
                continue
                
            if "y" in chart_config and chart_config["y"] not in df.columns:
                charts_html += f"<div><p>Error: Column {chart_config['y']} not found for chart {title}</p></div>"
                continue
            
            # Generate the chart figure
            try:
                if chart_type == "bar":
                    fig = self.create_bar_chart(df, chart_config, color_scheme)
                elif chart_type == "line":
                    fig = self.create_line_chart(df, chart_config, color_scheme)
                elif chart_type == "pie":
                    fig = self.create_pie_chart(df, chart_config, color_scheme)
                elif chart_type == "scatter":
                    fig = self.create_scatter_chart(df, chart_config, color_scheme)
                else:
                    charts_html += f"<div><p>Unsupported chart type: {chart_type}</p></div>"
                    continue
                    
                # Convert the figure to HTML
                chart_html = fig.to_html(full_html=False, include_plotlyjs=False)
                
                # Create the chart container
                charts_html += f"""
                <div class="chart-container">
                    <div class="chart-title">{title}</div>
                    {chart_html}
                </div>
                """
            except Exception as e:
                charts_html += f"""
                <div class="chart-container">
                    <div class="chart-title">{title} (Error)</div>
                    <p>Error generating chart: {str(e)}</p>
                </div>
                """
                
        return charts_html
        
    def create_bar_chart(self, df, config, color_scheme='default'):
        """Create a bar chart using Plotly Express"""
        x = config["x"]
        y = config["y"]
        color = config.get("color")
        
        # Get labels from config or use column names
        title = config.get("title", f"{y} by {x}")
        x_label = config.get("x_label") or x
        y_label = config.get("y_label") or y
        
        # Set color palette based on scheme
        color_map = {
            'default': px.colors.qualitative.Plotly,
            'pastel': px.colors.qualitative.Pastel,
            'dark': px.colors.qualitative.Dark24,
            'light': px.colors.qualitative.Light24,
            'bold': px.colors.qualitative.Bold
        }
        
        color_sequence = color_map.get(color_scheme, px.colors.qualitative.Plotly)
        
        # Create the bar chart
        if color:
            fig = px.bar(df, x=x, y=y, color=color, title=title, color_discrete_sequence=color_sequence)
        else:
            fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=color_sequence)
            
        # Update layout
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            margin=dict(l=40, r=40, t=50, b=40),
            height=400
        )
        
        return fig
        
    def create_line_chart(self, df, config, color_scheme='default'):
        """Create a line chart using Plotly Express"""
        x = config["x"]
        y = config["y"]
        color = config.get("color")
        
        # Get labels from config or use column names
        title = config.get("title", f"{y} over {x}")
        x_label = config.get("x_label") or x
        y_label = config.get("y_label") or y
        
        # Set color palette based on scheme
        color_map = {
            'default': px.colors.qualitative.Plotly,
            'pastel': px.colors.qualitative.Pastel,
            'dark': px.colors.qualitative.Dark24,
            'light': px.colors.qualitative.Light24,
            'bold': px.colors.qualitative.Bold
        }
        
        color_sequence = color_map.get(color_scheme, px.colors.qualitative.Plotly)
        
        # Create the line chart
        if color:
            fig = px.line(df, x=x, y=y, color=color, title=title, color_discrete_sequence=color_sequence)
        else:
            fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=color_sequence)
            
        # Update layout
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            margin=dict(l=40, r=40, t=50, b=40),
            height=400
        )
        
        return fig
        
    def create_pie_chart(self, df, config, color_scheme='default'):
        """Create a pie chart using Plotly Express"""
        names = config["x"]
        values = config["y"]
        
        # Get title from config
        title = config.get("title", f"{values} Distribution by {names}")
        
        # Set color palette based on scheme
        color_map = {
            'default': px.colors.qualitative.Plotly,
            'pastel': px.colors.qualitative.Pastel,
            'dark': px.colors.qualitative.Dark24,
            'light': px.colors.qualitative.Light24,
            'bold': px.colors.qualitative.Bold
        }
        
        color_sequence = color_map.get(color_scheme, px.colors.qualitative.Plotly)
        
        # Aggregate the data for the pie chart
        pie_data = df.groupby(names)[values].sum().reset_index()
        
        # Create the pie chart
        fig = px.pie(
            pie_data,
            names=names,
            values=values,
            title=title,
            color_discrete_sequence=color_sequence
        )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=40, r=40, t=50, b=40),
            height=400
        )
        
        return fig
        
    def create_scatter_chart(self, df, config, color_scheme='default'):
        """Create a scatter chart using Plotly Express"""
        x = config["x"]
        y = config["y"]
        color = config.get("color")
        
        # Get labels from config or use column names
        title = config.get("title", f"{y} vs {x}")
        x_label = config.get("x_label") or x
        y_label = config.get("y_label") or y
        
        # Set color palette based on scheme
        color_map = {
            'default': px.colors.qualitative.Plotly,
            'pastel': px.colors.qualitative.Pastel,
            'dark': px.colors.qualitative.Dark24,
            'light': px.colors.qualitative.Light24,
            'bold': px.colors.qualitative.Bold
        }
        
        color_sequence = color_map.get(color_scheme, px.colors.qualitative.Plotly)
        
        # Create the scatter chart
        if color:
            fig = px.scatter(df, x=x, y=y, color=color, title=title, color_discrete_sequence=color_sequence)
        else:
            fig = px.scatter(df, x=x, y=y, title=title, color_discrete_sequence=color_sequence)
            
        # Update layout
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            margin=dict(l=40, r=40, t=50, b=40),
            height=400
        )
        
        return fig 