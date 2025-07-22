"""
Validation Utilities

Comprehensive validation utilities for the Automated Review Engine.
Provides data validation, configuration validation, and input sanitization.
"""

import re
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import yaml

from .error_handler import ValidationError, ErrorSeverity

@dataclass
class ValidationRule:
    """Validation rule definition"""
    name: str
    validator: Callable[[Any], bool]
    error_message: str
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    
@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    field_errors: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.field_errors is None:
            self.field_errors = {}

class ValidatorRegistry:
    """Registry for validation rules and validators"""
    
    def __init__(self):
        self._validators: Dict[str, ValidationRule] = {}
        self._field_validators: Dict[str, List[ValidationRule]] = {}
        self._register_built_in_validators()
    
    def register_validator(self, name: str, validator: ValidationRule):
        """Register a validation rule"""
        self._validators[name] = validator
    
    def register_field_validator(self, field_name: str, validator: ValidationRule):
        """Register a validator for a specific field"""
        if field_name not in self._field_validators:
            self._field_validators[field_name] = []
        self._field_validators[field_name].append(validator)
    
    def get_validator(self, name: str) -> Optional[ValidationRule]:
        """Get validator by name"""
        return self._validators.get(name)
    
    def get_field_validators(self, field_name: str) -> List[ValidationRule]:
        """Get validators for a field"""
        return self._field_validators.get(field_name, [])
    
    def _register_built_in_validators(self):
        """Register built-in validation rules"""
        
        # String validators
        self.register_validator('required', ValidationRule(
            name='required',
            validator=lambda x: x is not None and str(x).strip() != '',
            error_message='This field is required'
        ))
        
        self.register_validator('email', ValidationRule(
            name='email',
            validator=lambda x: bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', str(x))) if x else True,
            error_message='Invalid email format'
        ))
        
        self.register_validator('url', ValidationRule(
            name='url',
            validator=lambda x: bool(re.match(r'^https?://.+', str(x))) if x else True,
            error_message='Invalid URL format'
        ))
        
        # Numeric validators
        self.register_validator('positive', ValidationRule(
            name='positive',
            validator=lambda x: float(x) > 0 if x is not None else True,
            error_message='Value must be positive'
        ))
        
        self.register_validator('non_negative', ValidationRule(
            name='non_negative',
            validator=lambda x: float(x) >= 0 if x is not None else True,
            error_message='Value must be non-negative'
        ))
        
        # File validators
        self.register_validator('file_exists', ValidationRule(
            name='file_exists',
            validator=lambda x: Path(x).exists() if x else True,
            error_message='File does not exist'
        ))
        
        self.register_validator('directory_exists', ValidationRule(
            name='directory_exists',
            validator=lambda x: Path(x).is_dir() if x else True,
            error_message='Directory does not exist'
        ))

class DataValidator:
    """
    Data validation utilities for the Automated Review Engine.
    
    Provides comprehensive validation for various data types,
    configurations, and user inputs.
    """
    
    def __init__(self, registry: Optional[ValidatorRegistry] = None):
        """
        Initialize data validator.
        
        Args:
            registry: Custom validator registry (optional)
        """
        self.registry = registry or ValidatorRegistry()
    
    def validate_dict(self, data: Dict[str, Any], 
                     schema: Dict[str, List[str]]) -> ValidationResult:
        """
        Validate dictionary against schema.
        
        Args:
            data: Data to validate
            schema: Validation schema {field_name: [validator_names]}
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(is_valid=True)
        
        try:
            for field_name, validator_names in schema.items():
                field_value = data.get(field_name)
                field_errors = []
                
                for validator_name in validator_names:
                    validator = self.registry.get_validator(validator_name)
                    if not validator:
                        result.warnings.append(f"Unknown validator: {validator_name}")
                        continue
                    
                    try:
                        if not validator.validator(field_value):
                            field_errors.append(validator.error_message)
                    except Exception as e:
                        field_errors.append(f"Validation error: {str(e)}")
                
                if field_errors:
                    result.field_errors[field_name] = field_errors
                    result.errors.extend([f"{field_name}: {error}" for error in field_errors])
                    result.is_valid = False
            
        except Exception as e:
            result.errors.append(f"Validation failed: {str(e)}")
            result.is_valid = False
        
        return result
    
    def validate_file_upload(self, file_path: Union[str, Path], 
                           config: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate file upload.
        
        Args:
            file_path: Path to uploaded file
            config: Upload configuration
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(is_valid=True)
        file_path = Path(file_path)
        config = config or {}
        
        try:
            # Check file exists
            if not file_path.exists():
                result.errors.append("File does not exist")
                result.is_valid = False
                return result
            
            # Check file size
            max_size_mb = config.get('max_file_size_mb', 50)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > max_size_mb:
                result.errors.append(f"File too large: {file_size_mb:.1f}MB exceeds limit of {max_size_mb}MB")
                result.is_valid = False
            
            # Check file extension
            allowed_extensions = config.get('allowed_extensions', ['.pdf', '.docx'])
            if file_path.suffix.lower() not in allowed_extensions:
                result.errors.append(f"File type not allowed: {file_path.suffix}")
                result.is_valid = False
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            allowed_mime_types = config.get('allowed_mime_types', [])
            if allowed_mime_types and mime_type not in allowed_mime_types:
                result.warnings.append(f"MIME type may not be supported: {mime_type}")
            
            # Check file name
            if not self._is_safe_filename(file_path.name):
                result.errors.append("Unsafe characters in filename")
                result.is_valid = False
            
            # Additional security checks
            if config.get('enable_security_checks', True):
                security_result = self._validate_file_security(file_path)
                result.errors.extend(security_result.errors)
                result.warnings.extend(security_result.warnings)
                if not security_result.is_valid:
                    result.is_valid = False
            
        except Exception as e:
            result.errors.append(f"File validation failed: {str(e)}")
            result.is_valid = False
        
        return result
    
    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate application configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Define configuration schema
            config_schema = {
                'environment': ['required'],
                'files.max_file_size_mb': ['required', 'positive'],
                'logging.level': ['required'],
                'ui.streamlit_port': ['required', 'positive'],
                'database.connection_timeout': ['positive'],
                'performance.memory_limit_mb': ['positive']
            }
            
            # Flatten config for validation
            flat_config = self._flatten_dict(config)
            
            # Validate against schema
            for config_key, validators in config_schema.items():
                value = flat_config.get(config_key)
                
                for validator_name in validators:
                    validator = self.registry.get_validator(validator_name)
                    if not validator:
                        continue
                    
                    try:
                        if not validator.validator(value):
                            result.errors.append(f"Configuration error in {config_key}: {validator.error_message}")
                            result.is_valid = False
                    except Exception as e:
                        result.errors.append(f"Configuration validation error in {config_key}: {str(e)}")
                        result.is_valid = False
            
            # Additional configuration checks
            self._validate_port_availability(config, result)
            self._validate_directory_permissions(config, result)
            
        except Exception as e:
            result.errors.append(f"Configuration validation failed: {str(e)}")
            result.is_valid = False
        
        return result
    
    def validate_document_content(self, content: str, 
                                config: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate document content.
        
        Args:
            content: Document text content
            config: Validation configuration
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(is_valid=True)
        config = config or {}
        
        try:
            # Check content exists
            if not content or not content.strip():
                result.errors.append("Document content is empty")
                result.is_valid = False
                return result
            
            # Check content length
            min_length = config.get('min_content_length', 10)
            max_length = config.get('max_content_length', 1000000)
            
            if len(content) < min_length:
                result.warnings.append(f"Content is very short ({len(content)} characters)")
            
            if len(content) > max_length:
                result.errors.append(f"Content too long: {len(content)} exceeds limit of {max_length}")
                result.is_valid = False
            
            # Check for suspicious content
            if config.get('check_suspicious_content', True):
                suspicious_patterns = [
                    r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # JavaScript
                    r'javascript:',  # JavaScript URLs
                    r'data:.*base64',  # Base64 data URLs
                ]
                
                for pattern in suspicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        result.warnings.append("Potentially suspicious content detected")
                        break
            
            # Check text encoding
            try:
                content.encode('utf-8')
            except UnicodeEncodeError:
                result.warnings.append("Content contains non-UTF-8 characters")
            
        except Exception as e:
            result.errors.append(f"Content validation failed: {str(e)}")
            result.is_valid = False
        
        return result
    
    def sanitize_input(self, input_value: str, input_type: str = 'text') -> str:
        """
        Sanitize user input.
        
        Args:
            input_value: Input value to sanitize
            input_type: Type of input (text, filename, path, etc.)
            
        Returns:
            Sanitized input value
        """
        if not input_value:
            return input_value
        
        if input_type == 'filename':
            # Remove/replace unsafe characters in filenames
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', input_value)
            sanitized = re.sub(r'\.+', '.', sanitized)  # Replace multiple dots
            sanitized = sanitized.strip('. ')  # Remove leading/trailing dots and spaces
            return sanitized[:255]  # Limit length
        
        elif input_type == 'path':
            # Sanitize file paths
            path = Path(input_value)
            safe_parts = []
            for part in path.parts:
                if part not in ['.', '..']:
                    safe_part = self.sanitize_input(part, 'filename')
                    safe_parts.append(safe_part)
            return str(Path(*safe_parts)) if safe_parts else ''
        
        elif input_type == 'text':
            # Basic text sanitization
            sanitized = input_value.strip()
            # Remove null bytes and control characters (except common whitespace)
            sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
            return sanitized
        
        else:
            return input_value.strip()
    
    def create_custom_validator(self, name: str, validator_func: Callable[[Any], bool], 
                              error_message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> ValidationRule:
        """
        Create and register custom validator.
        
        Args:
            name: Validator name
            validator_func: Validation function
            error_message: Error message for validation failure
            severity: Error severity level
            
        Returns:
            Created ValidationRule
        """
        rule = ValidationRule(name, validator_func, error_message, severity)
        self.registry.register_validator(name, rule)
        return rule
    
    def _is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe"""
        # Check for unsafe patterns
        unsafe_patterns = [
            r'\.\./',  # Directory traversal
            r'^\.+$',  # Dots only
            r'[<>:"/\\|?*]',  # Unsafe characters
            r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)',  # Windows reserved names
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        return True
    
    def _validate_file_security(self, file_path: Path) -> ValidationResult:
        """Perform security validation on file"""
        result = ValidationResult(is_valid=True)
        
        try:
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                result.errors.append("File is not readable")
                result.is_valid = False
            
            # Check for hidden files (may be suspicious)
            if file_path.name.startswith('.'):
                result.warnings.append("Hidden file detected")
            
            # Check file signature (basic check)
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(16)
                
                # Check for known file signatures
                if file_path.suffix.lower() == '.pdf' and not header.startswith(b'%PDF'):
                    result.warnings.append("File extension doesn't match content (PDF expected)")
                
                elif file_path.suffix.lower() == '.docx' and not header.startswith(b'PK'):
                    result.warnings.append("File extension doesn't match content (DOCX expected)")
                
            except Exception:
                result.warnings.append("Could not verify file signature")
            
        except Exception as e:
            result.warnings.append(f"Security validation incomplete: {str(e)}")
        
        return result
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _validate_port_availability(self, config: Dict[str, Any], result: ValidationResult):
        """Validate port availability"""
        try:
            import socket
            
            # Check Streamlit port
            ui_config = config.get('ui', {})
            port = ui_config.get('streamlit_port', 8501)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result_code = sock.connect_ex(('localhost', port))
                if result_code == 0:
                    result.warnings.append(f"Port {port} appears to be in use")
                    
        except Exception:
            # Port check failed, but not critical
            pass
    
    def _validate_directory_permissions(self, config: Dict[str, Any], result: ValidationResult):
        """Validate directory permissions"""
        try:
            # Check file directories
            files_config = config.get('files', {})
            directories = [
                files_config.get('upload_directory', 'data/uploads'),
                files_config.get('temp_directory', 'data/temp'),
            ]
            
            # Check logging directory
            logging_config = config.get('logging', {})
            log_file = logging_config.get('file_path', 'logs/application.log')
            directories.append(str(Path(log_file).parent))
            
            for directory in directories:
                dir_path = Path(directory)
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    if not os.access(dir_path, os.W_OK):
                        result.warnings.append(f"Directory not writable: {directory}")
                except Exception:
                    result.warnings.append(f"Cannot create directory: {directory}")
                    
        except Exception:
            # Directory check failed, but not critical
            pass

# Global validator instance
_validator: Optional[DataValidator] = None

def get_validator() -> DataValidator:
    """Get global validator instance"""
    global _validator
    if _validator is None:
        _validator = DataValidator()
    return _validator

def validate_file_upload(file_path: Union[str, Path], config: Dict[str, Any] = None) -> ValidationResult:
    """Validate file upload using global validator"""
    return get_validator().validate_file_upload(file_path, config)

def validate_configuration(config: Dict[str, Any]) -> ValidationResult:
    """Validate configuration using global validator"""
    return get_validator().validate_configuration(config)

def sanitize_input(input_value: str, input_type: str = 'text') -> str:
    """Sanitize input using global validator"""
    return get_validator().sanitize_input(input_value, input_type)
