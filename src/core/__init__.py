"""
Core Module

Core infrastructure components for the Automated Review Engine.

This module provides the foundational systems that support the entire application:
- Configuration management
- Logging and monitoring
- Error handling and recovery
- Data validation and sanitization

Components:
- ConfigManager: Centralized configuration management
- LoggingManager: Comprehensive logging system with rotation and structured logging
- ErrorHandler: Error handling framework with recovery suggestions
- DataValidator: Validation utilities for data integrity and security
"""

from .config_manager import (
    ConfigManager,
    AppConfig,
    DatabaseConfig,
    FileConfig,
    ProcessingConfig,
    ValidationConfig,
    LoggingConfig,
    UIConfig,
    SecurityConfig,
    PerformanceConfig,
    get_config_manager,
    load_config,
    get_config
)

from .logging_manager import (
    LoggingManager,
    PerformanceLogger,
    StructuredFormatter,
    LogEntry,
    performance_monitor,
    get_logging_manager,
    initialize_logging,
    get_logger
)

from .error_handler import (
    ErrorHandler,
    ErrorContext,
    ErrorSeverity,
    ErrorCategory,
    AutomatedReviewEngineError,
    ValidationError,
    ProcessingError,
    ConfigurationError,
    SecurityError,
    error_handler,
    get_error_handler,
    handle_error
)

from .validation_utils import (
    DataValidator,
    ValidationRule,
    ValidationResult,
    ValidatorRegistry,
    get_validator,
    validate_file_upload,
    validate_configuration,
    sanitize_input
)

__all__ = [
    # Configuration Management
    'ConfigManager',
    'AppConfig',
    'DatabaseConfig',
    'FileConfig',
    'ProcessingConfig',
    'ValidationConfig',
    'LoggingConfig',
    'UIConfig',
    'SecurityConfig',
    'PerformanceConfig',
    'get_config_manager',
    'load_config',
    'get_config',
    
    # Logging System
    'LoggingManager',
    'PerformanceLogger',
    'StructuredFormatter',
    'LogEntry',
    'performance_monitor',
    'get_logging_manager',
    'initialize_logging',
    'get_logger',
    
    # Error Handling
    'ErrorHandler',
    'ErrorContext',
    'ErrorSeverity',
    'ErrorCategory',
    'AutomatedReviewEngineError',
    'ValidationError',
    'ProcessingError',
    'ConfigurationError',
    'SecurityError',
    'error_handler',
    'get_error_handler',
    'handle_error',
    
    # Validation
    'DataValidator',
    'ValidationRule',
    'ValidationResult',
    'ValidatorRegistry',
    'get_validator',
    'validate_file_upload',
    'validate_configuration',
    'sanitize_input'
]
