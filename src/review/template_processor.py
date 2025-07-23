"""
Template Processor - Automated Review Engine

Template-based document validation for EU Declaration of Conformity documents.
Validates document structure, required sections, and compliance patterns.

Phase 3.2: Review Logic - Template Processing Component
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import re
import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Core imports
try:
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
    from src.core.config_manager import ConfigManager
except ImportError:
    LoggingManager = None
    ErrorHandler = None
    ConfigManager = None

# Review imports
try:
    from src.review.document_analyzer import DocumentAnalyzer, AnalysisResult, DocumentElement, DocumentStructure
except ImportError:
    DocumentAnalyzer = None
    AnalysisResult = None
    DocumentElement = None
    DocumentStructure = None


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RequirementStatus(Enum):
    """Template requirement validation status"""
    SATISFIED = "satisfied"
    PARTIALLY_SATISFIED = "partially_satisfied"
    NOT_SATISFIED = "not_satisfied"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during template processing"""
    severity: ValidationSeverity
    category: str
    title: str
    description: str
    section: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    regulation_reference: Optional[str] = None


@dataclass
class TemplateRequirement:
    """Represents a template requirement"""
    id: str
    title: str
    description: str
    required: bool
    patterns: List[str]
    validation_rules: List[str]
    severity: ValidationSeverity
    regulation_reference: Optional[str] = None
    examples: List[str] = field(default_factory=list)


@dataclass
class SectionMatch:
    """Represents a matched section in the document"""
    requirement_id: str
    content: str
    confidence: float
    start_position: int
    end_position: int
    matched_patterns: List[str]


@dataclass
class ValidationResult:
    """Template validation result"""
    template_name: str
    document_path: str
    overall_score: float
    compliance_percentage: float
    requirements_status: Dict[str, RequirementStatus]
    section_matches: List[SectionMatch]
    validation_issues: List[ValidationIssue]
    missing_sections: List[str]
    recommendations: List[str]
    processing_time: float
    success: bool


class EUDocTemplate:
    """EU Declaration of Conformity template definition"""
    
    def __init__(self):
        self.template_name = "EU Declaration of Conformity"
        self.template_version = "1.0"
        self.applicable_regulations = [
            "Regulation (EU) 2017/745 (MDR)",
            "Directive 93/42/EEC (MDD)",
            "Regulation (EU) 2016/425 (PPE)"
        ]
        
        # Define required sections and patterns
        self.requirements = self._define_requirements()
        
        # Define validation patterns
        self.validation_patterns = self._define_validation_patterns()
    
    def _define_requirements(self) -> List[TemplateRequirement]:
        """Define EU DoC template requirements"""
        return [
            # Manufacturer Information
            TemplateRequirement(
                id="manufacturer_info",
                title="Manufacturer Information",
                description="Name, address, and contact details of the manufacturer",
                required=True,
                patterns=[
                    r"manufacturer[\s\:]+([^\n]+)",
                    r"company[\s\:]+([^\n]+)",
                    r"address[\s\:]+([^\n]+)"
                ],
                validation_rules=[
                    "must_contain_company_name",
                    "must_contain_address",
                    "address_must_include_country"
                ],
                severity=ValidationSeverity.CRITICAL,
                regulation_reference="MDR Article 10",
                examples=["Manufacturer: ABC Medical Devices GmbH", "Address: Example Street 123, 12345 Berlin, Germany"]
            ),
            
            # Product Identification
            TemplateRequirement(
                id="product_identification",
                title="Product Identification",
                description="Clear identification of the medical device or product",
                required=True,
                patterns=[
                    r"product[\s\:]+([^\n]+)",
                    r"device[\s\:]+([^\n]+)",
                    r"model[\s\:]+([^\n]+)",
                    r"article[\s\:]+([^\n]+)"
                ],
                validation_rules=[
                    "must_contain_product_name",
                    "should_contain_model_number",
                    "should_contain_article_number"
                ],
                severity=ValidationSeverity.CRITICAL,
                regulation_reference="MDR Article 27",
                examples=["Product: XYZ Surgical Instrument", "Model: SI-2024-001"]
            ),
            
            # Declaration Statement
            TemplateRequirement(
                id="declaration_statement",
                title="Declaration of Conformity Statement",
                description="Formal declaration that the product meets applicable requirements",
                required=True,
                patterns=[
                    r"declaration\s+of\s+conformity",
                    r"hereby\s+declare",
                    r"we\s+declare\s+that",
                    r"conformity\s+is\s+declared"
                ],
                validation_rules=[
                    "must_contain_declaration_phrase",
                    "must_be_in_present_tense",
                    "should_reference_manufacturer"
                ],
                severity=ValidationSeverity.CRITICAL,
                regulation_reference="MDR Annex IV",
                examples=["We hereby declare that the above-mentioned product is in conformity"]
            ),
            
            # Applicable Regulations
            TemplateRequirement(
                id="applicable_regulations",
                title="Applicable Regulations",
                description="Reference to applicable EU regulations and directives",
                required=True,
                patterns=[
                    r"regulation\s+\(eu\)\s+\d+/\d+",
                    r"directive\s+\d+/\d+/eec",
                    r"mdr",
                    r"medical\s+device\s+regulation"
                ],
                validation_rules=[
                    "must_reference_mdr_or_mdd",
                    "regulation_numbers_must_be_correct",
                    "must_specify_applicable_annexes"
                ],
                severity=ValidationSeverity.HIGH,
                regulation_reference="MDR Article 19",
                examples=["Regulation (EU) 2017/745 (MDR)", "Directive 93/42/EEC (MDD)"]
            ),
            
            # Harmonised Standards
            TemplateRequirement(
                id="harmonised_standards",
                title="Harmonised Standards",
                description="List of harmonised standards applied",
                required=True,
                patterns=[
                    r"harmonised\s+standards?",
                    r"en\s+\d+",
                    r"iso\s+\d+",
                    r"iec\s+\d+"
                ],
                validation_rules=[
                    "must_list_applicable_standards",
                    "standards_must_include_version_dates",
                    "should_explain_standard_application"
                ],
                severity=ValidationSeverity.HIGH,
                regulation_reference="MDR Article 8",
                examples=["EN ISO 14971:2019", "EN ISO 10993-1:2018"]
            ),
            
            # Notified Body Information
            TemplateRequirement(
                id="notified_body",
                title="Notified Body Information",
                description="Information about notified body involvement (if applicable)",
                required=False,
                patterns=[
                    r"notified\s+body",
                    r"nb\s+\d+",
                    r"certificate\s+number",
                    r"conformity\s+assessment"
                ],
                validation_rules=[
                    "notified_body_number_must_be_valid",
                    "certificate_number_format_check",
                    "must_specify_assessment_procedure"
                ],
                severity=ValidationSeverity.MEDIUM,
                regulation_reference="MDR Article 35",
                examples=["Notified Body: TÜV SÜD Product Service GmbH (NB 0123)"]
            ),
            
            # CE Marking Declaration
            TemplateRequirement(
                id="ce_marking",
                title="CE Marking Declaration",
                description="Declaration regarding CE marking affixing",
                required=True,
                patterns=[
                    r"ce\s+marking",
                    r"ce\s+mark",
                    r"conformity\s+marking"
                ],
                validation_rules=[
                    "must_declare_ce_marking_affixed",
                    "should_specify_marking_location",
                    "must_confirm_marking_visibility"
                ],
                severity=ValidationSeverity.HIGH,
                regulation_reference="MDR Article 20",
                examples=["CE marking has been affixed to the product"]
            ),
            
            # Authorized Representative
            TemplateRequirement(
                id="authorized_representative",
                title="Authorized Representative",
                description="EU authorized representative information (if applicable)",
                required=False,
                patterns=[
                    r"authorized\s+representative",
                    r"authorised\s+representative",
                    r"eu\s+representative",
                    r"european\s+representative"
                ],
                validation_rules=[
                    "must_include_representative_name",
                    "must_include_eu_address",
                    "should_include_contact_details"
                ],
                severity=ValidationSeverity.MEDIUM,
                regulation_reference="MDR Article 11",
                examples=["Authorized Representative: EU MedTech Services, Amsterdam, Netherlands"]
            ),
            
            # Signature and Date
            TemplateRequirement(
                id="signature_date",
                title="Signature and Date",
                description="Authorized signature and declaration date",
                required=True,
                patterns=[
                    r"signature",
                    r"signed\s+by",
                    r"date[\s\:]+\d",
                    r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}"
                ],
                validation_rules=[
                    "must_include_signature_line",
                    "must_include_date",
                    "date_must_be_recent",
                    "signatory_must_be_authorized"
                ],
                severity=ValidationSeverity.HIGH,
                regulation_reference="MDR Annex IV",
                examples=["Date: 15.03.2024", "Signature: Dr. Med. Director"]
            )
        ]
    
    def _define_validation_patterns(self) -> Dict[str, List[str]]:
        """Define additional validation patterns"""
        return {
            'dates': [
                r'\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4}',
                r'\d{4}[\.\/\-]\d{1,2}[\.\/\-]\d{1,2}',
                r'\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b'
            ],
            'regulation_numbers': [
                r'regulation\s+\(eu\)\s+2017/745',
                r'regulation\s+\(eu\)\s+2016/425',
                r'directive\s+93/42/eec',
                r'directive\s+98/79/ec'
            ],
            'standard_numbers': [
                r'en\s+iso\s+\d+(?:[\-\:]\d+)*(?:\:\d{4})?',
                r'iso\s+\d+(?:[\-\:]\d+)*(?:\:\d{4})?',
                r'iec\s+\d+(?:[\-\:]\d+)*(?:\:\d{4})?'
            ],
            'notified_body_numbers': [
                r'nb\s+\d{4}',
                r'notified\s+body\s+\d{4}',
                r'\(\s*nb\s*\d{4}\s*\)'
            ]
        }


class TemplateProcessor:
    """Advanced template processor for document validation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize template processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = None
        self.error_handler = None
        
        # Initialize core components
        self._initialize_core_components()
        
        # Load templates
        self.templates = {
            'eu_doc': EUDocTemplate()
        }
        
        # Processing statistics
        self.processing_stats = {
            'documents_processed': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'total_processing_time': 0.0
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default processor configuration"""
        return {
            'strict_validation': True,
            'case_sensitive': False,
            'min_confidence_threshold': 0.7,
            'max_processing_time': 300,  # seconds
            'language_normalization': True,
            'fuzzy_matching': True,
            'pattern_matching_tolerance': 0.8,
            'section_detection_sensitivity': 0.6,
            'auto_fix_suggestions': True,
            'detailed_reporting': True
        }
    
    def _initialize_core_components(self):
        """Initialize core infrastructure components"""
        try:
            if LoggingManager:
                self.logger_manager = LoggingManager({'level': 'INFO'})
                self.logger_manager.initialize()
                self.logger = self.logger_manager.get_logger('review.template_processor')
            
            if ErrorHandler:
                self.error_handler = ErrorHandler()
            
            if self.logger:
                self.logger.info("Template processor initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize core components: {e}")
    
    def validate_document(
        self, 
        analysis_result: Any, 
        template_name: str = 'eu_doc'
    ) -> ValidationResult:
        """
        Validate document against template requirements
        
        Args:
            analysis_result: Document analysis result
            template_name: Template to validate against
            
        Returns:
            ValidationResult with validation findings
        """
        start_time = datetime.now()
        
        try:
            # Get template
            if template_name not in self.templates:
                raise ValueError(f"Unknown template: {template_name}")
            
            template = self.templates[template_name]
            
            # Initialize validation result
            validation_result = ValidationResult(
                template_name=template.template_name,
                document_path=getattr(analysis_result, 'document_path', 'unknown'),
                overall_score=0.0,
                compliance_percentage=0.0,
                requirements_status={},
                section_matches=[],
                validation_issues=[],
                missing_sections=[],
                recommendations=[],
                processing_time=0.0,
                success=False
            )
            
            # Validate each requirement
            total_requirements = len(template.requirements)
            satisfied_requirements = 0
            
            for requirement in template.requirements:
                status, matches, issues = self._validate_requirement(
                    requirement, 
                    analysis_result
                )
                
                validation_result.requirements_status[requirement.id] = status
                validation_result.section_matches.extend(matches)
                validation_result.validation_issues.extend(issues)
                
                if status == RequirementStatus.SATISFIED:
                    satisfied_requirements += 1
                elif status == RequirementStatus.PARTIALLY_SATISFIED:
                    satisfied_requirements += 0.5
                
                # Track missing sections
                if status == RequirementStatus.NOT_SATISFIED and requirement.required:
                    validation_result.missing_sections.append(requirement.title)
            
            # Calculate scores
            validation_result.compliance_percentage = (satisfied_requirements / total_requirements) * 100
            validation_result.overall_score = self._calculate_overall_score(validation_result)
            
            # Generate recommendations
            validation_result.recommendations = self._generate_recommendations(validation_result, template)
            
            # Set success flag
            validation_result.success = (
                len(validation_result.validation_issues) == 0 or
                all(issue.severity not in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH] 
                    for issue in validation_result.validation_issues)
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            validation_result.processing_time = processing_time
            
            self.processing_stats['documents_processed'] += 1
            self.processing_stats['total_processing_time'] += processing_time
            
            if validation_result.success:
                self.processing_stats['successful_validations'] += 1
            else:
                self.processing_stats['failed_validations'] += 1
            
            if self.logger:
                self.logger.info(f"Template validation completed: {template_name} "
                               f"(score: {validation_result.overall_score:.1f}, "
                               f"compliance: {validation_result.compliance_percentage:.1f}%)")
            
            return validation_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if self.error_handler:
                error_context = self.error_handler.handle_error(e)
                error_message = error_context.user_message
            else:
                error_message = str(e)
            
            if self.logger:
                self.logger.error(f"Template validation failed: {error_message}")
            
            # Return failed validation result
            return ValidationResult(
                template_name=template_name,
                document_path='unknown',
                overall_score=0.0,
                compliance_percentage=0.0,
                requirements_status={},
                section_matches=[],
                validation_issues=[ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category='processing_error',
                    title='Validation Failed',
                    description=error_message
                )],
                missing_sections=[],
                recommendations=[],
                processing_time=processing_time,
                success=False
            )
    
    def _validate_requirement(
        self, 
        requirement: TemplateRequirement, 
        analysis_result: Any
    ) -> Tuple[RequirementStatus, List[SectionMatch], List[ValidationIssue]]:
        """Validate a single requirement against document content"""
        
        matches = []
        issues = []
        
        # Search for requirement patterns in document text
        text_content = analysis_result.text_content.lower() if not self.config['case_sensitive'] else analysis_result.text_content
        
        pattern_matches = []
        for pattern in requirement.patterns:
            pattern_flags = re.IGNORECASE if not self.config['case_sensitive'] else 0
            regex_matches = list(re.finditer(pattern, text_content, pattern_flags))
            
            for match in regex_matches:
                confidence = self._calculate_pattern_confidence(match, pattern, text_content)
                
                if confidence >= self.config['min_confidence_threshold']:
                    section_match = SectionMatch(
                        requirement_id=requirement.id,
                        content=match.group(0),
                        confidence=confidence,
                        start_position=match.start(),
                        end_position=match.end(),
                        matched_patterns=[pattern]
                    )
                    matches.append(section_match)
                    pattern_matches.append(pattern)
        
        # Determine requirement status
        if len(matches) == 0:
            if requirement.required:
                status = RequirementStatus.NOT_SATISFIED
                issues.append(ValidationIssue(
                    severity=requirement.severity,
                    category='missing_section',
                    title=f"Missing Required Section: {requirement.title}",
                    description=f"Could not find {requirement.description.lower()}",
                    suggestion=f"Please include {requirement.title.lower()} with: {', '.join(requirement.examples[:2])}",
                    regulation_reference=requirement.regulation_reference
                ))
            else:
                status = RequirementStatus.NOT_APPLICABLE
        elif len(pattern_matches) >= len(requirement.patterns) * 0.7:
            status = RequirementStatus.SATISFIED
        else:
            status = RequirementStatus.PARTIALLY_SATISFIED
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category='incomplete_section',
                title=f"Incomplete Section: {requirement.title}",
                description=f"Section partially matches requirements but may be missing some elements",
                suggestion=f"Please verify that all required information is included in {requirement.title.lower()}",
                regulation_reference=requirement.regulation_reference
            ))
        
        # Apply validation rules
        rule_issues = self._apply_validation_rules(requirement, matches, analysis_result)
        issues.extend(rule_issues)
        
        return status, matches, issues
    
    def _calculate_pattern_confidence(self, match: re.Match, pattern: str, text: str) -> float:
        """Calculate confidence score for pattern match"""
        base_confidence = 0.8
        
        # Adjust confidence based on match context
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(text), match.end() + 50)
        context = text[start_pos:end_pos]
        
        # Boost confidence for matches in section headers
        if any(header_word in context.lower() for header_word in ['section', 'chapter', 'article']):
            base_confidence += 0.1
        
        # Boost confidence for matches near relevant keywords
        relevant_keywords = ['declaration', 'conformity', 'regulation', 'standard', 'device']
        keyword_count = sum(1 for keyword in relevant_keywords if keyword in context.lower())
        base_confidence += min(0.1, keyword_count * 0.02)
        
        return min(1.0, base_confidence)
    
    def _apply_validation_rules(
        self, 
        requirement: TemplateRequirement, 
        matches: List[SectionMatch], 
        analysis_result: Any
    ) -> List[ValidationIssue]:
        """Apply specific validation rules for a requirement"""
        issues = []
        
        for rule in requirement.validation_rules:
            try:
                rule_issues = self._execute_validation_rule(rule, requirement, matches, analysis_result)
                issues.extend(rule_issues)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to execute validation rule '{rule}': {e}")
        
        return issues
    
    def _execute_validation_rule(
        self, 
        rule: str, 
        requirement: TemplateRequirement, 
        matches: List[SectionMatch], 
        analysis_result: Any
    ) -> List[ValidationIssue]:
        """Execute a specific validation rule"""
        issues = []
        text_content = analysis_result.text_content.lower()
        
        # Rule implementations
        if rule == "must_contain_company_name":
            if not any(self._contains_company_indicators(match.content) for match in matches):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category='content_validation',
                    title="Missing Company Name",
                    description="Manufacturer section should include a clear company name",
                    suggestion="Include the full legal name of the manufacturing company"
                ))
        
        elif rule == "must_contain_address":
            if not any(self._contains_address_indicators(match.content) for match in matches):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category='content_validation',
                    title="Missing Address",
                    description="Manufacturer section should include a complete address",
                    suggestion="Include street address, city, postal code, and country"
                ))
        
        elif rule == "must_reference_mdr_or_mdd":
            mdr_pattern = r'regulation\s+\(eu\)\s+2017/745|mdr'
            mdd_pattern = r'directive\s+93/42/eec|mdd'
            
            if not (re.search(mdr_pattern, text_content, re.IGNORECASE) or 
                   re.search(mdd_pattern, text_content, re.IGNORECASE)):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category='regulatory_compliance',
                    title="Missing Regulatory Reference",
                    description="Document must reference either MDR or MDD",
                    suggestion="Include reference to 'Regulation (EU) 2017/745 (MDR)' or 'Directive 93/42/EEC (MDD)'",
                    regulation_reference="MDR Article 19"
                ))
        
        elif rule == "date_must_be_recent":
            # Check if date is within reasonable range (not future, not too old)
            date_patterns = self.templates['eu_doc'].validation_patterns['dates']
            dates_found = []
            
            for pattern in date_patterns:
                dates_found.extend(re.findall(pattern, text_content, re.IGNORECASE))
            
            if dates_found:
                # Simple validation - would need more sophisticated date parsing in production
                current_year = datetime.now().year
                for date_str in dates_found:
                    if re.search(r'20[0-9]{2}', date_str):
                        year_match = re.search(r'20([0-9]{2})', date_str)
                        if year_match:
                            year = int(f"20{year_match.group(1)}")
                            if year > current_year:
                                issues.append(ValidationIssue(
                                    severity=ValidationSeverity.MEDIUM,
                                    category='date_validation',
                                    title="Future Date Detected",
                                    description=f"Declaration date appears to be in the future: {date_str}",
                                    suggestion="Verify that the declaration date is correct"
                                ))
        
        return issues
    
    def _contains_company_indicators(self, text: str) -> bool:
        """Check if text contains company name indicators"""
        company_indicators = ['gmbh', 'ltd', 'inc', 'corp', 'ag', 'sa', 'bv', 'srl', 'spa']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in company_indicators)
    
    def _contains_address_indicators(self, text: str) -> bool:
        """Check if text contains address indicators"""
        address_indicators = ['street', 'str', 'avenue', 'ave', 'road', 'rd', 'germany', 'usa', 'uk', 'france']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in address_indicators) or bool(re.search(r'\d{4,5}', text))
    
    def _calculate_overall_score(self, validation_result: ValidationResult) -> float:
        """Calculate overall validation score"""
        base_score = validation_result.compliance_percentage
        
        # Adjust score based on validation issues
        penalty = 0
        for issue in validation_result.validation_issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                penalty += 20
            elif issue.severity == ValidationSeverity.HIGH:
                penalty += 10
            elif issue.severity == ValidationSeverity.MEDIUM:
                penalty += 5
            elif issue.severity == ValidationSeverity.LOW:
                penalty += 2
        
        adjusted_score = max(0, base_score - penalty)
        return min(100, adjusted_score)
    
    def _generate_recommendations(
        self, 
        validation_result: ValidationResult, 
        template: EUDocTemplate
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Recommendations based on missing sections
        if validation_result.missing_sections:
            recommendations.append(
                f"Add the following missing sections: {', '.join(validation_result.missing_sections)}"
            )
        
        # Recommendations based on validation issues
        critical_issues = [issue for issue in validation_result.validation_issues 
                          if issue.severity == ValidationSeverity.CRITICAL]
        
        if critical_issues:
            recommendations.append(
                f"Address {len(critical_issues)} critical compliance issues to ensure regulatory approval"
            )
        
        # Score-based recommendations
        if validation_result.overall_score < 70:
            recommendations.append(
                "Document requires significant improvements to meet compliance standards"
            )
        elif validation_result.overall_score < 85:
            recommendations.append(
                "Document is mostly compliant but could benefit from minor improvements"
            )
        
        # Specific improvement suggestions
        if validation_result.compliance_percentage < 80:
            recommendations.append(
                "Review template requirements and ensure all mandatory sections are included"
            )
        
        return recommendations
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template"""
        if template_name not in self.templates:
            return {}
        
        template = self.templates[template_name]
        
        return {
            'name': template.template_name,
            'version': template.template_version,
            'applicable_regulations': template.applicable_regulations,
            'requirements_count': len(template.requirements),
            'required_sections': [req.title for req in template.requirements if req.required],
            'optional_sections': [req.title for req in template.requirements if not req.required]
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processor statistics"""
        stats = self.processing_stats.copy()
        
        if stats['documents_processed'] > 0:
            stats['success_rate'] = stats['successful_validations'] / stats['documents_processed']
            stats['average_processing_time'] = stats['total_processing_time'] / stats['documents_processed']
        else:
            stats['success_rate'] = 0.0
            stats['average_processing_time'] = 0.0
        
        return stats
    
    def export_validation_report(
        self, 
        validation_result: ValidationResult, 
        format: str = 'json'
    ) -> Union[str, Dict[str, Any]]:
        """
        Export validation result as formatted report
        
        Args:
            validation_result: Validation result to export
            format: Export format ('json', 'text', 'html')
            
        Returns:
            Formatted report as string or dictionary
        """
        if format == 'json':
            return self._export_json_report(validation_result)
        elif format == 'text':
            return self._export_text_report(validation_result)
        elif format == 'html':
            return self._export_html_report(validation_result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json_report(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Export validation result as JSON"""
        return {
            'template_name': validation_result.template_name,
            'document_path': validation_result.document_path,
            'validation_summary': {
                'overall_score': validation_result.overall_score,
                'compliance_percentage': validation_result.compliance_percentage,
                'success': validation_result.success,
                'processing_time': validation_result.processing_time
            },
            'requirements_status': {k: v.value for k, v in validation_result.requirements_status.items()},
            'validation_issues': [
                {
                    'severity': issue.severity.value,
                    'category': issue.category,
                    'title': issue.title,
                    'description': issue.description,
                    'suggestion': issue.suggestion,
                    'regulation_reference': issue.regulation_reference
                }
                for issue in validation_result.validation_issues
            ],
            'missing_sections': validation_result.missing_sections,
            'recommendations': validation_result.recommendations,
            'section_matches': [
                {
                    'requirement_id': match.requirement_id,
                    'content': match.content[:100] + '...' if len(match.content) > 100 else match.content,
                    'confidence': match.confidence
                }
                for match in validation_result.section_matches
            ]
        }
    
    def _export_text_report(self, validation_result: ValidationResult) -> str:
        """Export validation result as text report"""
        report_lines = [
            f"VALIDATION REPORT",
            f"================",
            f"Template: {validation_result.template_name}",
            f"Document: {validation_result.document_path}",
            f"",
            f"SUMMARY",
            f"-------",
            f"Overall Score: {validation_result.overall_score:.1f}/100",
            f"Compliance: {validation_result.compliance_percentage:.1f}%",
            f"Status: {'PASSED' if validation_result.success else 'FAILED'}",
            f"Processing Time: {validation_result.processing_time:.2f}s",
            f""
        ]
        
        if validation_result.validation_issues:
            report_lines.extend([
                f"VALIDATION ISSUES ({len(validation_result.validation_issues)})",
                f"------------------"
            ])
            
            for issue in validation_result.validation_issues:
                report_lines.extend([
                    f"[{issue.severity.value.upper()}] {issue.title}",
                    f"  {issue.description}",
                    f"  Suggestion: {issue.suggestion or 'None'}",
                    f""
                ])
        
        if validation_result.recommendations:
            report_lines.extend([
                f"RECOMMENDATIONS",
                f"---------------"
            ])
            
            for i, rec in enumerate(validation_result.recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        
        return "\n".join(report_lines)
    
    def _export_html_report(self, validation_result: ValidationResult) -> str:
        """Export validation result as HTML report"""
        # Simplified HTML report - would be expanded in production
        html_template = f"""
        <html>
        <head><title>Validation Report</title></head>
        <body>
            <h1>Document Validation Report</h1>
            <h2>Summary</h2>
            <p>Overall Score: {validation_result.overall_score:.1f}/100</p>
            <p>Compliance: {validation_result.compliance_percentage:.1f}%</p>
            <p>Status: {'PASSED' if validation_result.success else 'FAILED'}</p>
            
            <h2>Issues</h2>
            <ul>
            {''.join(f'<li><strong>{issue.title}</strong>: {issue.description}</li>' 
                    for issue in validation_result.validation_issues)}
            </ul>
            
            <h2>Recommendations</h2>
            <ol>
            {''.join(f'<li>{rec}</li>' for rec in validation_result.recommendations)}
            </ol>
        </body>
        </html>
        """
        return html_template


def create_template_processor(config: Optional[Dict[str, Any]] = None) -> TemplateProcessor:
    """
    Create and return a TemplateProcessor instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured TemplateProcessor instance
    """
    return TemplateProcessor(config=config)
