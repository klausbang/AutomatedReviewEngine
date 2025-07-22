"""
Sidebar Layout - Automated Review Engine

Sidebar navigation and layout components.

Phase 3.1: UI Foundation - Sidebar Layout
"""

import streamlit as st
from typing import Dict, Any, Optional, List


class SidebarLayout:
    """Sidebar layout manager"""
    
    def __init__(self):
        """Initialize sidebar layout"""
        pass
    
    def render_navigation_menu(self, menu_items: Dict[str, str], current_page: str) -> Optional[str]:
        """
        Render navigation menu in sidebar
        
        Args:
            menu_items: Dict of display_name -> page_key
            current_page: Current active page
            
        Returns:
            Selected page key or None
        """
        selected_page = None
        
        st.markdown("## 🎯 Navigation")
        
        for display_name, page_key in menu_items.items():
            if st.button(display_name, key=f"nav_{page_key}", use_container_width=True):
                selected_page = page_key
        
        return selected_page
    
    def render_quick_stats(self, stats: Dict[str, Any]) -> None:
        """Render quick statistics in sidebar"""
        st.markdown("### 📈 Quick Stats")
        
        for label, value in stats.items():
            st.metric(label, value)


def create_sidebar_layout() -> SidebarLayout:
    """Create and return a SidebarLayout instance"""
    return SidebarLayout()
