"""
Review Panel Component - Automated Review Engine

Advanced review workflow and execution interface with full integration
to document analysis, template validation, and review engine components.

Phase 4.1: UI Integration - Enhanced Review Panel
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
import time
from datetime import datetime
import uuid

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Review engine imports
try:
    from src.review import (
        create_review_engine,
        create_review_request,
        ReviewEngine,
        ReviewRequest,
        ReviewStatus,
        ReviewType,
        ReviewPriority,
        COMPONENT_STATUS
    )
    REVIEW_ENGINE_AVAILABLE = True
except ImportError as e:
    st.error(f"Review engine not available: {e}")
    REVIEW_ENGINE_AVAILABLE = False
    create_review_engine = None
    create_review_request = None

# Core infrastructure imports
try:
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
except ImportError:
    LoggingManager = None
    ErrorHandler = None


class ReviewPanel:
    """Enhanced review panel with full review engine integration"""
    
    def __init__(self):
        """Initialize review panel with review engine"""
        self.review_engine = None
        self.logger = None
        self.error_handler = None
        
        # Initialize review engine if available
        if REVIEW_ENGINE_AVAILABLE:
            self._initialize_review_engine()
        
        # Session state keys
        self.state_keys = {
            'current_review_id': 'review_panel_current_review',
            'review_status': 'review_panel_status',
            'review_results': 'review_panel_results',
            'review_config': 'review_panel_config',
            'review_history': 'review_panel_history'
        }
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_review_engine(self):
        """Initialize review engine and supporting components"""
        try:
            # Create review engine
            engine_config = {
                'max_concurrent_reviews': 3,
                'enable_background_processing': True,
                'detailed_logging': True
            }
            self.review_engine = create_review_engine(engine_config)
            
            # Initialize logging if available
            if LoggingManager:
                logger_manager = LoggingManager({'level': 'INFO'})
                logger_manager.initialize()
                self.logger = logger_manager.get_logger('ui.review_panel')
            
            # Initialize error handler
            if ErrorHandler:
                self.error_handler = ErrorHandler()
            
            if self.logger:
                self.logger.info("Review panel initialized with review engine")
                
        except Exception as e:
            st.error(f"Failed to initialize review engine: {e}")
            self.review_engine = None
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        for key in self.state_keys.values():
            if key not in st.session_state:
                if 'history' in key:
                    st.session_state[key] = []
                elif 'config' in key:
                    st.session_state[key] = {
                        'template_name': 'eu_doc',
                        'review_type': 'eu_doc_validation',
                        'priority': 'normal',
                        'timeout_seconds': 300
                    }
                else:
                    st.session_state[key] = None
    
    def render_review_interface(self) -> None:
        """Render complete review interface with engine integration"""
        st.header("📋 Document Review Engine")
        
        # Check engine availability
        if not REVIEW_ENGINE_AVAILABLE or not self.review_engine:
            self._render_engine_unavailable()
            return
        
        # Component status display
        self._render_component_status()
        
        # Main review interface tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Review Execution", 
            "⚙️ Configuration", 
            "📊 Progress & Status",
            "📈 History & Statistics"
        ])
        
        with tab1:
            self._render_review_execution()
        
        with tab2:
            self._render_review_configuration()
        
        with tab3:
            self._render_progress_status()
        
        with tab4:
            self._render_history_statistics()
    
    def _render_engine_unavailable(self):
        """Render interface when review engine is unavailable"""
        st.error("🚫 Review Engine Not Available")
        
        st.markdown("""
        The review engine components are not properly initialized. This could be due to:
        
        - Missing dependencies (PyPDF2, pdfplumber, python-docx)
        - Import errors in review engine modules
        - Configuration issues
        
        **To resolve:**
        1. Check that all review engine files are present in `src/review/`
        2. Install required dependencies: `pip install PyPDF2 pdfplumber python-docx`
        3. Restart the application
        """)
        
        # Show component status for debugging
        if 'COMPONENT_STATUS' in globals():
            st.subheader("Component Status")
            for component, available in COMPONENT_STATUS.items():
                status_icon = "✅" if available else "❌"
                st.text(f"{status_icon} {component}: {'Available' if available else 'Unavailable'}")
    
    def _render_component_status(self):
        """Render component availability status"""
        with st.expander("🔧 System Status", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                analyzer_status = COMPONENT_STATUS.get('document_analyzer', False)
                st.metric(
                    "Document Analyzer", 
                    "✅ Ready" if analyzer_status else "❌ Not Available",
                    delta=None
                )
            
            with col2:
                processor_status = COMPONENT_STATUS.get('template_processor', False)
                st.metric(
                    "Template Processor", 
                    "✅ Ready" if processor_status else "❌ Not Available",
                    delta=None
                )
            
            with col3:
                engine_status = COMPONENT_STATUS.get('review_engine', False)
                st.metric(
                    "Review Engine", 
                    "✅ Ready" if engine_status else "❌ Not Available",
                    delta=None
                )
            
            with col4:
                workflow_status = COMPONENT_STATUS.get('workflow_manager', False)
                st.metric(
                    "Workflow Manager", 
                    "✅ Ready" if workflow_status else "❌ Not Available",
                    delta=None
                )
    
    def _render_review_execution(self):
        """Render review execution interface"""
        st.subheader("🚀 Execute Document Review")
        
        # Document selection
        uploaded_files = st.session_state.get('uploaded_files', [])
        
        if not uploaded_files:
            st.warning("📄 No documents uploaded. Please upload documents in the File Upload section first.")
            return
        
        # Document selection
        selected_file = st.selectbox(
            "Select document to review:",
            options=uploaded_files,
            format_func=lambda x: f"📄 {x['name']} ({x['size']:.1f} KB)" if isinstance(x, dict) else str(x)
        )
        
        if not selected_file:
            return
        
        # Review configuration summary
        config = st.session_state[self.state_keys['review_config']]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"""
            **Review Configuration:**
            - Template: {config['template_name']}
            - Review Type: {config['review_type']}
            - Priority: {config['priority']}
            - Timeout: {config['timeout_seconds']}s
            """)
        
        with col2:
            if st.button("🔍 Start Review", type="primary", use_container_width=True):
                self._execute_review(selected_file, config)
        
        # Current review status
        current_review_id = st.session_state[self.state_keys['current_review_id']]
        if current_review_id:
            self._render_current_review_status(current_review_id)
    
    def _render_review_configuration(self):
        """Render review configuration interface"""
        st.subheader("⚙️ Review Configuration")
        
        config = st.session_state[self.state_keys['review_config']]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Template selection
            template_options = [
                'eu_doc',
                'medical_device_declaration',
                'custom_template'
            ]
            
            new_template = st.selectbox(
                "Template:",
                options=template_options,
                index=template_options.index(config['template_name']) if config['template_name'] in template_options else 0,
                help="Select the validation template to use"
            )
            
            # Review type selection
            review_type_options = [
                'eu_doc_validation',
                'template_compliance', 
                'full_analysis',
                'custom_script'
            ]
            
            new_review_type = st.selectbox(
                "Review Type:",
                options=review_type_options,
                index=review_type_options.index(config['review_type']) if config['review_type'] in review_type_options else 0,
                help="Select the type of review to perform"
            )
        
        with col2:
            # Priority selection
            priority_options = ['low', 'normal', 'high', 'urgent']
            
            new_priority = st.selectbox(
                "Priority:",
                options=priority_options,
                index=priority_options.index(config['priority']) if config['priority'] in priority_options else 1,
                help="Set review priority level"
            )
            
            # Timeout setting
            new_timeout = st.number_input(
                "Timeout (seconds):",
                min_value=30,
                max_value=1800,
                value=config['timeout_seconds'],
                step=30,
                help="Maximum time to wait for review completion"
            )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings", expanded=False):
            st.checkbox("Enable detailed logging", value=True)
            st.checkbox("Generate comprehensive report", value=True)
            st.checkbox("Include raw analysis data", value=False)
            st.slider("Validation strictness", 1, 10, 7)
        
        # Update configuration
        if st.button("💾 Save Configuration"):
            st.session_state[self.state_keys['review_config']] = {
                'template_name': new_template,
                'review_type': new_review_type,
                'priority': new_priority,
                'timeout_seconds': new_timeout
            }
            st.success("Configuration saved!")
            st.rerun()
    
    def _render_progress_status(self):
        """Render progress and status monitoring"""
        st.subheader("📊 Review Progress & Status")
        
        current_review_id = st.session_state[self.state_keys['current_review_id']]
        
        if not current_review_id:
            st.info("No active review. Start a review to see progress here.")
            return
        
        # Get current review status
        review_status = self.review_engine.get_review_status(current_review_id)
        
        if not review_status:
            st.error("Could not retrieve review status")
            return
        
        # Status overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_color = {
                'pending': '🟡',
                'in_progress': '🔵', 
                'completed': '🟢',
                'failed': '🔴',
                'cancelled': '⚫'
            }
            
            st.metric(
                "Status",
                f"{status_color.get(review_status.status.value, '❓')} {review_status.status.value.title()}",
                delta=None
            )
        
        with col2:
            if review_status.started_at:
                elapsed = (datetime.now() - review_status.started_at).total_seconds()
                st.metric("Elapsed Time", f"{elapsed:.1f}s")
            else:
                st.metric("Elapsed Time", "Not started")
        
        with col3:
            if review_status.status.value in ['completed', 'failed']:
                st.metric("Processing Time", f"{review_status.processing_time:.2f}s")
            else:
                st.metric("Processing Time", "In progress...")
        
        # Progress details
        if review_status.status.value == 'in_progress':
            # Simulate progress updates (in real implementation, this would come from the engine)
            progress_value = min(90, int(time.time() * 10) % 100)
            st.progress(progress_value / 100, f"Processing... {progress_value}%")
            
            st.info("🔄 Review in progress. This page will auto-update...")
            time.sleep(1)
            st.rerun()
        
        # Results preview
        if review_status.status.value == 'completed':
            self._render_review_results(review_status)
        
        # Error display
        if review_status.error_message:
            st.error(f"❌ Error: {review_status.error_message}")
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Status"):
                st.rerun()
        
        with col2:
            if review_status.status.value in ['pending', 'in_progress']:
                if st.button("⏹️ Cancel Review", type="secondary"):
                    if self.review_engine.cancel_review(current_review_id):
                        st.success("Review cancelled")
                        st.session_state[self.state_keys['current_review_id']] = None
                        st.rerun()
        
        with col3:
            if review_status.status.value in ['completed', 'failed']:
                if st.button("🧹 Clear Review"):
                    st.session_state[self.state_keys['current_review_id']] = None
                    st.session_state[self.state_keys['review_results']] = None
                    st.rerun()
    
    def _render_history_statistics(self):
        """Render review history and engine statistics"""
        st.subheader("📈 Review History & Statistics")
        
        # Engine statistics
        if self.review_engine:
            stats = self.review_engine.get_engine_statistics()
            queue_status = self.review_engine.get_queue_status()
            
            st.subheader("📊 Engine Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Reviews", stats['reviews_processed'])
            
            with col2:
                st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
            
            with col3:
                st.metric("Active Reviews", stats['active_reviews'])
            
            with col4:
                st.metric("Queue Length", queue_status['queue_length'])
            
            # Additional statistics
            if stats['reviews_processed'] > 0:
                st.metric(
                    "Average Processing Time", 
                    f"{stats['average_processing_time']:.2f}s"
                )
        
        # Review history
        st.subheader("📋 Recent Reviews")
        
        history = st.session_state[self.state_keys['review_history']]
        
        if not history:
            st.info("No review history available yet.")
        else:
            for i, review in enumerate(reversed(history[-10:])):  # Show last 10
                with st.expander(f"Review {len(history) - i}: {review.get('document_name', 'Unknown')} - {review.get('status', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Template:** {review.get('template_name', 'Unknown')}")
                        st.write(f"**Status:** {review.get('status', 'Unknown')}")
                        st.write(f"**Started:** {review.get('started_at', 'Unknown')}")
                    
                    with col2:
                        if 'overall_score' in review:
                            st.write(f"**Score:** {review['overall_score']:.1f}/100")
                        if 'compliance_percentage' in review:
                            st.write(f"**Compliance:** {review['compliance_percentage']:.1f}%")
                        if 'processing_time' in review:
                            st.write(f"**Time:** {review['processing_time']:.2f}s")
    
    def _execute_review(self, selected_file: Dict, config: Dict):
        """Execute document review"""
        try:
            # Create review request
            if isinstance(selected_file, dict):
                document_path = selected_file.get('path', str(selected_file))
                document_name = selected_file.get('name', 'Unknown')
            else:
                document_path = str(selected_file)
                document_name = Path(document_path).name
            
            review_request = create_review_request(
                document_path=document_path,
                review_type=config['review_type'],
                template_name=config['template_name'],
                priority=config['priority'],
                timeout_seconds=config['timeout_seconds']
            )
            
            # Submit review
            review_id = self.review_engine.submit_review(review_request)
            
            # Update session state
            st.session_state[self.state_keys['current_review_id']] = review_id
            
            # Add to history
            history_entry = {
                'review_id': review_id,
                'document_name': document_name,
                'template_name': config['template_name'],
                'status': 'submitted',
                'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            history = st.session_state[self.state_keys['review_history']]
            history.append(history_entry)
            st.session_state[self.state_keys['review_history']] = history
            
            st.success(f"✅ Review started! Review ID: {review_id}")
            
            if self.logger:
                self.logger.info(f"Review started: {review_id} for document: {document_name}")
            
            # Auto-refresh to show progress
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            error_msg = f"Failed to start review: {str(e)}"
            st.error(error_msg)
            
            if self.logger:
                self.logger.error(error_msg)
    
    def _render_current_review_status(self, review_id: str):
        """Render current review status summary"""
        st.subheader("🔍 Current Review Status")
        
        review_status = self.review_engine.get_review_status(review_id)
        
        if review_status:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**ID:** {review_id[:8]}...")
                st.write(f"**Status:** {review_status.status.value}")
            
            with col2:
                st.write(f"**Template:** {review_status.template_name}")
                st.write(f"**Type:** {review_status.review_type.value}")
            
            with col3:
                if review_status.processing_time > 0:
                    st.write(f"**Time:** {review_status.processing_time:.2f}s")
                if hasattr(review_status, 'overall_score') and review_status.overall_score > 0:
                    st.write(f"**Score:** {review_status.overall_score:.1f}/100")
    
    def _render_review_results(self, review_status):
        """Render comprehensive review results"""
        st.subheader("📊 Review Results")
        
        # Overall scores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if hasattr(review_status, 'overall_score'):
                st.metric("Overall Score", f"{review_status.overall_score:.1f}/100")
        
        with col2:
            if hasattr(review_status, 'compliance_percentage'):
                st.metric("Compliance", f"{review_status.compliance_percentage:.1f}%")
        
        with col3:
            st.metric("Processing Time", f"{review_status.processing_time:.2f}s")
        
        # Critical issues
        if hasattr(review_status, 'critical_issues') and review_status.critical_issues:
            st.subheader("⚠️ Critical Issues")
            for issue in review_status.critical_issues:
                st.error(f"• {issue}")
        
        # Recommendations
        if hasattr(review_status, 'recommendations') and review_status.recommendations:
            st.subheader("💡 Recommendations")
            for rec in review_status.recommendations:
                st.info(f"• {rec}")
        
        # Export options
        st.subheader("📤 Export Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as Text"):
                try:
                    result_text = self.review_engine.export_review_results(
                        review_status.request_id, 
                        format='text'
                    )
                    st.download_button(
                        "⬇️ Download Text Report",
                        result_text,
                        f"review_report_{review_status.request_id[:8]}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col2:
            if st.button("📊 Export as JSON"):
                try:
                    result_json = self.review_engine.export_review_results(
                        review_status.request_id, 
                        format='json'
                    )
                    import json
                    st.download_button(
                        "⬇️ Download JSON Report",
                        json.dumps(result_json, indent=2),
                        f"review_report_{review_status.request_id[:8]}.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col3:
            st.info("PDF export coming in Phase 4.2")


def create_review_panel() -> ReviewPanel:
    """Create and return a ReviewPanel instance"""
    return ReviewPanel()
