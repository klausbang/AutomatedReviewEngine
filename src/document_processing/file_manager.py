"""
File Upload and Management System

This module handles file uploads, storage, and management for the
Automated Review Engine.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import uuid
import json

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class UploadedFile:
    """Represents an uploaded file"""
    id: str
    original_filename: str
    stored_filename: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    storage_path: Path
    metadata: Dict[str, Any]

@dataclass
class UploadResult:
    """Result of file upload operation"""
    success: bool
    file_info: Optional[UploadedFile]
    error_message: Optional[str] = None

class FileManager:
    """
    File upload and management system for the Automated Review Engine.
    
    Handles:
    - File uploads with validation
    - Secure file storage
    - File metadata management
    - Temporary file cleanup
    """
    
    def __init__(self, base_directory: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize file manager.
        
        Args:
            base_directory: Base directory for file storage
            config: Configuration dictionary
        """
        self.base_directory = Path(base_directory)
        self.config = config or {}
        
        # Configuration
        self.max_file_size_mb = self.config.get('max_file_size_mb', 50)
        self.allowed_extensions = self.config.get('allowed_extensions', ['.pdf', '.docx'])
        self.cleanup_temp_files = self.config.get('cleanup_temp_files', True)
        
        # Storage directories
        self.uploads_dir = self.base_directory / "uploads"
        self.documents_dir = self.uploads_dir / "documents"
        self.templates_dir = self.uploads_dir / "templates"
        self.scripts_dir = self.uploads_dir / "scripts"
        self.temp_dir = self.base_directory / "temp"
        self.metadata_dir = self.uploads_dir / "metadata"
        
        # Create directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary storage directories"""
        directories = [
            self.uploads_dir,
            self.documents_dir,
            self.templates_dir,
            self.scripts_dir,
            self.temp_dir,
            self.metadata_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def upload_document(self, file_content: bytes, filename: str, 
                       file_type: str = "document") -> UploadResult:
        """
        Upload a document file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            file_type: Type of file (document, template, script)
            
        Returns:
            UploadResult with upload status and file information
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Validate file
            validation_result = self._validate_upload(file_content, filename)
            if not validation_result['valid']:
                return UploadResult(
                    success=False,
                    file_info=None,
                    error_message=validation_result['error']
                )
            
            # Determine storage directory
            storage_dir = self._get_storage_directory(file_type)
            
            # Generate stored filename
            file_extension = Path(filename).suffix
            stored_filename = f"{file_id}{file_extension}"
            storage_path = storage_dir / stored_filename
            
            # Save file
            with open(storage_path, 'wb') as f:
                f.write(file_content)
            
            # Create file metadata
            upload_timestamp = datetime.now()
            file_info = UploadedFile(
                id=file_id,
                original_filename=filename,
                stored_filename=stored_filename,
                file_type=file_type,
                file_size=len(file_content),
                upload_timestamp=upload_timestamp,
                storage_path=storage_path,
                metadata={
                    'mime_type': validation_result.get('mime_type', ''),
                    'upload_session': self._get_session_id()
                }
            )
            
            # Save metadata
            self._save_file_metadata(file_info)
            
            logger.info(f"File uploaded successfully: {filename} -> {stored_filename}")
            
            return UploadResult(
                success=True,
                file_info=file_info
            )
            
        except Exception as e:
            logger.error(f"Upload error for {filename}: {str(e)}")
            return UploadResult(
                success=False,
                file_info=None,
                error_message=f"Upload failed: {str(e)}"
            )
    
    def upload_from_path(self, file_path: Path, file_type: str = "document") -> UploadResult:
        """
        Upload a file from local path.
        
        Args:
            file_path: Path to the file
            file_type: Type of file (document, template, script)
            
        Returns:
            UploadResult with upload status and file information
        """
        try:
            if not file_path.exists():
                return UploadResult(
                    success=False,
                    file_info=None,
                    error_message="File does not exist"
                )
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            return self.upload_document(file_content, file_path.name, file_type)
            
        except Exception as e:
            logger.error(f"Upload from path error for {file_path}: {str(e)}")
            return UploadResult(
                success=False,
                file_info=None,
                error_message=f"Upload failed: {str(e)}"
            )
    
    def get_file(self, file_id: str) -> Optional[UploadedFile]:
        """
        Get file information by ID.
        
        Args:
            file_id: File identifier
            
        Returns:
            UploadedFile if found, None otherwise
        """
        try:
            metadata_path = self.metadata_dir / f"{file_id}.json"
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return UploadedFile(
                id=metadata['id'],
                original_filename=metadata['original_filename'],
                stored_filename=metadata['stored_filename'],
                file_type=metadata['file_type'],
                file_size=metadata['file_size'],
                upload_timestamp=datetime.fromisoformat(metadata['upload_timestamp']),
                storage_path=Path(metadata['storage_path']),
                metadata=metadata.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {str(e)}")
            return None
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Get file content by ID.
        
        Args:
            file_id: File identifier
            
        Returns:
            File content as bytes if found, None otherwise
        """
        try:
            file_info = self.get_file(file_id)
            if not file_info:
                return None
            
            if not file_info.storage_path.exists():
                logger.warning(f"File not found on disk: {file_info.storage_path}")
                return None
            
            with open(file_info.storage_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading file content {file_id}: {str(e)}")
            return None
    
    def list_files(self, file_type: Optional[str] = None) -> List[UploadedFile]:
        """
        List uploaded files.
        
        Args:
            file_type: Filter by file type (optional)
            
        Returns:
            List of UploadedFile objects
        """
        files = []
        
        try:
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Filter by file type if specified
                    if file_type and metadata.get('file_type') != file_type:
                        continue
                    
                    file_info = UploadedFile(
                        id=metadata['id'],
                        original_filename=metadata['original_filename'],
                        stored_filename=metadata['stored_filename'],
                        file_type=metadata['file_type'],
                        file_size=metadata['file_size'],
                        upload_timestamp=datetime.fromisoformat(metadata['upload_timestamp']),
                        storage_path=Path(metadata['storage_path']),
                        metadata=metadata.get('metadata', {})
                    )
                    files.append(file_info)
                    
                except Exception as e:
                    logger.warning(f"Could not load metadata from {metadata_file}: {str(e)}")
                    continue
            
            # Sort by upload timestamp (newest first)
            files.sort(key=lambda x: x.upload_timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
        
        return files
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file and its metadata.
        
        Args:
            file_id: File identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_info = self.get_file(file_id)
            if not file_info:
                logger.warning(f"File not found: {file_id}")
                return False
            
            # Delete actual file
            if file_info.storage_path.exists():
                file_info.storage_path.unlink()
                logger.debug(f"Deleted file: {file_info.storage_path}")
            
            # Delete metadata
            metadata_path = self.metadata_dir / f"{file_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()
                logger.debug(f"Deleted metadata: {metadata_path}")
            
            logger.info(f"File deleted successfully: {file_info.original_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for temporary files
        """
        try:
            if not self.cleanup_temp_files:
                return
            
            current_time = datetime.now()
            deleted_count = 0
            
            for temp_file in self.temp_dir.glob("*"):
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    age_hours = (current_time - file_mtime).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        if temp_file.is_file():
                            temp_file.unlink()
                        elif temp_file.is_dir():
                            shutil.rmtree(temp_file)
                        deleted_count += 1
                        logger.debug(f"Deleted old temp file: {temp_file}")
                        
                except Exception as e:
                    logger.warning(f"Could not delete temp file {temp_file}: {str(e)}")
                    continue
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} temporary files")
                
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {str(e)}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0.0,
            'by_type': {},
            'storage_directories': {
                'documents': str(self.documents_dir),
                'templates': str(self.templates_dir),
                'scripts': str(self.scripts_dir),
                'temp': str(self.temp_dir)
            }
        }
        
        try:
            files = self.list_files()
            stats['total_files'] = len(files)
            
            for file_info in files:
                # Count by type
                file_type = file_info.file_type
                if file_type not in stats['by_type']:
                    stats['by_type'][file_type] = {'count': 0, 'size_mb': 0.0}
                
                stats['by_type'][file_type]['count'] += 1
                file_size_mb = file_info.file_size / (1024 * 1024)
                stats['by_type'][file_type]['size_mb'] += file_size_mb
                stats['total_size_mb'] += file_size_mb
            
        except Exception as e:
            logger.error(f"Error calculating storage stats: {str(e)}")
        
        return stats
    
    def _validate_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        try:
            # File size check
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {
                    'valid': False,
                    'error': f'File too large: {file_size_mb:.1f}MB exceeds limit of {self.max_file_size_mb}MB'
                }
            
            # Empty file check
            if len(file_content) == 0:
                return {'valid': False, 'error': 'File is empty'}
            
            # File extension check
            file_extension = Path(filename).suffix.lower()
            if file_extension not in self.allowed_extensions:
                return {
                    'valid': False,
                    'error': f'File type not allowed: {file_extension}. Allowed: {", ".join(self.allowed_extensions)}'
                }
            
            # Basic file signature check
            mime_type = self._detect_mime_type(file_content, filename)
            
            return {
                'valid': True,
                'mime_type': mime_type
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _detect_mime_type(self, file_content: bytes, filename: str) -> str:
        """Detect MIME type from file content"""
        try:
            # Check file signatures (magic bytes)
            if file_content.startswith(b'%PDF'):
                return 'application/pdf'
            elif file_content.startswith(b'PK\x03\x04') or file_content.startswith(b'PK\x05\x06'):
                # ZIP-based format (could be DOCX)
                return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
            # Fallback to extension-based detection
            extension = Path(filename).suffix.lower()
            extension_mappings = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword'
            }
            
            return extension_mappings.get(extension, 'application/octet-stream')
            
        except Exception:
            return 'application/octet-stream'
    
    def _get_storage_directory(self, file_type: str) -> Path:
        """Get storage directory for file type"""
        directory_mapping = {
            'document': self.documents_dir,
            'template': self.templates_dir,
            'script': self.scripts_dir
        }
        
        return directory_mapping.get(file_type, self.documents_dir)
    
    def _save_file_metadata(self, file_info: UploadedFile):
        """Save file metadata to JSON"""
        metadata_path = self.metadata_dir / f"{file_info.id}.json"
        
        metadata = {
            'id': file_info.id,
            'original_filename': file_info.original_filename,
            'stored_filename': file_info.stored_filename,
            'file_type': file_info.file_type,
            'file_size': file_info.file_size,
            'upload_timestamp': file_info.upload_timestamp.isoformat(),
            'storage_path': str(file_info.storage_path),
            'metadata': file_info.metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _get_session_id(self) -> str:
        """Get current session ID (placeholder for future session management)"""
        return "default_session"
