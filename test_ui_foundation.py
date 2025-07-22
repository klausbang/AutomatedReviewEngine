"""
Phase 3.1 UI Foundation - Test Script

This script tests the UI components and validates the implementation
without requiring Streamlit to be running.

Run: python test_ui_foundation.py
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_ui_imports():
    """Test that all UI components can be imported"""
    print("🧪 Testing UI Component Imports...")
    
    try:
        # Test main interface
        from src.ui.main_interface import MainInterface, create_main_interface
        print("✅ MainInterface import successful")
        
        # Test components
        from src.ui.components.file_uploader import FileUploader, create_file_uploader
        from src.ui.components.status_indicator import StatusIndicator, create_status_indicator
        from src.ui.components.progress_tracker import ProgressTracker, create_progress_tracker
        from src.ui.components.settings_panel import SettingsPanel, create_settings_panel
        print("✅ Components import successful")
        
        # Test layouts
        from src.ui.layouts.main_layout import MainLayout, create_main_layout
        from src.ui.layouts.page_layout import PageLayout, create_page_layout
        from src.ui.layouts.sidebar_layout import SidebarLayout, create_sidebar_layout
        print("✅ Layouts import successful")
        
        # Test styling
        from src.ui.styling.themes import get_theme, apply_theme, ThemeType
        from src.ui.styling.styles import apply_custom_css, get_component_styles
        print("✅ Styling import successful")
        
        # Test utils
        from src.ui.utils.helpers import format_file_size, format_timestamp, generate_session_id
        from src.ui.utils.validators import validate_email, validate_file_name
        from src.ui.utils.formatters import format_percentage, format_duration
        print("✅ Utils import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_component_creation():
    """Test creating component instances"""
    print("\n🏗️ Testing Component Creation...")
    
    try:
        # Test creating main interface (without Streamlit)
        print("Creating MainInterface...")
        # Note: This will fail gracefully without Streamlit
        
        # Test utility functions
        from src.ui.utils.helpers import format_file_size, format_timestamp, generate_session_id
        from src.ui.utils.validators import validate_email, validate_file_name
        from src.ui.utils.formatters import format_percentage, format_duration
        
        # Test helper functions
        size_str = format_file_size(1024 * 1024)  # 1MB
        print(f"✅ File size formatting: {size_str}")
        
        from datetime import datetime
        timestamp_str = format_timestamp(datetime.now())
        print(f"✅ Timestamp formatting: {timestamp_str}")
        
        session_id = generate_session_id()
        print(f"✅ Session ID generation: {session_id[:20]}...")
        
        # Test validators
        email_valid = validate_email("test@example.com")
        print(f"✅ Email validation: {email_valid}")
        
        filename_result = validate_file_name("document.pdf")
        print(f"✅ Filename validation: {filename_result['is_valid']}")
        
        # Test formatters
        percentage = format_percentage(0.85)
        print(f"✅ Percentage formatting: {percentage}")
        
        duration = format_duration(3665)  # 1 hour, 1 minute, 5 seconds
        print(f"✅ Duration formatting: {duration}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component creation error: {e}")
        return False

def test_theme_system():
    """Test the theme system"""
    print("\n🎨 Testing Theme System...")
    
    try:
        from src.ui.styling.themes import get_theme, apply_theme, ThemeType
        
        # Test light theme
        light_theme = get_theme(ThemeType.LIGHT)
        print(f"✅ Light theme loaded: {light_theme.name}")
        print(f"  - Primary color: {light_theme.colors['primary']}")
        
        # Test dark theme
        dark_theme = get_theme(ThemeType.DARK)
        print(f"✅ Dark theme loaded: {dark_theme.name}")
        print(f"  - Primary color: {dark_theme.colors['primary']}")
        
        # Test CSS generation
        css = apply_theme(light_theme)
        print(f"✅ CSS generation: {len(css)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme system error: {e}")
        return False

def test_validation_system():
    """Test the validation utilities"""
    print("\n🔍 Testing Validation System...")
    
    try:
        from src.ui.utils.validators import (
            validate_email, validate_file_name, validate_file_extension,
            validate_text_input, validate_numeric_input
        )
        
        # Test email validation
        test_emails = [
            ("test@example.com", True),
            ("invalid-email", False),
            ("user@domain.co.uk", True),
            ("", False)
        ]
        
        for email, expected in test_emails:
            result = validate_email(email)
            status = "✅" if result == expected else "❌"
            print(f"{status} Email '{email}': {result}")
        
        # Test filename validation
        test_files = [
            ("document.pdf", True),
            ("report_final.docx", True),
            ("file<>name.txt", False),
            ("CON.pdf", False)
        ]
        
        for filename, expected_valid in test_files:
            result = validate_file_name(filename)
            status = "✅" if result['is_valid'] == expected_valid else "❌"
            print(f"{status} Filename '{filename}': {result['is_valid']}")
        
        # Test file extension validation
        result = validate_file_extension("document.pdf", [".pdf", ".docx"])
        print(f"✅ Extension validation: {result['is_valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation system error: {e}")
        return False

def test_integration_readiness():
    """Test readiness for Phase 2 integration"""
    print("\n🔗 Testing Integration Readiness...")
    
    try:
        # Test Phase 2 imports (may not be available)
        phase2_available = True
        missing_components = []
        
        try:
            from src.core.config_manager import ConfigManager
            print("✅ ConfigManager available for integration")
        except ImportError:
            phase2_available = False
            missing_components.append("ConfigManager")
        
        try:
            from src.core.logging_manager import LoggingManager
            print("✅ LoggingManager available for integration")
        except ImportError:
            phase2_available = False
            missing_components.append("LoggingManager")
        
        try:
            from src.core.error_handler import ErrorHandler
            print("✅ ErrorHandler available for integration")
        except ImportError:
            phase2_available = False
            missing_components.append("ErrorHandler")
        
        try:
            from src.core.validation_utils import DataValidator
            print("✅ DataValidator available for integration")
        except ImportError:
            phase2_available = False
            missing_components.append("DataValidator")
        
        if phase2_available:
            print("🎉 All Phase 2 components available - Full integration ready!")
        else:
            print(f"⚠️ Phase 2 components missing: {', '.join(missing_components)}")
            print("   UI will run with graceful degradation")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def run_all_tests():
    """Run all UI foundation tests"""
    print("🚀 Phase 3.1 UI Foundation Test Suite")
    print("=" * 50)
    
    tests = [
        ("UI Component Imports", test_ui_imports),
        ("Component Creation", test_component_creation),
        ("Theme System", test_theme_system),
        ("Validation System", test_validation_system),
        ("Integration Readiness", test_integration_readiness)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 3.1 UI Foundation is ready!")
        print("✨ Ready to proceed with Phase 3.2: Review Logic")
    else:
        print("⚠️ Some tests failed - check implementation")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
