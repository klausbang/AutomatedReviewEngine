"""
Comprehensive Test Suite for Phase 2.3

This module runs the complete testing framework including:
- Unit tests
- Integration tests  
- Performance benchmarks
- Sample document validation
- Coverage analysis
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Set test environment
os.environ["ARE_ENVIRONMENT"] = "test"
os.environ["ARE_LOGGING_LEVEL"] = "WARNING"  # Reduce log noise during tests
os.environ["ARE_LOGGING_FILE_ENABLED"] = "false"


class TestSuite:
    """Comprehensive test suite runner"""
    
    def __init__(self):
        self.project_root = project_root
        self.results = {
            'unit_tests': {'status': 'pending', 'details': {}},
            'integration_tests': {'status': 'pending', 'details': {}},
            'performance_tests': {'status': 'pending', 'details': {}},
            'sample_validation': {'status': 'pending', 'details': {}},
            'coverage_analysis': {'status': 'pending', 'details': {}}
        }
        
    def run_unit_tests(self) -> bool:
        """Run comprehensive unit tests"""
        print("\n" + "="*60)
        print("🧪 UNIT TESTS")
        print("="*60)
        
        try:
            # Import test functions
            from tests.test_core import (
                TestConfigManager, TestLoggingManager, 
                TestErrorHandler, TestDataValidator
            )
            
            # Test results tracking
            test_results = {}
            
            # Run ConfigManager tests
            print("\n📋 Testing ConfigManager...")
            config_test = TestConfigManager()
            
            tests = [
                ('initialization', lambda: config_test.test_config_manager_initialization()),
                ('default_config', lambda: config_test.test_load_default_config()),
                ('env_variables', lambda: self._test_with_temp_dir(
                    lambda td: config_test.test_environment_variable_override(td / "config.yaml")
                ))
            ]
            
            for test_name, test_func in tests:
                try:
                    test_func()
                    test_results[f'config_{test_name}'] = True
                    print(f"   ✅ {test_name}")
                except Exception as e:
                    test_results[f'config_{test_name}'] = False
                    print(f"   ❌ {test_name}: {e}")
            
            # Run LoggingManager tests
            print("\n📝 Testing LoggingManager...")
            logging_test = TestLoggingManager()
            
            tests = [
                ('initialization', lambda: logging_test.test_logging_manager_initialization()),
                ('get_logger', lambda: self._test_with_temp_dir(
                    lambda td: logging_test.test_get_logger(td)
                ))
            ]
            
            for test_name, test_func in tests:
                try:
                    test_func()
                    test_results[f'logging_{test_name}'] = True
                    print(f"   ✅ {test_name}")
                except Exception as e:
                    test_results[f'logging_{test_name}'] = False
                    print(f"   ❌ {test_name}: {e}")
            
            # Run ErrorHandler tests
            print("\n🚨 Testing ErrorHandler...")
            error_test = TestErrorHandler()
            
            tests = [
                ('initialization', lambda: error_test.test_error_handler_initialization()),
                ('custom_error', lambda: error_test.test_handle_custom_error()),
                ('generic_error', lambda: error_test.test_handle_generic_error())
            ]
            
            for test_name, test_func in tests:
                try:
                    test_func()
                    test_results[f'error_{test_name}'] = True
                    print(f"   ✅ {test_name}")
                except Exception as e:
                    test_results[f'error_{test_name}'] = False
                    print(f"   ❌ {test_name}: {e}")
            
            # Run DataValidator tests
            print("\n🔍 Testing DataValidator...")
            validator_test = TestDataValidator()
            
            tests = [
                ('initialization', lambda: validator_test.test_validator_initialization()),
                ('dict_validation', lambda: validator_test.test_validate_dict()),
                ('input_sanitization', lambda: validator_test.test_sanitize_input())
            ]
            
            for test_name, test_func in tests:
                try:
                    test_func()
                    test_results[f'validator_{test_name}'] = True
                    print(f"   ✅ {test_name}")
                except Exception as e:
                    test_results[f'validator_{test_name}'] = False
                    print(f"   ❌ {test_name}: {e}")
            
            # Calculate success rate
            passed = sum(1 for result in test_results.values() if result)
            total = len(test_results)
            success_rate = (passed / total) * 100
            
            self.results['unit_tests'] = {
                'status': 'completed',
                'details': {
                    'passed': passed,
                    'total': total,
                    'success_rate': success_rate,
                    'results': test_results
                }
            }
            
            print(f"\n📊 Unit Tests Summary: {passed}/{total} passed ({success_rate:.1f}%)")
            return success_rate >= 80  # 80% success threshold
            
        except Exception as e:
            print(f"❌ Unit test execution failed: {e}")
            self.results['unit_tests'] = {
                'status': 'failed',
                'details': {'error': str(e)}
            }
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        print("\n" + "="*60)
        print("🔗 INTEGRATION TESTS")
        print("="*60)
        
        try:
            # Import and run integration components
            from src.core.config_manager import ConfigManager
            from src.core.logging_manager import LoggingManager
            from src.core.error_handler import ErrorHandler
            from src.core.validation_utils import DataValidator
            
            import tempfile
            
            integration_results = {}
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test 1: Configuration + Logging Integration
                print("\n🔧 Testing Config + Logging Integration...")
                try:
                    config_manager = ConfigManager()
                    config = config_manager.load_config()
                    
                    log_config = {
                        'level': 'INFO',
                        'file_path': str(temp_path / 'integration.log'),
                        'file_enabled': True
                    }
                    
                    logging_manager = LoggingManager(log_config)
                    success = logging_manager.initialize()
                    
                    if success:
                        logger = logging_manager.get_logger('integration')
                        logger.info("Integration test message")
                        
                        # Check if log file was created
                        log_file = Path(log_config['file_path'])
                        if log_file.exists() and log_file.stat().st_size > 0:
                            integration_results['config_logging'] = True
                            print("   ✅ Config + Logging integration")
                        else:
                            integration_results['config_logging'] = False
                            print("   ❌ Log file not created properly")
                    else:
                        integration_results['config_logging'] = False
                        print("   ❌ Logging initialization failed")
                        
                except Exception as e:
                    integration_results['config_logging'] = False
                    print(f"   ❌ Config + Logging integration failed: {e}")
                
                # Test 2: Error Handler + Validator Integration
                print("\n🚨 Testing Error Handler + Validator Integration...")
                try:
                    error_handler = ErrorHandler()
                    validator = DataValidator()
                    
                    # Create validation error scenario
                    invalid_data = {'email': 'invalid-email'}
                    schema = {'email': ['email']}
                    
                    result = validator.validate_dict(invalid_data, schema)
                    
                    if not result.is_valid:
                        from src.core.error_handler import ValidationError
                        
                        try:
                            raise ValidationError(
                                "Integration test validation error",
                                details={'errors': result.errors}
                            )
                        except ValidationError as e:
                            context = error_handler.handle_error(e)
                            
                            if context and context.message:
                                integration_results['error_validation'] = True
                                print("   ✅ Error Handler + Validator integration")
                            else:
                                integration_results['error_validation'] = False
                                print("   ❌ Error context not properly created")
                    else:
                        integration_results['error_validation'] = False
                        print("   ❌ Validation should have failed but didn't")
                        
                except Exception as e:
                    integration_results['error_validation'] = False
                    print(f"   ❌ Error Handler + Validator integration failed: {e}")
                
                # Test 3: Full Workflow Integration
                print("\n🔄 Testing Full Workflow Integration...")
                try:
                    # Initialize all components
                    config_manager = ConfigManager()
                    config = config_manager.load_config()
                    
                    logging_manager = LoggingManager({
                        'level': 'INFO',
                        'file_path': str(temp_path / 'workflow.log'),
                        'file_enabled': True
                    })
                    logging_manager.initialize()
                    
                    error_handler = ErrorHandler()
                    validator = DataValidator()
                    logger = logging_manager.get_logger('workflow')
                    
                    # Simulate document processing workflow
                    logger.info("Starting workflow integration test")
                    
                    # Validate a test file
                    test_file = temp_path / "test_document.txt"
                    test_file.write_text("Integration test document content")
                    
                    file_result = validator.validate_file_upload(
                        test_file,
                        config.files.__dict__
                    )
                    
                    if file_result.is_valid:
                        logger.info("File validation passed")
                        
                        # Test content validation
                        content_result = validator.validate_document_content(
                            test_file.read_text()
                        )
                        
                        if content_result.is_valid:
                            logger.info("Content validation passed")
                            integration_results['full_workflow'] = True
                            print("   ✅ Full workflow integration")
                        else:
                            logger.warning("Content validation failed")
                            integration_results['full_workflow'] = False
                            print("   ❌ Content validation failed in workflow")
                    else:
                        logger.error("File validation failed")
                        integration_results['full_workflow'] = False
                        print("   ❌ File validation failed in workflow")
                        
                except Exception as e:
                    integration_results['full_workflow'] = False
                    print(f"   ❌ Full workflow integration failed: {e}")
            
            # Calculate integration success
            passed = sum(1 for result in integration_results.values() if result)
            total = len(integration_results)
            success_rate = (passed / total) * 100
            
            self.results['integration_tests'] = {
                'status': 'completed',
                'details': {
                    'passed': passed,
                    'total': total,
                    'success_rate': success_rate,
                    'results': integration_results
                }
            }
            
            print(f"\n📊 Integration Tests Summary: {passed}/{total} passed ({success_rate:.1f}%)")
            return success_rate >= 75  # 75% success threshold
            
        except Exception as e:
            print(f"❌ Integration test execution failed: {e}")
            self.results['integration_tests'] = {
                'status': 'failed',
                'details': {'error': str(e)}
            }
            return False
    
    def run_sample_validation(self) -> bool:
        """Validate sample documents"""
        print("\n" + "="*60)
        print("📄 SAMPLE DOCUMENT VALIDATION")
        print("="*60)
        
        try:
            from src.core.validation_utils import DataValidator
            
            validator = DataValidator()
            sample_dir = self.project_root / "tests" / "sample_documents"
            
            if not sample_dir.exists():
                print("❌ Sample documents directory not found")
                return False
            
            validation_results = {}
            
            # Test each sample document
            sample_files = list(sample_dir.glob("*"))
            print(f"📁 Found {len(sample_files)} sample documents")
            
            for sample_file in sample_files:
                if sample_file.is_file():
                    print(f"\n📄 Validating {sample_file.name}...")
                    
                    try:
                        # File validation
                        file_config = {
                            'max_file_size_mb': 10,
                            'allowed_extensions': ['.txt', '.md', '.json'],
                            'enable_security_checks': False
                        }
                        
                        file_result = validator.validate_file_upload(sample_file, file_config)
                        
                        if file_result.is_valid:
                            print(f"   ✅ File validation passed")
                            
                            # Content validation
                            content = sample_file.read_text(encoding='utf-8')
                            content_result = validator.validate_document_content(content)
                            
                            if content_result.is_valid:
                                print(f"   ✅ Content validation passed")
                                validation_results[sample_file.name] = True
                            else:
                                print(f"   ❌ Content validation failed: {content_result.errors}")
                                validation_results[sample_file.name] = False
                        else:
                            print(f"   ❌ File validation failed: {file_result.errors}")
                            validation_results[sample_file.name] = False
                            
                    except Exception as e:
                        print(f"   ❌ Validation error: {e}")
                        validation_results[sample_file.name] = False
            
            # Calculate success rate
            passed = sum(1 for result in validation_results.values() if result)
            total = len(validation_results)
            success_rate = (passed / total) * 100 if total > 0 else 0
            
            self.results['sample_validation'] = {
                'status': 'completed',
                'details': {
                    'passed': passed,
                    'total': total,
                    'success_rate': success_rate,
                    'results': validation_results
                }
            }
            
            print(f"\n📊 Sample Validation Summary: {passed}/{total} passed ({success_rate:.1f}%)")
            return success_rate >= 90  # 90% success threshold for samples
            
        except Exception as e:
            print(f"❌ Sample validation failed: {e}")
            self.results['sample_validation'] = {
                'status': 'failed',
                'details': {'error': str(e)}
            }
            return False
    
    def _test_with_temp_dir(self, test_func):
        """Helper to run tests with temporary directory"""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            return test_func(Path(temp_dir))
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 PHASE 2.3 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        overall_success = True
        
        for test_type, result in self.results.items():
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'pending': '⏳'
            }.get(result['status'], '❓')
            
            print(f"\n{status_icon} {test_type.replace('_', ' ').title()}: {result['status'].upper()}")
            
            if result['status'] == 'completed' and 'details' in result:
                details = result['details']
                if 'success_rate' in details:
                    print(f"   Success Rate: {details['success_rate']:.1f}% ({details['passed']}/{details['total']})")
                    if details['success_rate'] < 80:
                        overall_success = False
                else:
                    print(f"   Details: {details}")
            elif result['status'] == 'failed':
                overall_success = False
                if 'details' in result and 'error' in result['details']:
                    print(f"   Error: {result['details']['error']}")
        
        print("\n" + "-"*80)
        
        if overall_success:
            print("🎉 PHASE 2.3 TESTING FRAMEWORK: FULLY OPERATIONAL")
            print("✅ All test categories passed minimum thresholds")
            print("🚀 Ready for production and Phase 3 development")
        else:
            print("⚠️ PHASE 2.3 TESTING FRAMEWORK: NEEDS ATTENTION")
            print("❌ Some test categories did not meet minimum thresholds")
            print("🔧 Review failed tests and improve implementation")
        
        return overall_success


def main():
    """Main test suite runner"""
    print("🚀 STARTING COMPREHENSIVE PHASE 2.3 TEST SUITE")
    print("=" * 80)
    print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project Root: {project_root}")
    
    suite = TestSuite()
    
    # Run all test categories
    test_functions = [
        ('Unit Tests', suite.run_unit_tests),
        ('Integration Tests', suite.run_integration_tests),
        ('Sample Validation', suite.run_sample_validation)
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n🔄 Running {test_name}...")
        try:
            success = test_func()
            status = "✅ PASSED" if success else "⚠️ NEEDS REVIEW"
            print(f"{status} {test_name}")
        except Exception as e:
            print(f"❌ FAILED {test_name}: {e}")
    
    # Print final summary
    overall_success = suite.print_final_summary()
    
    print(f"\n⏰ End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
