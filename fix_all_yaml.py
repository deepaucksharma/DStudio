#!/usr/bin/env python3
"""
Fix all YAML frontmatter issues in markdown files
"""

import os
import re
import yaml
import sys
from pathlib import Path

def extract_frontmatter(content):
    """Extract frontmatter from markdown content"""
    parts = content.split('---', 2)
    if len(parts) >= 3 and parts[0].strip() == '':
        return parts[1], parts[2]
    return None, content

def fix_multiline_description(frontmatter):
    """Fix multiline descriptions in YAML frontmatter"""
    # Pattern to find multiline descriptions
    desc_pattern = r'description:\s*"([^"]*)\n([^"]*)"'
    
    # Check if there's a multiline description issue
    if 'description: "' in frontmatter:
        # Find content between description: " and the next field or end
        lines = frontmatter.split('\n')
        new_lines = []
        in_description = False
        desc_content = []
        
        for i, line in enumerate(lines):
            if line.startswith('description: "') and not line.rstrip().endswith('"'):
                in_description = True
                # Extract initial part
                desc_content.append(line.split('description: "')[1])
            elif in_description:
                # Check if this line starts a new field
                if re.match(r'^[a-zA-Z_]+:', line):
                    # End of description, create proper single line
                    full_desc = ' '.join(desc_content).strip().rstrip('"')
                    # Clean up any special characters
                    full_desc = full_desc.replace('\n', ' ').replace('\r', ' ')
                    full_desc = re.sub(r'\s+', ' ', full_desc)
                    # Truncate if too long
                    if len(full_desc) > 200:
                        full_desc = full_desc[:197] + "..."
                    new_lines.append(f'description: "{full_desc}"')
                    new_lines.append(line)
                    in_description = False
                    desc_content = []
                else:
                    # Still part of description
                    desc_content.append(line.strip())
            else:
                new_lines.append(line)
        
        # Handle case where description goes to end
        if in_description and desc_content:
            full_desc = ' '.join(desc_content).strip().rstrip('"')
            full_desc = full_desc.replace('\n', ' ').replace('\r', ' ')
            full_desc = re.sub(r'\s+', ' ', full_desc)
            if len(full_desc) > 200:
                full_desc = full_desc[:197] + "..."
            new_lines.append(f'description: "{full_desc}"')
        
        frontmatter = '\n'.join(new_lines)
    
    # Fix empty descriptions
    frontmatter = re.sub(r'description:\s*""', 'description: "Documentation for distributed systems concepts"', frontmatter)
    
    return frontmatter

def fix_yaml_file(filepath):
    """Fix YAML frontmatter in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = extract_frontmatter(content)
        if not frontmatter:
            return False, "No frontmatter found"
        
        # Fix the frontmatter
        fixed_frontmatter = fix_multiline_description(frontmatter)
        
        # Validate the fixed YAML
        try:
            yaml_data = yaml.safe_load(fixed_frontmatter)
            if not isinstance(yaml_data, dict):
                return False, "Invalid YAML structure"
            
            # Ensure description is a string
            if 'description' in yaml_data and not isinstance(yaml_data['description'], str):
                return False, "Description is not a string"
            
        except yaml.YAMLError as e:
            return False, f"YAML validation error: {e}"
        
        # Write back the fixed content
        new_content = f"---{fixed_frontmatter}---{body}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "Fixed successfully"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix all YAML files in docs directory"""
    docs_dir = Path("docs")
    
    fixed_count = 0
    error_count = 0
    errors = []
    
    # Find all markdown files
    for md_file in docs_dir.rglob("*.md"):
        success, message = fix_yaml_file(md_file)
        
        if success:
            fixed_count += 1
            print(f"✓ Fixed: {md_file}")
        else:
            # Try to read and check if it's actually an error
            try:
                with open(md_file, 'r') as f:
                    content = f.read()
                if content.startswith('---'):
                    # Has frontmatter, this is a real error
                    error_count += 1
                    errors.append((md_file, message))
                    print(f"✗ Error: {md_file} - {message}")
            except:
                pass
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {fixed_count + error_count}")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    
    if errors:
        print("\n=== Files with errors ===")
        for filepath, error in errors:
            print(f"{filepath}: {error}")

if __name__ == "__main__":
    main()