"""
UI Formatters - Automated Review Engine

Data formatting utilities for consistent display in the user interface.

Phase 3.1: UI Foundation - Formatting Functions
"""

from typing import Union, Optional
from datetime import datetime, timedelta


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format a value as a percentage
    
    Args:
        value: Value to format (0.0 to 1.0)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        percentage = value * 100
        return f"{percentage:.{decimal_places}f}%"
    except (TypeError, ValueError):
        return "0.0%"


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds to human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    try:
        duration = timedelta(seconds=int(seconds))
        
        if duration.days > 0:
            return f"{duration.days}d {duration.seconds // 3600}h"
        elif duration.seconds >= 3600:
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        elif duration.seconds >= 60:
            minutes = duration.seconds // 60
            remaining_seconds = duration.seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{duration.seconds}s"
    except (TypeError, ValueError):
        return "0s"


def format_number_with_commas(number: Union[int, float]) -> str:
    """
    Format number with thousand separators
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string with commas
    """
    try:
        return f"{number:,}"
    except (TypeError, ValueError):
        return str(number)


def format_currency(amount: Union[int, float], currency: str = "$") -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        return f"{currency}{amount:,.2f}"
    except (TypeError, ValueError):
        return f"{currency}0.00"


def format_bytes_to_human(bytes_value: int) -> str:
    """
    Convert bytes to human readable format
    
    Args:
        bytes_value: Size in bytes
        
    Returns:
        Human readable size string
    """
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    size_index = 0
    size_value = float(bytes_value)
    
    while size_value >= 1024.0 and size_index < len(size_names) - 1:
        size_value /= 1024.0
        size_index += 1
    
    return f"{size_value:.1f} {size_names[size_index]}"


def format_boolean(value: bool, true_text: str = "Yes", false_text: str = "No") -> str:
    """
    Format boolean value as text
    
    Args:
        value: Boolean value
        true_text: Text for True value
        false_text: Text for False value
        
    Returns:
        Formatted boolean string
    """
    return true_text if value else false_text


def format_list_to_string(items: list, separator: str = ", ", max_items: Optional[int] = None) -> str:
    """
    Format list of items to string
    
    Args:
        items: List of items to format
        separator: Separator between items
        max_items: Maximum number of items to show
        
    Returns:
        Formatted string
    """
    if not items:
        return ""
    
    if max_items and len(items) > max_items:
        visible_items = items[:max_items]
        remaining = len(items) - max_items
        return separator.join(str(item) for item in visible_items) + f" and {remaining} more"
    
    return separator.join(str(item) for item in items)


def format_table_cell(value: Union[str, int, float, bool, None], max_length: int = 50) -> str:
    """
    Format value for display in a table cell
    
    Args:
        value: Value to format
        max_length: Maximum length before truncation
        
    Returns:
        Formatted cell value
    """
    if value is None:
        return "-"
    
    if isinstance(value, bool):
        return format_boolean(value)
    
    if isinstance(value, float):
        # Format float with appropriate precision
        if value == int(value):
            formatted = str(int(value))
        else:
            formatted = f"{value:.2f}"
    else:
        formatted = str(value)
    
    # Truncate if too long
    if len(formatted) > max_length:
        return formatted[:max_length-3] + "..."
    
    return formatted
