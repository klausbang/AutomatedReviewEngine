# Data Models Design

## Overview
This document defines the data models and structures used throughout the Automated Review Engine. These models represent the core entities and their relationships in the system.

## Core Data Models

### 1. Document Model
Represents a document under review.

```python
@dataclass
class Document:
    """Represents a document under review"""
    id: str                          # Unique document identifier
    filename: str                    # Original filename
    file_type: str                   # 'pdf' or 'docx'
    file_size: int                   # File size in bytes
    upload_timestamp: datetime       # When document was uploaded
    content: str                     # Extracted text content
    structure: DocumentStructure     # Document structure analysis
    metadata: Dict[str, Any]         # Additional metadata
    status: DocumentStatus           # Processing status
```

### 2. Template Model
Represents a document template with expected structure.

```python
@dataclass
class Template:
    """Represents a document template"""
    id: str                          # Unique template identifier
    name: str                        # Template name
    description: str                 # Template description
    filename: str                    # Template filename
    version: str                     # Template version
    sections: List[TemplateSection]  # Expected sections
    required_fields: List[str]       # Required content fields
    validation_rules: List[ValidationRule]  # Template-specific rules
    created_date: datetime           # Template creation date
    last_modified: datetime          # Last modification date
```

### 3. Review Script Model
Represents a review script with validation rules.

```python
@dataclass
class ReviewScript:
    """Represents a review script"""
    id: str                          # Unique script identifier
    name: str                        # Script name
    description: str                 # Script description
    version: str                     # Script version
    rules: List[ReviewRule]          # Review rules
    parameters: Dict[str, Any]       # Script parameters
    created_date: datetime           # Script creation date
    author: str                      # Script author
```

### 4. Review Session Model
Represents a complete review session.

```python
@dataclass
class ReviewSession:
    """Represents a review session"""
    id: str                          # Unique session identifier
    document: Document               # Document being reviewed
    template: Template               # Template used for review
    review_script: ReviewScript      # Review script used
    plm_data: PLMData               # PLM data used
    status: ReviewStatus             # Current session status
    start_time: datetime             # Review start time
    end_time: Optional[datetime]     # Review completion time
    results: Optional[ReviewResults] # Review results
    errors: List[ReviewError]        # Any errors encountered
```

## Supporting Data Models

### 5. Document Structure Model
Represents the analyzed structure of a document.

```python
@dataclass
class DocumentStructure:
    """Represents document structure analysis"""
    sections: List[DocumentSection]  # Document sections
    headings: List[Heading]          # Document headings
    tables: List[Table]              # Tables found
    figures: List[Figure]            # Figures/images found
    metadata: Dict[str, Any]         # Structural metadata
```

### 6. PLM Data Model
Represents Product Lifecycle Management data.

```python
@dataclass
class PLMData:
    """Represents PLM system data"""
    id: str                          # PLM data identifier
    source_type: str                 # 'manual_input' or 'csv_file'
    data: Dict[str, Any]            # PLM data fields
    product_info: ProductInfo        # Product information
    validation_status: ValidationStatus  # Data validation status
    input_timestamp: datetime        # When data was input
```

### 7. Review Results Model
Represents the complete results of a review.

```python
@dataclass
class ReviewResults:
    """Represents review results"""
    session_id: str                  # Associated session ID
    overall_status: str              # 'passed', 'failed', 'warning'
    findings: List[ReviewFinding]    # Individual findings
    plm_directions: PLMDirections    # Generated PLM search directions
    compliance_score: float          # Overall compliance score (0-100)
    summary: ReviewSummary           # Executive summary
    generated_timestamp: datetime    # When results were generated
```

## Detailed Component Models

### Template Section Model
```python
@dataclass
class TemplateSection:
    """Represents a section in a template"""
    id: str                          # Section identifier
    title: str                       # Section title
    order: int                       # Section order
    required: bool                   # Whether section is required
    content_type: str                # 'text', 'table', 'list', etc.
    expected_content: str            # Expected content pattern
    validation_rules: List[ValidationRule]  # Section-specific rules
```

### Review Rule Model
```python
@dataclass
class ReviewRule:
    """Represents a review rule"""
    id: str                          # Rule identifier
    name: str                        # Rule name
    description: str                 # Rule description
    rule_type: str                   # 'presence', 'format', 'content', etc.
    parameters: Dict[str, Any]       # Rule parameters
    severity: str                    # 'error', 'warning', 'info'
    target_section: Optional[str]    # Target section (if applicable)
```

### Review Finding Model
```python
@dataclass
class ReviewFinding:
    """Represents a single review finding"""
    id: str                          # Finding identifier
    rule_id: str                     # Associated rule ID
    finding_type: str                # 'missing', 'incorrect', 'warning', etc.
    severity: str                    # 'critical', 'major', 'minor'
    description: str                 # Finding description
    location: FindingLocation        # Where in document
    recommendation: str              # Recommended action
    evidence: Optional[str]          # Supporting evidence
```

### PLM Directions Model
```python
@dataclass
class PLMDirections:
    """Represents PLM search directions"""
    searches: List[PLMSearch]        # Individual search directions
    generated_timestamp: datetime    # When directions were generated
    context: str                     # Context for searches
```

### PLM Search Model
```python
@dataclass
class PLMSearch:
    """Represents a single PLM search direction"""
    search_mode: str                 # 'document_search', 'product_search', etc.
    search_field: str                # Field name for search
    search_string: str               # String to search for
    description: str                 # Human-readable description
    priority: int                    # Search priority (1-10)
```

## Enumeration Types

### Document Status
```python
class DocumentStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
```

### Review Status
```python
class ReviewStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### Validation Status
```python
class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"
```

## Data Validation Rules

### File Upload Validation
- File size limits (max 50MB for MVP)
- Supported file types (PDF, DOCX)
- File integrity checks
- Virus scanning (future enhancement)

### Content Validation
- Text encoding validation
- Structure validation against templates
- Required field presence
- Data format compliance

### PLM Data Validation
- Required fields presence
- Data type validation
- Cross-reference validation
- Business rule compliance

## Data Storage Strategy

### MVP File-Based Storage
```
data/
├── sessions/
│   └── {session_id}/
│       ├── document.json         # Document metadata
│       ├── template.json         # Template metadata
│       ├── script.json           # Review script
│       ├── plm_data.json         # PLM data
│       ├── results.json          # Review results
│       └── files/                # Actual uploaded files
├── templates/
│   └── {template_id}.json        # Template definitions
└── scripts/
    └── {script_id}.json          # Review script definitions
```

### Future Database Schema
```sql
-- Documents table
CREATE TABLE documents (
    id VARCHAR(50) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    metadata JSONB
);

-- Templates table
CREATE TABLE templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL,
    created_date TIMESTAMP NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    template_data JSONB NOT NULL
);

-- Review sessions table
CREATE TABLE review_sessions (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(id),
    template_id VARCHAR(50) REFERENCES templates(id),
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    session_data JSONB
);
```

## Data Serialization

### JSON Schema Examples

#### Document JSON Schema
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "filename": {"type": "string"},
    "file_type": {"type": "string", "enum": ["pdf", "docx"]},
    "file_size": {"type": "integer"},
    "upload_timestamp": {"type": "string", "format": "date-time"},
    "content": {"type": "string"},
    "structure": {"$ref": "#/definitions/DocumentStructure"},
    "metadata": {"type": "object"},
    "status": {"type": "string", "enum": ["uploaded", "processing", "processed", "error"]}
  },
  "required": ["id", "filename", "file_type", "file_size", "upload_timestamp", "status"]
}
```

#### Review Results JSON Schema
```json
{
  "type": "object",
  "properties": {
    "session_id": {"type": "string"},
    "overall_status": {"type": "string", "enum": ["passed", "failed", "warning"]},
    "findings": {
      "type": "array",
      "items": {"$ref": "#/definitions/ReviewFinding"}
    },
    "plm_directions": {"$ref": "#/definitions/PLMDirections"},
    "compliance_score": {"type": "number", "minimum": 0, "maximum": 100},
    "summary": {"$ref": "#/definitions/ReviewSummary"},
    "generated_timestamp": {"type": "string", "format": "date-time"}
  },
  "required": ["session_id", "overall_status", "findings", "generated_timestamp"]
}
```

## Data Migration Strategy

### Version Compatibility
- Maintain backward compatibility for data formats
- Provide migration scripts for data structure changes
- Version tracking for all data models

### Data Backup and Recovery
- Regular backup of session data
- Export/import functionality for templates and scripts
- Data integrity verification
