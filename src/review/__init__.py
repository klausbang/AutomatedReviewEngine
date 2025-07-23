"""
Review Package - Automated Review Engine

Complete document review and validation system for regulatory compliance.
Provides document analysis, template processing, and automated workflows.

Phase 3.2: Review Logic Implementation
"""

# Core review components
try:
    from .document_analyzer import (
        DocumentAnalyzer, 
        AnalysisResult, 
        DocumentElement, 
        DocumentMetadata,
        DocumentType,
        DocumentStructure,
        create_document_analyzer
    )
    DOCUMENT_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Document analyzer not available - {e}")
    DocumentAnalyzer = None
    AnalysisResult = None
    DocumentElement = None
    DocumentMetadata = None
    DocumentType = None
    DocumentStructure = None
    create_document_analyzer = None
    DOCUMENT_ANALYZER_AVAILABLE = False

try:
    from .template_processor import (
        TemplateProcessor,
        ValidationResult,
        ValidationIssue,
        TemplateRequirement,
        ValidationSeverity,
        RequirementStatus,
        EUDocTemplate,
        create_template_processor
    )
    TEMPLATE_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Template processor not available - {e}")
    TemplateProcessor = None
    ValidationResult = None
    ValidationIssue = None
    TemplateRequirement = None
    ValidationSeverity = None
    RequirementStatus = None
    EUDocTemplate = None
    create_template_processor = None
    TEMPLATE_PROCESSOR_AVAILABLE = False

try:
    from .review_engine import (
        ReviewEngine,
        ReviewResult,
        ReviewRequest,
        ReviewStatus,
        ReviewType,
        ReviewPriority,
        create_review_engine,
        create_review_request
    )
    REVIEW_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Review engine not available - {e}")
    ReviewEngine = None
    ReviewResult = None
    ReviewRequest = None
    ReviewStatus = None
    ReviewType = None
    ReviewPriority = None
    create_review_engine = None
    create_review_request = None
    REVIEW_ENGINE_AVAILABLE = False

try:
    from .workflow_manager import (
        WorkflowManager,
        WorkflowDefinition,
        WorkflowExecution,
        WorkflowStep,
        WorkflowStatus,
        StepType,
        ExecutionMode,
        create_workflow_manager
    )
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Workflow manager not available - {e}")
    WorkflowManager = None
    WorkflowDefinition = None
    WorkflowExecution = None
    WorkflowStep = None
    WorkflowStatus = None
    StepType = None
    ExecutionMode = None
    create_workflow_manager = None
    WORKFLOW_MANAGER_AVAILABLE = False

# Package metadata
__version__ = "1.0.0"
__author__ = "Automated Review Engine Team"
__description__ = "Document review and validation system for regulatory compliance"

# Component availability status
COMPONENT_STATUS = {
    'document_analyzer': DOCUMENT_ANALYZER_AVAILABLE,
    'template_processor': TEMPLATE_PROCESSOR_AVAILABLE,
    'review_engine': REVIEW_ENGINE_AVAILABLE,
    'workflow_manager': WORKFLOW_MANAGER_AVAILABLE
}

# Public API
__all__ = [
    # Document Analyzer
    'DocumentAnalyzer',
    'AnalysisResult', 
    'DocumentElement',
    'DocumentMetadata',
    'DocumentType',
    'DocumentStructure',
    'create_document_analyzer',
    
    # Template Processor
    'TemplateProcessor',
    'ValidationResult',
    'ValidationIssue',
    'TemplateRequirement',
    'ValidationSeverity',
    'RequirementStatus',
    'EUDocTemplate',
    'create_template_processor',
    
    # Review Engine
    'ReviewEngine',
    'ReviewResult',
    'ReviewRequest',
    'ReviewStatus',
    'ReviewType',
    'ReviewPriority',
    'create_review_engine',
    'create_review_request',
    
    # Workflow Manager
    'WorkflowManager',
    'WorkflowDefinition',
    'WorkflowExecution',
    'WorkflowStep',
    'WorkflowStatus',
    'StepType',
    'ExecutionMode',
    'create_workflow_manager',
    
    # Utilities
    'COMPONENT_STATUS',
    'get_package_info',
    'create_complete_review_system'
]


def get_package_info():
    """Get information about the review package and component availability"""
    available_components = [name for name, available in COMPONENT_STATUS.items() if available]
    unavailable_components = [name for name, available in COMPONENT_STATUS.items() if not available]
    
    return {
        'version': __version__,
        'description': __description__,
        'total_components': len(COMPONENT_STATUS),
        'available_components': available_components,
        'unavailable_components': unavailable_components,
        'component_status': COMPONENT_STATUS,
        'is_fully_functional': all(COMPONENT_STATUS.values())
    }


def create_complete_review_system(config=None):
    """
    Create a complete review system with all components
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing all available components
    """
    system = {}
    
    # Create document analyzer
    if DOCUMENT_ANALYZER_AVAILABLE and create_document_analyzer:
        analyzer_config = config.get('document_analyzer', {}) if config else {}
        system['document_analyzer'] = create_document_analyzer(analyzer_config)
    
    # Create template processor
    if TEMPLATE_PROCESSOR_AVAILABLE and create_template_processor:
        processor_config = config.get('template_processor', {}) if config else {}
        system['template_processor'] = create_template_processor(processor_config)
    
    # Create review engine
    if REVIEW_ENGINE_AVAILABLE and create_review_engine:
        engine_config = config.get('review_engine', {}) if config else {}
        system['review_engine'] = create_review_engine(engine_config)
    
    # Create workflow manager
    if WORKFLOW_MANAGER_AVAILABLE and create_workflow_manager:
        workflow_config = config.get('workflow_manager', {}) if config else {}
        system['workflow_manager'] = create_workflow_manager(workflow_config)
    
    return system

# Review engine configuration
REVIEW_ENGINE_CONFIG = {
    'supported_formats': ['.pdf', '.docx', '.doc'],
    'max_document_size_mb': 50,
    'template_validation_enabled': True,
    'script_execution_timeout': 300,  # 5 minutes
    'result_retention_days': 30
}
