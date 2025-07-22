"""
Status Indicator Component - Automated Review Engine

Simple status indicator components for displaying system status,
processing states, and user feedback.

Phase 3.1: UI Foundation - Status Components
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class StatusType(Enum):
    """Status indicator types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROCESSING = "processing"


class StatusIndicator:
    """Simple status indicator component"""
    
    def __init__(self):
        """Initialize status indicator"""
        self.status_history = []
    
    def render_status(self, 
                     status: StatusType, 
                     message: str, 
                     details: Optional[str] = None,
                     show_timestamp: bool = True) -> None:
        """
        Render a status indicator
        
        Args:
            status: Status type
            message: Status message
            details: Optional detailed information
            show_timestamp: Whether to show timestamp
        """
        # Status icons and colors
        status_config = {
            StatusType.SUCCESS: {"icon": "✅", "method": st.success},
            StatusType.ERROR: {"icon": "❌", "method": st.error},
            StatusType.WARNING: {"icon": "⚠️", "method": st.warning},
            StatusType.INFO: {"icon": "ℹ️", "method": st.info},
            StatusType.PROCESSING: {"icon": "🔄", "method": st.info}
        }
        
        config = status_config.get(status, status_config[StatusType.INFO])
        
        # Prepare message
        display_message = f"{config['icon']} {message}"
        
        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            display_message += f" ({timestamp})"
        
        # Display status
        config["method"](display_message)
        
        # Display details if provided
        if details:
            with st.expander("Details", expanded=False):
                st.text(details)
        
        # Add to history
        self.status_history.append({
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now()
        })
    
    def render_system_status(self, 
                           components: Dict[str, bool],
                           show_details: bool = False) -> None:
        """
        Render system component status
        
        Args:
            components: Dict of component name -> status
            show_details: Whether to show detailed status
        """
        st.markdown("### 🔧 System Status")
        
        if show_details:
            for component, status in components.items():
                icon = "✅" if status else "❌"
                color = "green" if status else "red"
                st.markdown(f":{color}[{icon} {component}]")
        else:
            # Compact view
            all_ok = all(components.values())
            overall_icon = "✅" if all_ok else "❌"
            st.markdown(f"{overall_icon} **System Status**: {'All OK' if all_ok else 'Issues Detected'}")


def create_status_indicator() -> StatusIndicator:
    """Create and return a StatusIndicator instance"""
    return StatusIndicator()
