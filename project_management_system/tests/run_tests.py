#!/usr/bin/env python3
"""
Test runner script for the Multi-Agent Project Management System.

This script provides a convenient way to run tests with various options:
- Run all tests
- Run specific test categories
- Run tests with different output formats
- Run performance tests
- Generate test reports
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        print("Please install pytest: pip install pytest pytest-asyncio")
        return False


def run_pytest_tests(test_paths: List[str], markers: Optional[List[str]] = None, 
                     output_format: str = "verbose", coverage: bool = False) -> bool:
    """Run pytest with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    # Add test paths
    cmd.extend(test_paths)
    
    # Add markers if specified
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    # Add output format
    if output_format == "verbose":
        cmd.append("-v")
    elif output_format == "quiet":
        cmd.append("-q")
    elif output_format == "minimal":
        cmd.append("--tb=short")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=project_management_system", "--cov-report=html", "--cov-report=term"])
    
    # Add other useful options
    cmd.extend([
        "--strict-markers",  # Ensure markers are properly defined
        "--tb=auto",         # Auto-determine traceback format
        "--durations=10",    # Show 10 slowest tests
    ])
    
    return run_command(cmd, "Pytest Tests")


def run_unittest_tests(test_paths: List[str]) -> bool:
    """Run unittest tests (fallback for tests not yet converted to pytest)."""
    # Add the project root to Python path for imports
    import sys
    import os
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variable to help with imports
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Change to the project root directory for running tests
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        cmd = ["python", "-m", "unittest", "discover"]
        
        if test_paths:
            cmd.extend(["-s", "-p", "*test*.py"])
            cmd.extend(test_paths)
        
        cmd.extend(["-v"])
        
        return run_command(cmd, "Unittest Tests")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def run_specific_test_category(category: str, output_format: str = "verbose") -> bool:
    """Run tests for a specific category."""
    test_mapping = {
        "knowledge_base": ["test_knowledge_base.py"],
        "document_store": ["test_document_store.py"],
        "agents": ["test_agents.py"],
        "unit": ["-m", "unit"],
        "integration": ["-m", "integration"],
        "performance": ["-m", "performance"],
        "all": []
    }
    
    if category not in test_mapping:
        print(f"Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_mapping.keys())}")
        return False
    
    if category == "all":
        return run_pytest_tests(["."], output_format=output_format)
    elif category in ["unit", "integration", "performance"]:
        return run_pytest_tests(["."], markers=[category], output_format=output_format)
    else:
        return run_pytest_tests(test_mapping[category], output_format=output_format)


def generate_test_report() -> bool:
    """Generate a comprehensive test report."""
    print("\nGenerating test report...")
    
    # Run tests with coverage
    success = run_pytest_tests(["."], output_format="quiet", coverage=True)
    
    if success:
        print("\nTest report generated successfully!")
        print("Coverage report available in htmlcov/index.html")
    
    return success


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for the Multi-Agent Project Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -c knowledge_base # Run only knowledge base tests
  python run_tests.py -m unit           # Run only unit tests
  python run_tests.py -o quiet          # Run tests with quiet output
  python run_tests.py --coverage        # Run tests with coverage report
  python run_tests.py --report          # Generate comprehensive test report
        """
    )
    
    parser.add_argument(
        "-c", "--category",
        choices=["knowledge_base", "document_store", "agents", "unit", "integration", "performance", "all"],
        default="all",
        help="Test category to run (default: all)"
    )
    
    parser.add_argument(
        "-o", "--output",
        choices=["verbose", "quiet", "minimal"],
        default="verbose",
        help="Output format (default: verbose)"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive test report with coverage"
    )
    
    parser.add_argument(
        "--unittest",
        action="store_true",
        help="Use unittest instead of pytest (fallback)"
    )
    
    args = parser.parse_args()
    
    # Change to tests directory
    tests_dir = Path(__file__).parent
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return 1
    
    os.chdir(tests_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Handle special cases
    if args.report:
        return 0 if generate_test_report() else 1
    
    # Run tests
    if args.unittest:
        success = run_unittest_tests([])
    else:
        success = run_specific_test_category(args.category, args.output)
        
        # Add coverage if requested
        if success and args.coverage:
            print("\nRunning tests with coverage...")
            success = run_pytest_tests(["."], output_format=args.output, coverage=True)
    
    if success:
        print("\n✅ All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    import os
    sys.exit(main())
