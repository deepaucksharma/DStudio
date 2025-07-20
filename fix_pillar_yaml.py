#!/usr/bin/env python3
"""
Fix YAML issues in pillar files
"""

import os
import re

# Files that need fixing
pillar_files = [
    "docs/part2-pillars/models-collide.md",
    "docs/part2-pillars/work/examples.md",
    "docs/part2-pillars/tradeoff-calculus.md",
    "docs/part2-pillars/failure-recap.md",
    "docs/part2-pillars/truth/examples.md",
    "docs/part2-pillars/truth/exercises.md",
    "docs/part2-pillars/models-comparison.md",
    "docs/part2-pillars/pattern-matrix.md"
]

# Generic descriptions for each file type
descriptions = {
    "examples.md": "Real-world examples and case studies demonstrating the concepts in practice",
    "exercises.md": "Hands-on exercises to build understanding through practical application",
    "models-collide.md": "Exploring conflicts between different distributed system models and approaches",
    "tradeoff-calculus.md": "Framework for analyzing and making architectural trade-offs in distributed systems",
    "failure-recap.md": "Analysis of failure modes and patterns across distributed systems",
    "models-comparison.md": "Comparative analysis of different distributed system models and architectures",
    "pattern-matrix.md": "Matrix view of patterns and their relationships in distributed systems"
}

def get_description(filepath):
    """Get appropriate description based on filename"""
    filename = os.path.basename(filepath)
    for key in descriptions:
        if filename.endswith(key):
            return descriptions[key]
    return "Documentation for distributed systems concepts"

def fix_yaml_description(filepath):
    """Fix multiline description in YAML frontmatter"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "No valid frontmatter"
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Check if description needs fixing
        if 'description: "' in frontmatter and not re.search(r'description:\s*"[^"\n]*"', frontmatter):
            # Get appropriate description
            new_desc = get_description(filepath)
            
            # Find and replace the entire description section
            lines = frontmatter.split('\n')
            new_lines = []
            in_desc = False
            
            for line in lines:
                if line.strip().startswith('description: "'):
                    new_lines.append(f'description: "{new_desc}"')
                    if not line.strip().endswith('"'):
                        in_desc = True
                elif in_desc:
                    # Skip lines that are part of multiline description
                    if re.match(r'^\s*[a-zA-Z_]+:', line):
                        # Found next field
                        new_lines.append(line)
                        in_desc = False
                else:
                    new_lines.append(line)
            
            frontmatter = '\n'.join(new_lines)
            
            # Write back
            new_content = f"---{frontmatter}---{body}"
            with open(filepath, 'w') as f:
                f.write(new_content)
                
            return True, "Fixed successfully"
        else:
            return False, "No fix needed"
            
    except Exception as e:
        return False, str(e)

def main():
    print("=== Fixing Pillar YAML Issues ===\n")
    
    fixed = 0
    for filepath in pillar_files:
        if os.path.exists(filepath):
            success, message = fix_yaml_description(filepath)
            if success:
                print(f"✓ {filepath}: {message}")
                fixed += 1
            else:
                print(f"- {filepath}: {message}")
        else:
            print(f"✗ {filepath}: File not found")
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {len(pillar_files)}")
    print(f"Files fixed: {fixed}")

if __name__ == "__main__":
    main()