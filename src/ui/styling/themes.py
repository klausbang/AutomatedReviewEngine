"""
Themes - Automated Review Engine

Color themes and design tokens for consistent UI styling.

Phase 3.1: UI Foundation - Theme System
"""

from typing import Dict, Any
from enum import Enum


class ThemeType(Enum):
    """Available theme types"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class Theme:
    """Theme configuration class"""
    
    def __init__(self, name: str, colors: Dict[str, str], typography: Dict[str, str]):
        self.name = name
        self.colors = colors
        self.typography = typography


# Light theme configuration
LIGHT_THEME = Theme(
    name="Light",
    colors={
        "primary": "#1f77b4",
        "secondary": "#ff7f0e", 
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "error": "#d62728",
        "background": "#ffffff",
        "surface": "#f8f9fa",
        "text": "#212529",
        "border": "#dee2e6"
    },
    typography={
        "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px"
    }
)

# Dark theme configuration  
DARK_THEME = Theme(
    name="Dark",
    colors={
        "primary": "#4fc3f7",
        "secondary": "#ffb74d",
        "success": "#81c784", 
        "warning": "#ffb74d",
        "error": "#e57373",
        "background": "#121212",
        "surface": "#1e1e1e",
        "text": "#ffffff",
        "border": "#404040"
    },
    typography={
        "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        "font_size_base": "14px", 
        "font_size_large": "18px",
        "font_size_small": "12px"
    }
)


def get_theme(theme_type: ThemeType = ThemeType.LIGHT) -> Theme:
    """
    Get theme configuration
    
    Args:
        theme_type: Type of theme to retrieve
        
    Returns:
        Theme configuration object
    """
    if theme_type == ThemeType.DARK:
        return DARK_THEME
    else:
        return LIGHT_THEME


def apply_theme(theme: Theme) -> str:
    """
    Generate CSS for theme application
    
    Args:
        theme: Theme configuration
        
    Returns:
        CSS string for theme
    """
    css = f"""
    <style>
        :root {{
            --primary-color: {theme.colors['primary']};
            --secondary-color: {theme.colors['secondary']};
            --success-color: {theme.colors['success']};
            --warning-color: {theme.colors['warning']};
            --error-color: {theme.colors['error']};
            --background-color: {theme.colors['background']};
            --surface-color: {theme.colors['surface']};
            --text-color: {theme.colors['text']};
            --border-color: {theme.colors['border']};
            
            --font-family: {theme.typography['font_family']};
            --font-size-base: {theme.typography['font_size_base']};
            --font-size-large: {theme.typography['font_size_large']};
            --font-size-small: {theme.typography['font_size_small']};
        }}
        
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: var(--font-family);
        }}
        
        .main-header {{
            background-color: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem;
        }}
        
        .status-success {{
            color: var(--success-color);
        }}
        
        .status-warning {{
            color: var(--warning-color);
        }}
        
        .status-error {{
            color: var(--error-color);
        }}
    </style>
    """
    
    return css
