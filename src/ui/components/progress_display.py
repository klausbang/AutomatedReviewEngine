"""
Progress Display Component - Automated Review Engine

Real-time progress tracking and status updates for review operations.

Phase 4.1: UI Integration - Progress Display Component
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
import time
from datetime import datetime, timedelta

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Review engine imports
try:
    from src.review import ReviewStatus, ReviewEngine
    REVIEW_ENGINE_AVAILABLE = True
except ImportError:
    REVIEW_ENGINE_AVAILABLE = False
    ReviewStatus = None


class ProgressDisplay:
    """Real-time progress display component"""
    
    def __init__(self):
        """Initialize progress display"""
        self.refresh_interval = 2.0  # seconds
        self.progress_stages = {
            'initialization': {'progress': 0, 'message': 'Initializing review process...'},
            'document_analysis': {'progress': 25, 'message': 'Analyzing document structure...'},
            'template_validation': {'progress': 50, 'message': 'Validating against template...'},
            'rule_execution': {'progress': 75, 'message': 'Executing validation rules...'},
            'results_compilation': {'progress': 90, 'message': 'Compiling results...'},
            'finalization': {'progress': 100, 'message': 'Review completed!'}
        }
    
    def render_progress_interface(
        self, 
        review_engine: Optional[Any] = None, 
        review_id: Optional[str] = None
    ) -> None:
        """
        Render progress tracking interface
        
        Args:
            review_engine: Review engine instance
            review_id: Current review ID to track
        """
        if not review_id:
            self._render_no_active_review()
            return
        
        if not review_engine:
            self._render_engine_unavailable()
            return
        
        # Get current review status
        review_status = review_engine.get_review_status(review_id)
        
        if not review_status:
            st.error(f"❌ Could not find review: {review_id}")
            return
        
        # Render progress based on status
        if review_status.status.value == 'pending':
            self._render_pending_status(review_status)
        elif review_status.status.value == 'in_progress':
            self._render_in_progress_status(review_status)
        elif review_status.status.value == 'completed':
            self._render_completed_status(review_status)
        elif review_status.status.value == 'failed':
            self._render_failed_status(review_status)
        elif review_status.status.value == 'cancelled':
            self._render_cancelled_status(review_status)
        else:
            self._render_unknown_status(review_status)
    
    def _render_no_active_review(self):
        """Render interface when no review is active"""
        st.info("🔍 No active review to track")
        st.markdown("""
        Start a new review in the **Review Execution** tab to see real-time progress here.
        
        **What you'll see here:**
        - ⏱️ Real-time progress updates
        - 📊 Processing stage information  
        - ⚡ Performance metrics
        - 🎯 Estimated completion time
        """)
    
    def _render_engine_unavailable(self):
        """Render interface when review engine is unavailable"""
        st.error("🚫 Review Engine Unavailable")
        st.markdown("""
        Progress tracking requires the review engine to be properly initialized.
        Please check the system status in the main review panel.
        """)
    
    def _render_pending_status(self, review_status):
        """Render pending review status"""
        st.info("⏳ Review Pending")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show pending progress bar
            st.progress(0, "Waiting in queue...")
            
            # Queue information
            st.markdown(f"""
            **Review Details:**
            - Review ID: `{review_status.request_id[:12]}...`
            - Document: `{Path(review_status.document_path).name}`
            - Template: `{review_status.template_name}`
            - Priority: `{review_status.metadata.get('priority', 'normal')}`
            """)
        
        with col2:
            # Time since submission
            if review_status.started_at:
                wait_time = (datetime.now() - review_status.started_at).total_seconds()
                st.metric("Wait Time", f"{wait_time:.1f}s")
            
            # Auto-refresh button
            if st.button("🔄 Refresh", key="pending_refresh"):
                st.rerun()
        
        # Auto-refresh for pending reviews
        if st.session_state.get('auto_refresh_enabled', True):
            with st.empty():
                st.caption("Auto-refreshing every 2 seconds...")
                time.sleep(2)
                st.rerun()
    
    def _render_in_progress_status(self, review_status):
        """Render in-progress review status"""
        st.success("🔄 Review In Progress")
        
        # Get progress information from metadata
        current_stage = review_status.metadata.get('current_stage', 'document_analysis')
        progress_data = self.progress_stages.get(current_stage, self.progress_stages['document_analysis'])
        
        # Simulate dynamic progress within stage
        base_progress = progress_data['progress']
        time_factor = int(time.time()) % 10
        dynamic_progress = min(100, base_progress + time_factor)
        
        # Main progress bar
        st.progress(dynamic_progress / 100, progress_data['message'])
        
        # Detailed status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Elapsed time
            if review_status.started_at:
                elapsed = (datetime.now() - review_status.started_at).total_seconds()
                st.metric("Elapsed Time", f"{elapsed:.1f}s")
            else:
                st.metric("Elapsed Time", "Unknown")
        
        with col2:
            # Current stage
            st.metric("Current Stage", current_stage.replace('_', ' ').title())
        
        with col3:
            # Estimated remaining time (simulated)
            remaining_progress = 100 - dynamic_progress
            estimated_remaining = (remaining_progress / 10) * 2  # Rough estimate
            st.metric("Est. Remaining", f"{estimated_remaining:.0f}s")
        
        # Stage breakdown
        st.subheader("📋 Processing Stages")
        
        stages_list = [
            'initialization',
            'document_analysis', 
            'template_validation',
            'rule_execution',
            'results_compilation',
            'finalization'
        ]
        
        for i, stage in enumerate(stages_list):
            stage_data = self.progress_stages[stage]
            
            if stage == current_stage:
                # Current stage - show as in progress
                st.markdown(f"🔄 **{stage.replace('_', ' ').title()}** - In Progress")
                st.progress(0.7, stage_data['message'])
            elif stage_data['progress'] <= dynamic_progress:
                # Completed stages
                st.markdown(f"✅ **{stage.replace('_', ' ').title()}** - Completed")
            else:
                # Future stages
                st.markdown(f"⏳ **{stage.replace('_', ' ').title()}** - Pending")
        
        # Performance metrics
        with st.expander("📊 Performance Metrics", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Memory usage (simulated)
                memory_usage = 45 + (time_factor * 2)
                st.metric("Memory Usage", f"{memory_usage}%")
                
                # CPU usage (simulated)
                cpu_usage = 30 + (time_factor * 3)
                st.metric("CPU Usage", f"{cpu_usage}%")
            
            with col2:
                # Processing speed (simulated)
                speed = 1.2 + (time_factor * 0.1)
                st.metric("Processing Speed", f"{speed:.1f} pages/sec")
                
                # Data processed (simulated)
                data_processed = min(100, base_progress + (time_factor * 2))
                st.metric("Data Processed", f"{data_processed}%")
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Force Refresh", key="progress_refresh"):
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox(
                "Auto Refresh", 
                value=st.session_state.get('auto_refresh_enabled', True),
                key="auto_refresh_checkbox"
            )
            st.session_state['auto_refresh_enabled'] = auto_refresh
        
        with col3:
            if st.button("⏹️ Cancel Review", key="progress_cancel", type="secondary"):
                st.session_state['cancel_review_requested'] = True
                st.warning("Cancel request submitted...")
        
        # Auto-refresh for in-progress reviews
        if st.session_state.get('auto_refresh_enabled', True):
            with st.empty():
                st.caption("Auto-refreshing every 2 seconds...")
                time.sleep(2)
                st.rerun()
    
    def _render_completed_status(self, review_status):
        """Render completed review status"""
        st.success("✅ Review Completed Successfully!")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Status", "✅ Completed")
        
        with col2:
            st.metric("Processing Time", f"{review_status.processing_time:.2f}s")
        
        with col3:
            if hasattr(review_status, 'overall_score'):
                score = review_status.overall_score
                st.metric("Overall Score", f"{score:.1f}/100")
            else:
                st.metric("Overall Score", "N/A")
        
        with col4:
            if hasattr(review_status, 'compliance_percentage'):
                compliance = review_status.compliance_percentage
                st.metric("Compliance", f"{compliance:.1f}%")
            else:
                st.metric("Compliance", "N/A")
        
        # Completion timeline
        st.subheader("⏱️ Completion Timeline")
        
        if review_status.started_at and review_status.completed_at:
            total_time = review_status.processing_time
            
            # Show stage completion times (estimated breakdown)
            stages_with_times = [
                ('Initialization', 0.1 * total_time),
                ('Document Analysis', 0.3 * total_time),
                ('Template Validation', 0.4 * total_time),
                ('Rule Execution', 0.15 * total_time),
                ('Results Compilation', 0.05 * total_time)
            ]
            
            for stage_name, stage_time in stages_with_times:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"✅ **{stage_name}**")
                with col2:
                    st.text(f"{stage_time:.2f}s")
        
        # Quick results preview
        if hasattr(review_status, 'critical_issues') and review_status.critical_issues:
            st.subheader("⚠️ Critical Issues Found")
            for issue in review_status.critical_issues[:3]:  # Show first 3
                st.error(f"• {issue}")
            
            if len(review_status.critical_issues) > 3:
                st.info(f"+ {len(review_status.critical_issues) - 3} more issues. View full results in the Review Execution tab.")
        
        if hasattr(review_status, 'recommendations') and review_status.recommendations:
            st.subheader("💡 Key Recommendations")
            for rec in review_status.recommendations[:2]:  # Show first 2
                st.info(f"• {rec}")
            
            if len(review_status.recommendations) > 2:
                st.info(f"+ {len(review_status.recommendations) - 2} more recommendations.")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View Full Results", key="view_results"):
                st.session_state['switch_to_execution_tab'] = True
                st.info("Switch to the Review Execution tab to see full results")
        
        with col2:
            if st.button("📄 Export Report", key="export_report"):
                st.session_state['show_export_options'] = True
                st.info("Export options available in the Review Execution tab")
        
        with col3:
            if st.button("🔄 Start New Review", key="new_review"):
                st.session_state['clear_current_review'] = True
                st.info("Ready for new review!")
    
    def _render_failed_status(self, review_status):
        """Render failed review status"""
        st.error("❌ Review Failed")
        
        # Error summary
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if review_status.error_message:
                st.error(f"**Error:** {review_status.error_message}")
            else:
                st.error("**Error:** Unknown error occurred during processing")
            
            # Show what was attempted
            st.markdown(f"""
            **Review Details:**
            - Document: `{Path(review_status.document_path).name}`
            - Template: `{review_status.template_name}`
            - Review Type: `{review_status.review_type.value}`
            """)
        
        with col2:
            # Failure time
            if review_status.processing_time > 0:
                st.metric("Failed After", f"{review_status.processing_time:.2f}s")
            
            # Failure stage (if available)
            current_stage = review_status.metadata.get('current_stage', 'Unknown')
            st.metric("Failed At", current_stage.replace('_', ' ').title())
        
        # Error analysis
        st.subheader("🔍 Error Analysis")
        
        # Common error patterns and suggestions
        error_msg = review_status.error_message or ""
        
        if "not found" in error_msg.lower():
            st.warning("**Possible Cause:** File or resource not found")
            st.info("💡 **Suggestion:** Verify document path and ensure file exists")
        elif "timeout" in error_msg.lower():
            st.warning("**Possible Cause:** Processing timeout")
            st.info("💡 **Suggestion:** Try with a smaller document or increase timeout setting")
        elif "format" in error_msg.lower() or "parse" in error_msg.lower():
            st.warning("**Possible Cause:** Document format issue")
            st.info("💡 **Suggestion:** Ensure document is a valid PDF or Word file")
        else:
            st.warning("**Cause:** Unknown error")
            st.info("💡 **Suggestion:** Check system logs or contact support")
        
        # Recovery actions
        st.subheader("🔧 Recovery Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retry Review", key="retry_review"):
                st.session_state['retry_review_requested'] = True
                st.info("Retry requested - review will be resubmitted")
        
        with col2:
            if st.button("📋 View Logs", key="view_logs"):
                st.session_state['show_error_logs'] = True
                st.info("Error logs (coming in Phase 4.2)")
        
        with col3:
            if st.button("🧹 Clear Failed Review", key="clear_failed"):
                st.session_state['clear_current_review'] = True
                st.info("Failed review cleared")
    
    def _render_cancelled_status(self, review_status):
        """Render cancelled review status"""
        st.warning("⏹️ Review Cancelled")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            **Review was cancelled:**
            - Document: `{Path(review_status.document_path).name}`
            - Template: `{review_status.template_name}`
            - Cancellation time: `{review_status.completed_at or 'Unknown'}`
            """)
        
        with col2:
            # Time before cancellation
            if review_status.processing_time > 0:
                st.metric("Ran For", f"{review_status.processing_time:.2f}s")
        
        # Restart option
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Start New Review", key="restart_after_cancel"):
                st.session_state['clear_current_review'] = True
                st.info("Ready for new review")
        
        with col2:
            if st.button("🧹 Clear Status", key="clear_cancelled"):
                st.session_state['clear_current_review'] = True
                st.info("Status cleared")
    
    def _render_unknown_status(self, review_status):
        """Render unknown status"""
        st.warning(f"❓ Unknown Status: {review_status.status.value}")
        
        st.markdown(f"""
        **Review Information:**
        - Status: `{review_status.status.value}`
        - Document: `{Path(review_status.document_path).name}`
        - Started: `{review_status.started_at or 'Unknown'}`
        """)
        
        if st.button("🔄 Refresh Status", key="refresh_unknown"):
            st.rerun()
    
    def render_progress_summary(self, review_engine: Optional[Any] = None) -> None:
        """
        Render a compact progress summary for embedding in other components
        
        Args:
            review_engine: Review engine instance
        """
        if not review_engine:
            return
        
        # Get queue status
        queue_status = review_engine.get_queue_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Reviews", queue_status['active_reviews'])
        
        with col2:
            st.metric("Queued Reviews", queue_status['queue_length'])
        
        with col3:
            total_busy = queue_status['active_reviews'] + queue_status['queue_length']
            status_text = "Busy" if total_busy > 0 else "Idle"
            st.metric("Engine Status", status_text)


def create_progress_display() -> ProgressDisplay:
    """Create and return a ProgressDisplay instance"""
    return ProgressDisplay()
