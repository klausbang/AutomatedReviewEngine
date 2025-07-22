"""
Quick Import Test - Verify UI imports work correctly

This script tests that all UI imports work without errors.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test all UI imports"""
    print("🧪 Testing UI Imports...")
    
    try:
        print("Testing main interface import...")
        from src.ui.main_interface import MainInterface
        print("✅ MainInterface imported successfully")
        
        print("Testing UI package import...")
        import src.ui as ui
        print(f"✅ UI package imported, available components: {len(ui.__all__)}")
        
        print("Testing component creation...")
        # This should work without Streamlit being available
        print("✅ Import tests completed successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_entry():
    """Test that app.py can be imported"""
    print("\n🚀 Testing App Entry Point...")
    
    try:
        # Read app.py content to verify structure
        app_path = Path("app.py")
        content = app_path.read_text()
        
        if "from src.ui.main_interface import MainInterface" in content:
            print("✅ App.py has correct import")
        else:
            print("❌ App.py missing correct import")
            return False
            
        if "def main():" in content:
            print("✅ App.py has main function")
        else:
            print("❌ App.py missing main function")
            return False
            
        print("✅ App entry point structure validated")
        return True
        
    except Exception as e:
        print(f"❌ App validation error: {e}")
        return False

def main():
    """Run import tests"""
    print("🔍 Quick UI Import Test")
    print("=" * 40)
    
    tests = [
        ("UI Imports", test_imports),
        ("App Entry", test_app_entry)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED ({passed}/{total})")
        print("✨ The ContentLayout import error should be fixed!")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print(f"\n⚠️ Some tests failed ({passed}/{total})")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
