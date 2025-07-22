"""
Performance Benchmarks for Phase 2.3

This module provides performance testing and benchmarking capabilities
for the Automated Review Engine core components.
"""

import time
import psutil
import json
import tempfile
import statistics
from pathlib import Path
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from contextlib import contextmanager

import sys
import os
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from src.core.config_manager import ConfigManager
    from src.core.logging_manager import LoggingManager
    from src.core.error_handler import ErrorHandler
    from src.core.validation_utils import DataValidator
except ImportError:
    # Alternative import for direct execution
    sys.path.append(str(project_root / "src" / "core"))
    from config_manager import ConfigManager
    from logging_manager import LoggingManager
    from error_handler import ErrorHandler
    from validation_utils import DataValidator


@dataclass
class BenchmarkResult:
    """Results of a performance benchmark"""
    name: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    iterations: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    success_rate: float


class PerformanceBenchmark:
    """Performance benchmarking utility"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()
        
    @contextmanager
    def measure_performance(self, name: str):
        """Context manager for measuring performance"""
        # Get initial metrics
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()
        
        try:
            yield
        finally:
            # Get final metrics
            end_time = time.perf_counter()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()
            
            duration_ms = (end_time - start_time) * 1000
            memory_mb = end_memory - start_memory
            cpu_percent = end_cpu - start_cpu
            
            print(f"⏱️  {name}: {duration_ms:.2f}ms, {memory_mb:.2f}MB, {cpu_percent:.1f}% CPU")
    
    def benchmark_function(self, 
                          func: Callable, 
                          name: str, 
                          iterations: int = 100,
                          *args, **kwargs) -> BenchmarkResult:
        """Benchmark a function with multiple iterations"""
        
        print(f"\n🔄 Benchmarking {name} ({iterations} iterations)...")
        
        times = []
        successes = 0
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        overall_start = time.perf_counter()
        
        for i in range(iterations):
            try:
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                duration_ms = (end_time - start_time) * 1000
                times.append(duration_ms)
                successes += 1
                
                if i % (iterations // 10) == 0:  # Progress indicator
                    print(f"   Progress: {i+1}/{iterations} ({duration_ms:.2f}ms)")
                    
            except Exception as e:
                print(f"   ❌ Iteration {i+1} failed: {e}")
        
        overall_end = time.perf_counter()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        end_cpu = self.process.cpu_percent()
        
        # Calculate statistics
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        else:
            avg_time = min_time = max_time = std_dev = 0.0
        
        result = BenchmarkResult(
            name=name,
            duration_ms=(overall_end - overall_start) * 1000,
            memory_mb=end_memory - start_memory,
            cpu_percent=end_cpu - start_cpu,
            iterations=iterations,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            std_dev_ms=std_dev,
            success_rate=(successes / iterations) * 100
        )
        
        self.results.append(result)
        return result
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n🎯 {result.name}")
            print(f"   Duration: {result.duration_ms:.2f}ms total")
            print(f"   Average:  {result.avg_time_ms:.3f}ms per operation")
            print(f"   Range:    {result.min_time_ms:.3f}ms - {result.max_time_ms:.3f}ms")
            print(f"   Std Dev:  {result.std_dev_ms:.3f}ms")
            print(f"   Memory:   {result.memory_mb:.2f}MB delta")
            print(f"   Success:  {result.success_rate:.1f}% ({result.iterations} iterations)")
    
    def save_results(self, output_file: Path):
        """Save benchmark results to JSON file"""
        data = {
            'timestamp': time.time(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'python_version': sys.version
            },
            'results': [
                {
                    'name': r.name,
                    'duration_ms': r.duration_ms,
                    'memory_mb': r.memory_mb,
                    'cpu_percent': r.cpu_percent,
                    'iterations': r.iterations,
                    'avg_time_ms': r.avg_time_ms,
                    'min_time_ms': r.min_time_ms,
                    'max_time_ms': r.max_time_ms,
                    'std_dev_ms': r.std_dev_ms,
                    'success_rate': r.success_rate
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📁 Benchmark results saved to: {output_file}")


def benchmark_config_manager():
    """Benchmark ConfigManager performance"""
    print("\n🔧 CONFIGURATION MANAGER BENCHMARKS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Benchmark config loading
        def load_config():
            manager = ConfigManager()
            return manager.load_config()
        
        benchmark.benchmark_function(
            load_config, 
            "ConfigManager.load_config()", 
            iterations=50
        )
        
        # Benchmark config updating
        def update_config():
            manager = ConfigManager()
            config = manager.load_config()
            updates = {
                'environment': 'benchmark',
                'files': {'max_file_size_mb': 75}
            }
            return manager.update_config(updates)
        
        benchmark.benchmark_function(
            update_config,
            "ConfigManager.update_config()",
            iterations=50
        )
        
        # Benchmark config saving
        def save_config():
            manager = ConfigManager()
            config = manager.load_config()
            output_file = temp_path / f"config_{time.time()}.yaml"
            return manager.save_config(output_file)
        
        benchmark.benchmark_function(
            save_config,
            "ConfigManager.save_config()",
            iterations=25
        )
    
    return benchmark


def benchmark_logging_manager():
    """Benchmark LoggingManager performance"""
    print("\n📝 LOGGING MANAGER BENCHMARKS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Benchmark logging initialization
        def init_logging():
            config = {
                'level': 'INFO',
                'file_path': str(temp_path / f"test_{time.time()}.log"),
                'file_enabled': True
            }
            manager = LoggingManager(config)
            return manager.initialize()
        
        benchmark.benchmark_function(
            init_logging,
            "LoggingManager.initialize()",
            iterations=20
        )
        
        # Benchmark log message writing
        manager = LoggingManager({
            'level': 'INFO',
            'file_path': str(temp_path / "benchmark.log"),
            'file_enabled': True
        })
        manager.initialize()
        logger = manager.get_logger('benchmark')
        
        def write_log():
            logger.info("Benchmark log message with some content")
            return True
        
        benchmark.benchmark_function(
            write_log,
            "Logger.info() message",
            iterations=1000
        )
        
        # Benchmark performance logging
        perf_logger = manager.get_performance_logger()
        
        def performance_log():
            op_id = f"bench_op_{time.time()}"
            perf_logger.log_operation_start(op_id, 'benchmark_operation')
            time.sleep(0.001)  # Simulate work
            perf_logger.log_operation_end(op_id, success=True)
            return True
        
        benchmark.benchmark_function(
            performance_log,
            "PerformanceLogger operation",
            iterations=100
        )
    
    return benchmark


def benchmark_error_handler():
    """Benchmark ErrorHandler performance"""
    print("\n🚨 ERROR HANDLER BENCHMARKS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Benchmark error handler initialization
    def init_error_handler():
        return ErrorHandler()
    
    benchmark.benchmark_function(
        init_error_handler,
        "ErrorHandler initialization",
        iterations=100
    )
    
    # Benchmark error handling
    handler = ErrorHandler()
    
    def handle_error():
        try:
            raise ValueError("Benchmark error message")
        except ValueError as e:
            return handler.handle_error(e)
    
    benchmark.benchmark_function(
        handle_error,
        "ErrorHandler.handle_error()",
        iterations=500
    )
    
    # Benchmark custom error handling
    from src.core.error_handler import ValidationError
    
    def handle_custom_error():
        try:
            raise ValidationError(
                "Benchmark validation error",
                field_name="test_field"
            )
        except ValidationError as e:
            return handler.handle_error(e)
    
    benchmark.benchmark_function(
        handle_custom_error,
        "Custom ValidationError handling",
        iterations=500
    )
    
    return benchmark


def benchmark_data_validator():
    """Benchmark DataValidator performance"""
    print("\n🔍 DATA VALIDATOR BENCHMARKS")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    # Benchmark validator initialization
    def init_validator():
        return DataValidator()
    
    benchmark.benchmark_function(
        init_validator,
        "DataValidator initialization",
        iterations=100
    )
    
    validator = DataValidator()
    
    # Benchmark dictionary validation
    test_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'score': 95.5
    }
    
    schema = {
        'name': ['required'],
        'email': ['required', 'email'],
        'age': ['required', 'positive'],
        'score': ['required', 'positive']
    }
    
    def validate_dict():
        return validator.validate_dict(test_data, schema)
    
    benchmark.benchmark_function(
        validate_dict,
        "DataValidator.validate_dict()",
        iterations=1000
    )
    
    # Benchmark file validation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Benchmark file content for validation testing. " * 100)
        temp_file = Path(f.name)
    
    try:
        file_config = {
            'max_file_size_mb': 1,
            'allowed_extensions': ['.txt']
        }
        
        def validate_file():
            return validator.validate_file_upload(temp_file, file_config)
        
        benchmark.benchmark_function(
            validate_file,
            "DataValidator.validate_file_upload()",
            iterations=200
        )
    finally:
        temp_file.unlink()
    
    # Benchmark content validation
    test_content = "This is test content for validation benchmarking. " * 50
    
    def validate_content():
        return validator.validate_document_content(test_content)
    
    benchmark.benchmark_function(
        validate_content,
        "DataValidator.validate_document_content()",
        iterations=500
    )
    
    return benchmark


def main():
    """Main benchmark runner"""
    print("🚀 PHASE 2.3 PERFORMANCE BENCHMARKS")
    print("=" * 80)
    print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / 1024**3:.1f}GB RAM")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    all_results = []
    
    # Run all benchmarks
    benchmarks = [
        benchmark_config_manager,
        benchmark_logging_manager,
        benchmark_error_handler,
        benchmark_data_validator
    ]
    
    for benchmark_func in benchmarks:
        try:
            result = benchmark_func()
            all_results.extend(result.results)
            result.print_summary()
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
    
    # Save combined results
    if all_results:
        output_file = Path("tests") / "benchmark_results.json"
        combined_benchmark = PerformanceBenchmark()
        combined_benchmark.results = all_results
        combined_benchmark.save_results(output_file)
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL PERFORMANCE SUMMARY")
    print("=" * 80)
    
    # Calculate overall metrics
    total_operations = sum(r.iterations for r in all_results)
    avg_performance = statistics.mean([r.avg_time_ms for r in all_results])
    total_memory = sum(r.memory_mb for r in all_results)
    
    print(f"📊 Total Operations: {total_operations:,}")
    print(f"⚡ Average Performance: {avg_performance:.3f}ms per operation")
    print(f"💾 Total Memory Delta: {total_memory:.2f}MB")
    print(f"✅ Overall Success Rate: {statistics.mean([r.success_rate for r in all_results]):.1f}%")
    
    # Performance targets
    print("\n🎯 PERFORMANCE TARGET ANALYSIS")
    print("-" * 40)
    
    targets = {
        "Configuration Loading": {"target": 50, "actual": None},
        "Logging Operations": {"target": 10, "actual": None},
        "Error Handling": {"target": 5, "actual": None},
        "Data Validation": {"target": 20, "actual": None}
    }
    
    for result in all_results:
        if "config" in result.name.lower():
            targets["Configuration Loading"]["actual"] = result.avg_time_ms
        elif "log" in result.name.lower() and "info" in result.name.lower():
            targets["Logging Operations"]["actual"] = result.avg_time_ms
        elif "error" in result.name.lower():
            targets["Error Handling"]["actual"] = result.avg_time_ms
        elif "validate" in result.name.lower() and "dict" in result.name.lower():
            targets["Data Validation"]["actual"] = result.avg_time_ms
    
    for name, data in targets.items():
        if data["actual"] is not None:
            status = "✅" if data["actual"] <= data["target"] else "⚠️"
            print(f"{status} {name}: {data['actual']:.3f}ms (target: {data['target']}ms)")
        else:
            print(f"❓ {name}: No data available")
    
    print(f"\n⏰ End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 Performance benchmarking complete!")


if __name__ == "__main__":
    main()
