"""
UI Package - Automated Review Engine

This package contains all user interface components for the Streamlit-based
web application, including:
- Main interface components
- Page layouts and navigation
- Form handlers and widgets
- Styling and theming
- Component utilities

Phase 3.1: UI Foundation Implementation
"""

from .main_interface import MainInterface

# Import components with error handling
try:
    from .components import (
        FileUploader, DocumentViewer, ReviewPanel, 
        SettingsPanel, StatusIndicator, ProgressTracker
    )
except ImportError:
    FileUploader = DocumentViewer = ReviewPanel = None
    SettingsPanel = StatusIndicator = ProgressTracker = None

# Import layouts with error handling
try:
    from .layouts import MainLayout, PageLayout, SidebarLayout
except ImportError:
    MainLayout = PageLayout = SidebarLayout = None

# Import styling with error handling
try:
    from .styling import get_theme, apply_theme
except ImportError:
    get_theme = apply_theme = None

# Import utils with error handling
try:
    from .utils import format_file_size, format_timestamp, generate_session_id
except ImportError:
    format_file_size = format_timestamp = generate_session_id = None

__version__ = "0.3.1"

# Build __all__ list dynamically based on available components
__all__ = ["MainInterface"]

if FileUploader:
    __all__.append("FileUploader")
if DocumentViewer:
    __all__.append("DocumentViewer")
if ReviewPanel:
    __all__.append("ReviewPanel")
if SettingsPanel:
    __all__.append("SettingsPanel")
if StatusIndicator:
    __all__.append("StatusIndicator")
if ProgressTracker:
    __all__.append("ProgressTracker")
if MainLayout:
    __all__.append("MainLayout")
if PageLayout:
    __all__.append("PageLayout")
if SidebarLayout:
    __all__.append("SidebarLayout")
