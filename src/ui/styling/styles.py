"""
Custom Styles - Automated Review Engine

Custom CSS styles and component styling for enhanced UI appearance.

Phase 3.1: UI Foundation - Custom Styles
"""

import streamlit as st


def apply_custom_css() -> None:
    """Apply custom CSS styles to the Streamlit app"""
    
    css = """
    <style>
        /* Custom styling for Automated Review Engine */
        
        /* Main app styling */
        .main > div {
            padding-top: 2rem;
        }
        
        /* Header styling */
        .app-header {
            background: linear-gradient(90deg, #1f77b4, #4fc3f7);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
        
        /* Status indicators */
        .status-card {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border-left: 4px solid;
        }
        
        .status-success {
            background-color: #d4edda;
            border-left-color: #28a745;
        }
        
        .status-warning {
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }
        
        .status-error {
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .status-info {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
        }
        
        /* File upload area */
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #1f77b4;
            background-color: #f8f9fa;
        }
        
        /* Navigation buttons */
        .nav-button {
            width: 100%;
            margin-bottom: 0.5rem;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            background-color: #f8f9fa;
            color: #495057;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .nav-button:hover {
            background-color: #e9ecef;
        }
        
        .nav-button.active {
            background-color: #1f77b4;
            color: white;
        }
        
        /* Progress indicators */
        .progress-container {
            margin: 1rem 0;
        }
        
        .progress-step {
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
        }
        
        .progress-step-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.5rem;
            font-size: 12px;
        }
        
        .progress-step-complete {
            background-color: #28a745;
            color: white;
        }
        
        .progress-step-current {
            background-color: #007bff;
            color: white;
        }
        
        .progress-step-pending {
            background-color: #6c757d;
            color: white;
        }
        
        /* Metrics and cards */
        .metric-card {
            background-color: #fff;
            border: 1px solid #dee2e6;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #6c757d;
            text-transform: uppercase;
        }
        
        /* Footer styling */
        .app-footer {
            margin-top: 3rem;
            padding: 1rem 0;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.875rem;
        }
        
        /* Dark theme overrides */
        @media (prefers-color-scheme: dark) {
            .metric-card {
                background-color: #343a40;
                border-color: #495057;
                color: #fff;
            }
            
            .upload-area {
                border-color: #495057;
            }
            
            .upload-area:hover {
                background-color: #495057;
            }
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .main > div {
                padding-top: 1rem;
            }
            
            .app-header {
                padding: 0.5rem;
                margin-bottom: 1rem;
            }
            
            .metric-card {
                margin: 0.25rem 0;
                padding: 0.75rem;
            }
        }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_component_styles() -> dict:
    """
    Get component-specific styling configurations
    
    Returns:
        Dictionary of component styles
    """
    return {
        "header": {
            "background": "linear-gradient(90deg, #1f77b4, #4fc3f7)",
            "color": "white",
            "padding": "1rem",
            "border_radius": "0.5rem"
        },
        "status": {
            "success": "#28a745",
            "warning": "#ffc107", 
            "error": "#dc3545",
            "info": "#17a2b8"
        },
        "buttons": {
            "primary": "#1f77b4",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545"
        }
    }
