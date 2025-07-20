#!/usr/bin/env python3
"""
Fix code blocks by adding appropriate language specifications
"""

import os
import re
from pathlib import Path
import json

class CodeBlockFixer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.fixed_count = 0
        self.files_processed = 0
        
        # Language detection patterns
        self.language_patterns = {
            # Configuration files
            r'(apiVersion|kind|metadata):\s*\w+': 'yaml',
            r'circuit_breaker:\s*\n': 'yaml',
            r'---\s*\n[\s\S]*?---': 'yaml',
            
            # Code patterns
            r'\bclass\s+\w+.*?:': 'python',
            r'\bdef\s+\w+\(.*?\):': 'python',
            r'\bimport\s+\w+': 'python',
            r'\bfrom\s+\w+\s+import': 'python',
            r'self\.\w+': 'python',
            r'if\s+__name__\s*==\s*["\']__main__["\']': 'python',
            
            r'\bpublic\s+class\s+\w+': 'java',
            r'\bpublic\s+static\s+void\s+main': 'java',
            r'System\.out\.println': 'java',
            r'@Override': 'java',
            
            r'\bfunction\s+\w+\(': 'javascript',
            r'\bconsole\.log\(': 'javascript',
            r'\bconst\s+\w+\s*=': 'javascript',
            r'\blet\s+\w+\s*=': 'javascript',
            r'\basync\s+function': 'javascript',
            r'require\(': 'javascript',
            
            r'#include\s*<': 'cpp',
            r'\bstd::\w+': 'cpp',
            r'\bclass\s+\w+\s*{': 'cpp',
            r'\bpublic:\s*': 'cpp',
            r'\bprivate:\s*': 'cpp',
            
            r'\bstruct\s+\w+\s*{': 'go',
            r'\bfunc\s+\w+\(': 'go',
            r'\bpackage\s+\w+': 'go',
            r'\bfmt\.Print': 'go',
            r'\bgo\s+func\(': 'go',
            
            r'\bfn\s+\w+\(': 'rust',
            r'\blet\s+mut\s+': 'rust',
            r'\buse\s+std::': 'rust',
            r'\bimpl\s+\w+': 'rust',
            
            # SQL
            r'\bSELECT\s+.*\bFROM\b': 'sql',
            r'\bINSERT\s+INTO\b': 'sql',
            r'\bCREATE\s+TABLE\b': 'sql',
            r'\bUPDATE\s+\w+\s+SET\b': 'sql',
            
            # Shell/Bash
            r'#!/bin/(bash|sh)': 'bash',
            r'\$\w+': 'bash',
            r'\becho\s+': 'bash',
            r'\bmkdir\s+-p': 'bash',
            r'\bsudo\s+': 'bash',
            
            # HTTP/REST
            r'\b(GET|POST|PUT|DELETE|PATCH)\s+/': 'http',
            r'\bHTTP/\d\.\d': 'http',
            r'\bContent-Type:\s*': 'http',
            
            # JSON
            r'{\s*"\w+":\s*': 'json',
            r'\[\s*{\s*"\w+"': 'json',
            
            # Docker
            r'\bFROM\s+[\w:/.]+': 'dockerfile',
            r'\bRUN\s+': 'dockerfile',
            r'\bCOPY\s+': 'dockerfile',
            r'\bEXPOSE\s+\d+': 'dockerfile',
            
            # Kubernetes
            r'\bapiVersion:\s*apps/v1': 'yaml',
            r'\bkind:\s*(Deployment|Service|Pod)': 'yaml',
            
            # Mermaid diagrams
            r'\bgraph\s+(TD|LR|TB)': 'mermaid',
            r'\bsequenceDiagram': 'mermaid',
            r'\bflowchart\s+': 'mermaid',
        }
        
        # Context-based language detection
        self.context_languages = {
            'patterns': 'python',  # Default for pattern examples
            'axiom': 'python',     # Default for axiom examples
            'quantitative': 'python',  # Math examples often in Python
            'case-studies': 'python',  # Case study code
        }
        
        # Content-based heuristics
        self.content_heuristics = {
            'terraform': ['resource "', 'provider "', 'variable "'],
            'makefile': ['PHONY:', '.PHONY:', '$(', '\t@'],
            'proto': ['syntax = "proto3"', 'message ', 'service '],
            'nginx': ['server {', 'location /', 'upstream '],
            'redis': ['SET ', 'GET ', 'HSET ', 'redis-cli'],
            'mongodb': ['db.', '.find(', '.insert(', 'ObjectId('],
        }
    
    def detect_language(self, code_content, file_path=None):
        """Detect the programming language of a code block"""
        code_lower = code_content.lower().strip()
        
        # Empty or very short blocks default to text
        if len(code_content.strip()) < 10:
            return 'text'
        
        # Check for specific content patterns first
        for lang, patterns in self.content_heuristics.items():
            if any(pattern.lower() in code_lower for pattern in patterns):
                return lang
        
        # Check regex patterns
        for pattern, language in self.language_patterns.items():
            if re.search(pattern, code_content, re.MULTILINE | re.IGNORECASE):
                return language
        
        # Context-based detection
        if file_path:
            path_str = str(file_path).lower()
            for context, lang in self.context_languages.items():
                if context in path_str:
                    # Additional checks for context
                    if lang == 'python' and any(keyword in code_content for keyword in ['def ', 'class ', 'import ', 'from ']):
                        return 'python'
                    elif context == 'quantitative' and any(keyword in code_content for keyword in ['=', '+', '-', '*', '/']):
                        return 'python'
        
        # Fallback heuristics
        if any(keyword in code_content for keyword in ['{', '}', ';', '()', 'function']):
            if 'console.log' in code_content or 'const ' in code_content:
                return 'javascript'
            elif 'System.out' in code_content or 'public class' in code_content:
                return 'java'
            elif 'std::' in code_content or '#include' in code_content:
                return 'cpp'
            else:
                return 'javascript'  # Default for structured code
        
        # Mathematical content
        if any(op in code_content for op in ['∑', '∫', '∂', 'λ', '→', '←', '↔']):
            return 'text'
        
        # Command-line tools
        if code_content.startswith(('$', '#', '%')) or 'command' in code_lower:
            return 'bash'
        
        # Configuration-like content
        if ':' in code_content and ('=' in code_content or '-' in code_content):
            return 'yaml'
        
        # Default fallback
        return 'text'
    
    def fix_code_blocks_in_content(self, content, file_path):
        """Fix all code blocks in content"""
        # Pattern to match code blocks with or without language
        pattern = r'```(\w+)?\s*\n(.*?)\n```'
        
        def replace_block(match):
            existing_lang = match.group(1)
            code_content = match.group(2)
            
            # If language already specified, keep it (unless it's obviously wrong)
            if existing_lang and existing_lang.lower() not in ['', 'text', 'none']:
                return match.group(0)  # Keep original
            
            # Detect appropriate language
            detected_lang = self.detect_language(code_content, file_path)
            
            # Special case: if content looks like output/example, use text
            if any(indicator in code_content.lower() for indicator in ['output:', 'result:', 'example:', '# output']):
                detected_lang = 'text'
            
            self.fixed_count += 1
            return f'```{detected_lang}\n{code_content}\n```'
        
        # Replace all code blocks
        new_content = re.sub(pattern, replace_block, content, flags=re.DOTALL)
        
        return new_content
    
    def fix_file(self, file_path):
        """Fix code blocks in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has code blocks without language specs
            pattern = r'```\s*\n'
            if not re.search(pattern, content):
                return False  # No unlabeled code blocks
            
            new_content = self.fix_code_blocks_in_content(content, file_path)
            
            # Only write if content changed
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def fix_all(self):
        """Fix code blocks in all markdown files"""
        print("🔧 Fixing code block language specifications...\n")
        
        files_changed = []
        
        for md_file in sorted(self.docs_dir.rglob("*.md")):
            # Skip template and meta files
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE', 'REPORT']):
                continue
            
            relative_path = md_file.relative_to(self.docs_dir)
            
            # Count blocks before fixing
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            unlabeled_blocks = len(re.findall(r'```\s*\n', content))
            
            if unlabeled_blocks > 0:
                print(f"Processing {relative_path} ({unlabeled_blocks} unlabeled blocks)...")
                
                if self.fix_file(md_file):
                    files_changed.append(str(relative_path))
                    print(f"  ✅ Fixed {unlabeled_blocks} code blocks")
                else:
                    print(f"  ⚠️ No changes made")
                    
            self.files_processed += 1
        
        print(f"\n✅ Processed {self.files_processed} files")
        print(f"📝 Fixed {self.fixed_count} code blocks")
        print(f"📁 Modified {len(files_changed)} files")
        
        # Save summary
        summary = {
            'files_processed': self.files_processed,
            'code_blocks_fixed': self.fixed_count,
            'files_changed': files_changed
        }
        
        with open('code_blocks_fix_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Report saved to: code_blocks_fix_report.json")
        
        return summary


if __name__ == "__main__":
    fixer = CodeBlockFixer()
    fixer.fix_all()