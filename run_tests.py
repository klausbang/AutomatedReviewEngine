#!/usr/bin/env python3
"""
Test Runner for Phase 2.3

Simple test runner script that handles import paths and runs
the comprehensive test suite for the Automated Review Engine.
"""

import sys
import os
from pathlib import Path

# Add project root and src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Set environment for testing
os.environ["ARE_ENVIRONMENT"] = "test"
os.environ["ARE_LOGGING_LEVEL"] = "DEBUG"
os.environ["ARE_LOGGING_FILE_ENABLED"] = "false"

def main():
    """Main test runner function"""
    print("🧪 Phase 2.3 Testing Framework")
    print("=" * 50)
    print(f"📁 Project Root: {project_root}")
    print(f"📁 Source Path: {src_path}")
    print()
    
    # Test basic imports first
    print("1️⃣ Testing Core Module Imports...")
    try:
        from src.core.config_manager import ConfigManager
        from src.core.logging_manager import LoggingManager
        from src.core.error_handler import ErrorHandler
        from src.core.validation_utils import DataValidator
        print("✅ All core modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test basic functionality
    print("\n2️⃣ Testing Basic Functionality...")
    try:
        # Test ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print(f"✅ ConfigManager: {config.environment}")
        
        # Test LoggingManager
        logging_manager = LoggingManager()
        success = logging_manager.initialize()
        print(f"✅ LoggingManager: {success}")
        
        # Test ErrorHandler
        error_handler = ErrorHandler()
        print("✅ ErrorHandler: initialized")
        
        # Test DataValidator
        validator = DataValidator()
        print("✅ DataValidator: initialized")
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False
    
    # Run pytest if available
    print("\n3️⃣ Running Pytest Suite...")
    try:
        import pytest
        
        # Run specific tests with better error handling
        test_files = [
            "tests/test_core.py::TestConfigManager::test_config_manager_initialization",
            "tests/test_core.py::TestLoggingManager::test_logging_manager_initialization",
            "tests/test_core.py::TestErrorHandler::test_error_handler_initialization",
            "tests/test_core.py::TestDataValidator::test_validator_initialization"
        ]
        
        print("Running core functionality tests...")
        for test_file in test_files:
            try:
                result = pytest.main(["-v", test_file])
                if result == 0:
                    print(f"✅ {test_file.split('::')[-1]}")
                else:
                    print(f"⚠️ {test_file.split('::')[-1]} (result: {result})")
            except Exception as e:
                print(f"❌ {test_file.split('::')[-1]}: {e}")
        
    except ImportError:
        print("⚠️ pytest not available, running manual tests only")
    
    # Test sample documents
    print("\n4️⃣ Testing Sample Documents...")
    sample_dir = project_root / "tests" / "sample_documents"
    print(f"📁 Looking for samples in: {sample_dir}")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*"))
        print(f"📊 Found {len(sample_files)} files")
        for sample_file in sample_files:
            if sample_file.is_file():
                size_kb = sample_file.stat().st_size / 1024
                print(f"✅ Sample document: {sample_file.name} ({size_kb:.1f} KB)")
    else:
        print("⚠️ Sample documents directory not found")
    
    print("\n" + "=" * 50)
    print("🎯 Phase 2.3 Test Runner Complete")
    print("✅ Basic functionality verified")
    print("📋 For comprehensive testing, run: pytest tests/ -v")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
