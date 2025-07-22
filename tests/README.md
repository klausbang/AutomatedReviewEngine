# Testing Framework - Phase 2.3

This directory contains the comprehensive testing framework for the Automated Review Engine, implementing Phase 2.3 of the development roadmap.

## 📁 Directory Structure

```
tests/
├── README.md                 # This file - testing documentation
├── pytest.ini              # Pytest configuration
├── integration_test.py      # Integration test script
├── test_core.py            # Core module unit tests
├── sample_documents/        # Test documents
│   ├── sample_text.txt     # Plain text document
│   ├── sample_markdown.md  # Markdown document
│   └── sample_json.json    # JSON document
└── coverage_html/          # Coverage reports (generated)
```

## 🧪 Test Categories

### Unit Tests (`test_core.py`)
Comprehensive unit tests for all core infrastructure components:

- **ConfigManager Tests**: Configuration loading, updating, saving, environment variables
- **LoggingManager Tests**: Logging initialization, performance monitoring, statistics
- **ErrorHandler Tests**: Custom error handling, classification, recovery suggestions
- **DataValidator Tests**: File validation, content validation, input sanitization
- **Integration Tests**: Component interaction and workflow testing

### Integration Tests (`integration_test.py`)
End-to-end testing of component integration:

1. **Configuration Management**: Load, update, and save configurations
2. **Logging System**: Initialize logging, performance monitoring, file output
3. **Error Handling**: Exception handling, custom error types, statistics
4. **Data Validation**: File, content, and configuration validation
5. **Component Integration**: Full workflow simulation

### Sample Documents
Test documents for various file format processing:

- **sample_text.txt**: Plain text with various content types
- **sample_markdown.md**: Markdown with formatting, code blocks, tables
- **sample_json.json**: JSON with nested structures, edge cases, validation data

## 🚀 Running Tests

### Prerequisites
```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-timeout

# Optional: Install parallel testing
pip install pytest-xdist
```

### Run All Tests
```bash
# From project root directory
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_core.py

# Integration tests only
python tests/integration_test.py

# Specific test class
pytest tests/test_core.py::TestConfigManager

# Specific test method
pytest tests/test_core.py::TestConfigManager::test_config_manager_initialization
```

### Run Tests with Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run core module tests
pytest -m core

# Run validation tests
pytest -m validation
```

## 📊 Test Coverage

The testing framework provides comprehensive coverage analysis:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage in terminal
pytest --cov=src --cov-report=term-missing

# Generate XML coverage for CI/CD
pytest --cov=src --cov-report=xml
```

Coverage reports are generated in:
- **HTML**: `tests/coverage_html/index.html`
- **XML**: `tests/coverage.xml`

## 🔍 Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Coverage reporting
- Logging configuration
- Timeout settings
- Custom markers

### Environment Variables
Tests can be configured using environment variables:

```bash
# Set test environment
export ARE_ENVIRONMENT=test

# Configure test logging
export ARE_LOGGING_LEVEL=DEBUG
export ARE_LOGGING_FILE_ENABLED=false

# Test file limits
export ARE_FILES_MAX_FILE_SIZE_MB=10
```

## 🎯 Test Markers

Custom markers for organizing tests:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.core`: Core module tests
- `@pytest.mark.config`: Configuration tests
- `@pytest.mark.logging`: Logging tests
- `@pytest.mark.validation`: Validation tests
- `@pytest.mark.error_handling`: Error handling tests

## 🛠️ Adding New Tests

### Test File Structure
```python
"""
Test module for [component name]
"""

import pytest
from unittest.mock import Mock, patch
from [component] import [ClassToTest]

class Test[ComponentName]:
    """Test suite for [ComponentName]"""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture for test data"""
        return {"key": "value"}
    
    def test_[functionality](self, sample_data):
        """Test [specific functionality]"""
        # Arrange
        component = ClassToTest()
        
        # Act
        result = component.method(sample_data)
        
        # Assert
        assert result.is_valid == True
```

### Best Practices
1. **Use descriptive test names**: `test_validate_file_upload_with_valid_extension`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures for setup**: Shared test data and temporary resources
4. **Mock external dependencies**: File system, network, time
5. **Test edge cases**: Empty inputs, invalid data, boundary conditions
6. **Add markers**: Categorize tests appropriately

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure project structure is correct
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   
   # Or run from project root
   python -m pytest tests/
   ```

2. **Permission Errors**
   ```bash
   # Ensure test directories are writable
   chmod 755 tests/
   ```

3. **Coverage Issues**
   ```bash
   # Install coverage dependencies
   pip install pytest-cov
   
   # Check coverage configuration in pytest.ini
   ```

4. **Timeout Issues**
   ```bash
   # Increase timeout in pytest.ini
   timeout = 600  # 10 minutes
   ```

### Debug Tests
```bash
# Run with debug output
pytest tests/ -s -vv

# Run single test with debugging
pytest tests/test_core.py::TestConfigManager::test_config_manager_initialization -s -vv

# Enable logging during tests
pytest tests/ --log-cli-level=DEBUG
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 🎉 Phase 2.3 Completion Criteria

The testing framework is considered complete when:

- ✅ All unit tests pass (100% success rate)
- ✅ Integration tests pass (all 5 components working together)
- ✅ Code coverage > 90% for core modules
- ✅ All sample documents process without errors
- ✅ Performance benchmarks meet requirements
- ✅ Error handling covers all exception types
- ✅ Configuration validation works for all scenarios

## 📞 Support

For testing-related questions or issues:

1. Check the troubleshooting section above
2. Review test output and error messages
3. Ensure all dependencies are installed
4. Verify project structure and file permissions

---

**Phase 2.3 Testing Framework** - Comprehensive testing infrastructure for the Automated Review Engine core components.
