import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import os

def render_dashboard(data, config):
    """
    Renders a dashboard based on the provided data and configuration.
    
    Args:
        data (pd.DataFrame): The data to visualize
        config (dict): Dashboard configuration containing:
            - title (str): Dashboard title
            - description (str): Dashboard description
            - metrics (list): List of metrics to display
            - charts (list): List of chart configurations 
            - filters (list): List of filter configurations
    """
    # Header
    st.title(config.get('title', 'Dashboard'))
    st.write(config.get('description', ''))
    
    # Apply filters
    filtered_data = apply_filters(data, config.get('filters', []))
    
    # Display metrics
    display_metrics(filtered_data, config.get('metrics', []))
    
    # Display charts
    display_charts(filtered_data, config.get('charts', []))
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Generated with CrewAI Dashboard Generator on {datetime.now().strftime('%Y-%m-%d')}*")


def apply_filters(data, filters):
    """Apply interactive filters to the data."""
    filtered_data = data.copy()
    
    if not filters:
        return filtered_data
    
    st.sidebar.title("Filters")
    
    for filter_config in filters:
        filter_type = filter_config.get('type')
        column = filter_config.get('column')
        
        if not column or column not in data.columns:
            continue
            
        if filter_type == 'date_range' and pd.api.types.is_datetime64_any_dtype(data[column]):
            min_date = pd.to_datetime(data[column].min())
            max_date = pd.to_datetime(data[column].max())
            date_range = st.sidebar.date_input(
                f"Select {column} range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                filtered_data = filtered_data[
                    (filtered_data[column] >= pd.to_datetime(date_range[0])) & 
                    (filtered_data[column] <= pd.to_datetime(date_range[1]))
                ]
        
        elif filter_type == 'categorical':
            unique_values = data[column].unique().tolist()
            selected_values = st.sidebar.multiselect(
                f"Select {column}",
                options=unique_values,
                default=unique_values
            )
            if selected_values:
                filtered_data = filtered_data[filtered_data[column].isin(selected_values)]
        
        elif filter_type == 'numeric_range':
            min_val = float(data[column].min())
            max_val = float(data[column].max())
            value_range = st.sidebar.slider(
                f"Select {column} range",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val)
            )
            filtered_data = filtered_data[
                (filtered_data[column] >= value_range[0]) & 
                (filtered_data[column] <= value_range[1])
            ]
    
    return filtered_data


def display_metrics(data, metrics):
    """Display metrics in a row of cards."""
    if not metrics:
        return
        
    cols = st.columns(min(len(metrics), 4))
    
    for i, metric in enumerate(metrics):
        column = metric.get('column')
        label = metric.get('label', column)
        agg_func = metric.get('aggregation', 'sum')
        
        if not column or column not in data.columns:
            continue
            
        col_idx = i % 4
        
        with cols[col_idx]:
            try:
                if agg_func == 'sum':
                    value = data[column].sum()
                elif agg_func == 'mean':
                    value = data[column].mean()
                elif agg_func == 'count':
                    value = data[column].count()
                elif agg_func == 'max':
                    value = data[column].max()
                elif agg_func == 'min':
                    value = data[column].min()
                else:
                    value = data[column].sum()
                
                # Format the value based on its type
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:,.2f}" if value % 1 else f"{int(value):,}"
                else:
                    formatted_value = str(value)
                    
                st.metric(label=label, value=formatted_value)
            except Exception as e:
                st.error(f"Error calculating {label}: {str(e)}")


def display_charts(data, charts):
    """Display charts based on configuration."""
    if not charts:
        return
    
    for i, chart in enumerate(charts):
        chart_type = chart.get('type', 'bar')
        title = chart.get('title', f'Chart {i+1}')
        x_column = chart.get('x')
        y_column = chart.get('y')
        color_column = chart.get('color')
        
        if not x_column or not y_column or x_column not in data.columns or y_column not in data.columns:
            st.warning(f"Could not create chart '{title}'. Missing or invalid columns.")
            continue
            
        st.subheader(title)
        
        try:
            if chart_type == 'bar':
                fig = create_bar_chart(data, x_column, y_column, color_column, chart)
            elif chart_type == 'line':
                fig = create_line_chart(data, x_column, y_column, color_column, chart)
            elif chart_type == 'scatter':
                fig = create_scatter_chart(data, x_column, y_column, color_column, chart)
            elif chart_type == 'pie':
                fig = create_pie_chart(data, x_column, y_column, chart)
            else:
                fig = create_bar_chart(data, x_column, y_column, color_column, chart)
                
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart '{title}': {str(e)}")


def create_bar_chart(data, x_column, y_column, color_column, config):
    """Create a bar chart."""
    if color_column and color_column in data.columns:
        fig = px.bar(
            data, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    else:
        fig = px.bar(
            data, 
            x=x_column, 
            y=y_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    
    return fig


def create_line_chart(data, x_column, y_column, color_column, config):
    """Create a line chart."""
    if color_column and color_column in data.columns:
        fig = px.line(
            data, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    else:
        fig = px.line(
            data, 
            x=x_column, 
            y=y_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    
    return fig


def create_scatter_chart(data, x_column, y_column, color_column, config):
    """Create a scatter chart."""
    if color_column and color_column in data.columns:
        fig = px.scatter(
            data, 
            x=x_column, 
            y=y_column, 
            color=color_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    else:
        fig = px.scatter(
            data, 
            x=x_column, 
            y=y_column,
            title=config.get('title', ''),
            labels={
                x_column: config.get('x_label', x_column),
                y_column: config.get('y_label', y_column)
            }
        )
    
    return fig


def create_pie_chart(data, names_column, values_column, config):
    """Create a pie chart."""
    agg_data = data.groupby(names_column)[values_column].sum().reset_index()
    
    fig = px.pie(
        agg_data, 
        names=names_column, 
        values=values_column,
        title=config.get('title', '')
    )
    
    return fig 