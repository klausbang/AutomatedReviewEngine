"""
Streamlit App Entry Point - Automated Review Engine

Main entry point for the Streamlit web application.
Run with: streamlit run app.py

Phase 3.1: UI Foundation - Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import main interface
try:
    from src.ui.main_interface import MainInterface
except ImportError as e:
    st.error(f"Failed to import main interface: {e}")
    st.stop()


def main():
    """Main application entry point"""
    try:
        # Create and run main interface
        app = MainInterface()
        app.run()
        
    except Exception as e:
        st.error(f"Application startup failed: {e}")
        st.markdown("### � Troubleshooting")
        st.markdown("""
        This error typically occurs when:
        1. Core infrastructure components are not initialized
        2. Required dependencies are missing
        3. Configuration files are not accessible
        
        **Solution Steps:**
        1. Ensure all Phase 2 components are properly installed
        2. Run: `pip install -r requirements.txt`
        3. Verify configuration files exist in the config/ directory
        4. Check that all module imports are working correctly
        """)


if __name__ == "__main__":
    main()
