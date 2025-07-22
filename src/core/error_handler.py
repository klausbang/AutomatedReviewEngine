"""
Error Handling Framework

Comprehensive error handling and exception management for the
Automated Review Engine.
"""

import traceback
import sys
from typing import Dict, Any, Optional, Type, Callable, List, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import functools

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    PROCESSING = "processing"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    SECURITY = "security"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    BUSINESS_LOGIC = "business_logic"

@dataclass
class ErrorContext:
    """Context information for errors"""
    timestamp: datetime
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Dict[str, Any]
    stack_trace: Optional[str] = None
    user_message: Optional[str] = None
    recovery_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []

class AutomatedReviewEngineError(Exception):
    """Base exception for Automated Review Engine"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM, details: Dict[str, Any] = None,
                 user_message: str = None, recovery_suggestions: List[str] = None):
        super().__init__(message)
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.user_message = user_message
        self.recovery_suggestions = recovery_suggestions or []
        self.error_id = self._generate_error_id()
        self.timestamp = datetime.now()
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ARE_{self.category.value.upper()}_{int(datetime.now().timestamp())}"
    
    def to_context(self) -> ErrorContext:
        """Convert to ErrorContext"""
        return ErrorContext(
            timestamp=self.timestamp,
            error_id=self.error_id,
            severity=self.severity,
            category=self.category,
            message=str(self),
            details=self.details,
            stack_trace=traceback.format_exc(),
            user_message=self.user_message,
            recovery_suggestions=self.recovery_suggestions
        )

class ValidationError(AutomatedReviewEngineError):
    """Error in data validation"""
    
    def __init__(self, message: str, field_name: str = None, field_value: Any = None, **kwargs):
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if field_value is not None:
            details['field_value'] = str(field_value)
        
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            details=details,
            user_message=kwargs.get('user_message', "Please check your input and try again."),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'user_message']}
        )

class ProcessingError(AutomatedReviewEngineError):
    """Error in document processing"""
    
    def __init__(self, message: str, file_path: str = None, processing_stage: str = None, **kwargs):
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if processing_stage:
            details['processing_stage'] = processing_stage
        
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PROCESSING,
            details=details,
            user_message=kwargs.get('user_message', "Document processing failed. Please try again or contact support."),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'user_message']}
        )

class ConfigurationError(AutomatedReviewEngineError):
    """Error in configuration"""
    
    def __init__(self, message: str, config_key: str = None, config_value: Any = None, **kwargs):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = str(config_value)
        
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            details=details,
            user_message=kwargs.get('user_message', "Configuration error. Please check your settings."),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'user_message']}
        )

class SecurityError(AutomatedReviewEngineError):
    """Security-related error"""
    
    def __init__(self, message: str, security_check: str = None, **kwargs):
        details = kwargs.get('details', {})
        if security_check:
            details['security_check'] = security_check
        
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            details=details,
            user_message=kwargs.get('user_message', "Security check failed. Operation blocked."),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'user_message']}
        )

class ErrorHandler:
    """
    Central error handler for the Automated Review Engine.
    
    Provides:
    - Error logging and tracking
    - User-friendly error messages
    - Recovery suggestions
    - Error analytics
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Logger instance for error logging
        """
        self.logger = logger or logging.getLogger(__name__)
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._error_history: List[ErrorContext] = []
        self._max_history_size = 1000
        
        # Register default handlers
        self._register_default_handlers()
    
    def register_handler(self, exception_type: Type[Exception], 
                        handler: Callable[[Exception], Optional[ErrorContext]]):
        """
        Register custom error handler.
        
        Args:
            exception_type: Exception type to handle
            handler: Handler function that takes exception and returns ErrorContext
        """
        self._error_handlers[exception_type] = handler
        self.logger.debug(f"Registered error handler for {exception_type.__name__}")
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
        """
        Handle an error and return error context.
        
        Args:
            error: Exception to handle
            context: Additional context information
            
        Returns:
            ErrorContext with error details and recovery information
        """
        try:
            # Check for custom handler
            error_type = type(error)
            if error_type in self._error_handlers:
                error_context = self._error_handlers[error_type](error)
                if error_context:
                    self._log_error(error_context)
                    self._store_error(error_context)
                    return error_context
            
            # Handle AutomatedReviewEngineError instances
            if isinstance(error, AutomatedReviewEngineError):
                error_context = error.to_context()
            else:
                # Create generic error context
                error_context = self._create_generic_error_context(error, context)
            
            # Add additional context if provided
            if context:
                error_context.details.update(context)
            
            # Log and store error
            self._log_error(error_context)
            self._store_error(error_context)
            
            return error_context
            
        except Exception as handler_error:
            # Fallback error handling
            self.logger.critical(f"Error handler failed: {str(handler_error)}")
            return self._create_fallback_error_context(error, handler_error)
    
    def _create_generic_error_context(self, error: Exception, 
                                    context: Dict[str, Any] = None) -> ErrorContext:
        """Create generic error context for unhandled exceptions"""
        # Determine category based on error type
        category = self._classify_error(error)
        
        # Determine severity
        severity = self._determine_severity(error, category)
        
        # Generate user message
        user_message = self._generate_user_message(error, category)
        
        # Generate recovery suggestions
        recovery_suggestions = self._generate_recovery_suggestions(error, category)
        
        return ErrorContext(
            timestamp=datetime.now(),
            error_id=f"ARE_GENERIC_{int(datetime.now().timestamp())}",
            severity=severity,
            category=category,
            message=str(error),
            details=context or {},
            stack_trace=traceback.format_exc(),
            user_message=user_message,
            recovery_suggestions=recovery_suggestions
        )
    
    def _create_fallback_error_context(self, original_error: Exception, 
                                     handler_error: Exception) -> ErrorContext:
        """Create fallback error context when error handling fails"""
        return ErrorContext(
            timestamp=datetime.now(),
            error_id=f"ARE_FALLBACK_{int(datetime.now().timestamp())}",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            message=f"Error handler failed: {str(handler_error)}. Original error: {str(original_error)}",
            details={
                'original_error': str(original_error),
                'handler_error': str(handler_error)
            },
            stack_trace=traceback.format_exc(),
            user_message="A critical system error occurred. Please contact support.",
            recovery_suggestions=["Contact technical support", "Restart the application"]
        )
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error into category"""
        error_name = type(error).__name__.lower()
        
        if any(x in error_name for x in ['validation', 'value', 'type']):
            return ErrorCategory.VALIDATION
        elif any(x in error_name for x in ['file', 'io', 'permission']):
            return ErrorCategory.PROCESSING
        elif any(x in error_name for x in ['config', 'setting']):
            return ErrorCategory.CONFIGURATION
        elif any(x in error_name for x in ['connection', 'network', 'timeout']):
            return ErrorCategory.NETWORK
        elif any(x in error_name for x in ['security', 'auth', 'permission']):
            return ErrorCategory.SECURITY
        elif any(x in error_name for x in ['memory', 'system', 'os']):
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.BUSINESS_LOGIC
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        error_name = type(error).__name__.lower()
        
        # Critical errors
        if any(x in error_name for x in ['critical', 'fatal', 'security']):
            return ErrorSeverity.CRITICAL
        
        # Category-based severity
        if category == ErrorCategory.SECURITY:
            return ErrorSeverity.CRITICAL
        elif category in [ErrorCategory.SYSTEM, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.PROCESSING, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory) -> str:
        """Generate user-friendly error message"""
        if category == ErrorCategory.VALIDATION:
            return "Please check your input and try again."
        elif category == ErrorCategory.PROCESSING:
            return "Document processing failed. Please try again or contact support."
        elif category == ErrorCategory.CONFIGURATION:
            return "Configuration error. Please check your settings."
        elif category == ErrorCategory.NETWORK:
            return "Network error. Please check your connection and try again."
        elif category == ErrorCategory.SECURITY:
            return "Security check failed. Operation blocked for safety."
        elif category == ErrorCategory.SYSTEM:
            return "System error occurred. Please try again or contact support."
        else:
            return "An error occurred. Please try again or contact support."
    
    def _generate_recovery_suggestions(self, error: Exception, 
                                     category: ErrorCategory) -> List[str]:
        """Generate recovery suggestions"""
        suggestions = []
        
        if category == ErrorCategory.VALIDATION:
            suggestions.extend([
                "Check input format and requirements",
                "Verify all required fields are filled",
                "Ensure data types are correct"
            ])
        elif category == ErrorCategory.PROCESSING:
            suggestions.extend([
                "Try uploading the file again",
                "Check file format and size",
                "Ensure file is not corrupted"
            ])
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Check configuration file syntax",
                "Verify all required settings are present",
                "Reset to default configuration if needed"
            ])
        elif category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check internet connection",
                "Try again in a few moments",
                "Contact network administrator if problem persists"
            ])
        elif category == ErrorCategory.SECURITY:
            suggestions.extend([
                "Verify file source and integrity",
                "Check file permissions",
                "Contact security administrator"
            ])
        elif category == ErrorCategory.SYSTEM:
            suggestions.extend([
                "Restart the application",
                "Check system resources",
                "Contact technical support"
            ])
        
        # General suggestions
        suggestions.extend([
            "Try the operation again",
            "Contact support if problem persists"
        ])
        
        return suggestions
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        log_data = {
            'error_id': error_context.error_id,
            'severity': error_context.severity.value,
            'category': error_context.category.value,
            'details': error_context.details
        }
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(error_context.message, extra={'extra_data': log_data})
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(error_context.message, extra={'extra_data': log_data})
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(error_context.message, extra={'extra_data': log_data})
        else:
            self.logger.info(error_context.message, extra={'extra_data': log_data})
    
    def _store_error(self, error_context: ErrorContext):
        """Store error in history"""
        self._error_history.append(error_context)
        
        # Maintain history size limit
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]
    
    def _register_default_handlers(self):
        """Register default error handlers"""
        
        def handle_file_not_found(error: FileNotFoundError) -> ErrorContext:
            return ErrorContext(
                timestamp=datetime.now(),
                error_id=f"ARE_FILE_NOT_FOUND_{int(datetime.now().timestamp())}",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.PROCESSING,
                message=str(error),
                details={'error_type': 'FileNotFoundError'},
                user_message="The requested file could not be found.",
                recovery_suggestions=[
                    "Check the file path",
                    "Ensure the file exists",
                    "Try uploading the file again"
                ]
            )
        
        def handle_permission_error(error: PermissionError) -> ErrorContext:
            return ErrorContext(
                timestamp=datetime.now(),
                error_id=f"ARE_PERMISSION_{int(datetime.now().timestamp())}",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SECURITY,
                message=str(error),
                details={'error_type': 'PermissionError'},
                user_message="Access denied. You don't have permission to perform this operation.",
                recovery_suggestions=[
                    "Check file permissions",
                    "Contact administrator",
                    "Try with different credentials"
                ]
            )
        
        def handle_memory_error(error: MemoryError) -> ErrorContext:
            return ErrorContext(
                timestamp=datetime.now(),
                error_id=f"ARE_MEMORY_{int(datetime.now().timestamp())}",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SYSTEM,
                message=str(error),
                details={'error_type': 'MemoryError'},
                user_message="System ran out of memory. Please try with smaller files.",
                recovery_suggestions=[
                    "Try processing smaller files",
                    "Close other applications",
                    "Restart the application",
                    "Contact technical support"
                ]
            )
        
        # Register handlers
        self.register_handler(FileNotFoundError, handle_file_not_found)
        self.register_handler(PermissionError, handle_permission_error)
        self.register_handler(MemoryError, handle_memory_error)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self._error_history:
            return {'total_errors': 0}
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = sum(
                1 for error in self._error_history if error.severity == severity
            )
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = sum(
                1 for error in self._error_history if error.category == category
            )
        
        # Recent errors (last 24 hours)
        recent_cutoff = datetime.now().timestamp() - (24 * 60 * 60)
        recent_errors = [
            error for error in self._error_history 
            if error.timestamp.timestamp() > recent_cutoff
        ]
        
        return {
            'total_errors': len(self._error_history),
            'recent_errors_24h': len(recent_errors),
            'by_severity': severity_counts,
            'by_category': category_counts,
            'last_error': self._error_history[-1].timestamp.isoformat() if self._error_history else None
        }

def error_handler(category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: str = None, recovery_suggestions: List[str] = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AutomatedReviewEngineError:
                # Re-raise our custom errors
                raise
            except Exception as e:
                # Convert to our custom error
                raise AutomatedReviewEngineError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    severity=severity,
                    category=category,
                    details={
                        'function': func.__name__,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs),
                        'original_error_type': type(e).__name__
                    },
                    user_message=user_message,
                    recovery_suggestions=recovery_suggestions
                )
        return wrapper
    return decorator

# Global error handler instance
_error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_error(error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
    """Handle an error using global error handler"""
    return get_error_handler().handle_error(error, context)
