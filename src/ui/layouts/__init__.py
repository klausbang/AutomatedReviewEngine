"""
UI Layouts Package - Automated Review Engine

Layout management and page structure components for the Streamlit application.

Phase 3.1: UI Foundation - Layout System

Layouts:
- MainLayout: Primary application layout
- PageLayout: Individual page layouts
- SidebarLayout: Sidebar navigation layout
"""

# Import layouts with error handling
try:
    from .main_layout import MainLayout
except ImportError:
    MainLayout = None

try:
    from .page_layout import PageLayout
except ImportError:
    PageLayout = None

try:
    from .sidebar_layout import SidebarLayout
except ImportError:
    SidebarLayout = None

# Only export available layouts
__all__ = []
if MainLayout:
    __all__.append('MainLayout')
if PageLayout:
    __all__.append('PageLayout')
if SidebarLayout:
    __all__.append('SidebarLayout')

# Layout version
__version__ = "0.3.1"
