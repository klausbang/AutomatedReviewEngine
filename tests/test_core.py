"""
Tests for Core Module

Comprehensive test suite for core infrastructure components including:
- Configuration management
- Logging system
- Error handling
- Validation utilities
"""

import pytest
import tempfile
import shutil
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Import components to test
from src.core import (
    ConfigManager, AppConfig, LoggingManager, ErrorHandler,
    DataValidator, ValidationError, ProcessingError,
    ErrorSeverity, ErrorCategory
)

class TestConfigManager:
    """Test suite for ConfigManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self, temp_dir):
        """Create sample configuration file"""
        config_file = temp_dir / "config.yaml"
        config_data = {
            'environment': 'test',
            'debug_mode': True,
            'files': {
                'max_file_size_mb': 25,
                'upload_directory': 'test/uploads'
            },
            'logging': {
                'level': 'DEBUG',
                'file_enabled': False
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        return config_file
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()
        assert manager is not None
        assert manager.config_file is None
        assert not manager._config_loaded
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        manager = ConfigManager()
        config = manager.load_config()
        
        assert isinstance(config, AppConfig)
        assert config.environment == "development"
        assert config.version == "0.2.2"
        assert config.files.max_file_size_mb == 50
    
    def test_load_config_from_file(self, sample_config):
        """Test loading configuration from file"""
        manager = ConfigManager()
        config = manager.load_config(sample_config)
        
        assert config.environment == "test"
        assert config.debug_mode == True
        assert config.files.max_file_size_mb == 25
        assert config.files.upload_directory == "test/uploads"
        assert config.logging.level == "DEBUG"
        assert config.logging.file_enabled == False
    
    def test_environment_variable_override(self, sample_config):
        """Test environment variable configuration override"""
        with patch.dict('os.environ', {
            'ARE_ENVIRONMENT': 'production',
            'ARE_FILES_MAX_FILE_SIZE_MB': '100'
        }):
            manager = ConfigManager()
            config = manager.load_config(sample_config)
            
            assert config.environment == "production"
            assert config.files.max_file_size_mb == 100
    
    def test_get_config_before_load(self):
        """Test getting config before loading"""
        manager = ConfigManager()
        
        with pytest.raises(RuntimeError):
            manager.get_config()
    
    def test_save_config(self, temp_dir):
        """Test saving configuration"""
        manager = ConfigManager()
        config = manager.load_config()
        
        output_file = temp_dir / "output_config.yaml"
        success = manager.save_config(output_file)
        
        assert success
        assert output_file.exists()
    
    def test_update_config(self):
        """Test updating configuration"""
        manager = ConfigManager()
        config = manager.load_config()
        
        updates = {
            'environment': 'updated',
            'files': {
                'max_file_size_mb': 75
            }
        }
        
        success = manager.update_config(updates)
        assert success
        
        updated_config = manager.get_config()
        assert updated_config.environment == "updated"
        assert updated_config.files.max_file_size_mb == 75
    
    def test_create_default_config_file(self, temp_dir):
        """Test creating default configuration file"""
        manager = ConfigManager()
        output_file = temp_dir / "default_config.yaml"
        
        success = manager.create_default_config_file(output_file)
        assert success
        assert output_file.exists()
    
    def test_environment_template_generation(self):
        """Test environment template generation"""
        manager = ConfigManager()
        template = manager.get_environment_template()
        
        assert isinstance(template, str)
        assert "ARE_ENVIRONMENT" in template
        assert "ARE_FILES_MAX_FILE_SIZE_MB" in template

class TestLoggingManager:
    """Test suite for LoggingManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_logging_manager_initialization(self):
        """Test LoggingManager initialization"""
        manager = LoggingManager()
        assert manager is not None
        assert not manager._initialized
    
    def test_logging_manager_with_config(self, temp_dir):
        """Test LoggingManager with custom configuration"""
        config = {
            'level': 'DEBUG',
            'file_path': str(temp_dir / 'test.log'),
            'console_enabled': False
        }
        
        manager = LoggingManager(config)
        success = manager.initialize()
        
        assert success
        assert manager._initialized
    
    def test_get_logger(self, temp_dir):
        """Test getting logger instance"""
        config = {
            'file_path': str(temp_dir / 'test.log')
        }
        
        manager = LoggingManager(config)
        manager.initialize()
        
        logger = manager.get_logger('test_logger')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'
    
    def test_set_logging_level(self, temp_dir):
        """Test setting logging level"""
        config = {
            'file_path': str(temp_dir / 'test.log')
        }
        
        manager = LoggingManager(config)
        manager.initialize()
        
        manager.set_level('ERROR')
        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR
    
    def test_performance_logger(self, temp_dir):
        """Test performance logging"""
        config = {
            'file_path': str(temp_dir / 'test.log')
        }
        
        manager = LoggingManager(config)
        manager.initialize()
        
        perf_logger = manager.get_performance_logger()
        assert perf_logger is not None
        
        # Test operation logging
        perf_logger.log_operation_start('test_op', 'test_operation', {'param': 'value'})
        perf_logger.log_operation_end('test_op', success=True)
        
        stats = perf_logger.get_operation_stats()
        assert isinstance(stats, dict)
        assert 'active_operations' in stats
    
    def test_log_statistics(self, temp_dir):
        """Test logging statistics"""
        config = {
            'file_path': str(temp_dir / 'test.log')
        }
        
        manager = LoggingManager(config)
        manager.initialize()
        
        stats = manager.get_log_statistics()
        assert isinstance(stats, dict)
        assert 'initialized' in stats
        assert stats['initialized'] == True

class TestErrorHandler:
    """Test suite for ErrorHandler"""
    
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization"""
        handler = ErrorHandler()
        assert handler is not None
        assert len(handler._error_handlers) > 0  # Should have default handlers
    
    def test_handle_custom_error(self):
        """Test handling custom AutomatedReviewEngineError"""
        handler = ErrorHandler()
        
        error = ValidationError(
            "Test validation error",
            field_name="test_field",
            user_message="Test user message"
        )
        
        context = handler.handle_error(error)
        
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.category == ErrorCategory.VALIDATION
        assert "test_field" in context.details
        assert context.user_message == "Test user message"
    
    def test_handle_generic_error(self):
        """Test handling generic Python exception"""
        handler = ErrorHandler()
        
        error = ValueError("Test value error")
        context = handler.handle_error(error)
        
        assert context.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
        assert context.category == ErrorCategory.VALIDATION
        assert context.message == "Test value error"
    
    def test_register_custom_handler(self):
        """Test registering custom error handler"""
        handler = ErrorHandler()
        
        def custom_handler(error):
            return None  # Return None to use default handling
        
        handler.register_handler(KeyError, custom_handler)
        assert KeyError in handler._error_handlers
    
    def test_error_statistics(self):
        """Test error statistics collection"""
        handler = ErrorHandler()
        
        # Generate some errors
        handler.handle_error(ValueError("Test error 1"))
        handler.handle_error(ValidationError("Test error 2"))
        
        stats = handler.get_error_statistics()
        assert isinstance(stats, dict)
        assert stats['total_errors'] >= 2
        assert 'by_severity' in stats
        assert 'by_category' in stats

class TestDataValidator:
    """Test suite for DataValidator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_file(self, temp_dir):
        """Create sample file for testing"""
        file_path = temp_dir / "sample.txt"
        with open(file_path, 'w') as f:
            f.write("Sample file content")
        return file_path
    
    def test_validator_initialization(self):
        """Test DataValidator initialization"""
        validator = DataValidator()
        assert validator is not None
        assert validator.registry is not None
    
    def test_validate_dict(self):
        """Test dictionary validation"""
        validator = DataValidator()
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30
        }
        
        schema = {
            'name': ['required'],
            'email': ['required', 'email'],
            'age': ['required', 'positive']
        }
        
        result = validator.validate_dict(data, schema)
        assert result.is_valid == True
        assert len(result.errors) == 0
    
    def test_validate_dict_with_errors(self):
        """Test dictionary validation with errors"""
        validator = DataValidator()
        
        data = {
            'name': '',
            'email': 'invalid-email',
            'age': -5
        }
        
        schema = {
            'name': ['required'],
            'email': ['required', 'email'],
            'age': ['required', 'positive']
        }
        
        result = validator.validate_dict(data, schema)
        assert result.is_valid == False
        assert len(result.errors) > 0
        assert 'name' in result.field_errors
        assert 'email' in result.field_errors
        assert 'age' in result.field_errors
    
    def test_validate_file_upload(self, sample_file):
        """Test file upload validation"""
        validator = DataValidator()
        
        config = {
            'max_file_size_mb': 1,
            'allowed_extensions': ['.txt'],
            'enable_security_checks': False
        }
        
        result = validator.validate_file_upload(sample_file, config)
        assert result.is_valid == True
    
    def test_validate_file_upload_size_limit(self, temp_dir):
        """Test file upload size limit validation"""
        validator = DataValidator()
        
        # Create large file
        large_file = temp_dir / "large.txt"
        with open(large_file, 'w') as f:
            f.write("x" * (2 * 1024 * 1024))  # 2MB
        
        config = {
            'max_file_size_mb': 1,  # 1MB limit
            'allowed_extensions': ['.txt']
        }
        
        result = validator.validate_file_upload(large_file, config)
        assert result.is_valid == False
        assert any("too large" in error.lower() for error in result.errors)
    
    def test_validate_file_upload_extension(self, sample_file):
        """Test file upload extension validation"""
        validator = DataValidator()
        
        config = {
            'allowed_extensions': ['.pdf', '.docx']  # .txt not allowed
        }
        
        result = validator.validate_file_upload(sample_file, config)
        assert result.is_valid == False
        assert any("not allowed" in error.lower() for error in result.errors)
    
    def test_validate_configuration(self):
        """Test configuration validation"""
        validator = DataValidator()
        
        config = {
            'environment': 'development',
            'files': {
                'max_file_size_mb': 50
            },
            'logging': {
                'level': 'INFO'
            },
            'ui': {
                'streamlit_port': 8501
            }
        }
        
        result = validator.validate_configuration(config)
        # Should pass basic validation
        assert isinstance(result.is_valid, bool)
    
    def test_validate_document_content(self):
        """Test document content validation"""
        validator = DataValidator()
        
        content = "This is a valid document content with sufficient length."
        result = validator.validate_document_content(content)
        
        assert result.is_valid == True
    
    def test_validate_empty_content(self):
        """Test validation of empty content"""
        validator = DataValidator()
        
        content = ""
        result = validator.validate_document_content(content)
        
        assert result.is_valid == False
        assert any("empty" in error.lower() for error in result.errors)
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        validator = DataValidator()
        
        # Test filename sanitization
        unsafe_filename = "test<>:|file.txt"
        safe_filename = validator.sanitize_input(unsafe_filename, 'filename')
        assert '<' not in safe_filename
        assert '>' not in safe_filename
        assert '|' not in safe_filename
    
    def test_create_custom_validator(self):
        """Test creating custom validator"""
        validator = DataValidator()
        
        def is_even(value):
            try:
                return int(value) % 2 == 0
            except (ValueError, TypeError):
                return False
        
        rule = validator.create_custom_validator(
            'even_number',
            is_even,
            'Value must be an even number'
        )
        
        assert rule.name == 'even_number'
        assert validator.registry.get_validator('even_number') is not None
        
        # Test the custom validator
        data = {'number': 4}
        schema = {'number': ['even_number']}
        result = validator.validate_dict(data, schema)
        assert result.is_valid == True
        
        data = {'number': 5}
        result = validator.validate_dict(data, schema)
        assert result.is_valid == False

class TestIntegration:
    """Integration tests for core components"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_config_and_logging_integration(self, temp_dir):
        """Test integration between configuration and logging"""
        # Create config with logging settings
        config_file = temp_dir / "config.yaml"
        config_data = {
            'logging': {
                'level': 'DEBUG',
                'file_path': str(temp_dir / 'test.log'),
                'file_enabled': True
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_file)
        
        # Initialize logging with config
        logging_config = {
            'level': config.logging.level,
            'file_path': config.logging.file_path,
            'file_enabled': config.logging.file_enabled
        }
        
        logging_manager = LoggingManager(logging_config)
        success = logging_manager.initialize()
        
        assert success
        assert Path(config.logging.file_path).parent.exists()
    
    def test_error_handling_with_validation(self):
        """Test error handling with validation errors"""
        validator = DataValidator()
        error_handler = ErrorHandler()
        
        # Create validation error
        try:
            data = {'email': 'invalid-email'}
            schema = {'email': ['email']}
            result = validator.validate_dict(data, schema)
            
            if not result.is_valid:
                raise ValidationError("Validation failed", details={'errors': result.errors})
                
        except ValidationError as e:
            context = error_handler.handle_error(e)
            
            assert context.category == ErrorCategory.VALIDATION
            assert context.severity == ErrorSeverity.MEDIUM
            assert 'errors' in context.details

if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
