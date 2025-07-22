"""
Main Layout - Automated Review Engine

Primary application layout structure and responsive design components.

Phase 3.1: UI Foundation - Main Layout
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable


class MainLayout:
    """Main application layout manager"""
    
    def __init__(self):
        """Initialize main layout"""
        self.header_height = 100
        self.footer_height = 50
        self.sidebar_width = 300
    
    def render_layout(self, 
                     header_component: Optional[Callable] = None,
                     sidebar_component: Optional[Callable] = None,
                     main_component: Optional[Callable] = None,
                     footer_component: Optional[Callable] = None) -> None:
        """
        Render complete application layout
        
        Args:
            header_component: Function to render header
            sidebar_component: Function to render sidebar
            main_component: Function to render main content
            footer_component: Function to render footer
        """
        # Header
        if header_component:
            header_component()
        
        # Main content with sidebar
        col1, col2 = st.columns([1, 4])  # Sidebar : Main content ratio
        
        with col1:
            if sidebar_component:
                sidebar_component()
        
        with col2:
            if main_component:
                main_component()
        
        # Footer
        if footer_component:
            footer_component()


def create_main_layout() -> MainLayout:
    """Create and return a MainLayout instance"""
    return MainLayout()
