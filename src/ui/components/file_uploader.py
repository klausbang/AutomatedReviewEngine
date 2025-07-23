"""
File Uploader Component - Automated Review Engine

Advanced file upload component with validation, security checks,
and integration with the Phase 2 validation system.

Phase 3.1: UI Foundation - File Upload Component
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tempfile
import hashlib
from datetime import datetime
import mimetypes

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import core components
try:
    from src.core.validation_utils import DataValidator
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
    # Import Phase 3.2 document analyzer for compatibility checking
    from src.review.document_analyzer import DocumentAnalyzer
    DOCUMENT_ANALYZER_AVAILABLE = True
except ImportError:
    DataValidator = None
    LoggingManager = None
    ErrorHandler = None
    DocumentAnalyzer = None
    DOCUMENT_ANALYZER_AVAILABLE = False


class FileUploader:
    """Advanced file uploader component with validation"""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 logger: Optional[Any] = None,
                 validator: Optional[Any] = None):
        """
        Initialize the file uploader
        
        Args:
            config: Upload configuration settings
            logger: Logger instance
            validator: Data validator instance
        """
        self.config = config or self._get_default_config()
        self.logger = logger
        self.validator = validator
        
        # Initialize session state for file tracking
        self._initialize_session_state()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default upload configuration"""
        return {
            'max_file_size_mb': 50,
            'allowed_extensions': ['.pdf', '.docx', '.doc'],
            'max_files': 10,
            'enable_virus_scan': True,
            'enable_hash_validation': True,
            'enable_metadata_extraction': True,
            'upload_directory': 'uploads',
            'allowed_mime_types': [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword'
            ]
        }
    
    def _initialize_session_state(self):
        """Initialize session state for file tracking"""
        if 'file_upload_history' not in st.session_state:
            st.session_state.file_upload_history = []
        
        if 'upload_stats' not in st.session_state:
            st.session_state.upload_stats = {
                'total_uploads': 0,
                'successful_uploads': 0,
                'failed_uploads': 0,
                'total_size_bytes': 0
            }
    
    def render_upload_interface(self, key_suffix: str = "") -> Optional[Dict[str, Any]]:
        """
        Render the main file upload interface
        
        Args:
            key_suffix: Suffix for Streamlit component keys
            
        Returns:
            Dict containing upload result information or None
        """
        st.markdown("### 📤 Document Upload")
        
        # Upload configuration display
        with st.expander("⚙️ Upload Settings", expanded=False):
            self._render_upload_settings(key_suffix)
        
        # File uploader widget
        uploaded_files = st.file_uploader(
            label="Choose documents for review",
            type=[ext.lstrip('.') for ext in self.config['allowed_extensions']],
            accept_multiple_files=True,
            key=f"file_uploader_{key_suffix}",
            help=f"Max {self.config['max_files']} files, {self.config['max_file_size_mb']}MB each"
        )
        
        if uploaded_files:
            return self._process_uploaded_files(uploaded_files, key_suffix)
        
        # Display upload history and stats
        self._render_upload_history(key_suffix)
        
        return None
    
    def _render_upload_settings(self, key_suffix: str):
        """Render upload configuration settings"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**File Restrictions:**")
            st.write(f"• Max size: {self.config['max_file_size_mb']} MB")
            st.write(f"• Max files: {self.config['max_files']}")
            st.write(f"• Extensions: {', '.join(self.config['allowed_extensions'])}")
        
        with col2:
            st.markdown("**Security Features:**")
            st.write(f"• Virus scan: {'✅' if self.config['enable_virus_scan'] else '❌'}")
            st.write(f"• Hash validation: {'✅' if self.config['enable_hash_validation'] else '❌'}")
            st.write(f"• Metadata extraction: {'✅' if self.config['enable_metadata_extraction'] else '❌'}")
    
    def _process_uploaded_files(self, uploaded_files: List[Any], key_suffix: str) -> Dict[str, Any]:
        """
        Process and validate uploaded files
        
        Args:
            uploaded_files: List of Streamlit uploaded file objects
            key_suffix: Key suffix for components
            
        Returns:
            Dict containing processing results
        """
        results = {
            'successful_files': [],
            'failed_files': [],
            'total_processed': len(uploaded_files),
            'processing_time': datetime.now()
        }
        
        # Display processing progress
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Processing Files")
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (idx + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {uploaded_file.name} ({idx + 1}/{len(uploaded_files)})")
            
            # Process individual file
            file_result = self._process_single_file(uploaded_file, key_suffix)
            
            if file_result['success']:
                results['successful_files'].append(file_result)
                st.session_state.upload_stats['successful_uploads'] += 1
            else:
                results['failed_files'].append(file_result)
                st.session_state.upload_stats['failed_uploads'] += 1
            
            st.session_state.upload_stats['total_uploads'] += 1
            st.session_state.upload_stats['total_size_bytes'] += uploaded_file.size
        
        # Clear progress indicators
        progress_container.empty()
        
        # Display results
        self._display_processing_results(results, key_suffix)
        
        return results
    
    def _process_single_file(self, uploaded_file: Any, key_suffix: str) -> Dict[str, Any]:
        """
        Process and validate a single uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            key_suffix: Key suffix for components
            
        Returns:
            Dict containing file processing result
        """
        file_info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'success': False,
            'errors': [],
            'warnings': [],
            'metadata': {},
            'hash': None,
            'upload_time': datetime.now()
        }
        
        try:
            # Basic validation
            validation_errors = self._validate_file_basic(uploaded_file)
            if validation_errors:
                file_info['errors'].extend(validation_errors)
                return file_info
            
            # Create temporary file for advanced validation
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = Path(tmp_file.name)
            
            # Advanced validation using Phase 2 validator
            if self.validator:
                validation_result = self.validator.validate_file_upload(tmp_path, self.config)
                
                if not validation_result.is_valid:
                    file_info['errors'].extend(validation_result.errors)
                    return file_info
                
                file_info['warnings'].extend(validation_result.warnings)
            
            # Phase 3.2 DocumentAnalyzer compatibility check
            if DOCUMENT_ANALYZER_AVAILABLE:
                analyzer_result = self._validate_document_analyzer_compatibility(tmp_path)
                if not analyzer_result['compatible']:
                    file_info['errors'].extend(analyzer_result['errors'])
                    return file_info
                
                if analyzer_result['warnings']:
                    file_info['warnings'].extend(analyzer_result['warnings'])
                
                # Add analyzer metadata
                file_info['analyzer_metadata'] = analyzer_result['metadata']
            
            # Generate file hash
            if self.config['enable_hash_validation']:
                file_info['hash'] = self._generate_file_hash(tmp_path)
            
            # Extract metadata
            if self.config['enable_metadata_extraction']:
                file_info['metadata'] = self._extract_file_metadata(tmp_path, uploaded_file)
            
            # Security scan simulation
            if self.config['enable_virus_scan']:
                scan_result = self._simulate_virus_scan(tmp_path)
                if not scan_result['clean']:
                    file_info['errors'].append(f"Security scan failed: {scan_result['reason']}")
                    return file_info
            
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)
            
            file_info['success'] = True
            
            # Add to upload history
            st.session_state.file_upload_history.append(file_info.copy())
            
        except Exception as e:
            file_info['errors'].append(f"Processing error: {str(e)}")
            if self.logger:
                self.logger.error(f"File processing error for {uploaded_file.name}: {e}")
        
        return file_info
    
    def _validate_file_basic(self, uploaded_file: Any) -> List[str]:
        """
        Perform basic file validation
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check file size
        max_size_bytes = self.config['max_file_size_mb'] * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            errors.append(f"File size ({uploaded_file.size:,} bytes) exceeds maximum ({max_size_bytes:,} bytes)")
        
        # Check file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in self.config['allowed_extensions']:
            errors.append(f"File extension '{file_ext}' not allowed. Allowed: {', '.join(self.config['allowed_extensions'])}")
        
        # Check MIME type
        if uploaded_file.type and uploaded_file.type not in self.config['allowed_mime_types']:
            errors.append(f"MIME type '{uploaded_file.type}' not allowed")
        
        # Check filename
        if not uploaded_file.name or len(uploaded_file.name.strip()) == 0:
            errors.append("Invalid filename")
        
        return errors
    
    def _generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _extract_file_metadata(self, file_path: Path, uploaded_file: Any) -> Dict[str, Any]:
        """Extract file metadata"""
        metadata = {
            'original_name': uploaded_file.name,
            'file_size': uploaded_file.size,
            'mime_type': uploaded_file.type,
            'file_extension': file_path.suffix,
            'creation_time': datetime.now().isoformat()
        }
        
        # Add MIME type detection
        detected_mime, _ = mimetypes.guess_type(str(file_path))
        if detected_mime:
            metadata['detected_mime_type'] = detected_mime
        
        return metadata
    
    def _simulate_virus_scan(self, file_path: Path) -> Dict[str, Any]:
        """Simulate virus scanning (placeholder for real implementation)"""
        # In a real implementation, this would integrate with antivirus software
        # For now, simulate a scan based on file properties
        
        file_size = file_path.stat().st_size
        
        # Simulate scan based on file size (very large files flagged as suspicious)
        if file_size > 100 * 1024 * 1024:  # 100MB
            return {
                'clean': False,
                'reason': 'File size exceeds security threshold'
            }
        
        return {
            'clean': True,
            'reason': 'No threats detected'
        }
    
    def _display_processing_results(self, results: Dict[str, Any], key_suffix: str):
        """Display file processing results"""
        st.markdown("### 📊 Upload Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", results['total_processed'])
        
        with col2:
            st.metric("Successful", len(results['successful_files']), 
                     delta=f"{len(results['successful_files'])}/{results['total_processed']}")
        
        with col3:
            st.metric("Failed", len(results['failed_files']),
                     delta=f"{len(results['failed_files'])}/{results['total_processed']}")
        
        # Successful files
        if results['successful_files']:
            st.success(f"✅ {len(results['successful_files'])} files uploaded successfully")
            
            with st.expander("📋 Successful Uploads", expanded=True):
                for file_info in results['successful_files']:
                    col1, col2, col3 = st.columns([3, 1, 2])
                    
                    with col1:
                        st.write(f"📄 **{file_info['name']}**")
                    
                    with col2:
                        st.write(f"{file_info['size']:,} bytes")
                    
                    with col3:
                        if file_info['hash']:
                            st.code(file_info['hash'][:16] + "...", language=None)
        
        # Failed files
        if results['failed_files']:
            st.error(f"❌ {len(results['failed_files'])} files failed to upload")
            
            with st.expander("🚨 Failed Uploads", expanded=True):
                for file_info in results['failed_files']:
                    st.write(f"📄 **{file_info['name']}**")
                    for error in file_info['errors']:
                        st.write(f"  ❌ {error}")
    
    def _render_upload_history(self, key_suffix: str):
        """Render upload history and statistics"""
        if st.session_state.file_upload_history:
            st.markdown("### 📚 Upload History")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Uploads", st.session_state.upload_stats['total_uploads'])
            
            with col2:
                st.metric("Successful", st.session_state.upload_stats['successful_uploads'])
            
            with col3:
                st.metric("Failed", st.session_state.upload_stats['failed_uploads'])
            
            with col4:
                total_mb = st.session_state.upload_stats['total_size_bytes'] / (1024 * 1024)
                st.metric("Total Size", f"{total_mb:.1f} MB")
            
            # Recent uploads
            with st.expander("📋 Recent Uploads", expanded=False):
                for file_info in reversed(st.session_state.file_upload_history[-10:]):
                    status_icon = "✅" if file_info['success'] else "❌"
                    st.write(f"{status_icon} **{file_info['name']}** - {file_info['upload_time'].strftime('%H:%M:%S')}")
    
    def clear_upload_history(self):
        """Clear upload history and reset statistics"""
        st.session_state.file_upload_history = []
        st.session_state.upload_stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_size_bytes': 0
        }
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get current upload statistics"""
        return st.session_state.upload_stats.copy()
    
    def render_compact_uploader(self, key_suffix: str = "") -> Optional[Dict[str, Any]]:
        """Render a compact version of the file uploader"""
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=[ext.lstrip('.') for ext in self.config['allowed_extensions']],
            key=f"compact_uploader_{key_suffix}",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            return self._process_single_file(uploaded_file, key_suffix)
        
        return None
    
    def _validate_document_analyzer_compatibility(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate file compatibility with DocumentAnalyzer from Phase 3.2
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dict with compatibility results
        """
        result = {
            'compatible': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        try:
            # Test DocumentAnalyzer initialization
            analyzer = DocumentAnalyzer()
            
            # Test file reading capability
            test_result = analyzer.analyze_document(str(file_path))
            
            if not test_result:
                result['compatible'] = False
                result['errors'].append("Document cannot be processed by the review engine")
                return result
            
            # Check if analysis was successful
            if not test_result.success:
                result['compatible'] = False
                result['errors'].append(f"Document analysis failed: {test_result.error_message or 'Unknown error'}")
                return result
            
            # Extract metadata from analysis
            result['metadata'] = {
                'document_type': test_result.document_type,
                'page_count': getattr(test_result.metadata, 'page_count', 'Unknown'),
                'extraction_method': getattr(test_result, 'extraction_method', 'Standard'),
                'text_extracted': bool(test_result.text_content),
                'text_length': len(test_result.text_content) if test_result.text_content else 0
            }
            
            # Add warnings for potential issues
            if test_result.extraction_errors:
                result['warnings'].extend([
                    f"Text extraction issue: {error}" for error in test_result.extraction_errors[:3]
                ])
            
            # Check text quality
            if test_result.text_content:
                text_length = len(test_result.text_content.strip())
                if text_length < 100:
                    result['warnings'].append("Document contains very little extractable text")
                elif text_length > 1000000:  # 1MB of text
                    result['warnings'].append("Document is very large and may take longer to process")
            else:
                result['warnings'].append("No text content could be extracted from document")
            
        except Exception as e:
            result['compatible'] = False
            result['errors'].append(f"DocumentAnalyzer compatibility check failed: {str(e)}")
        
        return result


# Factory function
def create_file_uploader(config: Optional[Dict[str, Any]] = None,
                        logger: Optional[Any] = None,
                        validator: Optional[Any] = None) -> FileUploader:
    """Create and return a FileUploader instance"""
    return FileUploader(config=config, logger=logger, validator=validator)
