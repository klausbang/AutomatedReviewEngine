"""
Workflow Manager - Automated Review Engine

Manages review workflows, custom scripts, and automated processes.
Coordinates multi-step review procedures and integrates with external tools.

Phase 3.2: Review Logic - Workflow Management Component
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import json
import subprocess
import importlib.util
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import shutil

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


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepType(Enum):
    """Types of workflow steps"""
    DOCUMENT_ANALYSIS = "document_analysis"
    TEMPLATE_VALIDATION = "template_validation"
    CUSTOM_SCRIPT = "custom_script"
    EXTERNAL_TOOL = "external_tool"
    CONDITION_CHECK = "condition_check"
    DATA_TRANSFORMATION = "data_transformation"
    NOTIFICATION = "notification"
    FILE_OPERATION = "file_operation"


class ExecutionMode(Enum):
    """Workflow execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class WorkflowStep:
    """Represents a single workflow step"""
    id: str
    name: str
    step_type: StepType
    configuration: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 60
    retry_count: int = 0
    continue_on_error: bool = False
    condition_script: Optional[str] = None


@dataclass
class StepResult:
    """Result of a workflow step execution"""
    step_id: str
    status: WorkflowStatus
    output_data: Any = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    definition: WorkflowDefinition
    step_results: Dict[str, StepResult]
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[str] = field(default_factory=list)


class CustomScriptExecutor:
    """Handles execution of custom Python scripts"""
    
    def __init__(self, logger: Optional[Any] = None):
        self.logger = logger
        self.script_cache = {}
    
    def execute_script(
        self, 
        script_path: Union[str, Path], 
        context_data: Dict[str, Any]
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute a custom Python script
        
        Args:
            script_path: Path to Python script
            context_data: Context data to pass to script
            
        Returns:
            Tuple of (success, result, error_message)
        """
        try:
            script_path = Path(script_path)
            
            if not script_path.exists():
                return False, None, f"Script not found: {script_path}"
            
            # Load and execute script
            spec = importlib.util.spec_from_file_location("custom_script", script_path)
            if not spec or not spec.loader:
                return False, None, f"Failed to load script: {script_path}"
            
            module = importlib.util.module_from_spec(spec)
            
            # Add context data to module
            module.__dict__.update(context_data)
            
            # Execute script
            spec.loader.exec_module(module)
            
            # Get result (look for main function or result variable)
            if hasattr(module, 'main'):
                result = module.main(context_data)
            elif hasattr(module, 'result'):
                result = module.result
            else:
                result = None
            
            return True, result, None
            
        except Exception as e:
            error_msg = f"Script execution failed: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, None, error_msg
    
    def validate_script(self, script_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a Python script without executing it
        
        Args:
            script_path: Path to Python script
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'has_main_function': False,
            'required_parameters': []
        }
        
        try:
            script_path = Path(script_path)
            
            if not script_path.exists():
                validation_result['errors'].append(f"Script file not found: {script_path}")
                return validation_result
            
            # Read and compile script
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Try to compile
            compile(script_content, str(script_path), 'exec')
            
            # Check for main function
            if 'def main(' in script_content:
                validation_result['has_main_function'] = True
            
            validation_result['is_valid'] = True
            
        except SyntaxError as e:
            validation_result['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result


class WorkflowManager:
    """Manages workflow definitions and executions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize workflow manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = None
        self.error_handler = None
        
        # Initialize core components
        self._initialize_core_components()
        
        # Workflow storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        
        # Executors
        self.script_executor = CustomScriptExecutor(self.logger)
        
        # Load built-in workflows
        self._load_builtin_workflows()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default workflow manager configuration"""
        return {
            'max_concurrent_workflows': 5,
            'default_step_timeout': 300,  # seconds
            'script_execution_timeout': 120,
            'enable_parallel_execution': True,
            'workflow_data_directory': 'data/workflows',
            'custom_scripts_directory': 'scripts',
            'temp_directory': None,  # Will use system temp
            'max_execution_history': 500,
            'auto_cleanup_completed': True,
            'cleanup_after_hours': 48,
            'detailed_logging': True
        }
    
    def _initialize_core_components(self):
        """Initialize core infrastructure components"""
        try:
            if LoggingManager:
                self.logger_manager = LoggingManager({'level': 'INFO'})
                self.logger_manager.initialize()
                self.logger = self.logger_manager.get_logger('review.workflow_manager')
            
            if ErrorHandler:
                self.error_handler = ErrorHandler()
            
            if self.logger:
                self.logger.info("Workflow manager initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize core components: {e}")
    
    def _load_builtin_workflows(self):
        """Load built-in workflow definitions"""
        try:
            # EU DoC Standard Review Workflow
            eu_doc_workflow = WorkflowDefinition(
                id="eu_doc_standard_review",
                name="EU Declaration of Conformity Standard Review",
                description="Standard workflow for reviewing EU DoC documents",
                version="1.0",
                steps=[
                    WorkflowStep(
                        id="document_analysis",
                        name="Document Analysis",
                        step_type=StepType.DOCUMENT_ANALYSIS,
                        configuration={
                            'extract_metadata': True,
                            'analyze_structure': True,
                            'extract_text': True
                        },
                        timeout_seconds=120
                    ),
                    WorkflowStep(
                        id="template_validation",
                        name="Template Validation",
                        step_type=StepType.TEMPLATE_VALIDATION,
                        configuration={
                            'template_name': 'eu_doc',
                            'strict_validation': True,
                            'generate_report': True
                        },
                        dependencies=["document_analysis"],
                        timeout_seconds=180
                    ),
                    WorkflowStep(
                        id="compliance_check",
                        name="Compliance Check",
                        step_type=StepType.CONDITION_CHECK,
                        configuration={
                            'min_compliance_percentage': 80,
                            'max_critical_issues': 0
                        },
                        dependencies=["template_validation"],
                        timeout_seconds=30
                    )
                ],
                execution_mode=ExecutionMode.SEQUENTIAL
            )
            
            self.workflow_definitions[eu_doc_workflow.id] = eu_doc_workflow
            
            # Enhanced Review Workflow
            enhanced_workflow = WorkflowDefinition(
                id="enhanced_document_review",
                name="Enhanced Document Review with Custom Scripts",
                description="Enhanced review workflow with custom validation scripts",
                version="1.0",
                steps=[
                    WorkflowStep(
                        id="document_analysis",
                        name="Document Analysis",
                        step_type=StepType.DOCUMENT_ANALYSIS,
                        configuration={
                            'extract_metadata': True,
                            'analyze_structure': True,
                            'extract_text': True,
                            'language_detection': True
                        },
                        timeout_seconds=120
                    ),
                    WorkflowStep(
                        id="custom_preprocessing",
                        name="Custom Preprocessing",
                        step_type=StepType.CUSTOM_SCRIPT,
                        configuration={
                            'script_path': 'scripts/preprocess_document.py',
                            'parameters': {
                                'clean_text': True,
                                'normalize_formatting': True
                            }
                        },
                        dependencies=["document_analysis"],
                        timeout_seconds=60
                    ),
                    WorkflowStep(
                        id="template_validation",
                        name="Template Validation",
                        step_type=StepType.TEMPLATE_VALIDATION,
                        configuration={
                            'template_name': 'eu_doc',
                            'strict_validation': True
                        },
                        dependencies=["custom_preprocessing"],
                        timeout_seconds=180
                    ),
                    WorkflowStep(
                        id="custom_validation",
                        name="Custom Validation Rules",
                        step_type=StepType.CUSTOM_SCRIPT,
                        configuration={
                            'script_path': 'scripts/custom_validation.py',
                            'parameters': {
                                'check_additional_requirements': True
                            }
                        },
                        dependencies=["template_validation"],
                        timeout_seconds=90
                    )
                ],
                execution_mode=ExecutionMode.SEQUENTIAL
            )
            
            self.workflow_definitions[enhanced_workflow.id] = enhanced_workflow
            
            if self.logger:
                self.logger.info(f"Loaded {len(self.workflow_definitions)} built-in workflows")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load built-in workflows: {e}")
    
    def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """
        Register a new workflow definition
        
        Args:
            workflow_def: Workflow definition to register
            
        Returns:
            True if registered successfully
        """
        try:
            # Validate workflow definition
            validation_result = self._validate_workflow_definition(workflow_def)
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid workflow definition: {validation_result['errors']}")
            
            # Register workflow
            self.workflow_definitions[workflow_def.id] = workflow_def
            
            if self.logger:
                self.logger.info(f"Workflow registered: {workflow_def.id} ({workflow_def.name})")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to register workflow {workflow_def.id}: {e}")
            return False
    
    def execute_workflow(
        self, 
        workflow_id: str, 
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start workflow execution
        
        Args:
            workflow_id: ID of workflow to execute
            context_data: Initial context data
            
        Returns:
            Execution ID
        """
        import uuid
        
        try:
            # Get workflow definition
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow_def = self.workflow_definitions[workflow_id]
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.PENDING,
                definition=workflow_def,
                step_results={},
                context_data=context_data or {},
                started_at=datetime.now()
            )
            
            # Add to active executions
            self.active_executions[execution_id] = execution
            
            # Start execution
            self._execute_workflow_async(execution)
            
            if self.logger:
                self.logger.info(f"Workflow execution started: {workflow_id} ({execution_id})")
            
            return execution_id
            
        except Exception as e:
            if self.error_handler:
                error_context = self.error_handler.handle_error(e)
                error_message = error_context.user_message
            else:
                error_message = str(e)
            
            if self.logger:
                self.logger.error(f"Failed to start workflow execution: {error_message}")
            
            raise
    
    def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        import threading
        
        def execute():
            try:
                execution.status = WorkflowStatus.RUNNING
                
                if execution.definition.execution_mode == ExecutionMode.SEQUENTIAL:
                    self._execute_sequential_workflow(execution)
                elif execution.definition.execution_mode == ExecutionMode.PARALLEL:
                    self._execute_parallel_workflow(execution)
                else:
                    raise ValueError(f"Unsupported execution mode: {execution.definition.execution_mode}")
                
                # Complete execution
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
                
            except Exception as e:
                execution.status = WorkflowStatus.FAILED
                execution.completed_at = datetime.now()
                execution.execution_log.append(f"Workflow failed: {str(e)}")
                
                if self.logger:
                    self.logger.error(f"Workflow execution failed: {execution.execution_id} - {e}")
            
            finally:
                # Move to history
                self.execution_history.append(execution)
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
        
        # Start execution in background thread
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
    
    def _execute_sequential_workflow(self, execution: WorkflowExecution):
        """Execute workflow steps sequentially"""
        # Build dependency graph
        completed_steps = set()
        
        while len(completed_steps) < len(execution.definition.steps):
            # Find next executable step
            next_step = None
            
            for step in execution.definition.steps:
                if (step.id not in completed_steps and 
                    all(dep in completed_steps for dep in step.dependencies)):
                    next_step = step
                    break
            
            if not next_step:
                raise RuntimeError("Workflow deadlock - no executable steps found")
            
            # Execute step
            execution.current_step = next_step.id
            step_result = self._execute_step(next_step, execution)
            execution.step_results[next_step.id] = step_result
            
            if step_result.status == WorkflowStatus.FAILED and not next_step.continue_on_error:
                raise RuntimeError(f"Step failed: {next_step.id} - {step_result.error_message}")
            
            completed_steps.add(next_step.id)
            execution.execution_log.append(f"Completed step: {next_step.id}")
    
    def _execute_parallel_workflow(self, execution: WorkflowExecution):
        """Execute workflow steps in parallel where possible"""
        import concurrent.futures
        
        completed_steps = set()
        
        while len(completed_steps) < len(execution.definition.steps):
            # Find all executable steps
            executable_steps = [
                step for step in execution.definition.steps
                if (step.id not in completed_steps and 
                    all(dep in completed_steps for dep in step.dependencies))
            ]
            
            if not executable_steps:
                raise RuntimeError("Workflow deadlock - no executable steps found")
            
            # Execute steps in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_step = {
                    executor.submit(self._execute_step, step, execution): step
                    for step in executable_steps
                }
                
                for future in concurrent.futures.as_completed(future_to_step):
                    step = future_to_step[future]
                    step_result = future.result()
                    
                    execution.step_results[step.id] = step_result
                    
                    if step_result.status == WorkflowStatus.FAILED and not step.continue_on_error:
                        raise RuntimeError(f"Step failed: {step.id} - {step_result.error_message}")
                    
                    completed_steps.add(step.id)
                    execution.execution_log.append(f"Completed step: {step.id}")
    
    def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> StepResult:
        """Execute a single workflow step"""
        start_time = datetime.now()
        
        step_result = StepResult(
            step_id=step.id,
            status=WorkflowStatus.RUNNING,
            started_at=start_time
        )
        
        try:
            # Check condition if specified
            if step.condition_script:
                condition_met = self._evaluate_condition(step.condition_script, execution.context_data)
                if not condition_met:
                    step_result.status = WorkflowStatus.COMPLETED
                    step_result.output_data = "Skipped due to condition"
                    return step_result
            
            # Execute step based on type
            if step.step_type == StepType.DOCUMENT_ANALYSIS:
                step_result.output_data = self._execute_document_analysis_step(step, execution)
            elif step.step_type == StepType.TEMPLATE_VALIDATION:
                step_result.output_data = self._execute_template_validation_step(step, execution)
            elif step.step_type == StepType.CUSTOM_SCRIPT:
                step_result.output_data = self._execute_custom_script_step(step, execution)
            elif step.step_type == StepType.CONDITION_CHECK:
                step_result.output_data = self._execute_condition_check_step(step, execution)
            else:
                raise ValueError(f"Unsupported step type: {step.step_type}")
            
            step_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            step_result.status = WorkflowStatus.FAILED
            step_result.error_message = str(e)
            
            if self.logger:
                self.logger.error(f"Step execution failed: {step.id} - {e}")
        
        finally:
            step_result.completed_at = datetime.now()
            step_result.execution_time = (step_result.completed_at - start_time).total_seconds()
        
        return step_result
    
    def _execute_document_analysis_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute document analysis step"""
        # This would integrate with the document analyzer
        config = step.configuration
        document_path = execution.context_data.get('document_path')
        
        if not document_path:
            raise ValueError("Document path not provided in context")
        
        # Simulate document analysis
        return {
            'document_analyzed': True,
            'document_path': document_path,
            'analysis_config': config
        }
    
    def _execute_template_validation_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute template validation step"""
        # This would integrate with the template processor
        config = step.configuration
        template_name = config.get('template_name', 'eu_doc')
        
        # Get analysis result from previous step
        analysis_step_id = step.dependencies[0] if step.dependencies else None
        if analysis_step_id and analysis_step_id in execution.step_results:
            analysis_result = execution.step_results[analysis_step_id].output_data
        else:
            analysis_result = None
        
        # Simulate template validation
        return {
            'template_validated': True,
            'template_name': template_name,
            'validation_config': config,
            'analysis_input': analysis_result
        }
    
    def _execute_custom_script_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute custom script step"""
        config = step.configuration
        script_path = config.get('script_path')
        
        if not script_path:
            raise ValueError("Script path not specified")
        
        # Prepare context data
        script_context = execution.context_data.copy()
        script_context.update(config.get('parameters', {}))
        
        # Add results from previous steps
        for step_id, result in execution.step_results.items():
            script_context[f'step_{step_id}_result'] = result.output_data
        
        # Execute script
        success, result, error = self.script_executor.execute_script(script_path, script_context)
        
        if not success:
            raise RuntimeError(f"Script execution failed: {error}")
        
        return result
    
    def _execute_condition_check_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Any:
        """Execute condition check step"""
        config = step.configuration
        
        # Get validation result from previous step
        validation_step_id = step.dependencies[0] if step.dependencies else None
        if validation_step_id and validation_step_id in execution.step_results:
            validation_result = execution.step_results[validation_step_id].output_data
        else:
            raise ValueError("No validation result available for condition check")
        
        # Check conditions
        checks = []
        
        min_compliance = config.get('min_compliance_percentage')
        if min_compliance is not None:
            # This would check actual compliance from validation result
            compliance_met = True  # Simulated
            checks.append({
                'condition': f'compliance >= {min_compliance}%',
                'passed': compliance_met
            })
        
        max_critical = config.get('max_critical_issues')
        if max_critical is not None:
            # This would check actual critical issues count
            critical_count = 0  # Simulated
            critical_check = critical_count <= max_critical
            checks.append({
                'condition': f'critical_issues <= {max_critical}',
                'passed': critical_check
            })
        
        all_passed = all(check['passed'] for check in checks)
        
        return {
            'condition_checks': checks,
            'all_conditions_passed': all_passed,
            'validation_input': validation_result
        }
    
    def _evaluate_condition(self, condition_script: str, context_data: Dict[str, Any]) -> bool:
        """Evaluate a condition script"""
        try:
            # Simple condition evaluation (would be expanded in production)
            # This is a simplified implementation
            local_vars = context_data.copy()
            return bool(eval(condition_script, {"__builtins__": {}}, local_vars))
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def _validate_workflow_definition(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        if not workflow_def.id:
            validation_result['errors'].append("Workflow ID is required")
        
        if not workflow_def.name:
            validation_result['errors'].append("Workflow name is required")
        
        if not workflow_def.steps:
            validation_result['errors'].append("Workflow must have at least one step")
        
        # Check step dependencies
        step_ids = {step.id for step in workflow_def.steps}
        
        for step in workflow_def.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    validation_result['errors'].append(f"Step {step.id} depends on unknown step: {dep}")
        
        # Check for circular dependencies (simplified)
        # In production, this would use proper graph algorithms
        
        validation_result['is_valid'] = len(validation_result['errors']) == 0
        return validation_result
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution
        
        return None
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            execution.execution_log.append("Workflow cancelled by user")
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            if self.logger:
                self.logger.info(f"Workflow cancelled: {execution_id}")
            
            return True
        
        return False
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflow definitions"""
        return [
            {
                'id': wf.id,
                'name': wf.name,
                'description': wf.description,
                'version': wf.version,
                'steps_count': len(wf.steps),
                'execution_mode': wf.execution_mode.value
            }
            for wf in self.workflow_definitions.values()
        ]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        total_executions = len(self.execution_history) + len(self.active_executions)
        
        completed_count = len([ex for ex in self.execution_history if ex.status == WorkflowStatus.COMPLETED])
        failed_count = len([ex for ex in self.execution_history if ex.status == WorkflowStatus.FAILED])
        active_count = len(self.active_executions)
        
        return {
            'total_executions': total_executions,
            'completed_executions': completed_count,
            'failed_executions': failed_count,
            'active_executions': active_count,
            'success_rate': (completed_count / max(1, total_executions - active_count)) * 100,
            'available_workflows': len(self.workflow_definitions)
        }


def create_workflow_manager(config: Optional[Dict[str, Any]] = None) -> WorkflowManager:
    """
    Create and return a WorkflowManager instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured WorkflowManager instance
    """
    return WorkflowManager(config=config)
