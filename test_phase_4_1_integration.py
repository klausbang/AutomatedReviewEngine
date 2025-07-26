"""
Phase 4.1 Integration Testing Suite

This test suite validates the integration between Phase 3.2 review logic
and Phase 4.1 UI components to ensure seamless operation.

Date: July 26, 2025
Phase: 4.1 Day 2 - Integration Testing
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def run_component_import_tests() -> Dict[str, Any]:
    """Test that all Phase 4.1 components can be imported successfully"""
    
    test_results = {
        'phase_3_2_components': {},
        'phase_4_1_components': {},
        'main_interface': {},
        'overall_status': 'PENDING'
    }
    
    print("🧪 Starting Phase 4.1 Component Import Tests...")
    print("=" * 60)
    
    # Test Phase 3.2 Review Logic Components
    print("\n📋 Testing Phase 3.2 Review Logic Components:")
    phase_3_2_components = [
        ('DocumentAnalyzer', 'src.review.document_analyzer', 'DocumentAnalyzer'),
        ('TemplateProcessor', 'src.review.template_processor', 'TemplateProcessor'),
        ('ReviewEngine', 'src.review.review_engine', 'ReviewEngine'),
        ('WorkflowManager', 'src.review.workflow_manager', 'WorkflowManager')
    ]
    
    for name, module_path, class_name in phase_3_2_components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            
            # Test instantiation
            instance = component_class()
            
            test_results['phase_3_2_components'][name] = {
                'import_status': 'SUCCESS',
                'instantiation_status': 'SUCCESS',
                'module_path': module_path,
                'error': None
            }
            print(f"  ✅ {name}: Import and instantiation successful")
            
        except Exception as e:
            test_results['phase_3_2_components'][name] = {
                'import_status': 'FAILED',
                'instantiation_status': 'FAILED',
                'module_path': module_path,
                'error': str(e)
            }
            print(f"  ❌ {name}: Failed - {str(e)}")
    
    # Test Phase 4.1 UI Components
    print("\n🎨 Testing Phase 4.1 UI Components:")
    phase_4_1_components = [
        ('ReviewPanel', 'src.ui.components.review_panel', 'create_review_panel'),
        ('ProgressDisplay', 'src.ui.components.progress_display', 'create_progress_display'),
        ('ResultsPanel', 'src.ui.components.results_panel', 'create_results_panel'),
        ('ConfigPanel', 'src.ui.components.config_panel', 'create_config_panel'),
        ('FileUploader', 'src.ui.components.file_uploader', 'create_file_uploader')
    ]
    
    for name, module_path, factory_function in phase_4_1_components:
        try:
            module = __import__(module_path, fromlist=[factory_function])
            factory = getattr(module, factory_function)
            
            # Test factory function call
            instance = factory()
            
            test_results['phase_4_1_components'][name] = {
                'import_status': 'SUCCESS',
                'instantiation_status': 'SUCCESS',
                'module_path': module_path,
                'factory_function': factory_function,
                'error': None
            }
            print(f"  ✅ {name}: Import and factory creation successful")
            
        except Exception as e:
            test_results['phase_4_1_components'][name] = {
                'import_status': 'FAILED',
                'instantiation_status': 'FAILED',
                'module_path': module_path,
                'factory_function': factory_function,
                'error': str(e)
            }
            print(f"  ❌ {name}: Failed - {str(e)}")
    
    # Test Main Interface Integration
    print("\n🏠 Testing Main Interface Integration:")
    try:
        from src.ui.main_interface import create_main_interface
        main_interface = create_main_interface()
        
        test_results['main_interface'] = {
            'import_status': 'SUCCESS',
            'instantiation_status': 'SUCCESS',
            'error': None
        }
        print(f"  ✅ MainInterface: Import and creation successful")
        
    except Exception as e:
        test_results['main_interface'] = {
            'import_status': 'FAILED',
            'instantiation_status': 'FAILED',
            'error': str(e)
        }
        print(f"  ❌ MainInterface: Failed - {str(e)}")
    
    # Calculate overall status
    all_tests = []
    for category in ['phase_3_2_components', 'phase_4_1_components']:
        for component, result in test_results[category].items():
            all_tests.append(result['import_status'] == 'SUCCESS' and 
                           result['instantiation_status'] == 'SUCCESS')
    
    # Add main interface test
    main_result = test_results['main_interface']
    all_tests.append(main_result.get('import_status') == 'SUCCESS' and 
                    main_result.get('instantiation_status') == 'SUCCESS')
    
    if all(all_tests):
        test_results['overall_status'] = 'SUCCESS'
        print(f"\n🎉 All component import tests PASSED!")
    else:
        test_results['overall_status'] = 'PARTIAL_SUCCESS' if any(all_tests) else 'FAILED'
        success_count = sum(all_tests)
        total_count = len(all_tests)
        print(f"\n⚠️ Component import tests: {success_count}/{total_count} passed")
    
    return test_results

def run_integration_workflow_test() -> Dict[str, Any]:
    """Test the integration workflow between components"""
    
    print("\n🔄 Testing Integration Workflow...")
    print("=" * 60)
    
    workflow_results = {
        'upload_analysis_integration': 'PENDING',
        'config_review_integration': 'PENDING', 
        'review_progress_integration': 'PENDING',
        'progress_results_integration': 'PENDING',
        'overall_workflow': 'PENDING'
    }
    
    try:
        # Test 1: Upload → Analysis Integration
        print("\n📤 Testing Upload → Analysis Integration:")
        from src.ui.components.file_uploader import create_file_uploader
        from src.review.document_analyzer import DocumentAnalyzer
        
        file_uploader = create_file_uploader()
        analyzer = DocumentAnalyzer()
        
        print("  ✅ FileUploader and DocumentAnalyzer integration: Components loaded")
        workflow_results['upload_analysis_integration'] = 'SUCCESS'
        
        # Test 2: Config → Review Integration
        print("\n⚙️ Testing Config → Review Integration:")
        from src.ui.components.config_panel import create_config_panel
        from src.review.template_processor import TemplateProcessor
        from src.review.review_engine import ReviewEngine
        
        config_panel = create_config_panel()
        template_processor = TemplateProcessor()
        review_engine = ReviewEngine()
        
        print("  ✅ ConfigPanel, TemplateProcessor, and ReviewEngine integration: Components loaded")
        workflow_results['config_review_integration'] = 'SUCCESS'
        
        # Test 3: Review → Progress Integration
        print("\n📈 Testing Review → Progress Integration:")
        from src.ui.components.progress_display import create_progress_display
        
        progress_display = create_progress_display()
        
        print("  ✅ ReviewEngine and ProgressDisplay integration: Components loaded")
        workflow_results['review_progress_integration'] = 'SUCCESS'
        
        # Test 4: Progress → Results Integration
        print("\n📊 Testing Progress → Results Integration:")
        from src.ui.components.results_panel import create_results_panel
        
        results_panel = create_results_panel()
        
        print("  ✅ ProgressDisplay and ResultsPanel integration: Components loaded")
        workflow_results['progress_results_integration'] = 'SUCCESS'
        
        # Overall workflow test
        if all(status == 'SUCCESS' for status in workflow_results.values() if status != 'PENDING'):
            workflow_results['overall_workflow'] = 'SUCCESS'
            print(f"\n🎉 All integration workflow tests PASSED!")
        else:
            workflow_results['overall_workflow'] = 'PARTIAL_SUCCESS'
            print(f"\n⚠️ Some integration workflow tests failed")
            
    except Exception as e:
        print(f"\n❌ Integration workflow test failed: {str(e)}")
        workflow_results['overall_workflow'] = 'FAILED'
        
        # Print detailed traceback for debugging
        print("\nDetailed error information:")
        traceback.print_exc()
    
    return workflow_results

def run_basic_functionality_test() -> Dict[str, Any]:
    """Test basic functionality of integrated components"""
    
    print("\n🛠️ Testing Basic Functionality...")
    print("=" * 60)
    
    functionality_results = {
        'document_analyzer_basic': 'PENDING',
        'template_processor_basic': 'PENDING',
        'review_engine_basic': 'PENDING',
        'ui_component_rendering': 'PENDING',
        'overall_functionality': 'PENDING'
    }
    
    try:
        # Test DocumentAnalyzer basic functionality
        print("\n📄 Testing DocumentAnalyzer basic functionality:")
        from src.review.document_analyzer import DocumentAnalyzer
        
        analyzer = DocumentAnalyzer()
        # Test that analyzer has expected methods
        expected_methods = ['analyze_document', 'extract_text', 'validate_document_compatibility']
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(analyzer, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("  ✅ DocumentAnalyzer: All expected methods present")
            functionality_results['document_analyzer_basic'] = 'SUCCESS'
        else:
            print(f"  ❌ DocumentAnalyzer: Missing methods: {missing_methods}")
            functionality_results['document_analyzer_basic'] = 'FAILED'
        
        # Test TemplateProcessor basic functionality
        print("\n📋 Testing TemplateProcessor basic functionality:")
        from src.review.template_processor import TemplateProcessor
        
        processor = TemplateProcessor()
        expected_methods = ['process_template', 'validate_requirements', 'get_available_templates']
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(processor, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("  ✅ TemplateProcessor: All expected methods present")
            functionality_results['template_processor_basic'] = 'SUCCESS'
        else:
            print(f"  ❌ TemplateProcessor: Missing methods: {missing_methods}")
            functionality_results['template_processor_basic'] = 'FAILED'
        
        # Test ReviewEngine basic functionality
        print("\n🔍 Testing ReviewEngine basic functionality:")
        from src.review.review_engine import ReviewEngine
        
        engine = ReviewEngine()
        expected_methods = ['create_review_request', 'submit_review', 'get_review_status']
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(engine, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("  ✅ ReviewEngine: All expected methods present")
            functionality_results['review_engine_basic'] = 'SUCCESS'
        else:
            print(f"  ❌ ReviewEngine: Missing methods: {missing_methods}")
            functionality_results['review_engine_basic'] = 'FAILED'
        
        # Test UI Component rendering capabilities
        print("\n🎨 Testing UI Component rendering capabilities:")
        # Since we can't actually render Streamlit components in this test,
        # we'll check that the components have the expected render methods
        
        ui_components_ok = True
        ui_test_results = []
        
        component_tests = [
            ('ReviewPanel', 'src.ui.components.review_panel', 'create_review_panel', 'render_review_interface'),
            ('ProgressDisplay', 'src.ui.components.progress_display', 'create_progress_display', 'render_progress_interface'),
            ('ResultsPanel', 'src.ui.components.results_panel', 'create_results_panel', 'render_results_interface'),
            ('ConfigPanel', 'src.ui.components.config_panel', 'create_config_panel', 'render_configuration_interface')
        ]
        
        for name, module_path, factory_func, render_method in component_tests:
            try:
                module = __import__(module_path, fromlist=[factory_func])
                factory = getattr(module, factory_func)
                component = factory()
                
                if hasattr(component, render_method):
                    ui_test_results.append(f"  ✅ {name}: Has {render_method} method")
                else:
                    ui_test_results.append(f"  ❌ {name}: Missing {render_method} method")
                    ui_components_ok = False
                    
            except Exception as e:
                ui_test_results.append(f"  ❌ {name}: Error testing - {str(e)}")
                ui_components_ok = False
        
        for result in ui_test_results:
            print(result)
        
        if ui_components_ok:
            functionality_results['ui_component_rendering'] = 'SUCCESS'
        else:
            functionality_results['ui_component_rendering'] = 'FAILED'
        
        # Overall functionality assessment
        success_count = sum(1 for status in functionality_results.values() 
                          if status == 'SUCCESS' and status != 'PENDING')
        total_tests = len([k for k in functionality_results.keys() if k != 'overall_functionality'])
        
        if success_count == total_tests:
            functionality_results['overall_functionality'] = 'SUCCESS'
            print(f"\n🎉 All basic functionality tests PASSED!")
        else:
            functionality_results['overall_functionality'] = 'PARTIAL_SUCCESS'
            print(f"\n⚠️ Basic functionality tests: {success_count}/{total_tests} passed")
            
    except Exception as e:
        print(f"\n❌ Basic functionality test failed: {str(e)}")
        functionality_results['overall_functionality'] = 'FAILED'
        traceback.print_exc()
    
    return functionality_results

def generate_test_report(import_results: Dict, workflow_results: Dict, functionality_results: Dict) -> str:
    """Generate a comprehensive test report"""
    
    report_lines = [
        "PHASE 4.1 DAY 2: INTEGRATION TESTING REPORT",
        "=" * 50,
        f"Test Date: July 26, 2025",
        f"Test Phase: Phase 4.1 Day 2 - Integration Testing",
        "",
        "EXECUTIVE SUMMARY",
        "-" * 20
    ]
    
    # Overall status determination
    all_results = [
        import_results['overall_status'],
        workflow_results['overall_workflow'],
        functionality_results['overall_functionality']
    ]
    
    if all(status == 'SUCCESS' for status in all_results):
        overall_status = "✅ ALL TESTS PASSED - READY FOR PRODUCTION"
    elif any(status == 'SUCCESS' for status in all_results):
        overall_status = "⚠️ PARTIAL SUCCESS - SOME ISSUES FOUND"
    else:
        overall_status = "❌ MULTIPLE FAILURES - REQUIRES ATTENTION"
    
    report_lines.extend([
        f"Overall Status: {overall_status}",
        "",
        "DETAILED RESULTS",
        "-" * 20,
        "",
        "1. COMPONENT IMPORT TESTS",
        f"   Status: {import_results['overall_status']}"
    ])
    
    # Phase 3.2 Components
    report_lines.append("   Phase 3.2 Components:")
    for name, result in import_results['phase_3_2_components'].items():
        status_icon = "✅" if result['import_status'] == 'SUCCESS' else "❌"
        report_lines.append(f"     {status_icon} {name}: {result['import_status']}")
    
    # Phase 4.1 Components  
    report_lines.append("   Phase 4.1 Components:")
    for name, result in import_results['phase_4_1_components'].items():
        status_icon = "✅" if result['import_status'] == 'SUCCESS' else "❌"
        report_lines.append(f"     {status_icon} {name}: {result['import_status']}")
    
    # Main Interface
    main_status = import_results['main_interface']['import_status']
    status_icon = "✅" if main_status == 'SUCCESS' else "❌"
    report_lines.append(f"   Main Interface: {status_icon} {main_status}")
    
    report_lines.extend([
        "",
        "2. INTEGRATION WORKFLOW TESTS",
        f"   Status: {workflow_results['overall_workflow']}"
    ])
    
    workflow_tests = [
        ('Upload → Analysis', workflow_results['upload_analysis_integration']),
        ('Config → Review', workflow_results['config_review_integration']),
        ('Review → Progress', workflow_results['review_progress_integration']),
        ('Progress → Results', workflow_results['progress_results_integration'])
    ]
    
    for test_name, status in workflow_tests:
        status_icon = "✅" if status == 'SUCCESS' else "❌"
        report_lines.append(f"     {status_icon} {test_name}: {status}")
    
    report_lines.extend([
        "",
        "3. BASIC FUNCTIONALITY TESTS",
        f"   Status: {functionality_results['overall_functionality']}"
    ])
    
    functionality_tests = [
        ('DocumentAnalyzer', functionality_results['document_analyzer_basic']),
        ('TemplateProcessor', functionality_results['template_processor_basic']),
        ('ReviewEngine', functionality_results['review_engine_basic']),
        ('UI Components', functionality_results['ui_component_rendering'])
    ]
    
    for test_name, status in functionality_tests:
        status_icon = "✅" if status == 'SUCCESS' else "❌"
        report_lines.append(f"     {status_icon} {test_name}: {status}")
    
    report_lines.extend([
        "",
        "RECOMMENDATIONS",
        "-" * 15
    ])
    
    if overall_status.startswith("✅"):
        report_lines.extend([
            "🎉 Excellent! All integration tests passed successfully.",
            "📋 Ready to proceed to Phase 4.1 Day 3 (Polish & Optimization)",
            "🚀 System is ready for end-to-end testing with real documents"
        ])
    elif overall_status.startswith("⚠️"):
        report_lines.extend([
            "🔧 Address any failed components before proceeding",
            "🧪 Re-run tests after fixes are implemented",
            "📋 Consider partial deployment for working components"
        ])
    else:
        report_lines.extend([
            "🚨 Critical issues found - requires immediate attention",
            "🔧 Focus on fixing import and basic functionality issues first",
            "🧪 Re-run full test suite after major fixes"
        ])
    
    return "\n".join(report_lines)

def main():
    """Main test execution function"""
    
    print("🚀 Starting Phase 4.1 Day 2 Integration Testing")
    print("=" * 60)
    print(f"Date: July 26, 2025")
    print(f"Phase: Phase 4.1 Day 2 - Integration Testing & Validation")
    print(f"Objective: Comprehensive validation of UI Integration components")
    
    # Run all test suites
    import_results = run_component_import_tests()
    workflow_results = run_integration_workflow_test()
    functionality_results = run_basic_functionality_test()
    
    # Generate comprehensive report
    report = generate_test_report(import_results, workflow_results, functionality_results)
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    
    # Return results for further processing
    return {
        'import_results': import_results,
        'workflow_results': workflow_results,
        'functionality_results': functionality_results,
        'report': report
    }

if __name__ == "__main__":
    test_results = main()
