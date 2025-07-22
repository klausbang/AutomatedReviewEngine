"""
Configuration Management System

Centralized configuration management for the Automated Review Engine.
Handles application settings, environment variables, and configuration validation.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import tempfile

# Configure basic logging for this module
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "automated_review_engine"
    username: str = ""
    password: str = ""
    connection_timeout: int = 30
    pool_size: int = 5

@dataclass
class FileConfig:
    """File handling configuration"""
    upload_directory: str = "data/uploads"
    temp_directory: str = "data/temp"
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = field(default_factory=lambda: ['.pdf', '.docx'])
    cleanup_temp_files: bool = True
    temp_file_retention_hours: int = 24

@dataclass
class ProcessingConfig:
    """Document processing configuration"""
    pdf_extraction_method: str = "dual"  # "pdfplumber", "pypdf2", "dual"
    extract_images: bool = False
    extract_metadata: bool = True
    extract_structure: bool = True
    language_detection: bool = True
    ocr_enabled: bool = False
    max_processing_time_minutes: int = 10

@dataclass
class ValidationConfig:
    """Document validation configuration"""
    enable_security_checks: bool = True
    enable_content_validation: bool = True
    enable_compliance_checking: bool = True
    malware_scanning: bool = False
    max_validation_time_minutes: int = 5
    strict_mode: bool = False

@dataclass
class LoggingConfig:
    """Logging system configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/application.log"
    file_max_size_mb: int = 10
    file_backup_count: int = 5
    console_enabled: bool = True
    structured_logging: bool = False

@dataclass
class UIConfig:
    """User interface configuration"""
    streamlit_port: int = 8501
    streamlit_host: str = "localhost"
    theme: str = "default"
    page_title: str = "Automated Review Engine"
    page_icon: str = "📋"
    layout: str = "wide"
    sidebar_state: str = "expanded"

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_authentication: bool = False
    session_timeout_minutes: int = 30
    max_login_attempts: int = 3
    enable_audit_logging: bool = True
    require_https: bool = False
    cors_enabled: bool = False

@dataclass
class PerformanceConfig:
    """Performance and resource configuration"""
    max_concurrent_uploads: int = 5
    max_concurrent_processing: int = 3
    memory_limit_mb: int = 1024
    enable_caching: bool = True
    cache_directory: str = "data/cache"
    cache_expiry_hours: int = 24

@dataclass
class AppConfig:
    """Main application configuration container"""
    # Core settings
    environment: str = "development"
    debug_mode: bool = False
    version: str = "0.2.2"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    files: FileConfig = field(default_factory=FileConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """
    Configuration manager for the Automated Review Engine.
    
    Handles loading, validation, and management of application configuration
    from multiple sources including files, environment variables, and defaults.
    """
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = Path(config_file) if config_file else None
        self._config: Optional[AppConfig] = None
        self._config_loaded = False
        
        # Set up basic logging for config manager
        self._setup_basic_logging()
        
        logger.info("Configuration manager initialized")
    
    def load_config(self, config_file: Optional[Union[str, Path]] = None) -> AppConfig:
        """
        Load configuration from file and environment variables.
        
        Args:
            config_file: Optional config file path (overrides init setting)
            
        Returns:
            Loaded AppConfig instance
        """
        if config_file:
            self.config_file = Path(config_file)
        
        logger.info("Loading application configuration")
        
        # Start with default configuration
        config_dict = asdict(AppConfig())
        
        # Load from file if specified and exists
        if self.config_file and self.config_file.exists():
            file_config = self._load_config_file(self.config_file)
            config_dict = self._merge_configs(config_dict, file_config)
            logger.info(f"Loaded configuration from file: {self.config_file}")
        
        # Override with environment variables
        env_config = self._load_environment_config()
        config_dict = self._merge_configs(config_dict, env_config)
        
        # Create AppConfig instance
        self._config = self._dict_to_config(config_dict)
        
        # Validate configuration
        self._validate_config()
        
        # Create necessary directories
        self._create_directories()
        
        self._config_loaded = True
        logger.info("Configuration loaded and validated successfully")
        
        return self._config
    
    def get_config(self) -> AppConfig:
        """
        Get current configuration.
        
        Returns:
            Current AppConfig instance
            
        Raises:
            RuntimeError: If configuration hasn't been loaded
        """
        if not self._config_loaded or self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        
        return self._config
    
    def save_config(self, config_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            config_file: Output file path (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._config:
                logger.error("No configuration to save")
                return False
            
            output_file = Path(config_file) if config_file else self.config_file
            if not output_file:
                logger.error("No output file specified")
                return False
            
            # Convert config to dictionary
            config_dict = asdict(self._config)
            
            # Remove default values to keep file clean
            config_dict = self._remove_default_values(config_dict)
            
            # Save based on file extension
            if output_file.suffix.lower() == '.json':
                self._save_json_config(config_dict, output_file)
            else:
                self._save_yaml_config(config_dict, output_file)
            
            logger.info(f"Configuration saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._config:
                logger.error("No configuration loaded")
                return False
            
            # Convert to dict, update, and convert back
            config_dict = asdict(self._config)
            config_dict = self._merge_configs(config_dict, updates)
            self._config = self._dict_to_config(config_dict)
            
            # Validate updated configuration
            self._validate_config()
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return False
    
    def get_environment_template(self) -> str:
        """
        Generate environment variable template.
        
        Returns:
            Environment template string
        """
        template = "# Automated Review Engine - Environment Variables\n"
        template += "# Copy this file to .env and customize as needed\n\n"
        
        template += "# Environment\n"
        template += "ARE_ENVIRONMENT=development\n"
        template += "ARE_DEBUG_MODE=false\n\n"
        
        template += "# Database\n"
        template += "ARE_DATABASE_TYPE=sqlite\n"
        template += "ARE_DATABASE_HOST=localhost\n"
        template += "ARE_DATABASE_NAME=automated_review_engine\n\n"
        
        template += "# File Handling\n"
        template += "ARE_FILES_UPLOAD_DIRECTORY=data/uploads\n"
        template += "ARE_FILES_MAX_FILE_SIZE_MB=50\n\n"
        
        template += "# Logging\n"
        template += "ARE_LOGGING_LEVEL=INFO\n"
        template += "ARE_LOGGING_FILE_PATH=logs/application.log\n\n"
        
        template += "# UI Settings\n"
        template += "ARE_UI_STREAMLIT_PORT=8501\n"
        template += "ARE_UI_PAGE_TITLE=Automated Review Engine\n\n"
        
        template += "# Security\n"
        template += "ARE_SECURITY_ENABLE_AUTHENTICATION=false\n"
        template += "ARE_SECURITY_SESSION_TIMEOUT_MINUTES=30\n\n"
        
        return template
    
    def create_default_config_file(self, output_file: Union[str, Path]) -> bool:
        """
        Create a default configuration file.
        
        Args:
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            default_config = AppConfig()
            config_dict = asdict(default_config)
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.suffix.lower() == '.json':
                self._save_json_config(config_dict, output_path)
            else:
                self._save_yaml_config(config_dict, output_path)
            
            logger.info(f"Default configuration file created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating default config file: {str(e)}")
            return False
    
    def _load_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {str(e)}")
            return {}
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        
        # Environment variables with ARE_ prefix
        for key, value in os.environ.items():
            if key.startswith('ARE_'):
                # Convert ARE_SECTION_SETTING to nested dict
                parts = key[4:].lower().split('_')
                current = env_config
                
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert string values to appropriate types
                current[parts[-1]] = self._convert_env_value(value)
        
        return env_config
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer values
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # List values (comma-separated)
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        # String value
        return value
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig instance"""
        # Helper function to create dataclass from dict
        def create_dataclass(cls, data):
            if not isinstance(data, dict):
                return data
            
            # Get field names and types
            field_names = {f.name: f.type for f in cls.__dataclass_fields__.values()}
            kwargs = {}
            
            for name, field_type in field_names.items():
                if name in data:
                    value = data[name]
                    # Handle nested dataclasses
                    if hasattr(field_type, '__dataclass_fields__'):
                        kwargs[name] = create_dataclass(field_type, value)
                    else:
                        kwargs[name] = value
            
            return cls(**kwargs)
        
        return create_dataclass(AppConfig, config_dict)
    
    def _validate_config(self):
        """Validate configuration values"""
        if not self._config:
            raise ValueError("No configuration to validate")
        
        config = self._config
        
        # Validate file size limits
        if config.files.max_file_size_mb <= 0:
            raise ValueError("Max file size must be positive")
        
        # Validate port numbers
        if not (1 <= config.ui.streamlit_port <= 65535):
            raise ValueError("Streamlit port must be between 1 and 65535")
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.logging.level.upper() not in valid_levels:
            raise ValueError(f"Invalid logging level: {config.logging.level}")
        
        # Validate directories exist or can be created
        directories = [
            config.files.upload_directory,
            config.files.temp_directory,
            Path(config.logging.file_path).parent,
            config.performance.cache_directory
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Cannot create directory {directory}: {str(e)}")
    
    def _create_directories(self):
        """Create necessary directories"""
        if not self._config:
            return
        
        directories = [
            self._config.files.upload_directory,
            self._config.files.temp_directory,
            Path(self._config.logging.file_path).parent,
            self._config.performance.cache_directory
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
    
    def _save_yaml_config(self, config_dict: Dict[str, Any], output_file: Path):
        """Save configuration as YAML file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    def _save_json_config(self, config_dict: Dict[str, Any], output_file: Path):
        """Save configuration as JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def _remove_default_values(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove default values to keep config file clean"""
        # This is a simplified version - in practice, you might want to
        # compare against default values and remove matching ones
        return config_dict
    
    def _setup_basic_logging(self):
        """Set up basic logging for configuration manager"""
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

# Global configuration instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def load_config(config_file: Optional[Union[str, Path]] = None) -> AppConfig:
    """Load application configuration"""
    return get_config_manager().load_config(config_file)

def get_config() -> AppConfig:
    """Get current application configuration"""
    return get_config_manager().get_config()
