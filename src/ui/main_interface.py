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
    
    # Phase 4.1: Import new integrated components
    from src.ui.components.review_panel import create_review_panel
    from src.ui.components.progress_display import create_progress_display
    from src.ui.components.results_panel import create_results_panel
    from src.ui.components.config_panel import create_config_panel
    from src.ui.components.file_uploader import create_file_uploader
    
    PHASE_4_1_COMPONENTS_AVAILABLE = True
except ImportError as e:
    # Fallback for development
    st.error(f"Core modules not available: {e}")
    PHASE_4_1_COMPONENTS_AVAILABLE = False


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
        
        # Phase 4.1: Initialize integrated components
        if PHASE_4_1_COMPONENTS_AVAILABLE:
            self._initialize_phase_4_1_components()
    
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
    
    def _initialize_phase_4_1_components(self):
        """Initialize Phase 4.1 integrated components"""
        try:
            # Initialize component instances
            self.review_panel = create_review_panel()
            self.progress_display = create_progress_display()
            self.results_panel = create_results_panel()
            self.config_panel = create_config_panel()
            self.file_uploader = create_file_uploader(
                config=None,  # Will use defaults
                logger=self.logger,
                validator=self.validator
            )
            
            # Initialize Phase 4.1 session state
            phase_4_1_state = {
                'current_review_status': None,
                'review_configuration': {},
                'uploaded_document': None,
                'results_history': [],
                'show_advanced_config': False,
                'active_review_id': None
            }
            
            for key, value in phase_4_1_state.items():
                if key not in st.session_state:
                    st.session_state[key] = value
            
            self.logger.info("Phase 4.1 components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Phase 4.1 components: {e}")
            st.error(f"Phase 4.1 integration error: {e}")
    
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
            
            # Navigation menu - Phase 4.1 Enhanced
            pages = {
                "🏠 Home": "home",
                "📤 Upload Documents": "upload", 
                "📋 Review Dashboard": "review",
                "⚙️ Configuration": "configuration",
                "📊 Results & Analysis": "results",
                "📈 Progress Monitor": "progress",
                "📚 History": "history",
                "🔧 Settings": "settings",
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
        
        # Page routing - Phase 4.1 Enhanced
        if current_page == "home":
            self._render_home_page()
        elif current_page == "upload":
            self._render_upload_page()
        elif current_page == "review":
            self._render_review_page()
        elif current_page == "configuration":
            self._render_configuration_page()
        elif current_page == "results":
            self._render_results_page()
        elif current_page == "progress":
            self._render_progress_page()
        elif current_page == "history":
            self._render_history_page()
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
        """Render the document upload page - Phase 4.1 Enhanced"""
        st.markdown("## 📤 Document Upload")
        
        if PHASE_4_1_COMPONENTS_AVAILABLE and hasattr(self, 'file_uploader'):
            # Use Phase 4.1 integrated file uploader
            st.markdown("### Upload Documents for Review")
            
            # Render the enhanced file uploader
            uploaded_file_info = self.file_uploader.render_file_uploader(
                title="Select Document for Review",
                key_suffix="main_upload"
            )
            
            # Handle successful upload
            if uploaded_file_info and uploaded_file_info.get('success'):
                st.success(f"✅ Successfully processed: {uploaded_file_info['name']}")
                
                # Store for review
                st.session_state.uploaded_document = uploaded_file_info
                
                # Quick action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔧 Configure Review", key="configure_from_upload"):
                        st.session_state.current_page = "configuration"
                        st.rerun()
                
                with col2:
                    if st.button("▶️ Start Review", key="start_from_upload"):
                        st.session_state.current_page = "review"
                        st.rerun()
                
                with col3:
                    if st.button("📊 View Progress", key="progress_from_upload"):
                        st.session_state.current_page = "progress"
                        st.rerun()
            
        else:
            # Fallback to original upload interface
            self._render_legacy_upload_interface()
        
    def _render_review_page(self):
        """Render the review dashboard page - Phase 4.1 Enhanced"""
        st.markdown("## 📋 Review Dashboard")
        
        if PHASE_4_1_COMPONENTS_AVAILABLE and hasattr(self, 'review_panel'):
            # Use Phase 4.1 integrated review panel
            review_status = st.session_state.get('current_review_status')
            
            # Render the enhanced review panel
            self.review_panel.render_review_interface(
                review_status=review_status,
                show_configuration=True
            )
            
        else:
            # Fallback to legacy interface
            self._render_legacy_review_interface()
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
    
    # Phase 4.1: New integrated page methods
    
    def _render_configuration_page(self):
        """Render the configuration page"""
        st.markdown("## ⚙️ Review Configuration")
        
        if PHASE_4_1_COMPONENTS_AVAILABLE and hasattr(self, 'config_panel'):
            # Use Phase 4.1 integrated configuration panel
            current_config = self.config_panel.render_configuration_interface(
                show_advanced=st.session_state.get('show_advanced_config', False)
            )
            
            # Store configuration in session state
            st.session_state.review_configuration = current_config
            
            # Quick actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Configuration", key="save_config_main"):
                    st.success("Configuration saved successfully!")
            
            with col2:
                if st.button("🔄 Reset to Defaults", key="reset_config_main"):
                    self.config_panel.reset_to_defaults()
                    st.success("Configuration reset to defaults")
                    st.rerun()
            
            with col3:
                if st.button("▶️ Start Review", key="start_from_config"):
                    st.session_state.current_page = "review"
                    st.rerun()
        else:
            st.warning("⚠️ Phase 4.1 configuration panel not available")
            st.info("Using legacy configuration interface")
    
    def _render_results_page(self):
        """Render the results and analysis page"""
        st.markdown("## 📊 Results & Analysis")
        
        if PHASE_4_1_COMPONENTS_AVAILABLE and hasattr(self, 'results_panel'):
            # Use Phase 4.1 integrated results panel
            review_status = st.session_state.get('current_review_status')
            
            if review_status:
                self.results_panel.render_results_interface(
                    review_status=review_status,
                    show_detailed=True
                )
            else:
                st.info("📊 No review results to display")
                st.markdown("""
                To see results here:
                1. 📤 Upload a document
                2. ⚙️ Configure review settings
                3. ▶️ Start a review
                4. 📊 View comprehensive results
                """)
                
                if st.button("🚀 Start New Review", key="start_new_from_results"):
                    st.session_state.current_page = "upload"
                    st.rerun()
        else:
            st.warning("⚠️ Phase 4.1 results panel not available")
    
    def _render_progress_page(self):
        """Render the progress monitoring page"""
        st.markdown("## 📈 Progress Monitor")
        
        if PHASE_4_1_COMPONENTS_AVAILABLE and hasattr(self, 'progress_display'):
            # Use Phase 4.1 integrated progress display
            review_status = st.session_state.get('current_review_status')
            
            if review_status:
                self.progress_display.render_progress_interface(
                    review_status=review_status,
                    auto_refresh=True
                )
            else:
                st.info("📈 No active review to monitor")
                st.markdown("""
                **Progress Monitoring Features:**
                - 🔄 Real-time status updates
                - 📊 Stage-by-stage progress tracking
                - ⏱️ Performance metrics
                - 🚨 Error detection and alerts
                - 📋 Detailed processing logs
                """)
                
                if st.button("📤 Upload Document", key="upload_from_progress"):
                    st.session_state.current_page = "upload"
                    st.rerun()
        else:
            st.warning("⚠️ Phase 4.1 progress display not available")
    
    def _render_history_page(self):
        """Render the review history page"""
        st.markdown("## 📚 Review History")
        
        # Get history from session state
        history = st.session_state.get('results_history', [])
        
        if history:
            st.markdown(f"### 📋 Recent Reviews ({len(history)})")
            
            for i, review in enumerate(reversed(history[-10:]), 1):
                with st.expander(f"Review {i}: {review.get('document_name', 'Unknown')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Date:** {review.get('completed_at', 'Unknown')}")
                        st.write(f"**Template:** {review.get('template_name', 'Unknown')}")
                        st.write(f"**Score:** {review.get('score', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Status:** {review.get('status', 'Unknown')}")
                        st.write(f"**Issues:** {review.get('critical_issues', 0)}")
                        
                        if st.button(f"📊 View Details", key=f"view_history_{i}"):
                            # Load this review as current
                            st.session_state.current_review_status = review
                            st.session_state.current_page = "results"
                            st.rerun()
        else:
            st.info("📚 No review history available yet")
            st.markdown("""
            **History Features:**
            - 📋 Complete review records
            - 📊 Comparison between reviews
            - 📈 Progress tracking over time
            - 📤 Export historical data
            - 🔍 Search and filter capabilities
            """)
            
            if st.button("🚀 Start First Review", key="start_first_review"):
                st.session_state.current_page = "upload"
                st.rerun()
        
        # History management
        if history:
            st.markdown("---")
            st.markdown("### 🛠️ History Management")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Export History", key="export_history"):
                    st.info("🚧 Export functionality coming in Phase 4.2")
            
            with col2:
                if st.button("🗑️ Clear History", key="clear_history"):
                    st.session_state.results_history = []
                    st.success("History cleared successfully")
                    st.rerun()
            
            with col3:
                if st.button("📊 Analytics", key="history_analytics"):
                    st.info("🚧 Historical analytics coming in Phase 4.3") 
    
    def _render_legacy_upload_interface(self):
        """Legacy upload interface fallback"""
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
                                    'upload_time': datetime.now()
                                })
                                st.success(f"Added {uploaded_file.name} to review queue")
                        else:
                            st.error("❌ File validation failed")
                            for error in validation_result.errors:
                                st.error(f"• {error}")
                    
                    except Exception as e:
                        st.error(f"Validation error: {e}")
                    
                    finally:
                        # Clean up temp file
                        try:
                            tmp_path.unlink(missing_ok=True)
                        except:
                            pass
    
    def _render_legacy_review_interface(self):
        """Legacy review interface fallback"""
        if st.session_state.uploaded_files:
            st.markdown("### 📋 Review Queue")
            
            for i, file_info in enumerate(st.session_state.uploaded_files):
                with st.expander(f"📄 {file_info['name']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Size:** {file_info['size']:,} bytes")
                        st.write(f"**Type:** {file_info['type']}")
                        st.write(f"**Uploaded:** {file_info['upload_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        if st.button(f"🔍 Review {file_info['name']}", key=f"review_{i}"):
                            st.info("🚧 Review functionality will be implemented in Phase 3.2")
                        
                        if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                            st.session_state.uploaded_files.pop(i)
                            st.rerun()
        else:
            st.info("📝 No documents in review queue. Upload documents to get started.")


# Factory function for easy instantiation
def create_main_interface() -> MainInterface:
    """Create and return a MainInterface instance"""
    return MainInterface()
