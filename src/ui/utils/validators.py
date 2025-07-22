"""
UI Validators - Automated Review Engine

Input validation utilities for user interface components.

Phase 3.1: UI Foundation - Validation Functions
"""

import re
from typing import List, Optional, Dict, Any
from pathlib import Path


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_file_name(filename: str, allowed_chars: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate filename for safety and compatibility
    
    Args:
        filename: Filename to validate
        allowed_chars: Optional custom allowed characters
        
    Returns:
        Dictionary with validation result and details
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    if not filename or not isinstance(filename, str):
        result['is_valid'] = False
        result['errors'].append("Filename is required")
        return result
    
    # Check length
    if len(filename) > 255:
        result['is_valid'] = False
        result['errors'].append("Filename too long (max 255 characters)")
    
    # Check for illegal characters
    illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in illegal_chars:
        if char in filename:
            result['is_valid'] = False
            result['errors'].append(f"Illegal character '{char}' in filename")
    
    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        result['is_valid'] = False
        result['errors'].append(f"'{name_without_ext}' is a reserved filename")
    
    # Check for leading/trailing spaces or periods
    if filename != filename.strip():
        result['warnings'].append("Filename has leading or trailing whitespace")
        result['suggestions'].append("Remove leading/trailing spaces")
    
    if filename.startswith('.') or filename.endswith('.'):
        result['warnings'].append("Filename starts or ends with period")
    
    return result


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Dict[str, Any]:
    """
    Validate file extension against allowed list
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (with or without dots)
        
    Returns:
        Dictionary with validation result
    """
    result = {
        'is_valid': True,
        'errors': [],
        'detected_extension': None
    }
    
    if not filename:
        result['is_valid'] = False
        result['errors'].append("Filename is required")
        return result
    
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    result['detected_extension'] = extension
    
    # Normalize allowed extensions (ensure they start with dot)
    normalized_extensions = []
    for ext in allowed_extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext.lower())
    
    if extension not in normalized_extensions:
        result['is_valid'] = False
        result['errors'].append(f"Extension '{extension}' not allowed. Allowed: {', '.join(normalized_extensions)}")
    
    return result


def validate_text_input(text: str, 
                       min_length: int = 0,
                       max_length: int = 1000,
                       required: bool = True,
                       allow_special_chars: bool = True) -> Dict[str, Any]:
    """
    Validate text input with various criteria
    
    Args:
        text: Text to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
        required: Whether text is required (non-empty)
        allow_special_chars: Whether special characters are allowed
        
    Returns:
        Dictionary with validation result
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check if required
    if required and (not text or not text.strip()):
        result['is_valid'] = False
        result['errors'].append("This field is required")
        return result
    
    # If not required and empty, return valid
    if not required and not text:
        return result
    
    # Check length
    if len(text) < min_length:
        result['is_valid'] = False
        result['errors'].append(f"Text too short (minimum {min_length} characters)")
    
    if len(text) > max_length:
        result['is_valid'] = False
        result['errors'].append(f"Text too long (maximum {max_length} characters)")
    
    # Check for special characters if not allowed
    if not allow_special_chars:
        special_char_pattern = r'[^a-zA-Z0-9\s]'
        if re.search(special_char_pattern, text):
            result['is_valid'] = False
            result['errors'].append("Special characters not allowed")
    
    return result


def validate_numeric_input(value: str, 
                          min_value: Optional[float] = None,
                          max_value: Optional[float] = None,
                          allow_decimal: bool = True,
                          required: bool = True) -> Dict[str, Any]:
    """
    Validate numeric input
    
    Args:
        value: Value to validate (as string)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_decimal: Whether decimal numbers are allowed
        required: Whether value is required
        
    Returns:
        Dictionary with validation result and parsed value
    """
    result = {
        'is_valid': True,
        'errors': [],
        'parsed_value': None
    }
    
    # Check if required
    if required and (not value or not str(value).strip()):
        result['is_valid'] = False
        result['errors'].append("This field is required")
        return result
    
    # If not required and empty, return valid
    if not required and not value:
        return result
    
    try:
        # Parse numeric value
        if allow_decimal:
            parsed_value = float(value)
        else:
            parsed_value = int(value)
        
        result['parsed_value'] = parsed_value
        
        # Check range
        if min_value is not None and parsed_value < min_value:
            result['is_valid'] = False
            result['errors'].append(f"Value must be at least {min_value}")
        
        if max_value is not None and parsed_value > max_value:
            result['is_valid'] = False
            result['errors'].append(f"Value must be at most {max_value}")
        
    except ValueError:
        result['is_valid'] = False
        result['errors'].append("Invalid numeric value")
    
    return result
