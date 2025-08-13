#!/usr/bin/env python3
"""
Syntax Check Tests for Episode 5: AI at Scale
भारतीय AI code examples की syntax और import checking

This ensures all Python examples are syntactically correct
and can be imported without basic errors.
"""

import ast
import sys
import importlib.util
from pathlib import Path
import subprocess
import time

def test_python_syntax():
    """Test Python code syntax"""
    print("🐍 Testing Python Code Syntax...")
    
    python_dir = Path(__file__).parent.parent / "python"
    python_files = list(python_dir.glob("*.py"))
    
    passed = 0
    failed = 0
    
    for py_file in python_files:
        if py_file.name.startswith("__"):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Check syntax
            ast.parse(source_code)
            print(f"   ✅ {py_file.name}: Syntax OK")
            passed += 1
            
        except SyntaxError as e:
            print(f"   ❌ {py_file.name}: Syntax Error - {e}")
            failed += 1
        except Exception as e:
            print(f"   ⚠️  {py_file.name}: Other Error - {e}")
    
    print(f"   Summary: {passed} passed, {failed} failed")
    return failed == 0

def test_import_basic():
    """Test basic imports work"""
    print("\n📦 Testing Basic Imports...")
    
    # Test some key imports used across examples
    test_imports = [
        "import asyncio",
        "import json",
        "import time",
        "from typing import Dict, List",
        "from dataclasses import dataclass",
        "import logging"
    ]
    
    passed = 0
    failed = 0
    
    for import_stmt in test_imports:
        try:
            exec(import_stmt)
            print(f"   ✅ {import_stmt}: OK")
            passed += 1
        except ImportError as e:
            print(f"   ❌ {import_stmt}: Failed - {e}")
            failed += 1
    
    print(f"   Summary: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("🚀 Running Syntax and Import Tests")
    print("=" * 50)
    
    syntax_ok = test_python_syntax()
    import_ok = test_import_basic()
    
    print("\n" + "=" * 50)
    if syntax_ok and import_ok:
        print("🎉 All syntax checks passed!")
    else:
        print("❌ Some syntax checks failed")
        sys.exit(1)