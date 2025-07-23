"""
Configuration Panel Component - Automated Review Engine

Advanced configuration interface for review parameters, template selection,
and analysis settings integration with Phase 3.2 components.

Phase 4.1: UI Integration - Configuration Panel Component
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
import json
from datetime import datetime

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Phase 3.2 imports
try:
    from src.review import ReviewType
    from src.review.template_processor import TemplateProcessor
    from src.review.workflow_manager import WorkflowManager
    REVIEW_ENGINE_AVAILABLE = True
except ImportError:
    ReviewType = None
    TemplateProcessor = None
    WorkflowManager = None
    REVIEW_ENGINE_AVAILABLE = False


class ConfigPanel:
    """Advanced configuration panel for review settings"""
    
    def __init__(self):
        """Initialize configuration panel"""
        self.default_config = self._get_default_configuration()
        
        # Initialize session state for configuration
        if 'review_config' not in st.session_state:
            st.session_state.review_config = self.default_config.copy()
        
        if 'saved_configurations' not in st.session_state:
            st.session_state.saved_configurations = {}
    
    def render_configuration_interface(self, show_advanced: bool = True) -> Dict[str, Any]:
        """
        Render comprehensive configuration interface
        
        Args:
            show_advanced: Whether to show advanced configuration options
            
        Returns:
            Current configuration settings
        """
        st.header("⚙️ Review Configuration")
        
        # Configuration tabs
        if show_advanced:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Basic Settings",
                "📄 Template Selection",
                "🔧 Analysis Parameters", 
                "🎯 Validation Rules",
                "💾 Saved Configurations"
            ])
            
            with tab1:
                self._render_basic_settings_tab()
            
            with tab2:
                self._render_template_selection_tab()
            
            with tab3:
                self._render_analysis_parameters_tab()
            
            with tab4:
                self._render_validation_rules_tab()
            
            with tab5:
                self._render_saved_configurations_tab()
        else:
            # Compact configuration
            self._render_compact_configuration()
        
        return st.session_state.review_config
    
    def _render_basic_settings_tab(self):
        """Render basic settings configuration"""
        st.subheader("🎯 Basic Review Settings")
        
        # Review type selection
        if REVIEW_ENGINE_AVAILABLE and ReviewType:
            review_types = [rt.value for rt in ReviewType]
            current_type = st.session_state.review_config.get('review_type', review_types[0])
            
            selected_type = st.selectbox(
                "Review Type",
                options=review_types,
                index=review_types.index(current_type) if current_type in review_types else 0,
                help="Select the type of regulatory review to perform",
                key="config_review_type"
            )
            
            st.session_state.review_config['review_type'] = selected_type
        else:
            st.warning("⚠️ Review engine not available - using default settings")
            st.session_state.review_config['review_type'] = 'compliance_review'
        
        # Processing options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Processing Options")
            
            # Processing mode
            processing_mode = st.selectbox(
                "Processing Mode",
                options=['standard', 'thorough', 'quick'],
                index=['standard', 'thorough', 'quick'].index(
                    st.session_state.review_config.get('processing_mode', 'standard')
                ),
                help="Standard: balanced speed/accuracy, Thorough: maximum accuracy, Quick: fastest processing",
                key="config_processing_mode"
            )
            st.session_state.review_config['processing_mode'] = processing_mode
            
            # Parallel processing
            enable_parallel = st.checkbox(
                "Enable Parallel Processing",
                value=st.session_state.review_config.get('enable_parallel_processing', True),
                help="Process multiple sections simultaneously for faster results",
                key="config_parallel"
            )
            st.session_state.review_config['enable_parallel_processing'] = enable_parallel
            
            # Auto-save results
            auto_save = st.checkbox(
                "Auto-save Results",
                value=st.session_state.review_config.get('auto_save_results', True),
                help="Automatically save review results to history",
                key="config_auto_save"
            )
            st.session_state.review_config['auto_save_results'] = auto_save
        
        with col2:
            st.subheader("📊 Output Settings")
            
            # Output format
            output_formats = ['detailed', 'summary', 'minimal']
            current_format = st.session_state.review_config.get('output_format', 'detailed')
            
            output_format = st.selectbox(
                "Output Detail Level",
                options=output_formats,
                index=output_formats.index(current_format) if current_format in output_formats else 0,
                help="Detailed: full analysis, Summary: key findings, Minimal: scores only",
                key="config_output_format"
            )
            st.session_state.review_config['output_format'] = output_format
            
            # Include recommendations
            include_recs = st.checkbox(
                "Include Recommendations",
                value=st.session_state.review_config.get('include_recommendations', True),
                help="Generate improvement recommendations",
                key="config_recommendations"
            )
            st.session_state.review_config['include_recommendations'] = include_recs
            
            # Include technical details
            include_tech = st.checkbox(
                "Include Technical Details",
                value=st.session_state.review_config.get('include_technical_details', False),
                help="Include detailed technical analysis information",
                key="config_technical"
            )
            st.session_state.review_config['include_technical_details'] = include_tech
        
        # Timeout settings
        st.subheader("⏱️ Timeout Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            analysis_timeout = st.number_input(
                "Analysis Timeout (minutes)",
                min_value=1,
                max_value=60,
                value=st.session_state.review_config.get('analysis_timeout_minutes', 10),
                help="Maximum time to spend on document analysis",
                key="config_analysis_timeout"
            )
            st.session_state.review_config['analysis_timeout_minutes'] = analysis_timeout
        
        with col2:
            validation_timeout = st.number_input(
                "Validation Timeout (minutes)",
                min_value=1,
                max_value=30,
                value=st.session_state.review_config.get('validation_timeout_minutes', 5),
                help="Maximum time to spend on template validation",
                key="config_validation_timeout"
            )
            st.session_state.review_config['validation_timeout_minutes'] = validation_timeout
        
        with col3:
            total_timeout = st.number_input(
                "Total Timeout (minutes)",
                min_value=2,
                max_value=120,
                value=st.session_state.review_config.get('total_timeout_minutes', 20),
                help="Maximum total processing time",
                key="config_total_timeout"
            )
            st.session_state.review_config['total_timeout_minutes'] = total_timeout
    
    def _render_template_selection_tab(self):
        """Render template selection and configuration"""
        st.subheader("📄 Template Selection & Configuration")
        
        # Get available templates
        if REVIEW_ENGINE_AVAILABLE and TemplateProcessor:
            try:
                processor = TemplateProcessor()
                available_templates = processor.get_available_templates()
                
                if available_templates:
                    # Template selection
                    template_names = list(available_templates.keys())
                    current_template = st.session_state.review_config.get('template_name', template_names[0])
                    
                    selected_template = st.selectbox(
                        "Select Review Template",
                        options=template_names,
                        index=template_names.index(current_template) if current_template in template_names else 0,
                        help="Choose the regulatory template for validation",
                        key="config_template_selection"
                    )
                    
                    st.session_state.review_config['template_name'] = selected_template
                    
                    # Template information
                    template_info = available_templates[selected_template]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Template Information:**")
                        st.info(f"**Type:** {template_info.get('type', 'Unknown')}")
                        st.info(f"**Version:** {template_info.get('version', 'Unknown')}")
                        st.info(f"**Requirements:** {len(template_info.get('requirements', []))}")
                        st.info(f"**Last Updated:** {template_info.get('last_updated', 'Unknown')}")
                    
                    with col2:
                        st.markdown("**Template Description:**")
                        description = template_info.get('description', 'No description available')
                        st.write(description)
                        
                        # Template validation rules
                        requirements = template_info.get('requirements', [])
                        if requirements:
                            with st.expander("📋 Template Requirements", expanded=False):
                                for i, req in enumerate(requirements[:10], 1):
                                    req_id = req.get('id', f'req_{i}')
                                    req_title = req.get('title', req_id)
                                    req_mandatory = req.get('mandatory', True)
                                    
                                    mandatory_icon = "🔴" if req_mandatory else "🟡"
                                    st.write(f"{mandatory_icon} **{req_title}**")
                                
                                if len(requirements) > 10:
                                    st.info(f"+ {len(requirements) - 10} more requirements")
                    
                    # Template-specific settings
                    st.subheader("🎛️ Template-Specific Settings")
                    
                    # Requirement strictness
                    strictness_levels = ['lenient', 'standard', 'strict']
                    current_strictness = st.session_state.review_config.get('requirement_strictness', 'standard')
                    
                    strictness = st.selectbox(
                        "Requirement Strictness",
                        options=strictness_levels,
                        index=strictness_levels.index(current_strictness) if current_strictness in strictness_levels else 1,
                        help="Lenient: flexible interpretation, Standard: balanced, Strict: exact compliance required",
                        key="config_strictness"
                    )
                    st.session_state.review_config['requirement_strictness'] = strictness
                    
                    # Custom requirement weights
                    if st.checkbox("Customize Requirement Weights", key="config_custom_weights"):
                        st.info("🚧 Custom requirement weighting will be available in Phase 4.2")
                
                else:
                    st.warning("No templates available")
                    st.session_state.review_config['template_name'] = 'default_template'
            
            except Exception as e:
                st.error(f"Failed to load templates: {e}")
                st.session_state.review_config['template_name'] = 'default_template'
        else:
            st.warning("⚠️ Template processor not available - using default template")
            st.session_state.review_config['template_name'] = 'default_template'
        
        # Template upload option (future feature)
        st.subheader("📤 Custom Template Upload")
        st.info("🚧 Custom template upload functionality coming in Phase 5")
        
        uploaded_template = st.file_uploader(
            "Upload Custom Template (JSON)",
            type=['json'],
            help="Upload a custom validation template",
            key="config_custom_template_upload",
            disabled=True
        )
    
    def _render_analysis_parameters_tab(self):
        """Render analysis parameters configuration"""
        st.subheader("🔧 Analysis Parameters")
        
        # Text analysis settings
        st.subheader("📝 Text Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Language detection
            enable_lang_detection = st.checkbox(
                "Enable Language Detection",
                value=st.session_state.review_config.get('enable_language_detection', True),
                help="Automatically detect document language",
                key="config_lang_detection"
            )
            st.session_state.review_config['enable_language_detection'] = enable_lang_detection
            
            # OCR settings
            enable_ocr = st.checkbox(
                "Enable OCR for Scanned Documents",
                value=st.session_state.review_config.get('enable_ocr', True),
                help="Use OCR to extract text from scanned documents",
                key="config_ocr"
            )
            st.session_state.review_config['enable_ocr'] = enable_ocr
            
            # Text cleaning
            enable_text_cleaning = st.checkbox(
                "Enable Text Cleaning",
                value=st.session_state.review_config.get('enable_text_cleaning', True),
                help="Clean and normalize extracted text",
                key="config_text_cleaning"
            )
            st.session_state.review_config['enable_text_cleaning'] = enable_text_cleaning
        
        with col2:
            # Confidence thresholds
            text_confidence = st.slider(
                "Text Extraction Confidence Threshold",
                min_value=0.5,
                max_value=1.0,
                value=st.session_state.review_config.get('text_confidence_threshold', 0.8),
                step=0.05,
                help="Minimum confidence level for text extraction",
                key="config_text_confidence"
            )
            st.session_state.review_config['text_confidence_threshold'] = text_confidence
            
            # OCR confidence
            ocr_confidence = st.slider(
                "OCR Confidence Threshold",
                min_value=0.5,
                max_value=1.0,
                value=st.session_state.review_config.get('ocr_confidence_threshold', 0.7),
                step=0.05,
                help="Minimum confidence level for OCR text",
                key="config_ocr_confidence"
            )
            st.session_state.review_config['ocr_confidence_threshold'] = ocr_confidence
        
        # Semantic analysis settings
        st.subheader("🧠 Semantic Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enable semantic analysis
            enable_semantic = st.checkbox(
                "Enable Semantic Analysis",
                value=st.session_state.review_config.get('enable_semantic_analysis', True),
                help="Use AI for semantic understanding of content",
                key="config_semantic"
            )
            st.session_state.review_config['enable_semantic_analysis'] = enable_semantic
            
            # Context window size
            context_window = st.number_input(
                "Context Window Size (tokens)",
                min_value=512,
                max_value=4096,
                value=st.session_state.review_config.get('context_window_size', 2048),
                step=256,
                help="Size of context window for semantic analysis",
                key="config_context_window"
            )
            st.session_state.review_config['context_window_size'] = context_window
        
        with col2:
            # Similarity threshold
            similarity_threshold = st.slider(
                "Semantic Similarity Threshold",
                min_value=0.5,
                max_value=1.0,
                value=st.session_state.review_config.get('semantic_similarity_threshold', 0.75),
                step=0.05,
                help="Threshold for semantic similarity matching",
                key="config_similarity"
            )
            st.session_state.review_config['semantic_similarity_threshold'] = similarity_threshold
        
        # Performance settings
        st.subheader("⚡ Performance Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_workers = st.number_input(
                "Max Worker Threads",
                min_value=1,
                max_value=8,
                value=st.session_state.review_config.get('max_worker_threads', 4),
                help="Maximum number of parallel processing threads",
                key="config_max_workers"
            )
            st.session_state.review_config['max_worker_threads'] = max_workers
        
        with col2:
            chunk_size = st.number_input(
                "Processing Chunk Size",
                min_value=1000,
                max_value=10000,
                value=st.session_state.review_config.get('processing_chunk_size', 5000),
                step=500,
                help="Size of text chunks for processing",
                key="config_chunk_size"
            )
            st.session_state.review_config['processing_chunk_size'] = chunk_size
        
        with col3:
            memory_limit = st.number_input(
                "Memory Limit (MB)",
                min_value=512,
                max_value=4096,
                value=st.session_state.review_config.get('memory_limit_mb', 1024),
                step=256,
                help="Maximum memory usage per review",
                key="config_memory_limit"
            )
            st.session_state.review_config['memory_limit_mb'] = memory_limit
    
    def _render_validation_rules_tab(self):
        """Render validation rules configuration"""
        st.subheader("🎯 Validation Rules Configuration")
        
        # Severity settings
        st.subheader("⚠️ Issue Severity Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Critical Issue Threshold**")
            critical_threshold = st.slider(
                "Critical Issue Score Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.review_config.get('critical_issue_threshold', 0.9),
                step=0.05,
                help="Score threshold for marking issues as critical",
                key="config_critical_threshold"
            )
            st.session_state.review_config['critical_issue_threshold'] = critical_threshold
            
            st.markdown("**High Priority Threshold**")
            high_threshold = st.slider(
                "High Priority Score Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.review_config.get('high_priority_threshold', 0.7),
                step=0.05,
                help="Score threshold for high priority issues",
                key="config_high_threshold"
            )
            st.session_state.review_config['high_priority_threshold'] = high_threshold
        
        with col2:
            st.markdown("**Compliance Thresholds**")
            
            min_compliance = st.slider(
                "Minimum Compliance Score",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.review_config.get('minimum_compliance_score', 0.8),
                step=0.05,
                help="Minimum overall compliance score for approval",
                key="config_min_compliance"
            )
            st.session_state.review_config['minimum_compliance_score'] = min_compliance
            
            target_compliance = st.slider(
                "Target Compliance Score",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.review_config.get('target_compliance_score', 0.95),
                step=0.05,
                help="Target compliance score for optimal results",
                key="config_target_compliance"
            )
            st.session_state.review_config['target_compliance_score'] = target_compliance
        
        # Rule categories
        st.subheader("📋 Validation Rule Categories")
        
        rule_categories = {
            'structural_validation': {
                'name': 'Structural Validation',
                'description': 'Validate document structure and format',
                'default': True
            },
            'content_validation': {
                'name': 'Content Validation', 
                'description': 'Validate required content and information',
                'default': True
            },
            'compliance_validation': {
                'name': 'Compliance Validation',
                'description': 'Check regulatory compliance requirements',
                'default': True
            },
            'quality_validation': {
                'name': 'Quality Validation',
                'description': 'Assess document quality and completeness',
                'default': True
            },
            'security_validation': {
                'name': 'Security Validation',
                'description': 'Check for security and confidentiality requirements',
                'default': False
            }
        }
        
        for rule_id, rule_info in rule_categories.items():
            enabled = st.checkbox(
                f"{rule_info['name']}",
                value=st.session_state.review_config.get(f'enable_{rule_id}', rule_info['default']),
                help=rule_info['description'],
                key=f"config_rule_{rule_id}"
            )
            st.session_state.review_config[f'enable_{rule_id}'] = enabled
        
        # Custom validation rules
        st.subheader("🔧 Custom Validation Rules")
        st.info("🚧 Custom validation rule editor coming in Phase 4.3")
        
        # Show current active rules summary
        with st.expander("📊 Active Rules Summary", expanded=False):
            active_rules = [
                rule_info['name'] for rule_id, rule_info in rule_categories.items()
                if st.session_state.review_config.get(f'enable_{rule_id}', rule_info['default'])
            ]
            
            if active_rules:
                st.success(f"**Active Rule Categories:** {', '.join(active_rules)}")
            else:
                st.warning("No validation rules are currently active")
    
    def _render_saved_configurations_tab(self):
        """Render saved configurations management"""
        st.subheader("💾 Saved Configurations")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Save current configuration
            config_name = st.text_input(
                "Configuration Name",
                placeholder="Enter a name for this configuration",
                key="config_save_name"
            )
        
        with col2:
            if st.button("💾 Save Configuration", key="config_save_button"):
                if config_name:
                    # Save configuration with timestamp
                    saved_config = st.session_state.review_config.copy()
                    saved_config['saved_at'] = datetime.now().isoformat()
                    saved_config['saved_name'] = config_name
                    
                    st.session_state.saved_configurations[config_name] = saved_config
                    st.success(f"Configuration '{config_name}' saved successfully!")
                else:
                    st.error("Please enter a configuration name")
        
        # Load saved configurations
        if st.session_state.saved_configurations:
            st.subheader("📂 Saved Configurations")
            
            config_names = list(st.session_state.saved_configurations.keys())
            selected_config = st.selectbox(
                "Select Configuration to Load",
                options=config_names,
                key="config_load_selection"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Load Configuration", key="config_load_button"):
                    if selected_config:
                        loaded_config = st.session_state.saved_configurations[selected_config].copy()
                        # Remove metadata
                        loaded_config.pop('saved_at', None)
                        loaded_config.pop('saved_name', None)
                        
                        st.session_state.review_config = loaded_config
                        st.success(f"Configuration '{selected_config}' loaded successfully!")
                        st.experimental_rerun()
            
            with col2:
                if st.button("🔄 Duplicate Configuration", key="config_duplicate_button"):
                    if selected_config:
                        duplicate_name = f"{selected_config}_copy"
                        duplicate_config = st.session_state.saved_configurations[selected_config].copy()
                        duplicate_config['saved_at'] = datetime.now().isoformat()
                        duplicate_config['saved_name'] = duplicate_name
                        
                        st.session_state.saved_configurations[duplicate_name] = duplicate_config
                        st.success(f"Configuration duplicated as '{duplicate_name}'")
            
            with col3:
                if st.button("🗑️ Delete Configuration", key="config_delete_button"):
                    if selected_config:
                        del st.session_state.saved_configurations[selected_config]
                        st.success(f"Configuration '{selected_config}' deleted")
                        st.experimental_rerun()
            
            # Configuration details
            if selected_config:
                with st.expander(f"📋 Details: {selected_config}", expanded=False):
                    config_details = st.session_state.saved_configurations[selected_config]
                    
                    st.write(f"**Saved:** {config_details.get('saved_at', 'Unknown')}")
                    st.write(f"**Review Type:** {config_details.get('review_type', 'Unknown')}")
                    st.write(f"**Template:** {config_details.get('template_name', 'Unknown')}")
                    st.write(f"**Processing Mode:** {config_details.get('processing_mode', 'Unknown')}")
        else:
            st.info("No saved configurations yet. Configure your settings and save them for future use.")
        
        # Export/Import configurations
        st.subheader("📤 Export/Import Configurations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export All Configurations", key="config_export_all"):
                export_data = {
                    'saved_configurations': st.session_state.saved_configurations,
                    'export_timestamp': datetime.now().isoformat(),
                    'export_version': '4.1'
                }
                
                st.download_button(
                    "⬇️ Download Configuration Export",
                    json.dumps(export_data, indent=2),
                    f"review_configurations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="config_download_export"
                )
        
        with col2:
            uploaded_config = st.file_uploader(
                "📤 Import Configurations",
                type=['json'],
                help="Upload a previously exported configuration file",
                key="config_import_upload"
            )
            
            if uploaded_config:
                try:
                    import_data = json.loads(uploaded_config.read().decode())
                    
                    if 'saved_configurations' in import_data:
                        # Merge imported configurations
                        for name, config in import_data['saved_configurations'].items():
                            st.session_state.saved_configurations[name] = config
                        
                        st.success(f"Imported {len(import_data['saved_configurations'])} configurations")
                    else:
                        st.error("Invalid configuration file format")
                
                except Exception as e:
                    st.error(f"Failed to import configurations: {e}")
    
    def _render_compact_configuration(self):
        """Render compact configuration interface"""
        st.subheader("⚙️ Quick Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Review type
            if REVIEW_ENGINE_AVAILABLE and ReviewType:
                review_types = [rt.value for rt in ReviewType]
                current_type = st.session_state.review_config.get('review_type', review_types[0])
                
                selected_type = st.selectbox(
                    "Review Type",
                    options=review_types,
                    index=review_types.index(current_type) if current_type in review_types else 0,
                    key="compact_config_review_type"
                )
                st.session_state.review_config['review_type'] = selected_type
            
            # Processing mode
            processing_mode = st.selectbox(
                "Processing Mode",
                options=['quick', 'standard', 'thorough'],
                index=['quick', 'standard', 'thorough'].index(
                    st.session_state.review_config.get('processing_mode', 'standard')
                ),
                key="compact_config_processing_mode"
            )
            st.session_state.review_config['processing_mode'] = processing_mode
        
        with col2:
            # Template selection (simplified)
            template_name = st.text_input(
                "Template Name",
                value=st.session_state.review_config.get('template_name', 'default_template'),
                key="compact_config_template"
            )
            st.session_state.review_config['template_name'] = template_name
            
            # Output format
            output_format = st.selectbox(
                "Output Format",
                options=['summary', 'detailed', 'minimal'],
                index=['summary', 'detailed', 'minimal'].index(
                    st.session_state.review_config.get('output_format', 'detailed')
                ),
                key="compact_config_output"
            )
            st.session_state.review_config['output_format'] = output_format
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration settings"""
        return {
            # Basic settings
            'review_type': 'compliance_review',
            'processing_mode': 'standard',
            'enable_parallel_processing': True,
            'auto_save_results': True,
            'output_format': 'detailed',
            'include_recommendations': True,
            'include_technical_details': False,
            
            # Template settings
            'template_name': 'default_template',
            'requirement_strictness': 'standard',
            
            # Analysis parameters
            'enable_language_detection': True,
            'enable_ocr': True,
            'enable_text_cleaning': True,
            'text_confidence_threshold': 0.8,
            'ocr_confidence_threshold': 0.7,
            'enable_semantic_analysis': True,
            'context_window_size': 2048,
            'semantic_similarity_threshold': 0.75,
            
            # Performance settings
            'max_worker_threads': 4,
            'processing_chunk_size': 5000,
            'memory_limit_mb': 1024,
            'analysis_timeout_minutes': 10,
            'validation_timeout_minutes': 5,
            'total_timeout_minutes': 20,
            
            # Validation rules
            'critical_issue_threshold': 0.9,
            'high_priority_threshold': 0.7,
            'minimum_compliance_score': 0.8,
            'target_compliance_score': 0.95,
            'enable_structural_validation': True,
            'enable_content_validation': True,
            'enable_compliance_validation': True,
            'enable_quality_validation': True,
            'enable_security_validation': False
        }
    
    def get_current_configuration(self) -> Dict[str, Any]:
        """Get current configuration settings"""
        return st.session_state.review_config.copy()
    
    def set_configuration(self, config: Dict[str, Any]):
        """Set configuration settings"""
        st.session_state.review_config = config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        st.session_state.review_config = self.default_config.copy()
        st.success("Configuration reset to defaults")


def create_config_panel() -> ConfigPanel:
    """Create and return a ConfigPanel instance"""
    return ConfigPanel()
