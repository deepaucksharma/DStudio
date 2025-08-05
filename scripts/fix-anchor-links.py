#!/usr/bin/env python3
"""Fix broken anchor links by analyzing content and adding missing sections."""

import re
from pathlib import Path

def extract_expected_anchors(file_path: Path) -> set:
    """Extract all anchor links that are referenced in the file."""
    content = file_path.read_text()
    # Find all links pointing to anchors
    anchor_pattern = r'\[[^\]]+\]\(#([^)]+)\)'
    return set(re.findall(anchor_pattern, content))

def extract_existing_anchors(content: str) -> set:
    """Extract all existing anchor targets in the content."""
    anchors = set()
    
    # Headers create automatic anchors
    header_pattern = r'^#{1,6}\s+(.+)$'
    for match in re.finditer(header_pattern, content, re.MULTILINE):
        header_text = match.group(1)
        # Convert to anchor format (lowercase, replace spaces with hyphens)
        anchor = header_text.lower().strip()
        anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
        anchor = re.sub(r'\s+', '-', anchor)  # Replace spaces with hyphens
        anchors.add(anchor)
    
    return anchors

def add_missing_sections(file_path: Path) -> bool:
    """Add missing sections for broken anchor links."""
    content = file_path.read_text()
    original_content = content
    
    expected_anchors = extract_expected_anchors(file_path)
    existing_anchors = extract_existing_anchors(content)
    
    missing_anchors = expected_anchors - existing_anchors
    
    if missing_anchors:
        # Add missing sections at the end
        sections_to_add = []
        
        for anchor in sorted(missing_anchors):
            # Convert anchor back to readable section name
            section_name = anchor.replace('-', ' ').title()
            
            # Special cases for common patterns
            if anchor == 'architecture-patterns':
                sections_to_add.append("\n## Architecture Patterns\n\n*Section to be completed*\n")
            elif anchor == 'engineering-excellence':
                sections_to_add.append("\n## Engineering Excellence\n\n*Section to be completed*\n")
            elif anchor == 'technical-mentorship':
                sections_to_add.append("\n## Technical Mentorship\n\n*Section to be completed*\n")
            elif anchor == 'cross-functional-leadership':
                sections_to_add.append("\n## Cross-Functional Leadership\n\n*Section to be completed*\n")
            elif anchor == 'stakeholder-management':
                sections_to_add.append("\n## Stakeholder Management\n\n*Section to be completed*\n")
            elif anchor == 'strategic-planning':
                sections_to_add.append("\n## Strategic Planning\n\n*Section to be completed*\n")
            elif anchor == 'product-business-alignment':
                sections_to_add.append("\n## Product Business Alignment\n\n*Section to be completed*\n")
            elif anchor == 'business-understanding':
                sections_to_add.append("\n## Business Understanding\n\n*Section to be completed*\n")
            else:
                sections_to_add.append(f"\n## {section_name}\n\n*Section to be completed*\n")
        
        if sections_to_add:
            # Add sections before the last section (if any) or at the end
            if '\n## ' in content:
                # Find the last major section
                last_section_match = list(re.finditer(r'\n## [^\n]+', content))[-1]
                insert_pos = last_section_match.start()
                content = content[:insert_pos] + ''.join(sections_to_add) + content[insert_pos:]
            else:
                content += '\n' + ''.join(sections_to_add)
    
    if content != original_content:
        # Ensure file ends with newline
        if not content.endswith('\n'):
            content += '\n'
        file_path.write_text(content)
        return True
    return False

def main():
    """Fix anchor links by adding missing sections."""
    docs_dir = Path("docs")
    fixed_count = 0
    
    # Focus on files with broken anchor links
    target_files = [
        "interview-prep/engineering-leadership/level-3-applications/technical-leadership/index.md",
        "interview-prep/engineering-leadership/level-3-applications/business-acumen/index.md",
    ]
    
    for file_path in target_files:
        full_path = docs_dir / file_path
        if full_path.exists() and add_missing_sections(full_path):
            fixed_count += 1
            print(f"Fixed: {full_path}")
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()