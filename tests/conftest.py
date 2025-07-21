"""
Test Configuration and Utilities

This module contains common test utilities and configuration
for the Automated Review Engine test suite.
"""

import pytest
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

# Sample file paths
SAMPLE_PDF_PATH = TEST_DATA_DIR / "sample_document.pdf"
SAMPLE_DOCX_PATH = TEST_DATA_DIR / "sample_document.docx"
SAMPLE_TEMPLATE_PATH = TEST_DATA_DIR / "sample_template.docx"

@pytest.fixture
def test_data_dir():
    """Fixture to provide test data directory path"""
    return TEST_DATA_DIR

@pytest.fixture
def sample_config():
    """Fixture to provide sample configuration for testing"""
    return {
        "app": {
            "name": "ARE Test",
            "version": "test",
            "debug": True
        },
        "document_processing": {
            "max_file_size_mb": 10,
            "supported_formats": ["pdf", "docx"]
        }
    }
