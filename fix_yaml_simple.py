#!/usr/bin/env python3
"""
Fix YAML frontmatter issues without external dependencies
"""

import os
import re
from pathlib import Path

def fix_yaml_file(filepath):
    """Fix YAML frontmatter in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return False, "No frontmatter"
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Invalid frontmatter structure"
        
        frontmatter = parts[1]
        body = parts[2]
        
        # Fix multiline descriptions
        if 'description: "' in frontmatter and not re.search(r'description:\s*"[^"]*"', frontmatter):
            lines = frontmatter.split('\n')
            fixed_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if line.strip().startswith('description: "') and not line.strip().endswith('"'):
                    # Found multiline description
                    desc_parts = [line.split('description: "')[1].strip()]
                    i += 1
                    
                    # Collect lines until we find next field or closing quote
                    while i < len(lines):
                        next_line = lines[i]
                        if re.match(r'^\s*[a-zA-Z_]+:', next_line):
                            # Found next field
                            break
                        desc_parts.append(next_line.strip().rstrip('"'))
                        i += 1
                        if next_line.strip().endswith('"'):
                            break
                    
                    # Combine description
                    full_desc = ' '.join(desc_parts).strip()
                    full_desc = full_desc.rstrip('"').rstrip('`').rstrip('"')
                    full_desc = re.sub(r'\s+', ' ', full_desc)
                    
                    # Truncate if needed
                    if len(full_desc) > 200:
                        full_desc = full_desc[:197] + "..."
                    
                    fixed_lines.append(f'description: "{full_desc}"')
                else:
                    fixed_lines.append(line)
                    i += 1
            
            frontmatter = '\n'.join(fixed_lines)
        
        # Fix empty descriptions
        frontmatter = re.sub(r'description:\s*""', 'description: "Documentation for distributed systems concepts"', frontmatter)
        
        # Write back
        new_content = f"---{frontmatter}---{body}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Fixed"
        
    except Exception as e:
        return False, str(e)

def main():
    """Process specific files we know have issues"""
    
    files_to_fix = [
        "docs/quantitative/queueing-models.md",
        "docs/quantitative/amdahl-gustafson.md",
        "docs/quantitative/availability-math.md",
        "docs/quantitative/universal-scalability.md",
        "docs/quantitative/problem-set.md",
        "docs/quantitative/index.md",
        "docs/quantitative/latency-ladder.md",
        "docs/quantitative/capacity-planning.md",
        "docs/quantitative/cache-economics.md",
        "docs/quantitative/coordination-costs.md",
        "docs/quantitative/littles-law.md",
    ]
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            success, message = fix_yaml_file(filepath)
            if success:
                print(f"✓ Fixed: {filepath}")
            else:
                print(f"✗ Error: {filepath} - {message}")

if __name__ == "__main__":
    main()