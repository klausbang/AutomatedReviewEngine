"""
Review Engine Core - Automated Review Engine

Main review processing engine that orchestrates document analysis, 
template validation, and review workflow execution.

Phase 3.2: Review Logic - Core Engine Component
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Core imports
try:
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
    from src.core.config_manager import ConfigManager
except ImportError:
    LoggingManager = None
    ErrorHandler = None
    ConfigManager = None

# Review imports
try:
    from src.review.document_analyzer import DocumentAnalyzer, AnalysisResult, create_document_analyzer
    from src.review.template_processor import TemplateProcessor, ValidationResult, create_template_processor
except ImportError:
    DocumentAnalyzer = None
    AnalysisResult = None
    TemplateProcessor = None
    ValidationResult = None
    create_document_analyzer = None
    create_template_processor = None


class ReviewStatus(Enum):
    """Review process status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewPriority(Enum):
    """Review priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewType(Enum):
    """Types of reviews supported"""
    EU_DOC_VALIDATION = "eu_doc_validation"
    TEMPLATE_COMPLIANCE = "template_compliance"
    CUSTOM_SCRIPT = "custom_script"
    FULL_ANALYSIS = "full_analysis"


@dataclass
class ReviewRequest:
    """Represents a review request"""
    id: str
    document_path: str
    review_type: ReviewType
    template_name: str = 'eu_doc'
    priority: ReviewPriority = ReviewPriority.NORMAL
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: Optional[str] = None
    timeout_seconds: int = 300


@dataclass
class ReviewProgress:
    """Review progress tracking"""
    stage: str
    progress_percentage: float
    current_operation: str
    estimated_remaining_time: Optional[float] = None
    detailed_status: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewResult:
    """Complete review result"""
    request_id: str
    status: ReviewStatus
    review_type: ReviewType
    document_path: str
    template_name: str
    
    # Analysis results
    analysis_result: Optional[Any] = None
    validation_result: Optional[Any] = None
    
    # Execution details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: float = 0.0
    
    # Results and findings
    overall_score: float = 0.0
    compliance_percentage: float = 0.0
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReviewEngine:
    """Main review processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize review engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = None
        self.error_handler = None
        
        # Initialize core components
        self._initialize_core_components()
        
        # Initialize review components
        self.document_analyzer = None
        self.template_processor = None
        self._initialize_review_components()
        
        # Review management
        self.active_reviews: Dict[str, ReviewResult] = {}
        self.review_history: List[ReviewResult] = []
        self.review_queue: List[ReviewRequest] = []
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        
        # Threading for async operations
        self._shutdown_event = threading.Event()
        self._worker_thread = None
        
        # Statistics
        self.engine_stats = {
            'reviews_processed': 0,
            'successful_reviews': 0,
            'failed_reviews': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'engine_start_time': datetime.now()
        }
        
        # Start background worker if enabled
        if self.config.get('enable_background_processing', True):
            self.start_background_worker()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default engine configuration"""
        return {
            'max_concurrent_reviews': 3,
            'default_timeout_seconds': 300,
            'enable_background_processing': True,
            'auto_cleanup_completed': True,
            'cleanup_after_hours': 24,
            'max_history_entries': 1000,
            'progress_update_interval': 5.0,  # seconds
            'enable_detailed_logging': True,
            'result_caching': True,
            'cache_duration_hours': 6,
            'queue_processing_interval': 2.0,  # seconds
            'document_analyzer_config': {},
            'template_processor_config': {}
        }
    
    def _initialize_core_components(self):
        """Initialize core infrastructure components"""
        try:
            if LoggingManager:
                self.logger_manager = LoggingManager({'level': 'INFO'})
                self.logger_manager.initialize()
                self.logger = self.logger_manager.get_logger('review.engine')
            
            if ErrorHandler:
                self.error_handler = ErrorHandler()
            
            if self.logger:
                self.logger.info("Review engine core components initialized")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize core components: {e}")
    
    def _initialize_review_components(self):
        """Initialize review processing components"""
        try:
            # Initialize document analyzer
            if create_document_analyzer:
                analyzer_config = self.config.get('document_analyzer_config', {})
                self.document_analyzer = create_document_analyzer(analyzer_config)
            
            # Initialize template processor
            if create_template_processor:
                processor_config = self.config.get('template_processor_config', {})
                self.template_processor = create_template_processor(processor_config)
            
            if self.logger:
                analyzer_status = "available" if self.document_analyzer else "unavailable"
                processor_status = "available" if self.template_processor else "unavailable"
                self.logger.info(f"Review components initialized - "
                               f"Analyzer: {analyzer_status}, Processor: {processor_status}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize review components: {e}")
    
    def submit_review(self, request: ReviewRequest) -> str:
        """
        Submit a review request for processing
        
        Args:
            request: Review request to process
            
        Returns:
            Request ID for tracking
        """
        try:
            # Validate request
            validation_result = self._validate_review_request(request)
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid review request: {validation_result['errors']}")
            
            # Check if document exists
            if not Path(request.document_path).exists():
                raise FileNotFoundError(f"Document not found: {request.document_path}")
            
            # Create review result entry
            review_result = ReviewResult(
                request_id=request.id,
                status=ReviewStatus.PENDING,
                review_type=request.review_type,
                document_path=request.document_path,
                template_name=request.template_name,
                metadata={
                    'priority': request.priority.value,
                    'requested_by': request.requested_by,
                    'timeout_seconds': request.timeout_seconds,
                    'parameters': request.parameters
                }
            )
            
            # Add to active reviews
            self.active_reviews[request.id] = review_result
            
            # Add to queue for processing
            self.review_queue.append(request)
            
            # Sort queue by priority
            self._sort_review_queue()
            
            if self.logger:
                self.logger.info(f"Review request submitted: {request.id} "
                               f"(type: {request.review_type.value}, priority: {request.priority.value})")
            
            return request.id
            
        except Exception as e:
            if self.error_handler:
                error_context = self.error_handler.handle_error(e)
                error_message = error_context.user_message
            else:
                error_message = str(e)
            
            if self.logger:
                self.logger.error(f"Failed to submit review request: {error_message}")
            
            raise
    
    def get_review_status(self, request_id: str) -> Optional[ReviewResult]:
        """
        Get current status of a review
        
        Args:
            request_id: Review request ID
            
        Returns:
            Current review result or None if not found
        """
        # Check active reviews
        if request_id in self.active_reviews:
            return self.active_reviews[request_id]
        
        # Check history
        for result in self.review_history:
            if result.request_id == request_id:
                return result
        
        return None
    
    def cancel_review(self, request_id: str) -> bool:
        """
        Cancel a pending or in-progress review
        
        Args:
            request_id: Review request ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            # Remove from queue if pending
            self.review_queue = [req for req in self.review_queue if req.id != request_id]
            
            # Update status if active
            if request_id in self.active_reviews:
                review_result = self.active_reviews[request_id]
                if review_result.status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]:
                    review_result.status = ReviewStatus.CANCELLED
                    review_result.completed_at = datetime.now()
                    
                    # Move to history
                    self.review_history.append(review_result)
                    del self.active_reviews[request_id]
                    
                    if self.logger:
                        self.logger.info(f"Review cancelled: {request_id}")
                    
                    return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to cancel review {request_id}: {e}")
            return False
    
    def process_review_sync(self, request: ReviewRequest) -> ReviewResult:
        """
        Process a review request synchronously
        
        Args:
            request: Review request to process
            
        Returns:
            Complete review result
        """
        review_result = ReviewResult(
            request_id=request.id,
            status=ReviewStatus.IN_PROGRESS,
            review_type=request.review_type,
            document_path=request.document_path,
            template_name=request.template_name,
            started_at=datetime.now()
        )
        
        try:
            # Update progress
            self._update_progress(request.id, ReviewProgress(
                stage="initialization",
                progress_percentage=0.0,
                current_operation="Initializing review process"
            ))
            
            # Document Analysis Phase
            self._update_progress(request.id, ReviewProgress(
                stage="document_analysis",
                progress_percentage=20.0,
                current_operation="Analyzing document structure and content"
            ))
            
            if not self.document_analyzer:
                raise RuntimeError("Document analyzer not available")
            
            analysis_result = self.document_analyzer.analyze_document(request.document_path)
            review_result.analysis_result = analysis_result
            
            if not analysis_result.success:
                raise RuntimeError(f"Document analysis failed: {', '.join(analysis_result.extraction_errors)}")
            
            # Template Validation Phase
            self._update_progress(request.id, ReviewProgress(
                stage="template_validation",
                progress_percentage=60.0,
                current_operation=f"Validating against {request.template_name} template"
            ))
            
            if not self.template_processor:
                raise RuntimeError("Template processor not available")
            
            validation_result = self.template_processor.validate_document(
                analysis_result, 
                request.template_name
            )
            review_result.validation_result = validation_result
            
            # Results Compilation Phase
            self._update_progress(request.id, ReviewProgress(
                stage="results_compilation",
                progress_percentage=80.0,
                current_operation="Compiling results and generating recommendations"
            ))
            
            # Compile final results
            review_result.overall_score = validation_result.overall_score
            review_result.compliance_percentage = validation_result.compliance_percentage
            
            # Extract critical issues
            critical_issues = [
                issue.title for issue in validation_result.validation_issues
                if issue.severity.value in ['critical', 'high']
            ]
            review_result.critical_issues = critical_issues
            review_result.recommendations = validation_result.recommendations
            
            # Set success status
            review_result.status = ReviewStatus.COMPLETED if validation_result.success else ReviewStatus.FAILED
            
            # Finalization
            self._update_progress(request.id, ReviewProgress(
                stage="finalization",
                progress_percentage=100.0,
                current_operation="Review completed successfully"
            ))
            
        except Exception as e:
            review_result.status = ReviewStatus.FAILED
            
            if self.error_handler:
                error_context = self.error_handler.handle_error(e)
                review_result.error_message = error_context.user_message
            else:
                review_result.error_message = str(e)
            
            if self.logger:
                self.logger.error(f"Review processing failed for {request.id}: {review_result.error_message}")
        
        # Complete review
        review_result.completed_at = datetime.now()
        if review_result.started_at:
            review_result.processing_time = (review_result.completed_at - review_result.started_at).total_seconds()
        
        # Update statistics
        self._update_statistics(review_result)
        
        return review_result
    
    def start_background_worker(self):
        """Start background worker thread for processing queued reviews"""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._shutdown_event.clear()
            self._worker_thread = threading.Thread(target=self._background_worker, daemon=True)
            self._worker_thread.start()
            
            if self.logger:
                self.logger.info("Background worker started")
    
    def stop_background_worker(self):
        """Stop background worker thread"""
        if self._worker_thread and self._worker_thread.is_alive():
            self._shutdown_event.set()
            self._worker_thread.join(timeout=5.0)
            
            if self.logger:
                self.logger.info("Background worker stopped")
    
    def _background_worker(self):
        """Background worker for processing review queue"""
        while not self._shutdown_event.is_set():
            try:
                # Process queue
                if self.review_queue and len([r for r in self.active_reviews.values() 
                                            if r.status == ReviewStatus.IN_PROGRESS]) < self.config['max_concurrent_reviews']:
                    
                    request = self.review_queue.pop(0)
                    
                    # Process review
                    review_result = self.process_review_sync(request)
                    
                    # Update active reviews
                    self.active_reviews[request.id] = review_result
                    
                    # Move completed reviews to history
                    if review_result.status in [ReviewStatus.COMPLETED, ReviewStatus.FAILED]:
                        self.review_history.append(review_result)
                        if request.id in self.active_reviews:
                            del self.active_reviews[request.id]
                
                # Cleanup old reviews
                if self.config.get('auto_cleanup_completed', True):
                    self._cleanup_old_reviews()
                
                # Wait before next iteration
                time.sleep(self.config.get('queue_processing_interval', 2.0))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in background worker: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _validate_review_request(self, request: ReviewRequest) -> Dict[str, Any]:
        """Validate review request"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate required fields
        if not request.id:
            validation_result['errors'].append("Request ID is required")
        
        if not request.document_path:
            validation_result['errors'].append("Document path is required")
        
        if not isinstance(request.review_type, ReviewType):
            validation_result['errors'].append("Invalid review type")
        
        # Validate file path
        document_path = Path(request.document_path)
        if not document_path.exists():
            validation_result['errors'].append(f"Document not found: {request.document_path}")
        elif document_path.suffix.lower() not in ['.pdf', '.docx', '.doc']:
            validation_result['warnings'].append(f"Unsupported file type: {document_path.suffix}")
        
        # Validate timeout
        if request.timeout_seconds <= 0 or request.timeout_seconds > 3600:
            validation_result['warnings'].append("Unusual timeout value")
        
        validation_result['is_valid'] = len(validation_result['errors']) == 0
        return validation_result
    
    def _sort_review_queue(self):
        """Sort review queue by priority"""
        priority_order = {
            ReviewPriority.URGENT: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.NORMAL: 2,
            ReviewPriority.LOW: 3
        }
        
        self.review_queue.sort(key=lambda req: (
            priority_order.get(req.priority, 99),
            req.created_at
        ))
    
    def _update_progress(self, request_id: str, progress: ReviewProgress):
        """Update review progress and notify callbacks"""
        # Update active review
        if request_id in self.active_reviews:
            self.active_reviews[request_id].metadata['last_progress'] = progress
        
        # Notify callbacks
        if request_id in self.progress_callbacks:
            for callback in self.progress_callbacks[request_id]:
                try:
                    callback(request_id, progress)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Progress callback failed: {e}")
    
    def _update_statistics(self, review_result: ReviewResult):
        """Update engine statistics"""
        self.engine_stats['reviews_processed'] += 1
        self.engine_stats['total_processing_time'] += review_result.processing_time
        
        if review_result.status == ReviewStatus.COMPLETED:
            self.engine_stats['successful_reviews'] += 1
        elif review_result.status == ReviewStatus.FAILED:
            self.engine_stats['failed_reviews'] += 1
        
        # Calculate average
        if self.engine_stats['reviews_processed'] > 0:
            self.engine_stats['average_processing_time'] = (
                self.engine_stats['total_processing_time'] / 
                self.engine_stats['reviews_processed']
            )
    
    def _cleanup_old_reviews(self):
        """Clean up old completed reviews"""
        try:
            cleanup_threshold = datetime.now() - timedelta(hours=self.config.get('cleanup_after_hours', 24))
            
            # Remove old entries from history
            self.review_history = [
                result for result in self.review_history
                if result.completed_at and result.completed_at > cleanup_threshold
            ]
            
            # Limit history size
            max_entries = self.config.get('max_history_entries', 1000)
            if len(self.review_history) > max_entries:
                self.review_history = self.review_history[-max_entries:]
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Cleanup failed: {e}")
    
    def register_progress_callback(self, request_id: str, callback: Callable):
        """Register a progress callback for a specific review"""
        if request_id not in self.progress_callbacks:
            self.progress_callbacks[request_id] = []
        self.progress_callbacks[request_id].append(callback)
    
    def unregister_progress_callback(self, request_id: str, callback: Callable):
        """Unregister a progress callback"""
        if request_id in self.progress_callbacks:
            try:
                self.progress_callbacks[request_id].remove(callback)
                if not self.progress_callbacks[request_id]:
                    del self.progress_callbacks[request_id]
            except ValueError:
                pass
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        stats = self.engine_stats.copy()
        
        # Add current status
        stats.update({
            'active_reviews': len(self.active_reviews),
            'queued_reviews': len(self.review_queue),
            'history_entries': len(self.review_history),
            'uptime_hours': (datetime.now() - stats['engine_start_time']).total_seconds() / 3600,
            'success_rate': (
                stats['successful_reviews'] / max(1, stats['reviews_processed'])
            ) * 100
        })
        
        return stats
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'queue_length': len(self.review_queue),
            'active_reviews': len([r for r in self.active_reviews.values() 
                                 if r.status == ReviewStatus.IN_PROGRESS]),
            'pending_reviews': len([r for r in self.active_reviews.values() 
                                  if r.status == ReviewStatus.PENDING]),
            'queue_by_priority': {
                priority.value: len([req for req in self.review_queue 
                                   if req.priority == priority])
                for priority in ReviewPriority
            }
        }
    
    def export_review_results(
        self, 
        request_id: str, 
        format: str = 'json',
        include_raw_data: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Export review results in specified format
        
        Args:
            request_id: Review request ID
            format: Export format ('json', 'text', 'pdf')
            include_raw_data: Whether to include raw analysis data
            
        Returns:
            Formatted export data
        """
        review_result = self.get_review_status(request_id)
        if not review_result:
            raise ValueError(f"Review not found: {request_id}")
        
        if format == 'json':
            return self._export_json_results(review_result, include_raw_data)
        elif format == 'text':
            return self._export_text_results(review_result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json_results(self, review_result: ReviewResult, include_raw_data: bool) -> Dict[str, Any]:
        """Export results as JSON"""
        export_data = {
            'request_id': review_result.request_id,
            'status': review_result.status.value,
            'review_type': review_result.review_type.value,
            'document_path': review_result.document_path,
            'template_name': review_result.template_name,
            'processing_time': review_result.processing_time,
            'overall_score': review_result.overall_score,
            'compliance_percentage': review_result.compliance_percentage,
            'critical_issues': review_result.critical_issues,
            'recommendations': review_result.recommendations,
            'error_message': review_result.error_message,
            'warnings': review_result.warnings,
            'metadata': review_result.metadata
        }
        
        if include_raw_data:
            if review_result.validation_result and hasattr(review_result.validation_result, 'export_validation_report'):
                export_data['validation_details'] = review_result.validation_result.export_validation_report('json')
        
        return export_data
    
    def _export_text_results(self, review_result: ReviewResult) -> str:
        """Export results as text"""
        lines = [
            f"REVIEW RESULTS",
            f"=============",
            f"Request ID: {review_result.request_id}",
            f"Status: {review_result.status.value.upper()}",
            f"Document: {review_result.document_path}",
            f"Template: {review_result.template_name}",
            f"Processing Time: {review_result.processing_time:.2f}s",
            f"",
            f"SCORES",
            f"------",
            f"Overall Score: {review_result.overall_score:.1f}/100",
            f"Compliance: {review_result.compliance_percentage:.1f}%",
            f""
        ]
        
        if review_result.critical_issues:
            lines.extend([
                f"CRITICAL ISSUES",
                f"--------------"
            ])
            for issue in review_result.critical_issues:
                lines.append(f"• {issue}")
            lines.append("")
        
        if review_result.recommendations:
            lines.extend([
                f"RECOMMENDATIONS",
                f"---------------"
            ])
            for i, rec in enumerate(review_result.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        if review_result.error_message:
            lines.extend([
                f"ERROR",
                f"-----",
                review_result.error_message
            ])
        
        return "\n".join(lines)
    
    def shutdown(self):
        """Gracefully shutdown the review engine"""
        if self.logger:
            self.logger.info("Shutting down review engine...")
        
        # Stop background worker
        self.stop_background_worker()
        
        # Cancel all pending reviews
        for request_id in list(self.active_reviews.keys()):
            review_result = self.active_reviews[request_id]
            if review_result.status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]:
                self.cancel_review(request_id)
        
        if self.logger:
            self.logger.info("Review engine shutdown complete")


def create_review_engine(config: Optional[Dict[str, Any]] = None) -> ReviewEngine:
    """
    Create and return a ReviewEngine instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured ReviewEngine instance
    """
    return ReviewEngine(config=config)


def create_review_request(
    document_path: str,
    review_type: Union[str, ReviewType] = ReviewType.EU_DOC_VALIDATION,
    template_name: str = 'eu_doc',
    priority: Union[str, ReviewPriority] = ReviewPriority.NORMAL,
    **kwargs
) -> ReviewRequest:
    """
    Create a review request with sensible defaults
    
    Args:
        document_path: Path to document to review
        review_type: Type of review to perform
        template_name: Template to validate against
        priority: Review priority
        **kwargs: Additional parameters
        
    Returns:
        Configured ReviewRequest
    """
    import uuid
    
    # Convert string enums to enum instances
    if isinstance(review_type, str):
        review_type = ReviewType(review_type)
    
    if isinstance(priority, str):
        priority = ReviewPriority(priority)
    
    return ReviewRequest(
        id=kwargs.get('id', str(uuid.uuid4())),
        document_path=document_path,
        review_type=review_type,
        template_name=template_name,
        priority=priority,
        parameters=kwargs.get('parameters', {}),
        requested_by=kwargs.get('requested_by'),
        timeout_seconds=kwargs.get('timeout_seconds', 300)
    )
