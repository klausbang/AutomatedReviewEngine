"""
Basic Application Tests

Test suite for the main application functionality.
"""

def test_app_imports():
    """Test that the main app module can be imported"""
    try:
        import sys
        from pathlib import Path
        
        # Add src to path for testing
        project_root = Path(__file__).parent.parent
        src_path = project_root / "src"
        sys.path.insert(0, str(src_path))
        
        # Test basic imports
        import src
        assert hasattr(src, '__version__')
        
    except ImportError as e:
        assert False, f"Failed to import required modules: {e}"

def test_project_structure():
    """Test that the project structure is correctly set up"""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (project_root / "src").exists()
    assert (project_root / "config").exists()
    assert (project_root / "data").exists()
    assert (project_root / "tests").exists()
    
    # Check main files exist
    assert (project_root / "app.py").exists()
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "README.md").exists()

def test_config_files():
    """Test that configuration files are present"""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config"
    
    assert (config_dir / "config.yaml").exists()
    assert (config_dir / "env.template").exists()
