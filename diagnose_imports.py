#!/usr/bin/env python3
"""
Diagnostic script to check component imports
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== Import Diagnostic ===")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries
print()

# Test core imports
try:
    print("Testing core imports...")
    from src.core.config_manager import ConfigManager
    print("✅ ConfigManager imported successfully")
except ImportError as e:
    print(f"❌ ConfigManager import failed: {e}")

try:
    from src.core.logging_manager import LoggingManager
    print("✅ LoggingManager imported successfully")
except ImportError as e:
    print(f"❌ LoggingManager import failed: {e}")

try:
    from src.core.error_handler import ErrorHandler
    print("✅ ErrorHandler imported successfully")
except ImportError as e:
    print(f"❌ ErrorHandler import failed: {e}")

try:
    from src.core.validation_utils import DataValidator
    print("✅ DataValidator imported successfully")
except ImportError as e:
    print(f"❌ DataValidator import failed: {e}")

print()
print("Testing UI component imports...")

# Test UI component imports
components = [
    "review_panel",
    "progress_display", 
    "results_panel",
    "config_panel",
    "file_uploader",
    "performance_monitor"
]

for component in components:
    try:
        module = __import__(f"src.ui.components.{component}", fromlist=[f"create_{component}"])
        create_func = getattr(module, f"create_{component}")
        print(f"✅ {component} imported successfully")
    except ImportError as e:
        print(f"❌ {component} import failed: {e}")
    except AttributeError as e:
        print(f"❌ {component} create function missing: {e}")

print()
print("=== Diagnostic Complete ===")
