"""
Document Processing Module

This module handles document processing, validation, and analysis
for the Automated Review Engine.

Components:
- PDFProcessor: PDF document processing and text extraction
- WordProcessor: Word document processing and content analysis
- DocumentValidator: Document validation and compliance checking
- FileManager: File upload and management system
- DocumentAnalyzer: Main analysis engine orchestrating all components
"""

from .pdf_processor import PDFProcessor, PDFProcessingResult
from .word_processor import WordProcessor, WordProcessingResult
from .document_validator import (
    DocumentValidator, 
    ValidationResult, 
    CompletenessResult, 
    ComplianceResult
)
from .file_manager import FileManager, UploadedFile, UploadResult
from .document_analyzer import DocumentAnalyzer, AnalysisConfig, AnalysisResult

__all__ = [
    # Main classes
    'PDFProcessor',
    'WordProcessor', 
    'DocumentValidator',
    'FileManager',
    'DocumentAnalyzer',
    
    # Configuration classes
    'AnalysisConfig',
    
    # Result classes
    'PDFProcessingResult',
    'WordProcessingResult',
    'ValidationResult',
    'CompletenessResult',
    'ComplianceResult',
    'UploadedFile',
    'UploadResult',
    'AnalysisResult'
]
