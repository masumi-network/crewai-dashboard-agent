import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
import logging

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
                    <div class="metrics-container grid">{metrics_html}</div>
                    <div class="charts-container grid">{charts_html}</div>
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
            <style>
                {theme_styles}
                
                /* Layout styles */
                .dashboard-layout {{
                    display: flex;
                    gap: 20px;
                }}
                
                .sidebar {{
                    flex: 0 0 250px;
                }}
                
                .main-content {{
                    flex: 1;
                }}
                
                /* Grid layout */
                .grid-layout {{
                    display: grid;
                    gap: 20px;
                }}
                
                /* Compact layout */
                .metrics-container.compact {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}
                
                .metrics-container.compact .metric-box {{
                    flex: 1 0 150px;
                    max-width: 200px;
                    padding: 10px;
                }}
                
                /* Expanded layout */
                .metrics-container.expanded .metric-box,
                .charts-container.expanded .chart-container {{
                    margin-bottom: 20px;
                    width: 100%;
                }}
                
                /* Standard layout for metrics */
                .metrics-container .metric-box {{
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 8px;
                }}
                
                /* Chart containers */
                .chart-container {{
                    margin-bottom: 25px;
                    padding: 15px;
                    border-radius: 8px;
                }}
                
                /* Filter section */
                .filters-section {{
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <header>
                    <h1>{title}</h1>
                    <p>{description}</p>
                </header>
                
                {filters_html}
                
                {main_content}
            </div>
            
            <script>
                // Dashboard initialization and filter handling
                $(document).ready(function() {{
                    // Add filter event handlers
                    // This is a simplified example - in a real implementation, 
                    // you'd have more robust filtering logic
                    $('.filter-input').on('change', function() {{
                        // In a real implementation, this would apply the filters
                        console.log('Filter changed:', $(this).attr('name'), $(this).val());
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return html
    
    def apply_styling(self, theme):
        """Apply CSS styling based on the selected theme"""
        if theme == 'dark':
            return """
                body {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    font-family: Arial, sans-serif;
                }
                header {
                    background-color: #333;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                header h1 {
                    margin-top: 0;
                    color: #fff;
                }
                .metric-box {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                }
                .metric-value {
                    color: #4fc3f7;
                    font-size: 24px;
                    font-weight: bold;
                }
                .chart-container {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                }
                .filters-section {
                    background-color: #333;
                    border: 1px solid #444;
                }
            """
        elif theme == 'light':
            return """
                body {
                    background-color: #f5f5f5;
                    color: #333;
                    font-family: Arial, sans-serif;
                }
                header {
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                header h1 {
                    margin-top: 0;
                    color: #2196F3;
                }
                .metric-box {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .metric-value {
                    color: #2196F3;
                    font-size: 24px;
                    font-weight: bold;
                }
                .chart-container {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .filters-section {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
            """
        elif theme == 'colorful':
            return """
                body {
                    background-color: #f0f8ff;
                    color: #333;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                header {
                    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                header h1 {
                    margin-top: 0;
                    color: #fff;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
                }
                header p {
                    color: rgba(255,255,255,0.9);
                }
                .metric-box {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border: none;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                .metric-box:hover {
                    transform: translateY(-5px);
                }
                .metric-value {
                    color: #5e35b1;
                    font-size: 28px;
                    font-weight: bold;
                }
                .chart-container {
                    background-color: #ffffff;
                    border: none;
                    border-radius: 12px;
                    box-shadow: 0 6px 12px rgba(0,0,0,0.08);
                    overflow: hidden;
                }
                .filters-section {
                    background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                    border: none;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
            """
        else:  # default theme
            return """
                body {
                    background-color: #ffffff;
                    color: #333333;
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                header {
                    background-color: #4285f4;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                header h1 {
                    margin-top: 0;
                }
                header p {
                    margin-bottom: 0;
                    opacity: 0.9;
                }
                .dashboard-container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .metric-box {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .metric-label {
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 5px;
                }
                .metric-value {
                    color: #4285f4;
                    font-size: 24px;
                    font-weight: bold;
                }
                .chart-container {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    padding: 15px;
                }
                .chart-title {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .filters-section {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                }
                .filter-group {
                    margin-bottom: 10px;
                }
                .filter-label {
                    font-size: 14px;
                    margin-bottom: 5px;
                }
                .filter-input {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
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
        
        for metric in metrics_config:
            column = metric["column"]
            label = metric.get("label", column)
            aggregation = metric.get("aggregation", "sum")
            
            # Skip if column doesn't exist
            if column not in df.columns:
                continue
                
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
                
            # Format the value (simple formatting, can be enhanced)
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
                
            # Create metric box HTML
            class_suffix = " compact" if compact else ""
            metrics_html += f"""
                <div class="metric-box{class_suffix}">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{formatted_value}</div>
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
            
        filters_html = '<div class="filters-section"><h3>Filters</h3>'
        
        for filter_config in filters_config:
            filter_type = filter_config["type"]
            column = filter_config["column"]
            label = filter_config.get("label", column)
            
            # Skip if column doesn't exist
            if column not in df.columns:
                continue
                
            if filter_type == "date_range":
                # Date range filter
                min_date = df[column].min()
                max_date = df[column].max()
                
                filters_html += f"""
                <div class="filter-group">
                    <div class="filter-label">{label} Range</div>
                    <div class="date-range-filter">
                        <input type="date" name="filter_{column}_start" class="filter-input" 
                               value="{min_date}" min="{min_date}" max="{max_date}">
                        <span>to</span>
                        <input type="date" name="filter_{column}_end" class="filter-input" 
                               value="{max_date}" min="{min_date}" max="{max_date}">
                    </div>
                </div>
                """
            elif filter_type == "categorical":
                # Categorical filter (dropdown)
                unique_values = df[column].dropna().unique()
                
                options_html = ""
                for value in unique_values:
                    options_html += f'<option value="{value}">{value}</option>'
                
                filters_html += f"""
                <div class="filter-group">
                    <div class="filter-label">{label}</div>
                    <select name="filter_{column}" class="filter-input">
                        <option value="">All {label}</option>
                        {options_html}
                    </select>
                </div>
                """
            elif filter_type == "numeric_range":
                # Numeric range filter
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                
                filters_html += f"""
                <div class="filter-group">
                    <div class="filter-label">{label} Range</div>
                    <div class="numeric-range-filter">
                        <input type="number" name="filter_{column}_min" class="filter-input" 
                               value="{min_val}" min="{min_val}" max="{max_val}" step="any">
                        <span>to</span>
                        <input type="number" name="filter_{column}_max" class="filter-input" 
                               value="{max_val}" min="{min_val}" max="{max_val}" step="any">
                    </div>
                </div>
                """
                
        filters_html += '</div>'
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