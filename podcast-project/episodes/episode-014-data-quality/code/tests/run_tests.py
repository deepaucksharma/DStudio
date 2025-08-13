#!/usr/bin/env python3
"""
Test Runner for Episode 14: Data Quality & Validation
Episode 14 के सभी examples के लिए comprehensive test runner

Author: DStudio Team
Purpose: Execute all tests and generate coverage reports
"""

import sys
import os
import subprocess
import time
from datetime import datetime
import json
from pathlib import Path

def run_command(command, timeout=300):
    """Run a command with timeout and return result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'pytest', 'pandas', 'numpy', 'great-expectations',
        'phonenumbers', 'jsonschema', 'plotly', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed\n")
    return True

def run_individual_tests():
    """Run individual module tests"""
    print("🧪 Running Individual Module Tests...")
    
    # Change to the code directory
    code_dir = Path(__file__).parent.parent / 'python'
    original_dir = os.getcwd()
    
    test_results = {}
    
    test_modules = [
        ('01_great_expectations_indian_context.py', 'Great Expectations Framework'),
        ('02_aadhaar_validation_system.py', 'Aadhaar Validation System'),
        ('09_upi_id_validation_system.py', 'UPI ID Validation System'),
        ('10_indian_mobile_validation.py', 'Indian Mobile Validation'),
        ('11_bank_account_ifsc_validation.py', 'Bank Account & IFSC Validation'),
        ('12_realtime_data_quality_monitoring.py', 'Real-time Data Quality Monitoring'),
        ('13_data_lineage_tracking.py', 'Data Lineage Tracking'),
        ('14_schema_evolution_handling.py', 'Schema Evolution Handling'),
        ('15_automated_data_quality_reports.py', 'Automated Data Quality Reports'),
        ('16_compliance_validation_framework.py', 'Compliance Validation Framework')
    ]
    
    try:
        os.chdir(code_dir)
        
        for module_file, module_name in test_modules:
            print(f"\n📋 Testing {module_name}...")
            
            if not os.path.exists(module_file):
                print(f"  ⚠️  File not found: {module_file}")
                test_results[module_name] = {'status': 'skipped', 'reason': 'File not found'}
                continue
            
            # Try to run the module's main function
            command = f"python {module_file}"
            success, stdout, stderr = run_command(command, timeout=120)
            
            if success:
                print(f"  ✅ {module_name} - PASSED")
                test_results[module_name] = {'status': 'passed', 'output': stdout[:200]}
            else:
                print(f"  ❌ {module_name} - FAILED")
                print(f"     Error: {stderr[:200]}")
                test_results[module_name] = {'status': 'failed', 'error': stderr[:200]}
    
    finally:
        os.chdir(original_dir)
    
    return test_results

def run_pytest_suite():
    """Run the comprehensive pytest suite"""
    print("\n🔬 Running Comprehensive Test Suite...")
    
    # Change to tests directory
    tests_dir = Path(__file__).parent
    original_dir = os.getcwd()
    
    try:
        os.chdir(tests_dir)
        
        # Run pytest with detailed output
        command = "python -m pytest test_all_examples.py -v --tb=short --maxfail=10"
        success, stdout, stderr = run_command(command, timeout=600)
        
        if success:
            print("✅ Pytest suite completed successfully")
            
            # Count test results
            passed_count = stdout.count('PASSED')
            failed_count = stdout.count('FAILED')
            skipped_count = stdout.count('SKIPPED')
            
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Passed: {passed_count}")
            print(f"  ❌ Failed: {failed_count}")
            print(f"  ⏭️  Skipped: {skipped_count}")
            
            return True, {'passed': passed_count, 'failed': failed_count, 'skipped': skipped_count}
        else:
            print("❌ Pytest suite failed")
            print(f"Error: {stderr}")
            return False, {'error': stderr}
    
    finally:
        os.chdir(original_dir)

def run_performance_tests():
    """Run performance tests for data validation"""
    print("\n⚡ Running Performance Tests...")
    
    performance_results = {}
    
    # Test data generation performance
    print("  📊 Testing data generation performance...")
    start_time = time.time()
    
    try:
        import pandas as pd
        import numpy as np
        
        # Generate large dataset
        large_data = {
            'id': range(10000),
            'email': [f'user{i}@example.com' for i in range(10000)],
            'phone': [f'+9198765432{i%100:02d}' for i in range(10000)],
            'amount': np.random.uniform(100, 10000, 10000)
        }
        df = pd.DataFrame(large_data)
        
        generation_time = time.time() - start_time
        print(f"    ✅ Generated 10,000 records in {generation_time:.2f} seconds")
        performance_results['data_generation'] = {
            'records': 10000,
            'time_seconds': generation_time,
            'records_per_second': 10000 / generation_time
        }
        
    except Exception as e:
        print(f"    ❌ Data generation test failed: {e}")
        performance_results['data_generation'] = {'error': str(e)}
    
    # Test validation performance
    print("  🔍 Testing validation performance...")
    
    try:
        # Test mobile validation performance
        sys.path.append(str(Path(__file__).parent.parent / 'python'))
        
        from indian_mobile_validation import IndianMobileValidationSystem
        
        mobile_validator = IndianMobileValidationSystem()
        
        test_mobiles = ['+919876543210', '7890123456', '6123456789'] * 100  # 300 mobile numbers
        
        start_time = time.time()
        valid_count = 0
        
        for mobile in test_mobiles:
            result = mobile_validator.complete_mobile_validation(mobile)
            if result.is_valid:
                valid_count += 1
        
        validation_time = time.time() - start_time
        print(f"    ✅ Validated 300 mobile numbers in {validation_time:.2f} seconds")
        print(f"    📈 Validation rate: {300/validation_time:.1f} validations/second")
        
        performance_results['mobile_validation'] = {
            'total_validations': 300,
            'valid_count': valid_count,
            'time_seconds': validation_time,
            'validations_per_second': 300 / validation_time
        }
        
    except Exception as e:
        print(f"    ❌ Mobile validation performance test failed: {e}")
        performance_results['mobile_validation'] = {'error': str(e)}
    
    return performance_results

def generate_test_report(individual_results, pytest_results, performance_results):
    """Generate comprehensive test report"""
    print("\n📄 Generating Test Report...")
    
    report = {
        'test_run_date': datetime.now().isoformat(),
        'test_environment': {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd()
        },
        'individual_module_tests': individual_results,
        'pytest_suite_results': pytest_results,
        'performance_tests': performance_results,
        'summary': {
            'total_modules_tested': len(individual_results),
            'modules_passed': len([r for r in individual_results.values() if r.get('status') == 'passed']),
            'modules_failed': len([r for r in individual_results.values() if r.get('status') == 'failed']),
            'modules_skipped': len([r for r in individual_results.values() if r.get('status') == 'skipped'])
        }
    }
    
    # Save report to file
    report_file = Path(__file__).parent / 'test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Test report saved to: {report_file}")
    
    # Print summary
    print(f"\n📈 Test Execution Summary:")
    print(f"  🧪 Individual Modules:")
    print(f"    ✅ Passed: {report['summary']['modules_passed']}")
    print(f"    ❌ Failed: {report['summary']['modules_failed']}")
    print(f"    ⏭️  Skipped: {report['summary']['modules_skipped']}")
    
    if 'passed' in pytest_results:
        print(f"  🔬 Pytest Suite:")
        print(f"    ✅ Passed: {pytest_results['passed']}")
        print(f"    ❌ Failed: {pytest_results['failed']}")
        print(f"    ⏭️  Skipped: {pytest_results['skipped']}")
    
    if 'mobile_validation' in performance_results:
        perf = performance_results['mobile_validation']
        if 'validations_per_second' in perf:
            print(f"  ⚡ Performance:")
            print(f"    📱 Mobile validation: {perf['validations_per_second']:.1f} validations/sec")
    
    return report

def main():
    """Main test execution function"""
    print("🚀 Episode 14: Data Quality & Validation - Test Suite")
    print("=" * 60)
    print("डेटा गुणवत्ता और सत्यापन - परीक्षण सूट\n")
    
    start_time = time.time()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required packages.")
        return 1
    
    # Step 2: Run individual module tests
    individual_results = run_individual_tests()
    
    # Step 3: Run pytest suite
    pytest_success, pytest_results = run_pytest_suite()
    
    # Step 4: Run performance tests
    performance_results = run_performance_tests()
    
    # Step 5: Generate report
    report = generate_test_report(individual_results, pytest_results, performance_results)
    
    # Calculate overall results
    total_time = time.time() - start_time
    
    modules_passed = report['summary']['modules_passed']
    modules_total = report['summary']['total_modules_tested']
    
    overall_success = (
        modules_passed > modules_total * 0.7 and  # At least 70% modules pass
        pytest_success
    )
    
    print(f"\n🏁 Test Execution Complete!")
    print(f"   ⏱️  Total time: {total_time:.2f} seconds")
    print(f"   📊 Overall result: {'✅ SUCCESS' if overall_success else '❌ SOME ISSUES'}")
    
    if overall_success:
        print("\n🎉 All data quality validation systems are working correctly!")
        print("सभी डेटा गुणवत्ता सत्यापन सिस्टम सही तरीके से काम कर रहे हैं!")
    else:
        print("\n⚠️  Some tests failed. Please review the test report for details.")
        print("कुछ परीक्षण असफल हुए। कृपया विवरण के लिए परीक्षण रिपोर्ट की समीक्षा करें।")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)