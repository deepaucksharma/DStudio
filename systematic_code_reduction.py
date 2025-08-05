#!/usr/bin/env python3
"""
Systematic code reduction script for pattern library files.
Removes repetitive placeholder diagrams, excessive code examples, and appendices.
"""

import os
import re
from pathlib import Path

def reduce_file_content(file_path):
    """Aggressively reduce code content in a pattern file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_lines = len(content.split('\n'))
    
    # 1. Remove repetitive nested details sections with placeholder mermaid
    content = re.sub(r'<details>\s*<summary>📄 View.*?</summary>\s*(?:<details>.*?</details>\s*)*```mermaid\s*graph TD\s*A\[Input\].*?```\s*(?:</details>\s*)*', 
                     '', content, flags=re.DOTALL)
    
    # 2. Remove excessive nested details sections
    content = re.sub(r'(?:<details>\s*<summary>📄 View.*?</summary>\s*){5,}', 
                     '**Implementation details available in production systems**\n\n', content, flags=re.DOTALL)
    
    # 3. Remove "See Implementation Example X in Appendix" references
    content = re.sub(r'\*See Implementation Example \d+ in Appendix\*\s*', '', content)
    
    # 4. Remove appendix sections entirely (massive code duplication)
    content = re.sub(r'## Appendix:.*$', '', content, flags=re.DOTALL)
    
    # 5. Replace large sequence diagrams with conceptual summaries
    def replace_large_sequence_diagram(match):
        diagram_content = match.group(0)
        if len(diagram_content) > 500:  # Large diagrams only
            return "**Process Flow:**\n1. Client initiates request\n2. System processes request\n3. Response returned with result\n\n"
        return diagram_content
    
    content = re.sub(r'```mermaid\s*sequenceDiagram.*?```', replace_large_sequence_diagram, content, flags=re.DOTALL)
    
    # 6. Replace complex architecture diagrams with bullet points
    def replace_complex_architecture(match):
        diagram_content = match.group(0)
        if 'subgraph' in diagram_content and len(diagram_content) > 400:
            return "**Architecture Components:**\n- Service layer\n- Processing components\n- Data storage\n- External integrations\n\n"
        return diagram_content
    
    content = re.sub(r'```mermaid\s*graph (?:TB|TD|LR).*?```', replace_complex_architecture, content, flags=re.DOTALL)
    
    # 7. Remove excessive code examples (keep max 5-10 lines)
    def reduce_code_block(match):
        code_content = match.group(0)
        lines = code_content.split('\n')
        if len(lines) > 15:  # Large code blocks
            # Extract language
            lang = lines[0].replace('```', '').strip()
            return f"```{lang}\n// Conceptual implementation\n// See production systems for full examples\n```\n\n"
        return code_content
    
    content = re.sub(r'```\w*\n.*?```', reduce_code_block, content, flags=re.DOTALL)
    
    # 8. Remove duplicate pattern decision trees (replace with simple tables)
    content = re.sub(r'```mermaid\s*flowchart.*?Start\[Need This Pattern\?\].*?```', 
                     '**Decision Criteria:** Use when distributed coordination needed, avoid for simple systems.', 
                     content, flags=re.DOTALL)
    
    # 9. Clean up excessive whitespace
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 10. Remove empty details sections
    content = re.sub(r'<details>\s*<summary>.*?</summary>\s*</details>', '', content, flags=re.DOTALL)
    
    final_lines = len(content.split('\n'))
    reduction_percent = ((original_lines - final_lines) / original_lines) * 100
    
    # Write the reduced content back
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: {original_lines} → {final_lines} lines ({reduction_percent:.1f}% reduction)")
        return True
    except Exception as e:
        print(f"❌ Error writing {file_path}: {e}")
        return False

def main():
    """Process all pattern files systematically."""
    pattern_dirs = [
        'architecture', 'communication', 'coordination', 
        'data-management', 'resilience', 'scaling'
    ]
    
    base_path = Path('/home/deepak/DStudio/docs/pattern-library')
    processed = 0
    successful = 0
    
    print("🔄 Starting systematic code reduction across all patterns...")
    
    for pattern_dir in pattern_dirs:
        dir_path = base_path / pattern_dir
        if not dir_path.exists():
            continue
            
        print(f"\n📁 Processing {pattern_dir}/ directory...")
        
        for file_path in dir_path.glob('*.md'):
            if file_path.name == 'index.md':
                continue
                
            processed += 1
            if reduce_file_content(file_path):
                successful += 1
    
    print(f"\n🎯 Reduction complete!")
    print(f"   Processed: {processed} patterns")
    print(f"   Successful: {successful} patterns")
    print(f"   Success rate: {(successful/processed)*100:.1f}%")

if __name__ == "__main__":
    main()