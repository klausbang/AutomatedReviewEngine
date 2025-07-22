"""
UI Styling Package - Automated Review Engine

Custom CSS, themes, and styling utilities for the Streamlit application.

Phase 3.1: UI Foundation - Styling System

Modules:
- themes: Color themes and design tokens
- styles: CSS styles and custom components
"""

# Import styling components with error handling
try:
    from .themes import get_theme, apply_theme
except ImportError:
    get_theme = None
    apply_theme = None

try:
    from .styles import apply_custom_css, get_component_styles
except ImportError:
    apply_custom_css = None
    get_component_styles = None

# Only export available functions
__all__ = []
if get_theme and apply_theme:
    __all__.extend(['get_theme', 'apply_theme'])
if apply_custom_css and get_component_styles:
    __all__.extend(['apply_custom_css', 'get_component_styles'])

# Styling version
__version__ = "0.3.1"
