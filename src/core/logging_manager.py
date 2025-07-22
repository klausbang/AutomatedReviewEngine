"""
Logging System

Comprehensive logging system for the Automated Review Engine.
Provides structured logging, file rotation, and performance monitoring.
"""

import logging
import logging.handlers
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import threading
import time
import functools

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    extra_data: Dict[str, Any] = None
    exception_info: Optional[str] = None

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        try:
            # Create structured log entry
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                thread_id=record.thread,
                process_id=record.process,
                extra_data=getattr(record, 'extra_data', {}),
                exception_info=self.formatException(record.exc_info) if record.exc_info else None
            )
            
            # Convert to JSON
            return json.dumps(asdict(log_entry), default=str)
            
        except Exception as e:
            # Fallback to standard formatting if JSON fails
            return super().format(record)

class PerformanceLogger:
    """Performance monitoring and logging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._operation_stats = {}
        self._lock = threading.Lock()
    
    def log_operation_start(self, operation_id: str, operation_type: str, details: Dict[str, Any] = None):
        """Log the start of an operation"""
        with self._lock:
            self._operation_stats[operation_id] = {
                'type': operation_type,
                'start_time': time.time(),
                'details': details or {}
            }
        
        self.logger.info(
            f"Operation started: {operation_type}",
            extra={'extra_data': {
                'operation_id': operation_id,
                'operation_type': operation_type,
                'details': details or {}
            }}
        )
    
    def log_operation_end(self, operation_id: str, success: bool = True, 
                         result_details: Dict[str, Any] = None, error: Exception = None):
        """Log the end of an operation"""
        with self._lock:
            if operation_id not in self._operation_stats:
                self.logger.warning(f"Operation end logged without start: {operation_id}")
                return
            
            operation = self._operation_stats.pop(operation_id)
            duration = time.time() - operation['start_time']
        
        log_data = {
            'operation_id': operation_id,
            'operation_type': operation['type'],
            'duration_seconds': round(duration, 3),
            'success': success,
            'start_details': operation['details'],
            'result_details': result_details or {}
        }
        
        if success:
            self.logger.info(
                f"Operation completed: {operation['type']} ({duration:.3f}s)",
                extra={'extra_data': log_data}
            )
        else:
            if error:
                log_data['error_type'] = type(error).__name__
                log_data['error_message'] = str(error)
            
            self.logger.error(
                f"Operation failed: {operation['type']} ({duration:.3f}s)",
                extra={'extra_data': log_data},
                exc_info=error
            )
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get current operation statistics"""
        with self._lock:
            return {
                'active_operations': len(self._operation_stats),
                'operations': dict(self._operation_stats)
            }

def performance_monitor(operation_type: str = None, logger_name: str = None):
    """Decorator for automatic performance monitoring"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger
            logger = logging.getLogger(logger_name or func.__module__)
            perf_logger = PerformanceLogger(logger)
            
            # Generate operation ID and type
            op_type = operation_type or f"{func.__module__}.{func.__name__}"
            op_id = f"{op_type}_{int(time.time() * 1000000)}"
            
            # Log operation start
            perf_logger.log_operation_start(op_id, op_type, {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            })
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful completion
                perf_logger.log_operation_end(op_id, success=True, result_details={
                    'result_type': type(result).__name__ if result is not None else 'None'
                })
                
                return result
                
            except Exception as e:
                # Log failed completion
                perf_logger.log_operation_end(op_id, success=False, error=e)
                raise
        
        return wrapper
    return decorator

class LoggingManager:
    """
    Central logging manager for the Automated Review Engine.
    
    Provides:
    - Centralized logger configuration
    - File rotation and management
    - Structured logging support
    - Performance monitoring
    - Log level management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize logging manager.
        
        Args:
            config: Logging configuration dictionary
        """
        self.config = config or {}
        self._loggers: Dict[str, logging.Logger] = {}
        self._performance_logger: Optional[PerformanceLogger] = None
        self._initialized = False
        
        # Default configuration
        self.default_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_enabled': True,
            'file_path': 'logs/application.log',
            'file_max_size_mb': 10,
            'file_backup_count': 5,
            'console_enabled': True,
            'structured_logging': False
        }
        
        # Merge with provided config
        self.config = {**self.default_config, **self.config}
    
    def initialize(self) -> bool:
        """
        Initialize the logging system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create logs directory
            log_file = Path(self.config['file_path'])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, self.config['level'].upper()))
            
            # Clear existing handlers
            root_logger.handlers.clear()
            
            # Set up formatters
            if self.config['structured_logging']:
                formatter = StructuredFormatter()
            else:
                formatter = logging.Formatter(self.config['format'])
            
            # Console handler
            if self.config['console_enabled']:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                console_handler.setLevel(getattr(logging, self.config['level'].upper()))
                root_logger.addHandler(console_handler)
            
            # File handler with rotation
            if self.config['file_enabled']:
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=self.config['file_path'],
                    maxBytes=self.config['file_max_size_mb'] * 1024 * 1024,
                    backupCount=self.config['file_backup_count'],
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(getattr(logging, self.config['level'].upper()))
                root_logger.addHandler(file_handler)
            
            # Initialize performance logger
            self._performance_logger = PerformanceLogger(self.get_logger('performance'))
            
            self._initialized = True
            
            # Log initialization
            logger = self.get_logger('logging_manager')
            logger.info("Logging system initialized successfully")
            logger.info(f"Configuration: {self.config}")
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize logging system: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if not self._initialized:
            # Return basic logger if not initialized
            return logging.getLogger(name)
        
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        
        return self._loggers[name]
    
    def set_level(self, level: Union[str, int], logger_name: Optional[str] = None):
        """
        Set logging level.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            logger_name: Specific logger name (None for root logger)
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        
        if logger_name:
            logger = self.get_logger(logger_name)
            logger.setLevel(level)
        else:
            logging.getLogger().setLevel(level)
            # Update all handlers
            for handler in logging.getLogger().handlers:
                handler.setLevel(level)
    
    def get_performance_logger(self) -> Optional[PerformanceLogger]:
        """Get performance logger instance"""
        return self._performance_logger
    
    def log_system_info(self):
        """Log system information"""
        logger = self.get_logger('system_info')
        
        import platform
        import psutil
        
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_usage': {
                'total_gb': round(psutil.disk_usage('.').total / (1024**3), 2),
                'free_gb': round(psutil.disk_usage('.').free / (1024**3), 2)
            }
        }
        
        logger.info("System information", extra={'extra_data': system_info})
    
    def log_application_start(self, version: str, config_summary: Dict[str, Any]):
        """Log application startup"""
        logger = self.get_logger('application')
        
        startup_info = {
            'event': 'application_start',
            'version': version,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'config_summary': config_summary
        }
        
        logger.info(f"Application started - version {version}", extra={'extra_data': startup_info})
    
    def log_application_stop(self, version: str):
        """Log application shutdown"""
        logger = self.get_logger('application')
        
        shutdown_info = {
            'event': 'application_stop',
            'version': version,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Application stopped - version {version}", extra={'extra_data': shutdown_info})
    
    def create_audit_logger(self, audit_file: str = "logs/audit.log") -> logging.Logger:
        """
        Create specialized audit logger.
        
        Args:
            audit_file: Audit log file path
            
        Returns:
            Audit logger instance
        """
        audit_logger = logging.getLogger('audit')
        audit_logger.setLevel(logging.INFO)
        
        # Audit log should always use structured format
        audit_formatter = StructuredFormatter()
        
        # Create audit file handler
        audit_file_path = Path(audit_file)
        audit_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        audit_handler = logging.handlers.RotatingFileHandler(
            filename=audit_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        
        # Prevent propagation to root logger
        audit_logger.propagate = False
        
        return audit_logger
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            'initialized': self._initialized,
            'active_loggers': len(self._loggers),
            'logger_names': list(self._loggers.keys()),
            'config': self.config
        }
        
        if self._performance_logger:
            stats['performance'] = self._performance_logger.get_operation_stats()
        
        # Check log file sizes
        if self.config['file_enabled']:
            log_file = Path(self.config['file_path'])
            if log_file.exists():
                stats['log_file_size_mb'] = round(log_file.stat().st_size / (1024**2), 2)
            
            # Check for rotated log files
            log_dir = log_file.parent
            pattern = f"{log_file.stem}.*{log_file.suffix}"
            rotated_files = list(log_dir.glob(pattern))
            stats['rotated_log_files'] = len(rotated_files)
        
        return stats
    
    def cleanup_old_logs(self, max_age_days: int = 30):
        """
        Clean up old log files.
        
        Args:
            max_age_days: Maximum age of log files to keep
        """
        try:
            logger = self.get_logger('log_cleanup')
            
            if not self.config['file_enabled']:
                return
            
            log_file = Path(self.config['file_path'])
            log_dir = log_file.parent
            
            if not log_dir.exists():
                return
            
            # Find old log files
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0
            
            for log_path in log_dir.glob("*.log*"):
                try:
                    if log_path.stat().st_mtime < cutoff_time:
                        log_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old log file: {log_path}")
                except Exception as e:
                    logger.warning(f"Could not delete log file {log_path}: {str(e)}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log files")
                
        except Exception as e:
            print(f"Error during log cleanup: {str(e)}")

# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None

def get_logging_manager() -> LoggingManager:
    """Get global logging manager instance"""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager

def initialize_logging(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize the global logging system"""
    global _logging_manager
    _logging_manager = LoggingManager(config)
    return _logging_manager.initialize()

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return get_logging_manager().get_logger(name)
