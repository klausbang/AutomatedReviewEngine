"""
Progress Tracker Component - Automated Review Engine

Progress tracking components for monitoring review workflows,
file processing, and system operations.

Phase 3.1: UI Foundation - Progress Components
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class ProgressTracker:
    """Progress tracking component"""
    
    def __init__(self):
        """Initialize progress tracker"""
        self.active_operations = {}
    
    def render_progress_bar(self, 
                          progress: float,
                          title: str = "Progress",
                          show_percentage: bool = True,
                          color: str = "normal") -> None:
        """
        Render a progress bar
        
        Args:
            progress: Progress value (0.0 to 1.0)
            title: Progress bar title
            show_percentage: Whether to show percentage
            color: Progress bar color theme
        """
        # Clamp progress between 0 and 1
        progress = max(0.0, min(1.0, progress))
        
        if show_percentage:
            title += f" ({progress:.1%})"
        
        st.progress(progress, text=title)
    
    def render_step_progress(self, 
                           current_step: int,
                           total_steps: int,
                           step_names: Optional[List[str]] = None,
                           show_details: bool = True) -> None:
        """
        Render step-based progress
        
        Args:
            current_step: Current step number (1-indexed)
            total_steps: Total number of steps
            step_names: Optional list of step names
            show_details: Whether to show step details
        """
        progress = (current_step - 1) / total_steps if total_steps > 0 else 0
        
        st.progress(progress, text=f"Step {current_step} of {total_steps}")
        
        if show_details and step_names:
            # Show step indicators
            cols = st.columns(min(total_steps, 5))  # Max 5 columns
            
            for i, col in enumerate(cols):
                if i < total_steps:
                    step_num = i + 1
                    step_name = step_names[i] if i < len(step_names) else f"Step {step_num}"
                    
                    if step_num < current_step:
                        col.success(f"✅ {step_name}")
                    elif step_num == current_step:
                        col.info(f"🔄 {step_name}")
                    else:
                        col.write(f"⏳ {step_name}")


def create_progress_tracker() -> ProgressTracker:
    """Create and return a ProgressTracker instance"""
    return ProgressTracker()
