"""
Document Analyzer

Main analysis engine that orchestrates document processing,
validation, and content analysis for regulatory documents.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from .pdf_processor import PDFProcessor
from .word_processor import WordProcessor
from .document_validator import DocumentValidator
from .file_manager import FileManager, UploadedFile

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration for document analysis"""
    extract_text: bool = True
    extract_metadata: bool = True
    extract_structure: bool = True
    extract_images: bool = False
    validate_document: bool = True
    check_completeness: bool = True
    check_compliance: bool = True
    language_detection: bool = True
    max_file_size_mb: int = 50

@dataclass
class AnalysisResult:
    """Complete analysis result for a document"""
    # Basic information
    document_id: str
    filename: str
    file_type: str
    analysis_timestamp: datetime
    
    # Processing results
    text_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    document_structure: Optional[Dict[str, Any]] = None
    images: Optional[List[Dict[str, Any]]] = None
    
    # Validation results
    validation_result: Optional[Dict[str, Any]] = None
    compliance_check: Optional[Dict[str, Any]] = None
    completeness_check: Optional[Dict[str, Any]] = None
    
    # Analysis metadata
    processing_time_seconds: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class DocumentAnalyzer:
    """
    Main document analysis engine that orchestrates all processing components.
    
    Handles:
    - Document processing (PDF, Word)
    - Content validation
    - Regulatory compliance checking
    - Completeness analysis
    - Result aggregation and reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize document analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize processors
        self.pdf_processor = PDFProcessor(self.config.get('pdf_config', {}))
        self.word_processor = WordProcessor(self.config.get('word_config', {}))
        self.document_validator = DocumentValidator(self.config.get('validation_config', {}))
        
        # Initialize file manager if base directory is provided
        base_directory = self.config.get('base_directory')
        if base_directory:
            self.file_manager = FileManager(Path(base_directory), self.config.get('file_config', {}))
        else:
            self.file_manager = None
        
        # Analysis configuration
        self.default_analysis_config = AnalysisConfig(**self.config.get('analysis_config', {}))
        
        logger.info("Document analyzer initialized")
    
    def analyze_file(self, file_path: Union[str, Path], 
                    analysis_config: Optional[AnalysisConfig] = None) -> AnalysisResult:
        """
        Analyze a document file.
        
        Args:
            file_path: Path to the document file
            analysis_config: Analysis configuration (uses default if not provided)
            
        Returns:
            AnalysisResult with complete analysis results
        """
        start_time = datetime.now()
        file_path = Path(file_path)
        
        # Use default config if not provided
        if analysis_config is None:
            analysis_config = self.default_analysis_config
        
        # Initialize result
        result = AnalysisResult(
            document_id=str(file_path.stem),
            filename=file_path.name,
            file_type=file_path.suffix.lower(),
            analysis_timestamp=start_time
        )
        
        try:
            logger.info(f"Starting analysis of: {file_path}")
            
            # Validate file exists
            if not file_path.exists():
                result.errors.append(f"File not found: {file_path}")
                return result
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > analysis_config.max_file_size_mb:
                result.errors.append(
                    f"File too large: {file_size_mb:.1f}MB exceeds limit of {analysis_config.max_file_size_mb}MB"
                )
                return result
            
            # Process document based on type
            if file_path.suffix.lower() == '.pdf':
                self._process_pdf(file_path, result, analysis_config)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                self._process_word(file_path, result, analysis_config)
            else:
                result.errors.append(f"Unsupported file type: {file_path.suffix}")
                return result
            
            # Validate document if requested
            if analysis_config.validate_document and not result.errors:
                self._validate_document(file_path, result, analysis_config)
            
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Analysis completed in {result.processing_time_seconds:.2f}s")
            
        except Exception as e:
            logger.error(f"Analysis error for {file_path}: {str(e)}")
            result.errors.append(f"Analysis failed: {str(e)}")
        
        return result
    
    def analyze_uploaded_file(self, file_id: str, 
                             analysis_config: Optional[AnalysisConfig] = None) -> AnalysisResult:
        """
        Analyze an uploaded file by ID.
        
        Args:
            file_id: File identifier from file manager
            analysis_config: Analysis configuration
            
        Returns:
            AnalysisResult with complete analysis results
        """
        if not self.file_manager:
            raise ValueError("File manager not initialized")
        
        # Get file information
        file_info = self.file_manager.get_file(file_id)
        if not file_info:
            result = AnalysisResult(
                document_id=file_id,
                filename="unknown",
                file_type="unknown",
                analysis_timestamp=datetime.now()
            )
            result.errors.append(f"File not found: {file_id}")
            return result
        
        # Analyze the file
        return self.analyze_file(file_info.storage_path, analysis_config)
    
    def batch_analyze(self, file_paths: List[Union[str, Path]], 
                     analysis_config: Optional[AnalysisConfig] = None) -> List[AnalysisResult]:
        """
        Analyze multiple files in batch.
        
        Args:
            file_paths: List of file paths
            analysis_config: Analysis configuration
            
        Returns:
            List of AnalysisResult objects
        """
        results = []
        
        logger.info(f"Starting batch analysis of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                logger.info(f"Processing file {i}/{len(file_paths)}: {file_path}")
                result = self.analyze_file(file_path, analysis_config)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch analysis error for {file_path}: {str(e)}")
                error_result = AnalysisResult(
                    document_id=str(Path(file_path).stem),
                    filename=str(Path(file_path).name),
                    file_type=str(Path(file_path).suffix.lower()),
                    analysis_timestamp=datetime.now()
                )
                error_result.errors.append(f"Analysis failed: {str(e)}")
                results.append(error_result)
        
        logger.info(f"Batch analysis completed: {len(results)} results")
        return results
    
    def get_analysis_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Generate summary statistics from analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {"error": "No results provided"}
        
        summary = {
            "total_files": len(results),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "files_with_warnings": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "file_types": {},
            "common_errors": {},
            "validation_summary": {
                "valid_documents": 0,
                "invalid_documents": 0,
                "compliance_passed": 0,
                "compliance_failed": 0
            }
        }
        
        try:
            for result in results:
                # Basic statistics
                if result.errors:
                    summary["failed_analyses"] += 1
                else:
                    summary["successful_analyses"] += 1
                
                if result.warnings:
                    summary["files_with_warnings"] += 1
                
                summary["total_processing_time"] += result.processing_time_seconds
                
                # File type statistics
                file_type = result.file_type
                if file_type not in summary["file_types"]:
                    summary["file_types"][file_type] = 0
                summary["file_types"][file_type] += 1
                
                # Error tracking
                for error in result.errors:
                    if error not in summary["common_errors"]:
                        summary["common_errors"][error] = 0
                    summary["common_errors"][error] += 1
                
                # Validation summary
                if result.validation_result:
                    if result.validation_result.get('is_valid', False):
                        summary["validation_summary"]["valid_documents"] += 1
                    else:
                        summary["validation_summary"]["invalid_documents"] += 1
                
                if result.compliance_check:
                    if result.compliance_check.get('compliant', False):
                        summary["validation_summary"]["compliance_passed"] += 1
                    else:
                        summary["validation_summary"]["compliance_failed"] += 1
            
            # Calculate average processing time
            if summary["total_files"] > 0:
                summary["average_processing_time"] = summary["total_processing_time"] / summary["total_files"]
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {str(e)}")
            summary["summary_error"] = str(e)
        
        return summary
    
    def export_results(self, results: List[AnalysisResult], 
                      output_path: Union[str, Path], 
                      format: str = 'json') -> bool:
        """
        Export analysis results to file.
        
        Args:
            results: List of analysis results
            output_path: Output file path
            format: Export format ('json', 'csv')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            if format.lower() == 'json':
                return self._export_json(results, output_path)
            elif format.lower() == 'csv':
                return self._export_csv(results, output_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return False
    
    def _process_pdf(self, file_path: Path, result: AnalysisResult, config: AnalysisConfig):
        """Process PDF document"""
        try:
            pdf_result = self.pdf_processor.process_pdf(file_path)
            
            if pdf_result.success:
                if config.extract_text:
                    result.text_content = pdf_result.text_content
                
                if config.extract_metadata:
                    result.metadata = pdf_result.metadata
                
                if config.extract_structure:
                    result.document_structure = pdf_result.document_structure
                
                if config.extract_images:
                    result.images = pdf_result.images
                
                # Add any warnings
                result.warnings.extend(pdf_result.warnings or [])
                
            else:
                result.errors.append(f"PDF processing failed: {pdf_result.error_message}")
                
        except Exception as e:
            result.errors.append(f"PDF processing error: {str(e)}")
    
    def _process_word(self, file_path: Path, result: AnalysisResult, config: AnalysisConfig):
        """Process Word document"""
        try:
            word_result = self.word_processor.process_document(file_path)
            
            if word_result.success:
                if config.extract_text:
                    result.text_content = word_result.text_content
                
                if config.extract_metadata:
                    result.metadata = word_result.metadata
                
                if config.extract_structure:
                    result.document_structure = word_result.document_structure
                
                if config.extract_images:
                    result.images = word_result.images
                
                # Add any warnings
                result.warnings.extend(word_result.warnings or [])
                
            else:
                result.errors.append(f"Word processing failed: {word_result.error_message}")
                
        except Exception as e:
            result.errors.append(f"Word processing error: {str(e)}")
    
    def _validate_document(self, file_path: Path, result: AnalysisResult, config: AnalysisConfig):
        """Validate document"""
        try:
            # Basic validation
            validation_result = self.document_validator.validate_document(
                file_path, result.text_content
            )
            result.validation_result = asdict(validation_result)
            
            # Completeness check
            if config.check_completeness:
                completeness_result = self.document_validator.check_completeness(
                    result.text_content or "", result.metadata or {}
                )
                result.completeness_check = asdict(completeness_result)
            
            # Compliance check
            if config.check_compliance:
                compliance_result = self.document_validator.check_compliance(
                    result.text_content or "", result.metadata or {}
                )
                result.compliance_check = asdict(compliance_result)
                
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
    
    def _export_json(self, results: List[AnalysisResult], output_path: Path) -> bool:
        """Export results to JSON"""
        try:
            # Convert results to dictionaries
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_results": len(results),
                "results": [asdict(result) for result in results],
                "summary": self.get_analysis_summary(results)
            }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Results exported to JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"JSON export error: {str(e)}")
            return False
    
    def _export_csv(self, results: List[AnalysisResult], output_path: Path) -> bool:
        """Export results to CSV"""
        try:
            import csv
            
            # Define CSV columns
            columns = [
                'document_id', 'filename', 'file_type', 'analysis_timestamp',
                'processing_time_seconds', 'has_errors', 'has_warnings',
                'text_length', 'is_valid', 'is_compliant', 'is_complete'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                
                for result in results:
                    row = [
                        result.document_id,
                        result.filename,
                        result.file_type,
                        result.analysis_timestamp.isoformat(),
                        result.processing_time_seconds,
                        len(result.errors) > 0,
                        len(result.warnings) > 0,
                        len(result.text_content) if result.text_content else 0,
                        result.validation_result.get('is_valid', False) if result.validation_result else False,
                        result.compliance_check.get('compliant', False) if result.compliance_check else False,
                        result.completeness_check.get('complete', False) if result.completeness_check else False
                    ]
                    writer.writerow(row)
            
            logger.info(f"Results exported to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"CSV export error: {str(e)}")
            return False
