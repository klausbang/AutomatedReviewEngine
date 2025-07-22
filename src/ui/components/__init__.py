"""
UI Components Package - Automated Review Engine

This package contains reusable UI components for the Streamlit application.

Phase 3.1: UI Foundation - Component Architecture

Components:
- FileUploader: Advanced file upload with validation
- DocumentViewer: PDF/Word document display
- ReviewPanel: Review workflow interface  
- SettingsPanel: Configuration management
- StatusIndicator: System status displays
- ProgressTracker: Review progress monitoring
"""

# Import components that are available
try:
    from .file_uploader import FileUploader
except ImportError:
    FileUploader = None

try:
    from .document_viewer import DocumentViewer
except ImportError:
    DocumentViewer = None

try:
    from .review_panel import ReviewPanel
except ImportError:
    ReviewPanel = None

try:
    from .settings_panel import SettingsPanel
except ImportError:
    SettingsPanel = None

try:
    from .status_indicator import StatusIndicator
except ImportError:
    StatusIndicator = None

try:
    from .progress_tracker import ProgressTracker
except ImportError:
    ProgressTracker = None

# Only export available components
__all__ = []
if FileUploader:
    __all__.append('FileUploader')
if DocumentViewer:
    __all__.append('DocumentViewer')
if ReviewPanel:
    __all__.append('ReviewPanel')
if SettingsPanel:
    __all__.append('SettingsPanel')
if StatusIndicator:
    __all__.append('StatusIndicator')
if ProgressTracker:
    __all__.append('ProgressTracker')

# Component version
__version__ = "0.3.1"

# Component registry for dynamic loading
COMPONENT_REGISTRY = {}
if FileUploader:
    COMPONENT_REGISTRY['file_uploader'] = FileUploader
if DocumentViewer:
    COMPONENT_REGISTRY['document_viewer'] = DocumentViewer
if ReviewPanel:
    COMPONENT_REGISTRY['review_panel'] = ReviewPanel
if SettingsPanel:
    COMPONENT_REGISTRY['settings_panel'] = SettingsPanel
if StatusIndicator:
    COMPONENT_REGISTRY['status_indicator'] = StatusIndicator
if ProgressTracker:
    COMPONENT_REGISTRY['progress_tracker'] = ProgressTracker
