"""
UI Utils Package - Automated Review Engine

Utility functions and helpers for the Streamlit user interface.

Phase 3.1: UI Foundation - Utilities

Modules:
- helpers: General UI helper functions
- validators: Input validation utilities
- formatters: Data formatting utilities
"""

# Import utilities with error handling
try:
    from .helpers import format_file_size, format_timestamp, generate_session_id
except ImportError:
    format_file_size = None
    format_timestamp = None
    generate_session_id = None

try:
    from .validators import validate_email, validate_file_name
except ImportError:
    validate_email = None
    validate_file_name = None

try:
    from .formatters import format_percentage, format_duration
except ImportError:
    format_percentage = None
    format_duration = None

# Only export available functions
__all__ = []
if format_file_size:
    __all__.append('format_file_size')
if format_timestamp:
    __all__.append('format_timestamp')
if generate_session_id:
    __all__.append('generate_session_id')
if validate_email:
    __all__.append('validate_email')
if validate_file_name:
    __all__.append('validate_file_name')
if format_percentage:
    __all__.append('format_percentage')
if format_duration:
    __all__.append('format_duration')

# Utils version
__version__ = "0.3.1"
