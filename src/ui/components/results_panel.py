"""
Results Panel Component - Automated Review Engine

Comprehensive results visualization and analysis interface for completed reviews.

Phase 4.1: UI Integration - Results Panel Component
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Review engine imports
try:
    from src.review import ReviewStatus, ValidationSeverity
    REVIEW_ENGINE_AVAILABLE = True
except ImportError:
    REVIEW_ENGINE_AVAILABLE = False
    ReviewStatus = None
    ValidationSeverity = None


class ResultsPanel:
    """Comprehensive results display and analysis component"""
    
    def __init__(self):
        """Initialize results panel"""
        self.severity_colors = {
            'critical': '#ff4444',
            'high': '#ff8800', 
            'medium': '#ffbb00',
            'low': '#88cc00',
            'info': '#4488ff'
        }
        
        self.score_thresholds = {
            'excellent': 90,
            'good': 75,
            'acceptable': 60,
            'poor': 40
        }
    
    def render_results_interface(
        self, 
        review_status: Any,
        show_detailed: bool = True
    ) -> None:
        """
        Render comprehensive results interface
        
        Args:
            review_status: Review status object with results
            show_detailed: Whether to show detailed analysis
        """
        if not review_status:
            self._render_no_results()
            return
        
        if review_status.status.value != 'completed':
            self._render_incomplete_review(review_status)
            return
        
        # Main results header
        self._render_results_header(review_status)
        
        # Results tabs
        if show_detailed:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview",
                "⚠️ Issues & Findings", 
                "💡 Recommendations",
                "📋 Detailed Analysis",
                "📤 Export & Actions"
            ])
            
            with tab1:
                self._render_overview_tab(review_status)
            
            with tab2:
                self._render_issues_tab(review_status)
            
            with tab3:
                self._render_recommendations_tab(review_status)
            
            with tab4:
                self._render_detailed_analysis_tab(review_status)
            
            with tab5:
                self._render_export_tab(review_status)
        else:
            # Compact view
            self._render_compact_results(review_status)
    
    def _render_no_results(self):
        """Render interface when no results are available"""
        st.info("📊 No results to display")
        st.markdown("""
        Complete a document review to see comprehensive results here.
        
        **What you'll see:**
        - 📈 Overall scores and compliance metrics
        - ⚠️ Detailed issue analysis and findings
        - 💡 Actionable recommendations
        - 📋 Template validation results
        - 📊 Visual analytics and charts
        - 📤 Export options for reports
        """)
    
    def _render_incomplete_review(self, review_status):
        """Render interface for incomplete reviews"""
        status_messages = {
            'pending': '⏳ Review is pending - results will appear when complete',
            'in_progress': '🔄 Review in progress - results will appear when complete', 
            'failed': '❌ Review failed - no results available',
            'cancelled': '⏹️ Review was cancelled - no results available'
        }
        
        message = status_messages.get(
            review_status.status.value, 
            f"❓ Review status: {review_status.status.value}"
        )
        
        st.warning(message)
        
        # Show basic info for failed reviews
        if review_status.status.value == 'failed' and review_status.error_message:
            st.error(f"**Error:** {review_status.error_message}")
            
            # Recovery suggestions
            st.subheader("🔧 Suggested Actions")
            st.info("• Try uploading the document again")
            st.info("• Check document format and integrity")
            st.info("• Contact support if the problem persists")
    
    def _render_results_header(self, review_status):
        """Render results header with key metrics"""
        st.header("📊 Review Results")
        
        # Document info banner
        document_name = Path(review_status.document_path).name
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <h4 style="margin: 0;">📄 {document_name}</h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">
                Template: {review_status.template_name} | 
                Processed: {review_status.completed_at or 'Unknown'} | 
                Time: {review_status.processing_time:.2f}s
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = getattr(review_status, 'overall_score', 0)
            score_color = self._get_score_color(score)
            st.metric(
                "Overall Score", 
                f"{score:.1f}/100",
                delta=None,
                help="Combined score based on compliance and validation results"
            )
        
        with col2:
            compliance = getattr(review_status, 'compliance_percentage', 0)
            st.metric(
                "Compliance", 
                f"{compliance:.1f}%",
                delta=None,
                help="Percentage of template requirements satisfied"
            )
        
        with col3:
            critical_count = len(getattr(review_status, 'critical_issues', []))
            delta_color = "normal" if critical_count == 0 else "inverse"
            st.metric(
                "Critical Issues", 
                str(critical_count),
                delta=None,
                help="Number of critical compliance issues found"
            )
        
        with col4:
            recommendations_count = len(getattr(review_status, 'recommendations', []))
            st.metric(
                "Recommendations", 
                str(recommendations_count),
                delta=None,
                help="Number of improvement recommendations generated"
            )
    
    def _render_overview_tab(self, review_status):
        """Render overview tab with summary visualizations"""
        st.subheader("📈 Overview & Summary")
        
        # Score visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_score_gauge(review_status)
        
        with col2:
            self._render_compliance_breakdown(review_status)
        
        # Quick status summary
        st.subheader("🎯 Review Summary")
        
        score = getattr(review_status, 'overall_score', 0)
        compliance = getattr(review_status, 'compliance_percentage', 0)
        critical_issues = len(getattr(review_status, 'critical_issues', []))
        
        # Determine overall assessment
        if score >= 90 and compliance >= 95 and critical_issues == 0:
            assessment = "🟢 **Excellent** - Document meets all requirements"
            st.success(assessment)
        elif score >= 75 and compliance >= 80 and critical_issues <= 1:
            assessment = "🟡 **Good** - Document meets most requirements with minor issues"
            st.info(assessment)
        elif score >= 60 and compliance >= 70:
            assessment = "🟠 **Acceptable** - Document has several issues requiring attention"
            st.warning(assessment)
        else:
            assessment = "🔴 **Poor** - Document has significant compliance issues"
            st.error(assessment)
        
        # Key findings summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Key Findings")
            
            # Most critical issues (top 3)
            critical_issues = getattr(review_status, 'critical_issues', [])
            if critical_issues:
                for i, issue in enumerate(critical_issues[:3], 1):
                    st.error(f"{i}. {issue}")
                
                if len(critical_issues) > 3:
                    st.info(f"+ {len(critical_issues) - 3} more critical issues")
            else:
                st.success("✅ No critical issues found")
        
        with col2:
            st.subheader("💡 Priority Actions")
            
            # Top recommendations
            recommendations = getattr(review_status, 'recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations[:3], 1):
                    st.info(f"{i}. {rec}")
                
                if len(recommendations) > 3:
                    st.caption(f"+ {len(recommendations) - 3} more recommendations in the Recommendations tab")
            else:
                st.info("No specific recommendations at this time")
        
        # Processing statistics
        with st.expander("📊 Processing Statistics", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Processing Time", f"{review_status.processing_time:.2f}s")
                st.metric("Document Type", review_status.review_type.value.replace('_', ' ').title())
            
            with col2:
                # Document size (if available)
                doc_size = review_status.metadata.get('document_size', 'Unknown')
                st.metric("Document Size", doc_size)
                
                # Pages processed (if available)
                pages = review_status.metadata.get('pages_processed', 'Unknown')
                st.metric("Pages Processed", pages)
            
            with col3:
                # Template coverage
                template_coverage = "95%" if compliance > 90 else "Partial"
                st.metric("Template Coverage", template_coverage)
                
                # Validation rules applied
                rules_applied = review_status.metadata.get('validation_rules_applied', 'Standard')
                st.metric("Rules Applied", rules_applied)
    
    def _render_issues_tab(self, review_status):
        """Render issues and findings tab"""
        st.subheader("⚠️ Issues & Findings Analysis")
        
        # Get validation result if available
        validation_result = getattr(review_status, 'validation_result', None)
        
        if not validation_result:
            st.warning("Detailed validation results not available")
            
            # Show critical issues from summary
            critical_issues = getattr(review_status, 'critical_issues', [])
            if critical_issues:
                st.subheader("Critical Issues")
                for issue in critical_issues:
                    st.error(f"• {issue}")
            
            return
        
        # Group issues by severity
        validation_issues = getattr(validation_result, 'validation_issues', [])
        
        if not validation_issues:
            st.success("🎉 No validation issues found!")
            st.balloons()
            return
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in validation_issues:
            severity = issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity)
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        # Issue severity summary
        self._render_issues_summary_chart(issues_by_severity)
        
        # Detailed issues by severity
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        
        for severity in severity_order:
            if severity not in issues_by_severity:
                continue
            
            issues = issues_by_severity[severity]
            severity_icon = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢',
                'info': '🔵'
            }.get(severity, '⚪')
            
            with st.expander(f"{severity_icon} {severity.title()} Issues ({len(issues)})", expanded=(severity in ['critical', 'high'])):
                for i, issue in enumerate(issues, 1):
                    # Issue card
                    st.markdown(f"""
                    <div style="border-left: 4px solid {self.severity_colors.get(severity, '#ccc')}; 
                                padding: 1rem; margin: 0.5rem 0; background-color: #f8f9fa;">
                        <h5 style="margin-top: 0;">{i}. {getattr(issue, 'title', 'Unknown Issue')}</h5>
                        <p><strong>Description:</strong> {getattr(issue, 'description', 'No description available')}</p>
                        {f'<p><strong>Section:</strong> {issue.section}</p>' if getattr(issue, 'section', None) else ''}
                        {f'<p><strong>Suggestion:</strong> {issue.suggestion}</p>' if getattr(issue, 'suggestion', None) else ''}
                        {f'<p><strong>Regulation:</strong> {issue.regulation_reference}</p>' if getattr(issue, 'regulation_reference', None) else ''}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Issue resolution tracking
        st.subheader("🔧 Issue Resolution Guide")
        
        # Prioritized action plan
        critical_and_high = len(issues_by_severity.get('critical', [])) + len(issues_by_severity.get('high', []))
        
        if critical_and_high > 0:
            st.error(f"🚨 **Immediate Action Required:** {critical_and_high} critical/high priority issues must be resolved")
            
            st.markdown("""
            **Resolution Priority:**
            1. 🔴 **Critical Issues** - Must be fixed before approval
            2. 🟠 **High Issues** - Should be fixed for compliance
            3. 🟡 **Medium Issues** - Recommended to fix
            4. 🟢 **Low Issues** - Optional improvements
            """)
        else:
            st.success("✅ No critical or high priority issues requiring immediate attention")
    
    def _render_recommendations_tab(self, review_status):
        """Render recommendations tab"""
        st.subheader("💡 Recommendations & Improvement Suggestions")
        
        recommendations = getattr(review_status, 'recommendations', [])
        
        if not recommendations:
            st.info("No specific recommendations generated for this review.")
            return
        
        # Categorize recommendations
        categories = {
            'immediate': [],
            'important': [],
            'suggested': [],
            'optional': []
        }
        
        # Simple categorization based on keywords
        for rec in recommendations:
            rec_lower = rec.lower()
            if any(word in rec_lower for word in ['must', 'required', 'critical', 'immediate']):
                categories['immediate'].append(rec)
            elif any(word in rec_lower for word in ['should', 'important', 'recommended']):
                categories['important'].append(rec)
            elif any(word in rec_lower for word in ['could', 'consider', 'improve']):
                categories['suggested'].append(rec)
            else:
                categories['optional'].append(rec)
        
        # Render categorized recommendations
        if categories['immediate']:
            st.subheader("🚨 Immediate Actions Required")
            for i, rec in enumerate(categories['immediate'], 1):
                st.error(f"{i}. {rec}")
        
        if categories['important']:
            st.subheader("⚠️ Important Improvements")
            for i, rec in enumerate(categories['important'], 1):
                st.warning(f"{i}. {rec}")
        
        if categories['suggested']:
            st.subheader("💡 Suggested Enhancements")
            for i, rec in enumerate(categories['suggested'], 1):
                st.info(f"{i}. {rec}")
        
        if categories['optional']:
            st.subheader("🔧 Optional Improvements")
            for i, rec in enumerate(categories['optional'], 1):
                st.success(f"{i}. {rec}")
        
        # Implementation checklist
        st.subheader("📋 Implementation Checklist")
        
        st.markdown("""
        Use this checklist to track your progress implementing the recommendations:
        """)
        
        all_recommendations = (categories['immediate'] + categories['important'] + 
                              categories['suggested'] + categories['optional'])
        
        for i, rec in enumerate(all_recommendations, 1):
            # Create checkbox for each recommendation
            checked = st.checkbox(f"{rec}", key=f"rec_checkbox_{i}")
            if checked:
                st.success("✅ Marked as implemented")
        
        # Progress tracking
        total_recs = len(all_recommendations)
        if total_recs > 0:
            # This would need session state tracking in a real implementation
            implemented_count = 0  # Placeholder
            progress = implemented_count / total_recs
            
            st.subheader("📊 Implementation Progress")
            st.progress(progress, f"Progress: {implemented_count}/{total_recs} recommendations implemented")
    
    def _render_detailed_analysis_tab(self, review_status):
        """Render detailed analysis tab"""
        st.subheader("📋 Detailed Analysis & Technical Details")
        
        # Template validation details
        validation_result = getattr(review_status, 'validation_result', None)
        
        if validation_result:
            st.subheader("📄 Template Validation Results")
            
            # Requirements status
            requirements_status = getattr(validation_result, 'requirements_status', {})
            
            if requirements_status:
                # Create status summary table
                status_data = []
                for req_id, status in requirements_status.items():
                    status_value = status.value if hasattr(status, 'value') else str(status)
                    status_icon = {
                        'satisfied': '✅',
                        'partially_satisfied': '🟡',
                        'not_satisfied': '❌',
                        'not_applicable': '⚪'
                    }.get(status_value, '❓')
                    
                    status_data.append({
                        'Requirement': req_id.replace('_', ' ').title(),
                        'Status': f"{status_icon} {status_value.replace('_', ' ').title()}",
                        'ID': req_id
                    })
                
                # Display as table
                import pandas as pd
                df = pd.DataFrame(status_data)
                st.dataframe(df[['Requirement', 'Status']], use_container_width=True)
        
        # Document analysis details
        analysis_result = getattr(review_status, 'analysis_result', None)
        
        if analysis_result:
            st.subheader("📖 Document Analysis Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Document Type:** {getattr(analysis_result, 'document_type', 'Unknown')}")
                st.markdown(f"**Text Extraction:** {'✅ Success' if getattr(analysis_result, 'success', False) else '❌ Failed'}")
                
                # Text statistics
                text_content = getattr(analysis_result, 'text_content', '')
                if text_content:
                    word_count = len(text_content.split())
                    char_count = len(text_content)
                    st.markdown(f"**Word Count:** {word_count:,}")
                    st.markdown(f"**Character Count:** {char_count:,}")
            
            with col2:
                # Metadata
                metadata = getattr(analysis_result, 'metadata', None)
                if metadata:
                    st.markdown("**Document Metadata:**")
                    if hasattr(metadata, 'page_count'):
                        st.markdown(f"• Pages: {metadata.page_count}")
                    if hasattr(metadata, 'author'):
                        st.markdown(f"• Author: {metadata.author or 'Unknown'}")
                    if hasattr(metadata, 'creation_date'):
                        st.markdown(f"• Created: {metadata.creation_date or 'Unknown'}")
            
            # Extraction errors
            extraction_errors = getattr(analysis_result, 'extraction_errors', [])
            if extraction_errors:
                st.subheader("⚠️ Extraction Issues")
                for error in extraction_errors:
                    st.warning(f"• {error}")
        
        # Processing metadata
        st.subheader("🔧 Processing Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Review ID:** `{review_status.request_id}`")
            st.markdown(f"**Template:** {review_status.template_name}")
            st.markdown(f"**Review Type:** {review_status.review_type.value}")
            st.markdown(f"**Processing Time:** {review_status.processing_time:.3f} seconds")
        
        with col2:
            st.markdown(f"**Started:** {review_status.started_at or 'Unknown'}")
            st.markdown(f"**Completed:** {review_status.completed_at or 'Unknown'}")
            st.markdown(f"**Document Path:** `{Path(review_status.document_path).name}`")
        
        # Raw data export for technical users
        with st.expander("🔍 Raw Analysis Data (Technical)", expanded=False):
            st.warning("⚠️ This section contains technical data for debugging purposes")
            
            # Show serializable parts of the results
            raw_data = {
                'request_id': review_status.request_id,
                'status': review_status.status.value,
                'overall_score': getattr(review_status, 'overall_score', None),
                'compliance_percentage': getattr(review_status, 'compliance_percentage', None),
                'processing_time': review_status.processing_time,
                'metadata': review_status.metadata
            }
            
            st.json(raw_data)
    
    def _render_export_tab(self, review_status):
        """Render export and actions tab"""
        st.subheader("📤 Export Results & Actions")
        
        # Export options
        st.subheader("📄 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📄 Text Report**")
            st.markdown("Plain text summary report with findings and recommendations")
            
            if st.button("📄 Generate Text Report", key="export_text"):
                try:
                    # This would use the review engine's export functionality
                    report_content = self._generate_text_report(review_status)
                    
                    st.download_button(
                        "⬇️ Download Text Report",
                        report_content,
                        f"review_report_{review_status.request_id[:8]}.txt",
                        mime="text/plain",
                        key="download_text"
                    )
                except Exception as e:
                    st.error(f"Failed to generate text report: {e}")
        
        with col2:
            st.markdown("**📊 JSON Data**")
            st.markdown("Structured data export for integration with other systems")
            
            if st.button("📊 Generate JSON Export", key="export_json"):
                try:
                    json_data = self._generate_json_export(review_status)
                    
                    st.download_button(
                        "⬇️ Download JSON Data",
                        json.dumps(json_data, indent=2),
                        f"review_data_{review_status.request_id[:8]}.json",
                        mime="application/json",
                        key="download_json"
                    )
                except Exception as e:
                    st.error(f"Failed to generate JSON export: {e}")
        
        with col3:
            st.markdown("**📋 PDF Report**")
            st.markdown("Professional PDF report for documentation and compliance")
            st.info("🚧 PDF export coming in Phase 4.2")
        
        # Action buttons
        st.subheader("🔧 Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Re-run Review", key="rerun_review"):
                st.session_state['rerun_review_requested'] = True
                st.info("Re-run requested - review will be resubmitted with same parameters")
        
        with col2:
            if st.button("📝 Save to History", key="save_history"):
                st.session_state['save_to_history_requested'] = True
                st.success("Results saved to review history")
        
        with col3:
            if st.button("📧 Share Results", key="share_results"):
                st.session_state['share_results_requested'] = True
                st.info("🚧 Sharing functionality coming in Phase 4.3")
        
        # Comparison with previous reviews
        st.subheader("📊 Historical Comparison")
        st.info("🚧 Historical comparison will be available after multiple reviews")
        
        # Integration options
        with st.expander("🔗 Integration Options", expanded=False):
            st.markdown("""
            **Available Integrations:**
            - 📊 Export to Excel/CSV for further analysis
            - 🔗 Webhook notifications (coming in Phase 5)
            - 📧 Email reports (coming in Phase 5)
            - 📋 Integration with PLM systems (coming in Phase 6)
            """)
    
    def _render_compact_results(self, review_status):
        """Render compact results view"""
        st.subheader("📊 Results Summary")
        
        # Key metrics in compact format
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score = getattr(review_status, 'overall_score', 0)
            st.metric("Score", f"{score:.1f}/100")
        
        with col2:
            compliance = getattr(review_status, 'compliance_percentage', 0)
            st.metric("Compliance", f"{compliance:.1f}%")
        
        with col3:
            critical_count = len(getattr(review_status, 'critical_issues', []))
            st.metric("Critical Issues", critical_count)
        
        # Quick summary
        critical_issues = getattr(review_status, 'critical_issues', [])
        if critical_issues:
            st.subheader("⚠️ Critical Issues")
            for issue in critical_issues[:2]:  # Show top 2
                st.error(f"• {issue}")
            
            if len(critical_issues) > 2:
                st.info(f"+ {len(critical_issues) - 2} more issues")
        else:
            st.success("✅ No critical issues found")
    
    def _render_score_gauge(self, review_status):
        """Render score gauge visualization"""
        score = getattr(review_status, 'overall_score', 0)
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self._get_score_color(score)},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 60], 'color': "gray"},
                    {'range': [60, 80], 'color': "lightblue"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_compliance_breakdown(self, review_status):
        """Render compliance breakdown chart"""
        # Get validation result
        validation_result = getattr(review_status, 'validation_result', None)
        
        if not validation_result:
            st.info("Detailed compliance data not available")
            return
        
        # Get requirements status
        requirements_status = getattr(validation_result, 'requirements_status', {})
        
        if not requirements_status:
            st.info("Requirements status not available")
            return
        
        # Count status types
        status_counts = {}
        for status in requirements_status.values():
            status_value = status.value if hasattr(status, 'value') else str(status)
            status_counts[status_value] = status_counts.get(status_value, 0) + 1
        
        # Create pie chart
        labels = list(status_counts.keys())
        values = list(status_counts.values())
        
        colors = {
            'satisfied': '#00cc44',
            'partially_satisfied': '#ffaa00', 
            'not_satisfied': '#ff4444',
            'not_applicable': '#cccccc'
        }
        
        fig = px.pie(
            values=values, 
            names=[label.replace('_', ' ').title() for label in labels],
            title="Requirements Status",
            color_discrete_map={label.replace('_', ' ').title(): colors.get(label, '#666666') for label in labels}
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_issues_summary_chart(self, issues_by_severity):
        """Render issues summary chart"""
        if not issues_by_severity:
            return
        
        # Create bar chart of issues by severity
        severities = list(issues_by_severity.keys())
        counts = [len(issues_by_severity[sev]) for sev in severities]
        colors = [self.severity_colors.get(sev, '#666666') for sev in severities]
        
        fig = go.Figure(data=[
            go.Bar(
                x=severities,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Issues by Severity",
            xaxis_title="Severity Level",
            yaxis_title="Number of Issues",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 90:
            return '#00cc44'  # Green
        elif score >= 75:
            return '#88cc00'  # Light green
        elif score >= 60:
            return '#ffbb00'  # Yellow
        elif score >= 40:
            return '#ff8800'  # Orange
        else:
            return '#ff4444'  # Red
    
    def _generate_text_report(self, review_status):
        """Generate text report content"""
        document_name = Path(review_status.document_path).name
        
        report_lines = [
            "AUTOMATED REVIEW ENGINE - REVIEW REPORT",
            "=" * 50,
            f"Document: {document_name}",
            f"Template: {review_status.template_name}",
            f"Review Date: {review_status.completed_at or 'Unknown'}",
            f"Processing Time: {review_status.processing_time:.2f} seconds",
            "",
            "SUMMARY RESULTS",
            "-" * 20,
            f"Overall Score: {getattr(review_status, 'overall_score', 0):.1f}/100",
            f"Compliance Percentage: {getattr(review_status, 'compliance_percentage', 0):.1f}%",
            f"Critical Issues: {len(getattr(review_status, 'critical_issues', []))}",
            ""
        ]
        
        # Add critical issues
        critical_issues = getattr(review_status, 'critical_issues', [])
        if critical_issues:
            report_lines.extend([
                "CRITICAL ISSUES",
                "-" * 15
            ])
            for i, issue in enumerate(critical_issues, 1):
                report_lines.append(f"{i}. {issue}")
            report_lines.append("")
        
        # Add recommendations
        recommendations = getattr(review_status, 'recommendations', [])
        if recommendations:
            report_lines.extend([
                "RECOMMENDATIONS",
                "-" * 15
            ])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        
        return "\n".join(report_lines)
    
    def _generate_json_export(self, review_status):
        """Generate JSON export data"""
        return {
            'review_id': review_status.request_id,
            'document_name': Path(review_status.document_path).name,
            'template_name': review_status.template_name,
            'review_date': str(review_status.completed_at or 'Unknown'),
            'processing_time': review_status.processing_time,
            'results': {
                'overall_score': getattr(review_status, 'overall_score', 0),
                'compliance_percentage': getattr(review_status, 'compliance_percentage', 0),
                'critical_issues': getattr(review_status, 'critical_issues', []),
                'recommendations': getattr(review_status, 'recommendations', [])
            },
            'status': review_status.status.value,
            'metadata': review_status.metadata
        }


def create_results_panel() -> ResultsPanel:
    """Create and return a ResultsPanel instance"""
    return ResultsPanel()
