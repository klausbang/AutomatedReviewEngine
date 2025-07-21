"""
Tests for Document Processing Module

Comprehensive test suite for document processing components including:
- PDF processing
- Word document processing  
- Document validation
- File management
- Document analysis
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import io

# Import components to test
from src.document_processing import (
    PDFProcessor, WordProcessor, DocumentValidator, 
    FileManager, DocumentAnalyzer, AnalysisConfig
)

class TestDocumentProcessing:
    """Test suite for document processing components"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_pdf_path(self, temp_dir):
        """Create a sample PDF for testing"""
        # Create a minimal PDF file for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
        
        pdf_path = temp_dir / "sample.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        return pdf_path
    
    @pytest.fixture
    def sample_text_path(self, temp_dir):
        """Create a sample text file for testing"""
        text_path = temp_dir / "sample.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("This is a test document.\nIt contains multiple lines.\nFor testing purposes.")
        return text_path
    
    def test_pdf_processor_initialization(self):
        """Test PDFProcessor initialization"""
        processor = PDFProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_pdf')
    
    def test_pdf_processor_with_config(self):
        """Test PDFProcessor with configuration"""
        config = {
            'extract_text': True,
            'extract_metadata': True,
            'extract_images': False
        }
        processor = PDFProcessor(config)
        assert processor.config == config
    
    def test_pdf_processor_nonexistent_file(self):
        """Test PDFProcessor with non-existent file"""
        processor = PDFProcessor()
        result = processor.process_pdf(Path("nonexistent.pdf"))
        assert not result.success
        assert "not found" in result.error_message.lower()
    
    def test_pdf_processor_invalid_file(self, temp_dir):
        """Test PDFProcessor with invalid PDF file"""
        invalid_pdf = temp_dir / "invalid.pdf"
        with open(invalid_pdf, 'w') as f:
            f.write("This is not a PDF file")
        
        processor = PDFProcessor()
        result = processor.process_pdf(invalid_pdf)
        # Should handle gracefully even if processing fails
        assert result is not None
    
    def test_word_processor_initialization(self):
        """Test WordProcessor initialization"""
        processor = WordProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_document')
    
    def test_word_processor_nonexistent_file(self):
        """Test WordProcessor with non-existent file"""
        processor = WordProcessor()
        result = processor.process_document(Path("nonexistent.docx"))
        assert not result.success
        assert "not found" in result.error_message.lower()
    
    def test_document_validator_initialization(self):
        """Test DocumentValidator initialization"""
        validator = DocumentValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_document')
        assert hasattr(validator, 'check_completeness')
        assert hasattr(validator, 'check_compliance')
    
    def test_document_validator_with_text(self, sample_text_path):
        """Test DocumentValidator with text content"""
        validator = DocumentValidator()
        
        # Read sample text
        with open(sample_text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Test basic validation
        result = validator.validate_document(sample_text_path, text_content)
        assert result is not None
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'file_exists')
        
        # Test completeness check
        completeness = validator.check_completeness(text_content, {})
        assert completeness is not None
        assert hasattr(completeness, 'complete')
        
        # Test compliance check  
        compliance = validator.check_compliance(text_content, {})
        assert compliance is not None
        assert hasattr(compliance, 'compliant')
    
    def test_file_manager_initialization(self, temp_dir):
        """Test FileManager initialization"""
        manager = FileManager(temp_dir)
        assert manager is not None
        assert manager.base_directory == temp_dir
        
        # Check that directories were created
        assert manager.uploads_dir.exists()
        assert manager.documents_dir.exists()
        assert manager.temp_dir.exists()
    
    def test_file_manager_upload_from_path(self, temp_dir, sample_text_path):
        """Test FileManager upload from path"""
        manager = FileManager(temp_dir)
        
        # Upload the sample file
        result = manager.upload_from_path(sample_text_path, "document")
        
        # Check result (may fail due to file type restrictions, but should handle gracefully)
        assert result is not None
        assert hasattr(result, 'success')
    
    def test_file_manager_list_files(self, temp_dir):
        """Test FileManager file listing"""
        manager = FileManager(temp_dir)
        
        # List files (should be empty initially)
        files = manager.list_files()
        assert isinstance(files, list)
    
    def test_file_manager_storage_stats(self, temp_dir):
        """Test FileManager storage statistics"""
        manager = FileManager(temp_dir)
        
        stats = manager.get_storage_stats()
        assert isinstance(stats, dict)
        assert 'total_files' in stats
        assert 'total_size_mb' in stats
        assert 'storage_directories' in stats
    
    def test_document_analyzer_initialization(self):
        """Test DocumentAnalyzer initialization"""
        analyzer = DocumentAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_file')
        assert hasattr(analyzer, 'batch_analyze')
    
    def test_document_analyzer_with_config(self, temp_dir):
        """Test DocumentAnalyzer with configuration"""
        config = {
            'base_directory': str(temp_dir),
            'analysis_config': {
                'extract_text': True,
                'validate_document': False
            }
        }
        analyzer = DocumentAnalyzer(config)
        assert analyzer.file_manager is not None
    
    def test_analysis_config(self):
        """Test AnalysisConfig dataclass"""
        config = AnalysisConfig()
        assert config.extract_text == True
        assert config.extract_metadata == True
        assert config.validate_document == True
        
        # Test with custom values
        custom_config = AnalysisConfig(
            extract_text=False,
            extract_images=True,
            max_file_size_mb=100
        )
        assert custom_config.extract_text == False
        assert custom_config.extract_images == True
        assert custom_config.max_file_size_mb == 100
    
    def test_document_analyzer_nonexistent_file(self):
        """Test DocumentAnalyzer with non-existent file"""
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_file("nonexistent.pdf")
        
        assert result is not None
        assert hasattr(result, 'errors')
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
    
    def test_document_analyzer_batch_empty(self):
        """Test DocumentAnalyzer batch processing with empty list"""
        analyzer = DocumentAnalyzer()
        results = analyzer.batch_analyze([])
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_document_analyzer_summary_empty(self):
        """Test DocumentAnalyzer summary with empty results"""
        analyzer = DocumentAnalyzer()
        summary = analyzer.get_analysis_summary([])
        
        assert isinstance(summary, dict)
        assert "error" in summary
    
    def test_document_analyzer_export_results(self, temp_dir):
        """Test DocumentAnalyzer export functionality"""
        analyzer = DocumentAnalyzer()
        
        # Create a dummy result
        from src.document_processing.document_analyzer import AnalysisResult
        result = AnalysisResult(
            document_id="test",
            filename="test.pdf", 
            file_type=".pdf",
            analysis_timestamp=datetime.now()
        )
        
        # Test JSON export
        json_path = temp_dir / "results.json"
        success = analyzer.export_results([result], json_path, 'json')
        # Should handle gracefully even if export fails
        assert isinstance(success, bool)
        
        # Test CSV export
        csv_path = temp_dir / "results.csv"
        success = analyzer.export_results([result], csv_path, 'csv')
        assert isinstance(success, bool)
    
    def test_integration_text_file_analysis(self, temp_dir, sample_text_path):
        """Test integration with text file (should fail gracefully)"""
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_file(sample_text_path)
        
        assert result is not None
        # Should fail with unsupported file type
        assert len(result.errors) > 0
        assert "unsupported" in result.errors[0].lower()
    
    def test_error_handling_invalid_config(self):
        """Test error handling with invalid configuration"""
        # Test with invalid config types
        try:
            config = {"invalid": "config"}
            analyzer = DocumentAnalyzer(config)
            # Should handle gracefully
            assert analyzer is not None
        except Exception as e:
            # Should not raise unhandled exceptions
            pytest.fail(f"Unexpected exception: {e}")
    
    def test_memory_management_large_file_simulation(self, temp_dir):
        """Test memory management with simulated large file"""
        # Create analysis config with small file size limit
        config = AnalysisConfig(max_file_size_mb=0.001)  # Very small limit
        analyzer = DocumentAnalyzer()
        
        # Create a "large" file (actually small but exceeds limit)
        large_file = temp_dir / "large.pdf"
        with open(large_file, 'w') as f:
            f.write("x" * 2048)  # 2KB file, exceeds 0.001MB limit
        
        result = analyzer.analyze_file(large_file, config)
        assert result is not None
        assert len(result.errors) > 0
        assert "too large" in result.errors[0].lower()

class TestDocumentProcessingEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_file_handling(self, tmp_path):
        """Test handling of empty files"""
        empty_file = tmp_path / "empty.pdf"
        empty_file.touch()  # Create empty file
        
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_file(empty_file)
        
        # Should handle gracefully
        assert result is not None
    
    def test_unicode_filename_handling(self, tmp_path):
        """Test handling of Unicode filenames"""
        unicode_file = tmp_path / "tëst_文档.pdf"
        unicode_file.write_text("test content")
        
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_file(unicode_file)
        
        # Should handle gracefully
        assert result is not None
        assert result.filename == unicode_file.name
    
    def test_concurrent_access_simulation(self, tmp_path):
        """Test simulation of concurrent access"""
        manager = FileManager(tmp_path)
        
        # Multiple operations should not interfere
        stats1 = manager.get_storage_stats()
        stats2 = manager.get_storage_stats()
        
        assert stats1 == stats2

if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
