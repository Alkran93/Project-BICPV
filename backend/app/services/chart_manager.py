"""
Chart Manager Service
Generates PNG/SVG charts from sensor data using matplotlib.
Supports line charts, bar charts, and comparison overlays.

HU06: View line and bar charts to easily interpret data.
HU09: Graphically compare two facades by overlaying charts to evaluate performance.
"""
import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


def generate_line_chart(
    data: List[Dict[str, Any]],
    x_field: str = "ts",
    y_field: str = "value",
    title: str = "Line Chart",
    xlabel: str = "Time",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (12, 6)
) -> bytes:
    """
    Generates a line chart as PNG bytes from time series data.

    HU06: View line charts to easily interpret data.

    Parameters:
    - data (List[Dict[str, Any]]): List of data records containing x and y values.
    - x_field (str): Key for x-axis data (typically timestamp). Default: "ts".
    - y_field (str): Key for y-axis data (typically sensor value). Default: "value".
    - title (str): Chart title. Default: "Line Chart".
    - xlabel (str): Label for x-axis. Default: "Time".
    - ylabel (str): Label for y-axis. Default: "Value".
    - figsize (Tuple[int, int]): Figure size in inches (width, height). Default: (12, 6).

    Returns:
    - bytes: PNG image data as bytes.

    Exceptions:
    - ValueError: Raised if data is empty or missing required fields.
    - Exception: Raised for matplotlib rendering errors.
    """
    if not data:
        raise ValueError("No data provided for chart generation")

    # Extract x and y values
    x_values = []
    y_values = []
    
    for record in data:
        x_val = record.get(x_field)
        y_val = record.get(y_field)
        
        if x_val is None or y_val is None:
            continue
            
        # Convert timestamp strings to datetime objects
        if isinstance(x_val, str):
            try:
                x_val = datetime.fromisoformat(x_val.replace('Z', '+00:00'))
            except ValueError:
                continue
        
        x_values.append(x_val)
        y_values.append(float(y_val))
    
    if not x_values or not y_values:
        raise ValueError("No valid data points found for plotting")
    
    # Create figure and plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x_values, y_values, marker='o', linestyle='-', linewidth=2, markersize=4)
    
    # Format datetime axis if applicable
    if isinstance(x_values[0], datetime):
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()


def generate_bar_chart(
    data: Dict[str, float],
    title: str = "Bar Chart",
    xlabel: str = "Category",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (10, 6)
) -> bytes:
    """
    Generates a bar chart as PNG bytes from categorical data.

    HU06: View bar charts to easily interpret data.

    Parameters:
    - data (Dict[str, float]): Dictionary mapping category names to values.
    - title (str): Chart title. Default: "Bar Chart".
    - xlabel (str): Label for x-axis. Default: "Category".
    - ylabel (str): Label for y-axis. Default: "Value".
    - figsize (Tuple[int, int]): Figure size in inches (width, height). Default: (10, 6).

    Returns:
    - bytes: PNG image data as bytes.

    Exceptions:
    - ValueError: Raised if data dictionary is empty.
    - Exception: Raised for matplotlib rendering errors.
    """
    if not data:
        raise ValueError("No data provided for bar chart generation")
    
    # Extract categories and values
    categories = list(data.keys())
    values = list(data.values())
    
    # Create figure and plot
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(categories, values, color='steelblue', alpha=0.8, edgecolor='black')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=10)
    
    # Set labels and title
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()


def generate_comparison_chart(
    data1: List[Dict[str, Any]],
    data2: List[Dict[str, Any]],
    label1: str = "Series 1",
    label2: str = "Series 2",
    x_field: str = "ts",
    y_field: str = "value",
    title: str = "Comparison Chart",
    xlabel: str = "Time",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (14, 7)
) -> bytes:
    """
    Generates an overlay comparison chart of two data series.

    HU09: Graphically compare two facades by overlaying charts to evaluate performance.

    Parameters:
    - data1 (List[Dict[str, Any]]): First data series (e.g., refrigerated facade).
    - data2 (List[Dict[str, Any]]): Second data series (e.g., non-refrigerated facade).
    - label1 (str): Legend label for first series. Default: "Series 1".
    - label2 (str): Legend label for second series. Default: "Series 2".
    - x_field (str): Key for x-axis data. Default: "ts".
    - y_field (str): Key for y-axis data. Default: "value".
    - title (str): Chart title. Default: "Comparison Chart".
    - xlabel (str): Label for x-axis. Default: "Time".
    - ylabel (str): Label for y-axis. Default: "Value".
    - figsize (Tuple[int, int]): Figure size in inches. Default: (14, 7).

    Returns:
    - bytes: PNG image data as bytes.

    Exceptions:
    - ValueError: Raised if either data series is empty.
    - Exception: Raised for matplotlib rendering errors.
    """
    if not data1 and not data2:
        raise ValueError("No data provided for comparison chart")
    
    # Helper function to extract x and y values
    def extract_values(data):
        x_values = []
        y_values = []
        for record in data:
            x_val = record.get(x_field)
            y_val = record.get(y_field)
            if x_val is None or y_val is None:
                continue
            if isinstance(x_val, str):
                try:
                    x_val = datetime.fromisoformat(x_val.replace('Z', '+00:00'))
                except ValueError:
                    continue
            x_values.append(x_val)
            y_values.append(float(y_val))
        return x_values, y_values
    
    # Extract values for both series
    x1, y1 = extract_values(data1)
    x2, y2 = extract_values(data2)
    
    # Create figure and plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot both series with different colors
    if x1 and y1:
        ax.plot(x1, y1, marker='o', linestyle='-', linewidth=2, markersize=4,
                label=label1, color='#1f77b4', alpha=0.8)
    
    if x2 and y2:
        ax.plot(x2, y2, marker='s', linestyle='--', linewidth=2, markersize=4,
                label=label2, color='#ff7f0e', alpha=0.8)
    
    # Format datetime axis if applicable
    if (x1 and isinstance(x1[0], datetime)) or (x2 and isinstance(x2[0], datetime)):
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')
    
    # Set labels, title, and legend
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()


def generate_multi_series_chart(
    data_series: List[Tuple[List[Dict[str, Any]], str]],
    x_field: str = "ts",
    y_field: str = "value",
    title: str = "Multi-Series Chart",
    xlabel: str = "Time",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (14, 7)
) -> bytes:
    """
    Generates a chart with multiple data series overlaid.

    Parameters:
    - data_series (List[Tuple[List[Dict[str, Any]], str]]): List of tuples containing data and label.
    - x_field (str): Key for x-axis data. Default: "ts".
    - y_field (str): Key for y-axis data. Default: "value".
    - title (str): Chart title. Default: "Multi-Series Chart".
    - xlabel (str): Label for x-axis. Default: "Time".
    - ylabel (str): Label for y-axis. Default: "Value".
    - figsize (Tuple[int, int]): Figure size in inches. Default: (14, 7).

    Returns:
    - bytes: PNG image data as bytes.

    Exceptions:
    - ValueError: Raised if no data series provided.
    - Exception: Raised for matplotlib rendering errors.
    """
    if not data_series:
        raise ValueError("No data series provided for chart generation")
    
    # Color palette for multiple series
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each series
    for idx, (data, label) in enumerate(data_series):
        x_values = []
        y_values = []
        
        for record in data:
            x_val = record.get(x_field)
            y_val = record.get(y_field)
            if x_val is None or y_val is None:
                continue
            if isinstance(x_val, str):
                try:
                    x_val = datetime.fromisoformat(x_val.replace('Z', '+00:00'))
                except ValueError:
                    continue
            x_values.append(x_val)
            y_values.append(float(y_val))
        
        if x_values and y_values:
            color = colors[idx % len(colors)]
            ax.plot(x_values, y_values, marker='o', linestyle='-', linewidth=2,
                   markersize=3, label=label, color=color, alpha=0.8)
    
    # Format x-axis if datetime
    if data_series and data_series[0][0]:
        first_record = data_series[0][0][0]
        x_val = first_record.get(x_field)
        if isinstance(x_val, (str, datetime)):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45, ha='right')
    
    # Set labels, title, and legend
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer.getvalue()
