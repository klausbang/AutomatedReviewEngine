"""
PDF Document Processor

This module handles PDF document reading, text extraction, and structure analysis
for the Automated Review Engine.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import PyPDF2
import pdfplumber
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class PDFSection:
    """Represents a section found in a PDF document"""
    title: str
    content: str
    page_number: int
    position: Dict[str, float]  # x, y coordinates
    level: int  # heading level (1-6)

@dataclass
class PDFTable:
    """Represents a table found in a PDF document"""
    page_number: int
    position: Dict[str, float]
    headers: List[str]
    rows: List[List[str]]
    
@dataclass
class PDFProcessingResult:
    """Result of PDF processing"""
    success: bool
    content: str
    sections: List[PDFSection]
    tables: List[PDFTable]
    metadata: Dict[str, Any]
    page_count: int
    error_message: Optional[str] = None

class PDFProcessor:
    """
    PDF document processor for extracting text and structure from PDF files.
    
    Uses both PyPDF2 and pdfplumber for comprehensive PDF processing:
    - PyPDF2 for basic text extraction and metadata
    - pdfplumber for advanced text extraction and table detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PDF processor with configuration.
        
        Args:
            config: Configuration dictionary with processing options
        """
        self.config = config or {}
        self.max_file_size_mb = self.config.get('max_file_size_mb', 50)
        self.extract_tables = self.config.get('extract_tables', True)
        self.extract_sections = self.config.get('extract_sections', True)
        
    def process_pdf(self, file_path: Path) -> PDFProcessingResult:
        """
        Process a PDF file and extract content, structure, and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PDFProcessingResult with extracted content and structure
        """
        try:
            # Validate file
            validation_result = self._validate_file(file_path)
            if not validation_result['valid']:
                return PDFProcessingResult(
                    success=False,
                    content="",
                    sections=[],
                    tables=[],
                    metadata={},
                    page_count=0,
                    error_message=validation_result['error']
                )
            
            # Extract content using both processors
            pypdf_result = self._extract_with_pypdf2(file_path)
            pdfplumber_result = self._extract_with_pdfplumber(file_path)
            
            # Combine results
            content = pdfplumber_result.get('content', '') or pypdf_result.get('content', '')
            sections = pdfplumber_result.get('sections', [])
            tables = pdfplumber_result.get('tables', [])
            metadata = pypdf_result.get('metadata', {})
            page_count = pypdf_result.get('page_count', 0)
            
            # Extract sections if enabled
            if self.extract_sections and not sections:
                sections = self._extract_sections(content)
            
            return PDFProcessingResult(
                success=True,
                content=content,
                sections=sections,
                tables=tables,
                metadata=metadata,
                page_count=page_count
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return PDFProcessingResult(
                success=False,
                content="",
                sections=[],
                tables=[],
                metadata={},
                page_count=0,
                error_message=f"Processing error: {str(e)}"
            )
    
    def process_pdf_from_bytes(self, pdf_bytes: bytes, filename: str = "uploaded.pdf") -> PDFProcessingResult:
        """
        Process PDF from bytes (useful for uploaded files).
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename for reference
            
        Returns:
            PDFProcessingResult with extracted content and structure
        """
        try:
            # Validate file size
            file_size_mb = len(pdf_bytes) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return PDFProcessingResult(
                    success=False,
                    content="",
                    sections=[],
                    tables=[],
                    metadata={},
                    page_count=0,
                    error_message=f"File too large: {file_size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB"
                )
            
            # Process using both methods
            pypdf_result = self._extract_with_pypdf2_bytes(pdf_bytes)
            pdfplumber_result = self._extract_with_pdfplumber_bytes(pdf_bytes)
            
            # Combine results
            content = pdfplumber_result.get('content', '') or pypdf_result.get('content', '')
            sections = pdfplumber_result.get('sections', [])
            tables = pdfplumber_result.get('tables', [])
            metadata = pypdf_result.get('metadata', {})
            metadata['filename'] = filename
            page_count = pypdf_result.get('page_count', 0)
            
            # Extract sections if needed
            if self.extract_sections and not sections:
                sections = self._extract_sections(content)
            
            return PDFProcessingResult(
                success=True,
                content=content,
                sections=sections,
                tables=tables,
                metadata=metadata,
                page_count=page_count
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF bytes for {filename}: {str(e)}")
            return PDFProcessingResult(
                success=False,
                content="",
                sections=[],
                tables=[],
                metadata={},
                page_count=0,
                error_message=f"Processing error: {str(e)}"
            )
    
    def _validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate PDF file before processing"""
        try:
            if not file_path.exists():
                return {'valid': False, 'error': 'File does not exist'}
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {'valid': False, 'error': f'File too large: {file_size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB'}
            
            # Check file extension
            if file_path.suffix.lower() != '.pdf':
                return {'valid': False, 'error': 'File is not a PDF'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Extract content using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {}
                if reader.metadata:
                    metadata = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'producer': reader.metadata.get('/Producer', ''),
                        'creation_date': reader.metadata.get('/CreationDate', ''),
                        'modification_date': reader.metadata.get('/ModDate', '')
                    }
                
                # Extract text from all pages
                content = ""
                page_count = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            content += f"\n--- Page {page_num + 1} ---\n"
                            content += page_text
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                
                return {
                    'content': content,
                    'metadata': metadata,
                    'page_count': page_count
                }
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            return {'content': '', 'metadata': {}, 'page_count': 0}
    
    def _extract_with_pypdf2_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract content using PyPDF2 from bytes"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                    'modification_date': reader.metadata.get('/ModDate', '')
                }
            
            # Extract text
            content = ""
            page_count = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        content += f"\n--- Page {page_num + 1} ---\n"
                        content += page_text
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
            
            return {
                'content': content,
                'metadata': metadata,
                'page_count': page_count
            }
            
        except Exception as e:
            logger.error(f"PyPDF2 bytes extraction failed: {str(e)}")
            return {'content': '', 'metadata': {}, 'page_count': 0}
    
    def _extract_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Extract content using pdfplumber (better for tables and layout)"""
        try:
            with pdfplumber.open(file_path) as pdf:
                content = ""
                tables = []
                sections = []
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        content += f"\n--- Page {page_num + 1} ---\n"
                        content += page_text
                    
                    # Extract tables if enabled
                    if self.extract_tables:
                        page_tables = page.extract_tables()
                        for table_data in page_tables:
                            if table_data and len(table_data) > 0:
                                headers = table_data[0] if table_data[0] else []
                                rows = table_data[1:] if len(table_data) > 1 else []
                                
                                table = PDFTable(
                                    page_number=page_num + 1,
                                    position={'x': 0, 'y': 0},  # Could be enhanced with actual coordinates
                                    headers=headers,
                                    rows=rows
                                )
                                tables.append(table)
                
                return {
                    'content': content,
                    'tables': tables,
                    'sections': sections
                }
                
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return {'content': '', 'tables': [], 'sections': []}
    
    def _extract_with_pdfplumber_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract content using pdfplumber from bytes"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            with pdfplumber.open(pdf_file) as pdf:
                content = ""
                tables = []
                sections = []
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        content += f"\n--- Page {page_num + 1} ---\n"
                        content += page_text
                    
                    # Extract tables if enabled
                    if self.extract_tables:
                        page_tables = page.extract_tables()
                        for table_data in page_tables:
                            if table_data and len(table_data) > 0:
                                headers = table_data[0] if table_data[0] else []
                                rows = table_data[1:] if len(table_data) > 1 else []
                                
                                table = PDFTable(
                                    page_number=page_num + 1,
                                    position={'x': 0, 'y': 0},
                                    headers=headers,
                                    rows=rows
                                )
                                tables.append(table)
                
                return {
                    'content': content,
                    'tables': tables,
                    'sections': sections
                }
                
        except Exception as e:
            logger.error(f"pdfplumber bytes extraction failed: {str(e)}")
            return {'content': '', 'tables': [], 'sections': []}
    
    def _extract_sections(self, content: str) -> List[PDFSection]:
        """Extract sections from text content based on patterns"""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Simple section detection (can be enhanced)
            # Look for numbered sections, capitalized headers, etc.
            if self._is_section_header(line):
                # Save previous section
                if current_section:
                    section = PDFSection(
                        title=current_section,
                        content='\n'.join(current_content),
                        page_number=1,  # Would need enhancement to track actual page
                        position={'x': 0, 'y': line_num},
                        level=self._get_section_level(current_section)
                    )
                    sections.append(section)
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add last section
        if current_section:
            section = PDFSection(
                title=current_section,
                content='\n'.join(current_content),
                page_number=1,
                position={'x': 0, 'y': len(lines)},
                level=self._get_section_level(current_section)
            )
            sections.append(section)
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if a line is likely a section header"""
        line = line.strip()
        
        # Check for numbered sections (1., 2., etc.)
        if line and line[0].isdigit() and '.' in line[:5]:
            return True
        
        # Check for all caps headers
        if line.isupper() and len(line) > 3 and len(line) < 100:
            return True
        
        # Check for specific regulatory document patterns
        regulatory_headers = [
            'PRODUCT IDENTIFICATION',
            'REGULATORY CLASSIFICATION',
            'CONFORMITY ASSESSMENT',
            'APPLIED STANDARDS',
            'AUTHORIZED REPRESENTATIVE',
            'DECLARATION STATEMENT'
        ]
        
        if line.upper() in regulatory_headers:
            return True
        
        return False
    
    def _get_section_level(self, header: str) -> int:
        """Determine the level of a section header"""
        if header.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            if '.' in header[2:5]:  # Sub-section like 1.1, 1.2
                return 2
            return 1
        
        if header.isupper():
            return 1
        
        return 2
