"""
UI Helpers - Automated Review Engine

General utility functions for the user interface.

Phase 3.1: UI Foundation - Helper Functions
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Union


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size_value = float(size_bytes)
    
    while size_value >= 1024.0 and size_index < len(size_names) - 1:
        size_value /= 1024.0
        size_index += 1
    
    return f"{size_value:.1f} {size_names[size_index]}"


def format_timestamp(timestamp: datetime, format_type: str = "full") -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Datetime object to format
        format_type: Type of formatting ("full", "short", "time", "date")
        
    Returns:
        Formatted timestamp string
    """
    if format_type == "full":
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "short":
        return timestamp.strftime("%m/%d %H:%M")
    elif format_type == "time":
        return timestamp.strftime("%H:%M:%S")
    elif format_type == "date":
        return timestamp.strftime("%Y-%m-%d")
    else:
        return str(timestamp)


def generate_session_id() -> str:
    """
    Generate a unique session ID
    
    Returns:
        Unique session ID string
    """
    return f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"


def format_duration(start_time: datetime, end_time: Optional[datetime] = None) -> str:
    """
    Format duration between two timestamps
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp (defaults to current time)
        
    Returns:
        Formatted duration string
    """
    if end_time is None:
        end_time = datetime.now()
    
    duration = end_time - start_time
    
    if duration.days > 0:
        return f"{duration.days}d {duration.seconds // 3600}h"
    elif duration.seconds >= 3600:
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    elif duration.seconds >= 60:
        minutes = duration.seconds // 60
        seconds = duration.seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        return f"{duration.seconds}s"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default on division by zero
    
    Args:
        numerator: Numerator value
        denominator: Denominator value  
        default: Default value for division by zero
        
    Returns:
        Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def get_relative_time(timestamp: datetime) -> str:
    """
    Get relative time description (e.g., "2 minutes ago")
    
    Args:
        timestamp: Timestamp to compare to current time
        
    Returns:
        Relative time description
    """
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 7:
        return timestamp.strftime("%Y-%m-%d")
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
