"""
Main Interface - Automated Review Engine

This module contains the main Streamlit interface components and navigation
for the Automated Review Engine application.

Phase 3.1: UI Foundation - Main Interface Implementation
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import core components
try:
    from src.core.config_manager import ConfigManager
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
    from src.core.validation_utils import DataValidator
except ImportError:
    # Fallback for development
    st.error("Core modules not available. Please ensure Phase 2 infrastructure is set up.")


class MainInterface:
    """Main interface controller for the Streamlit application"""
    
    def __init__(self):
        """Initialize the main interface"""
        self.config = None
        self.logger = None
        self.error_handler = None
        self.validator = None
        self.page_config_set = False
        
        # Initialize session state
        self._initialize_session_state()
        
        # Initialize core components
        self._initialize_core_components()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        default_state = {
            'current_page': 'home',
            'uploaded_files': [],
            'review_results': {},
            'user_settings': {},
            'app_initialized': False,
            'last_activity': datetime.now(),
            'session_id': f"session_{int(time.time())}"
        }
        
        for key, value in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _initialize_core_components(self):
        """Initialize core infrastructure components"""
        try:
            # Initialize configuration
            self.config = ConfigManager()
            config = self.config.load_config()
            
            # Initialize logging
            logging_config = {
                'level': 'INFO',
                'file_enabled': config.logging.file_enabled,
                'console_enabled': config.logging.console_enabled,
                'file_path': config.logging.file_path
            }
            
            self.logger_manager = LoggingManager(logging_config)
            self.logger_manager.initialize()
            self.logger = self.logger_manager.get_logger('ui.main_interface')
            
            # Initialize error handler
            self.error_handler = ErrorHandler()
            
            # Initialize validator
            self.validator = DataValidator()
            
            self.logger.info("Main interface initialized successfully")
            st.session_state.app_initialized = True
            
        except Exception as e:
            st.error(f"Failed to initialize core components: {e}")
            st.session_state.app_initialized = False
    
    def configure_page(self):
        """Configure Streamlit page settings"""
        if not self.page_config_set:
            st.set_page_config(
                page_title="Automated Review Engine",
                page_icon="📋",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': 'https://github.com/your-repo/automated-review-engine',
                    'Report a bug': 'https://github.com/your-repo/automated-review-engine/issues',
                    'About': 'Automated Review Engine v0.3.1 - Regulatory Document Review System'
                }
            )
            self.page_config_set = True
    
    def render_header(self):
        """Render the main application header"""
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.title("🔍 Automated Review Engine")
            
        with col2:
            st.markdown("### *Regulatory Document Review System*")
            
        with col3:
            if st.session_state.app_initialized:
                st.success("✅ Ready")
            else:
                st.error("❌ Error")
        
        # Application status and breadcrumb
        self._render_status_bar()
    
    def _render_status_bar(self):
        """Render application status bar"""
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            st.metric(
                label="📊 Phase Progress", 
                value="3.1", 
                delta="UI Foundation"
            )
            
        with col2:
            st.metric(
                label="📄 Documents", 
                value=len(st.session_state.uploaded_files),
                delta="Uploaded"
            )
            
        with col3:
            st.metric(
                label="⏱️ Session Time",
                value=self._get_session_duration(),
                delta="Active"
            )
            
        with col4:
            if st.button("🔄 Refresh", key="refresh_app"):
                st.rerun()
    
    def _get_session_duration(self) -> str:
        """Get formatted session duration"""
        if 'last_activity' in st.session_state:
            duration = datetime.now() - st.session_state.last_activity
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes}m"
        return "0m"
    
    def render_sidebar(self):
        """Render the main sidebar navigation"""
        with st.sidebar:
            st.markdown("## 🎯 Navigation")
            
            # Navigation menu
            pages = {
                "🏠 Home": "home",
                "📤 Upload Documents": "upload", 
                "📋 Review Dashboard": "review",
                "📊 Reports": "reports",
                "⚙️ Settings": "settings",
                "ℹ️ About": "about"
            }
            
            # Page selection
            for page_label, page_key in pages.items():
                if st.button(page_label, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.session_state.last_activity = datetime.now()
                    st.rerun()
            
            st.markdown("---")
            
            # Quick stats
            self._render_sidebar_stats()
            
            st.markdown("---")
            
            # System status
            self._render_system_status()
    
    def _render_sidebar_stats(self):
        """Render quick statistics in sidebar"""
        st.markdown("### 📈 Quick Stats")
        
        stats = {
            "Files Uploaded": len(st.session_state.uploaded_files),
            "Reviews Completed": len(st.session_state.review_results),
            "Session ID": st.session_state.session_id[-6:],
            "App Version": "v0.3.1"
        }
        
        for label, value in stats.items():
            st.text(f"{label}: {value}")
    
    def _render_system_status(self):
        """Render system status indicators"""
        st.markdown("### 🔧 System Status")
        
        status_items = [
            ("Configuration", self.config is not None),
            ("Logging", self.logger is not None),
            ("Validation", self.validator is not None),
            ("Error Handling", self.error_handler is not None)
        ]
        
        for component, status in status_items:
            icon = "✅" if status else "❌"
            st.text(f"{icon} {component}")
    
    def render_main_content(self):
        """Render main content area based on current page"""
        current_page = st.session_state.current_page
        
        # Page routing
        if current_page == "home":
            self._render_home_page()
        elif current_page == "upload":
            self._render_upload_page()
        elif current_page == "review":
            self._render_review_page()
        elif current_page == "reports":
            self._render_reports_page()
        elif current_page == "settings":
            self._render_settings_page()
        elif current_page == "about":
            self._render_about_page()
        else:
            self._render_home_page()
    
    def _render_home_page(self):
        """Render the home/dashboard page"""
        st.markdown("## 🏠 Dashboard")
        
        # Welcome message
        if st.session_state.app_initialized:
            st.success("Welcome to the Automated Review Engine! All systems are operational.")
        else:
            st.warning("System initialization in progress...")
        
        # Feature overview cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container(border=True):
                st.markdown("### 📤 Document Upload")
                st.markdown("Upload PDF and Word documents for automated review.")
                if st.button("Go to Upload", key="goto_upload"):
                    st.session_state.current_page = "upload"
                    st.rerun()
        
        with col2:
            with st.container(border=True):
                st.markdown("### 📋 Review Process")
                st.markdown("Automated validation against regulatory templates.")
                if st.button("View Reviews", key="goto_review"):
                    st.session_state.current_page = "review"
                    st.rerun()
        
        with col3:
            with st.container(border=True):
                st.markdown("### 📊 Reports")
                st.markdown("Generate comprehensive compliance reports.")
                if st.button("Generate Reports", key="goto_reports"):
                    st.session_state.current_page = "reports"
                    st.rerun()
        
        # Recent activity
        st.markdown("## 📈 Recent Activity")
        
        if st.session_state.uploaded_files:
            st.info(f"📄 {len(st.session_state.uploaded_files)} documents uploaded")
        else:
            st.info("📝 No recent activity. Upload documents to get started.")
        
        # Phase 3.1 development status
        self._render_development_status()
    
    def _render_upload_page(self):
        """Render the document upload page"""
        st.markdown("## 📤 Document Upload")
        
        # Upload interface
        uploaded_file = st.file_uploader(
            "Choose a document to review",
            type=['pdf', 'docx', 'doc'],
            help="Upload PDF or Word documents for automated review"
        )
        
        if uploaded_file is not None:
            # File information
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**File Name:** {uploaded_file.name}")
                st.info(f"**File Size:** {uploaded_file.size:,} bytes")
                st.info(f"**File Type:** {uploaded_file.type}")
            
            with col2:
                if self.validator:
                    # Validate file using Phase 2 validator
                    file_config = {
                        'max_file_size_mb': 50,
                        'allowed_extensions': ['.pdf', '.docx', '.doc'],
                        'enable_security_checks': True
                    }
                    
                    # For demonstration, create a temp file
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = Path(tmp_file.name)
                    
                    try:
                        validation_result = self.validator.validate_file_upload(tmp_path, file_config)
                        
                        if validation_result.is_valid:
                            st.success("✅ File validation passed")
                            
                            if st.button("Add to Review Queue", key="add_to_queue"):
                                st.session_state.uploaded_files.append({
                                    'name': uploaded_file.name,
                                    'size': uploaded_file.size,
                                    'type': uploaded_file.type,
                                    'upload_time': datetime.now(),
                                    'status': 'queued'
                                })
                                st.success(f"✅ {uploaded_file.name} added to review queue!")
                                st.rerun()
                        else:
                            st.error(f"❌ File validation failed: {validation_result.errors}")
                    
                    finally:
                        # Clean up temp file
                        tmp_path.unlink(missing_ok=True)
                else:
                    st.warning("⚠️ Validator not available")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.markdown("### 📋 Upload Queue")
            
            for idx, file_info in enumerate(st.session_state.uploaded_files):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.text(file_info['name'])
                
                with col2:
                    st.text(f"{file_info['size']:,} bytes")
                
                with col3:
                    status_color = {"queued": "🟡", "processing": "🔵", "completed": "🟢", "error": "🔴"}
                    st.text(f"{status_color.get(file_info['status'], '⚪')} {file_info['status'].title()}")
                
                with col4:
                    if st.button("🗑️", key=f"remove_{idx}", help="Remove file"):
                        st.session_state.uploaded_files.pop(idx)
                        st.rerun()
    
    def _render_review_page(self):
        """Render the review dashboard page"""
        st.markdown("## 📋 Review Dashboard")
        
        if not st.session_state.uploaded_files:
            st.info("📝 No documents uploaded yet. Visit the Upload page to get started.")
            return
        
        st.markdown(f"### 📊 {len(st.session_state.uploaded_files)} Documents in Queue")
        
        # Review controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start All Reviews", key="start_all_reviews"):
                st.success("🔄 Review process started! (Demo mode)")
                
        with col2:
            if st.button("⏸️ Pause Reviews", key="pause_reviews"):
                st.info("⏸️ Reviews paused")
                
        with col3:
            if st.button("🔄 Refresh Status", key="refresh_reviews"):
                st.rerun()
        
        # Document list with status
        for idx, file_info in enumerate(st.session_state.uploaded_files):
            with st.expander(f"📄 {file_info['name']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Size:** {file_info['size']:,} bytes")
                    st.markdown(f"**Type:** {file_info['type']}")
                    st.markdown(f"**Uploaded:** {file_info['upload_time'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.markdown(f"**Status:** {file_info['status'].title()}")
                    
                    if st.button(f"📋 Review Details", key=f"review_details_{idx}"):
                        st.info("📋 Detailed review interface will be implemented in Phase 3.2")
    
    def _render_reports_page(self):
        """Render the reports page"""
        st.markdown("## 📊 Reports & Analytics")
        
        if not st.session_state.uploaded_files:
            st.info("📝 No data available for reports. Upload and review documents first.")
            return
        
        # Report options
        report_type = st.selectbox(
            "Select Report Type",
            ["Summary Report", "Detailed Analysis", "Compliance Check", "Export Data"],
            key="report_type_selector"
        )
        
        # Generate report button
        if st.button("📈 Generate Report", key="generate_report"):
            with st.spinner("Generating report..."):
                time.sleep(2)  # Simulate processing
                st.success(f"✅ {report_type} generated successfully!")
                
                # Sample report data
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Documents Processed", len(st.session_state.uploaded_files))
                    st.metric("Compliance Score", "85%", delta="5%")
                
                with col2:
                    st.metric("Issues Found", "3", delta="-1")
                    st.metric("Review Time", "2.5 min", delta="-0.5 min")
                
                # Sample chart
                import pandas as pd
                import numpy as np
                
                chart_data = pd.DataFrame(
                    np.random.randn(20, 3),
                    columns=['Compliance', 'Quality', 'Completeness']
                )
                st.line_chart(chart_data)
    
    def _render_settings_page(self):
        """Render the settings page"""
        st.markdown("## ⚙️ Application Settings")
        
        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "📄 Document", "🔒 Security", "📊 Advanced"])
        
        with tab1:
            st.markdown("### General Settings")
            
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme_setting")
            language = st.selectbox("Language", ["English", "German", "French"], key="language_setting")
            auto_save = st.checkbox("Auto-save progress", value=True, key="auto_save_setting")
            
            if st.button("💾 Save General Settings", key="save_general"):
                st.session_state.user_settings.update({
                    'theme': theme,
                    'language': language,
                    'auto_save': auto_save
                })
                st.success("✅ Settings saved successfully!")
        
        with tab2:
            st.markdown("### Document Processing Settings")
            
            max_file_size = st.number_input("Max file size (MB)", min_value=1, max_value=100, value=50, key="max_file_size_setting")
            allowed_formats = st.multiselect("Allowed formats", ["PDF", "DOCX", "DOC"], default=["PDF", "DOCX"], key="allowed_formats_setting")
            auto_review = st.checkbox("Enable auto-review", value=True, key="auto_review_setting")
            
            if st.button("💾 Save Document Settings", key="save_document"):
                st.success("✅ Document settings saved!")
        
        with tab3:
            st.markdown("### Security Settings")
            
            enable_encryption = st.checkbox("Enable file encryption", value=True, key="encryption_setting")
            virus_scan = st.checkbox("Enable virus scanning", value=True, key="virus_scan_setting")
            audit_log = st.checkbox("Enable audit logging", value=True, key="audit_log_setting")
            
            if st.button("💾 Save Security Settings", key="save_security"):
                st.success("✅ Security settings saved!")
        
        with tab4:
            st.markdown("### Advanced Settings")
            
            debug_mode = st.checkbox("Enable debug mode", value=False, key="debug_mode_setting")
            api_timeout = st.number_input("API timeout (seconds)", min_value=5, max_value=300, value=30, key="api_timeout_setting")
            cache_size = st.number_input("Cache size (MB)", min_value=10, max_value=1000, value=100, key="cache_size_setting")
            
            if st.button("💾 Save Advanced Settings", key="save_advanced"):
                st.success("✅ Advanced settings saved!")
        
        # Reset all settings
        st.markdown("---")
        if st.button("🔄 Reset All Settings", key="reset_all_settings", type="secondary"):
            st.session_state.user_settings = {}
            st.success("✅ All settings reset to defaults!")
    
    def _render_about_page(self):
        """Render the about page"""
        st.markdown("## ℹ️ About Automated Review Engine")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🎯 Mission
            The Automated Review Engine (ARE) streamlines regulatory document review processes 
            for medical device companies, focusing on EU Declaration of Conformity compliance.
            
            ### 🚀 Features
            - **Automated Document Processing**: PDF and Word document analysis
            - **Template Validation**: Structure compliance checking
            - **Review Script Execution**: Customizable review workflows
            - **PLM Integration**: Search direction generation
            - **Comprehensive Reporting**: Detailed compliance reports
            
            ### 📊 Current Status
            - **Version**: v0.3.1 (Phase 3.1 - UI Foundation)
            - **Development Phase**: User Interface Implementation
            - **Overall Progress**: 40% complete
            
            ### 🏗️ Architecture
            Built on modern Python technologies:
            - **Frontend**: Streamlit web framework
            - **Backend**: Python with modular architecture
            - **Configuration**: YAML-based configuration management
            - **Logging**: Comprehensive logging and monitoring
            - **Testing**: Full test coverage with pytest
            """)
        
        with col2:
            st.markdown("### 📈 Development Timeline")
            phases = [
                ("✅ Phase 1: Foundation", "Completed"),
                ("✅ Phase 2.1: Document Processing", "Completed"),
                ("✅ Phase 2.2: Configuration & Logging", "Completed"),
                ("✅ Phase 2.3: Testing Framework", "Completed"),
                ("🔄 Phase 3.1: UI Foundation", "In Progress"),
                ("📋 Phase 3.2: Review Logic", "Planned"),
                ("📋 Phase 3.3: Report Generation", "Planned"),
                ("📋 Phase 4: Compliance Engine", "Planned")
            ]
            
            for phase, status in phases:
                st.text(f"{phase}")
                st.caption(f"Status: {status}")
        
        # System information
        st.markdown("---")
        st.markdown("### 🔧 System Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.text(f"Session ID: {st.session_state.session_id}")
            st.text(f"App Initialized: {'Yes' if st.session_state.app_initialized else 'No'}")
            
        with col2:
            st.text(f"Current Page: {st.session_state.current_page}")
            st.text(f"Uploaded Files: {len(st.session_state.uploaded_files)}")
            
        with col3:
            st.text(f"Python Version: {sys.version.split()[0]}")
            st.text(f"Streamlit Version: {st.__version__}")
    
    def _render_development_status(self):
        """Render development status information"""
        st.markdown("---")
        
        with st.expander("🚧 Phase 3.1 Development Status", expanded=False):
            st.markdown("""
            ### ✅ Completed Features
            - Main interface framework
            - Navigation system  
            - Page routing
            - Session state management
            - Core component integration
            - File upload interface
            - Settings management
            - System status monitoring
            
            ### 🔄 In Development
            - Advanced file processing
            - Review workflow integration
            - Real-time status updates
            - Enhanced error handling
            
            ### 📋 Upcoming (Phase 3.2)
            - Document review logic
            - Template validation
            - Review script execution
            - Progress tracking
            """)
    
    def render_footer(self):
        """Render application footer"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Automated Review Engine v0.3.1**")
            
        with col2:
            st.markdown(f"**Session:** {st.session_state.session_id[-8:]}")
            
        with col3:
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    def run(self):
        """Main application run method"""
        try:
            # Configure page
            self.configure_page()
            
            # Render header
            self.render_header()
            
            # Create layout
            self.render_sidebar()
            
            # Render main content
            self.render_main_content()
            
            # Render footer
            self.render_footer()
            
            # Update activity timestamp
            st.session_state.last_activity = datetime.now()
            
        except Exception as e:
            if self.error_handler:
                error_context = self.error_handler.handle_error(e)
                st.error(f"Application Error: {error_context.user_message}")
                if self.logger:
                    self.logger.error(f"Application error: {error_context.message}")
            else:
                st.error(f"Application Error: {str(e)}")


# Factory function for easy instantiation
def create_main_interface() -> MainInterface:
    """Create and return a MainInterface instance"""
    return MainInterface()
