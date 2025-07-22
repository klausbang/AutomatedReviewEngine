"""
Integration Test Script for Phase 2.2

This script demonstrates the integration of all Phase 2.2 components:
- Configuration Management
- Logging System  
- Error Handling
- Data Validation

Run this script to verify that all core infrastructure components
work together correctly.
"""

import os
import sys
from pathlib import Path
import tempfile
import json
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import core components
from core.config_manager import ConfigManager, AppConfig
from core.logging_manager import LoggingManager, performance_monitor
from core.error_handler import ErrorHandler, ValidationError
from core.validation_utils import DataValidator

def main():
    """Main integration test function"""
    print("🚀 Starting Phase 2.2 Integration Test")
    print("=" * 60)
    
    # Create temporary directory for test outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"📁 Using temporary directory: {temp_path}")
        
        # Test 1: Configuration Management
        print("\n1️⃣ Testing Configuration Management...")
        config_success = test_configuration_management(temp_path)
        
        # Test 2: Logging System
        print("\n2️⃣ Testing Logging System...")
        logging_success = test_logging_system(temp_path)
        
        # Test 3: Error Handling
        print("\n3️⃣ Testing Error Handling...")
        error_handling_success = test_error_handling()
        
        # Test 4: Data Validation
        print("\n4️⃣ Testing Data Validation...")
        validation_success = test_data_validation(temp_path)
        
        # Test 5: Component Integration
        print("\n5️⃣ Testing Component Integration...")
        integration_success = test_component_integration(temp_path)
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Configuration Management", config_success),
            ("Logging System", logging_success),
            ("Error Handling", error_handling_success),
            ("Data Validation", validation_success),
            ("Component Integration", integration_success)
        ]
        
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests PASSED! Phase 2.2 is ready.")
            return True
        else:
            print("⚠️  Some tests FAILED. Please review the issues above.")
            return False

def test_configuration_management(temp_path: Path) -> bool:
    """Test configuration management functionality"""
    try:
        # Initialize ConfigManager
        config_manager = ConfigManager()
        
        # Load default configuration
        config = config_manager.load_config()
        print(f"   ✓ Default config loaded: {config.environment}")
        
        # Update configuration
        updates = {
            'environment': 'integration_test',
            'files': {
                'upload_directory': str(temp_path / 'uploads')
            }
        }
        config_manager.update_config(updates)
        updated_config = config_manager.get_config()
        print(f"   ✓ Config updated: {updated_config.environment}")
        
        # Save configuration
        output_file = temp_path / "test_config.yaml"
        config_manager.save_config(output_file)
        print(f"   ✓ Config saved to: {output_file}")
        
        # Create environment template
        env_template = config_manager.get_environment_template()
        print(f"   ✓ Environment template generated ({len(env_template)} characters)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_logging_system(temp_path: Path) -> bool:
    """Test logging system functionality"""
    try:
        # Setup logging configuration
        log_file = temp_path / "test.log"
        logging_config = {
            'level': 'DEBUG',
            'file_path': str(log_file),
            'file_enabled': True,
            'console_enabled': True,
            'rotation_enabled': True
        }
        
        # Initialize LoggingManager
        logging_manager = LoggingManager(logging_config)
        success = logging_manager.initialize()
        if not success:
            print("   ❌ Failed to initialize logging manager")
            return False
        print("   ✓ Logging manager initialized")
        
        # Get logger and test basic logging
        logger = logging_manager.get_logger('integration_test')
        logger.info("Integration test log message")
        logger.debug("Debug message for testing")
        logger.warning("Warning message for testing")
        print("   ✓ Basic logging tested")
        
        # Test performance logging
        perf_logger = logging_manager.get_performance_logger()
        perf_logger.log_operation_start('test_op', 'Integration Test Operation')
        time.sleep(0.1)  # Simulate work
        perf_logger.log_operation_end('test_op', success=True)
        print("   ✓ Performance logging tested")
        
        # Test performance monitor decorator
        @performance_monitor('test_function')
        def test_function():
            time.sleep(0.05)
            return "test_result"
        
        result = test_function()
        print(f"   ✓ Performance monitor decorator tested: {result}")
        
        # Check if log file was created
        if log_file.exists():
            print(f"   ✓ Log file created: {log_file}")
        
        # Get statistics
        stats = logging_manager.get_log_statistics()
        print(f"   ✓ Logging statistics: {stats['initialized']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Logging test failed: {e}")
        return False

def test_error_handling() -> bool:
    """Test error handling functionality"""
    try:
        # Initialize ErrorHandler
        error_handler = ErrorHandler()
        print("   ✓ Error handler initialized")
        
        # Test handling ValidationError
        try:
            raise ValidationError(
                "Test validation error",
                field_name="test_field",
                user_message="User-friendly error message"
            )
        except ValidationError as e:
            context = error_handler.handle_error(e)
            print(f"   ✓ ValidationError handled: {context.severity}")
        
        # Test handling generic exception
        try:
            raise ValueError("Test generic error")
        except ValueError as e:
            context = error_handler.handle_error(e)
            print(f"   ✓ Generic error handled: {context.category}")
        
        # Test custom error handler registration
        def custom_handler(error):
            return None  # Use default handling
        
        error_handler.register_handler(KeyError, custom_handler)
        print("   ✓ Custom error handler registered")
        
        # Get error statistics
        stats = error_handler.get_error_statistics()
        print(f"   ✓ Error statistics: {stats['total_errors']} total errors")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

def test_data_validation(temp_path: Path) -> bool:
    """Test data validation functionality"""
    try:
        # Initialize DataValidator
        validator = DataValidator()
        print("   ✓ Data validator initialized")
        
        # Test dictionary validation
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
        if result.is_valid:
            print("   ✓ Dictionary validation passed")
        else:
            print(f"   ❌ Dictionary validation failed: {result.errors}")
            return False
        
        # Test file validation
        test_file = temp_path / "test_file.txt"
        test_file.write_text("Test file content for validation")
        
        file_config = {
            'max_file_size_mb': 1,
            'allowed_extensions': ['.txt'],
            'enable_security_checks': False
        }
        
        file_result = validator.validate_file_upload(test_file, file_config)
        if file_result.is_valid:
            print("   ✓ File validation passed")
        else:
            print(f"   ❌ File validation failed: {file_result.errors}")
            return False
        
        # Test configuration validation
        config_data = {
            'environment': 'test',
            'files': {'max_file_size_mb': 50},
            'logging': {'level': 'INFO'}
        }
        
        config_result = validator.validate_configuration(config_data)
        print(f"   ✓ Configuration validation: {config_result.is_valid}")
        
        # Test content validation
        content = "This is test content with sufficient length for validation."
        content_result = validator.validate_document_content(content)
        if content_result.is_valid:
            print("   ✓ Content validation passed")
        else:
            print(f"   ❌ Content validation failed: {content_result.errors}")
            return False
        
        # Test input sanitization
        unsafe_input = "test<script>alert('xss')</script>input"
        safe_input = validator.sanitize_input(unsafe_input, 'text')
        print(f"   ✓ Input sanitization: '{unsafe_input}' -> '{safe_input}'")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data validation test failed: {e}")
        return False

def test_component_integration(temp_path: Path) -> bool:
    """Test integration between all components"""
    try:
        print("   🔄 Testing full component integration...")
        
        # 1. Setup configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 2. Initialize logging with config
        log_file = temp_path / "integration.log"
        logging_config = {
            'level': config.logging.level,
            'file_path': str(log_file),
            'file_enabled': True
        }
        
        logging_manager = LoggingManager(logging_config)
        logging_manager.initialize()
        logger = logging_manager.get_logger('integration')
        
        # 3. Initialize error handler
        error_handler = ErrorHandler()
        
        # 4. Initialize validator
        validator = DataValidator()
        
        print("   ✓ All components initialized")
        
        # 5. Simulate realistic workflow
        @performance_monitor('integration_workflow')
        def integration_workflow():
            # Log workflow start
            logger.info("Starting integration workflow")
            
            # Validate some data
            test_data = {
                'document_name': 'test_document.txt',
                'content_length': 1500,
                'upload_time': '2025-01-22T09:30:00Z'
            }
            
            schema = {
                'document_name': ['required'],
                'content_length': ['required', 'positive'],
                'upload_time': ['required']
            }
            
            validation_result = validator.validate_dict(test_data, schema)
            
            if not validation_result.is_valid:
                # Simulate error handling
                try:
                    raise ValidationError(
                        "Workflow validation failed",
                        details={'errors': validation_result.errors}
                    )
                except ValidationError as e:
                    error_context = error_handler.handle_error(e)
                    logger.error(f"Validation error: {error_context.message}")
                    return False
            
            logger.info("Workflow validation passed")
            
            # Simulate file processing
            test_file = temp_path / "workflow_test.txt"
            test_file.write_text("Integration test file content")
            
            file_result = validator.validate_file_upload(
                test_file,
                config.files.__dict__
            )
            
            if file_result.is_valid:
                logger.info(f"File validation passed: {test_file.name}")
            else:
                logger.warning(f"File validation issues: {file_result.errors}")
            
            return True
        
        # Run workflow
        workflow_success = integration_workflow()
        
        if workflow_success:
            print("   ✓ Integration workflow completed successfully")
        else:
            print("   ❌ Integration workflow failed")
            return False
        
        # 6. Verify all components recorded activity
        
        # Check log file
        if log_file.exists() and log_file.stat().st_size > 0:
            print("   ✓ Logging system recorded activity")
        else:
            print("   ❌ No log activity recorded")
            return False
        
        # Check error statistics
        error_stats = error_handler.get_error_statistics()
        print(f"   ✓ Error handler statistics available: {error_stats}")
        
        # Check performance data
        perf_logger = logging_manager.get_performance_logger()
        perf_stats = perf_logger.get_operation_stats()
        print(f"   ✓ Performance data collected: {perf_stats}")
        
        print("   🎯 Full integration test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set up environment
    print("🔧 Setting up test environment...")
    
    # Ensure we can import the modules
    try:
        from core.config_manager import ConfigManager
        print("✓ Core modules importable")
    except ImportError as e:
        print(f"❌ Cannot import core modules: {e}")
        print("Please ensure the src directory is in your Python path")
        sys.exit(1)
    
    # Run integration tests
    success = main()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    print(f"\n🏁 Integration test completed with exit code: {exit_code}")
    sys.exit(exit_code)
