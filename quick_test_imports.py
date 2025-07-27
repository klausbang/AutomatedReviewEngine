#!/usr/bin/env python3
"""
Quick test script to check main interface import
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== Quick Import Test ===")

# Test the main interface import
try:
    print("Testing main interface import...")
    from src.ui.main_interface import MainInterface
    print("✅ MainInterface imported successfully")
    
    # Try to create instance
    print("Creating MainInterface instance...")
    app = MainInterface()
    print("✅ MainInterface instance created successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n=== Test Complete ===")
