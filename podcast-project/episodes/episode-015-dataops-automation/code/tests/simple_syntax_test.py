#!/usr/bin/env python3
"""
Simple Syntax Test for DataOps Examples
Tests Python syntax without requiring external dependencies

Author: DataOps Architecture Series
Episode: 015 - DataOps Automation
"""

import os
import sys
import ast
from pathlib import Path

def check_python_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, "Syntax valid"
    
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def analyze_code_quality(file_path):
    """Analyze basic code quality metrics"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metrics = {
            'has_docstring': '"""' in content or "'''" in content,
            'has_main_function': 'def main(' in content,
            'has_error_handling': 'try:' in content and 'except' in content,
            'has_logging': 'logging.' in content,
            'has_indian_context': any(term in content.lower() for term in [
                'indian', 'india', 'inr', 'mumbai', 'delhi', 'bangalore',
                'paytm', 'flipkart', 'irctc', 'aadhaar', 'pan', 'upi'
            ]),
            'line_count': len(content.split('\n')),
            'function_count': content.count('def '),
            'class_count': content.count('class ')
        }
        
        return metrics
    
    except Exception as e:
        return {'error': str(e)}

def main():
    """Run simple syntax and quality tests"""
    
    print("🧪 DataOps Examples - Syntax & Quality Check")
    print("=" * 60)
    
    # Find all Python files
    code_dir = Path(__file__).parent.parent / "python"
    python_files = list(code_dir.glob("*.py"))
    
    if not python_files:
        print("❌ No Python files found in code/python/")
        return False
    
    total_files = len(python_files)
    syntax_valid = 0
    quality_scores = []
    
    print(f"\n📁 Found {total_files} Python files to test")
    
    for py_file in sorted(python_files):
        file_name = py_file.name
        
        # Check syntax
        is_valid, message = check_python_syntax(py_file)
        
        if is_valid:
            syntax_valid += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"   {status} {file_name}: {message}")
        
        # Analyze quality if syntax is valid
        if is_valid:
            metrics = analyze_code_quality(py_file)
            
            if 'error' not in metrics:
                # Calculate quality score
                quality_factors = [
                    metrics['has_docstring'],
                    metrics['has_main_function'],
                    metrics['has_error_handling'],
                    metrics['has_logging'],
                    metrics['has_indian_context'],
                    metrics['line_count'] > 50,  # Substantial code
                    metrics['function_count'] >= 2,  # Multiple functions
                ]
                
                quality_score = sum(quality_factors) / len(quality_factors) * 100
                quality_scores.append(quality_score)
                
                print(f"      📊 Lines: {metrics['line_count']}, Functions: {metrics['function_count']}, Classes: {metrics['class_count']}")
                print(f"      🎯 Quality: {quality_score:.1f}% (Indian context: {'✅' if metrics['has_indian_context'] else '❌'})")
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Syntax valid: {syntax_valid}/{total_files} ({syntax_valid/total_files*100:.1f}%)")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"   Average quality: {avg_quality:.1f}%")
        print(f"   Quality range: {min(quality_scores):.1f}% - {max(quality_scores):.1f}%")
    
    # Check for required examples
    expected_examples = [
        "01_ml_pipeline_automation_indian_ai.py",
        "02_data_versioning_lineage_tracking.py", 
        "03_automated_data_quality_testing.py",
        "04_dataops_cicd_pipeline.py",
        "05_monitoring_alerting_system.py",
        "06_cost_optimization_framework.py",
        "07_compliance_automation.py"
    ]
    
    found_examples = [f.name for f in python_files]
    missing_examples = [ex for ex in expected_examples if ex not in found_examples]
    
    if missing_examples:
        print(f"\n⚠️  Missing expected examples: {missing_examples}")
    else:
        print(f"\n✅ All expected examples present")
    
    # Overall assessment
    success_rate = syntax_valid / total_files
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    print(f"\n🎯 Overall Assessment:")
    
    if success_rate == 1.0 and avg_quality >= 80:
        print(f"   🏆 Excellent! All files pass syntax and quality checks")
        result = "excellent"
    elif success_rate >= 0.9 and avg_quality >= 70:
        print(f"   ✅ Good! Most files meet quality standards")
        result = "good"
    elif success_rate >= 0.8:
        print(f"   ⚠️  Acceptable, but some improvements needed")
        result = "acceptable"
    else:
        print(f"   ❌ Poor quality - significant issues found")
        result = "poor"
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if syntax_valid < total_files:
        print(f"   • Fix syntax errors in {total_files - syntax_valid} files")
    
    if avg_quality < 80:
        print(f"   • Improve code documentation and error handling")
        print(f"   • Add more Indian business context")
        print(f"   • Implement comprehensive logging")
    
    print(f"   • Ensure all examples are production-ready")
    print(f"   • Add comprehensive unit tests")
    print(f"   • Document deployment procedures")
    
    return success_rate >= 0.8

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("🎉 DataOps examples are ready for Episode 015!")
    else:
        print("🔧 DataOps examples need improvement before publication")
    
    sys.exit(0 if success else 1)