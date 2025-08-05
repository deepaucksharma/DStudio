#!/usr/bin/env python3
"""Validate and fix navigation structure based on documented standards."""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import yaml

class NavigationValidator:
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = docs_dir
        self.issues = []
        self.fixed_count = 0
        
        # Define correct structures
        self.law_slugs = {
            'law1-failure': 'correlated-failure',
            'law2-asynchrony': 'asynchronous-reality', 
            'law3-chaos': 'emergent-chaos',
            'law3-emergence': 'emergent-chaos',
            'law4-tradeoffs': 'multidimensional-optimization',
            'law5-epistemology': 'distributed-knowledge',
            'law6-load': 'cognitive-load',
            'law6-human-api': 'cognitive-load',
            'law7-economics': 'economic-reality',
        }
        
        self.pattern_categories = [
            'architecture', 'communication', 'coordination',
            'data-management', 'resilience', 'scaling'
        ]
        
    def validate_file(self, file_path: Path) -> List[Dict]:
        """Validate all references in a single file."""
        issues = []
        content = file_path.read_text()
        
        # Check for old law references
        old_law_patterns = [
            r'law\d-[a-z]+',
            r'part1-axioms',
            r'part2-pillars',
            r'/axioms/',
        ]
        
        for pattern in old_law_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append({
                    'file': str(file_path.relative_to(self.docs_dir)),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'old_reference',
                    'found': match.group(),
                    'context': content[max(0, match.start()-50):match.end()+50]
                })
        
        # Check for broken paths
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_path = match.group(2)
            
            # Skip external links and anchors
            if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
                
            # Check if it's a law reference
            for old_slug, new_slug in self.law_slugs.items():
                if old_slug in link_path:
                    issues.append({
                        'file': str(file_path.relative_to(self.docs_dir)),
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'old_law_link',
                        'found': link_path,
                        'should_be': link_path.replace(old_slug, new_slug)
                    })
                    
        return issues
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix all issues in a file."""
        content = file_path.read_text()
        original_content = content
        
        # Fix frontmatter first
        if content.startswith('---'):
            content = self.fix_frontmatter(content)
        
        # Fix all old references
        replacements = [
            # Old axiom/pillar paths
            ('part1-axioms/', 'core-principles/laws/'),
            ('part2-pillars/', 'core-principles/pillars/'),
            ('/axioms/', '/laws/'),
            
            # With ../
            ('../part1-axioms/', '../core-principles/laws/'),
            ('../part2-pillars/', '../core-principles/pillars/'),
            ('../../part1-axioms/', '../../core-principles/laws/'),
            ('../../part2-pillars/', '../../core-principles/pillars/'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Fix specific law references
        for old_slug, new_slug in self.law_slugs.items():
            # In links
            content = re.sub(
                rf'\](\([^)]*){old_slug}([^)]*\))',
                rf']\1{new_slug}\2',
                content
            )
            # In paths
            content = content.replace(f'/{old_slug}/', f'/{new_slug}/')
            content = content.replace(f'/{old_slug})', f'/{new_slug})')
            content = content.replace(f'/{old_slug}.md', f'/{new_slug}.md')
        
        if content != original_content:
            file_path.write_text(content)
            return True
        return False
    
    def fix_frontmatter(self, content: str) -> str:
        """Fix frontmatter tags and prerequisites."""
        parts = content.split('---', 2)
        if len(parts) < 3:
            return content
            
        try:
            frontmatter = yaml.safe_load(parts[1])
            if not frontmatter:
                return content
                
            # Fix tags
            if 'tags' in frontmatter and isinstance(frontmatter['tags'], list):
                new_tags = []
                for tag in frontmatter['tags']:
                    # Map old law tags
                    new_tag = self.law_slugs.get(tag, tag)
                    # Remove path-like tags
                    if '/' not in new_tag and new_tag not in ['part1-axioms', 'part2-pillars']:
                        new_tags.append(new_tag)
                frontmatter['tags'] = new_tags
            
            # Fix prerequisites
            if 'prerequisites' in frontmatter and isinstance(frontmatter['prerequisites'], list):
                new_prereqs = []
                for prereq in frontmatter['prerequisites']:
                    # Fix paths
                    prereq = prereq.replace('part1-axioms/', 'core-principles/laws/')
                    prereq = prereq.replace('part2-pillars/', 'core-principles/pillars/')
                    # Fix law references
                    for old_slug, new_slug in self.law_slugs.items():
                        prereq = prereq.replace(old_slug, new_slug)
                    new_prereqs.append(prereq)
                frontmatter['prerequisites'] = new_prereqs
            
            # Rebuild
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            return f"---\n{new_frontmatter}---{parts[2]}"
        except:
            # If YAML fails, do simple string replacement
            fm = parts[1]
            for old_slug, new_slug in self.law_slugs.items():
                fm = fm.replace(f'- {old_slug}', f'- {new_slug}')
                fm = fm.replace(f': {old_slug}', f': {new_slug}')
            fm = fm.replace('part1-axioms', 'laws')
            fm = fm.replace('part2-pillars', 'pillars')
            return f"---{fm}---{parts[2]}"
    
    def validate_all(self) -> Dict:
        """Validate entire documentation structure."""
        all_issues = []
        
        for md_file in self.docs_dir.glob("**/*.md"):
            issues = self.validate_file(md_file)
            all_issues.extend(issues)
        
        # Group by type
        by_type = {}
        for issue in all_issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        return {
            'total': len(all_issues),
            'by_type': by_type,
            'files_affected': len(set(i['file'] for i in all_issues))
        }
    
    def fix_all(self) -> int:
        """Fix all navigation issues."""
        fixed_files = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            if self.fix_file(md_file):
                fixed_files += 1
                print(f"Fixed: {md_file.relative_to(self.docs_dir)}")
        
        return fixed_files

def main():
    """Run validation and optionally fix issues."""
    import sys
    
    validator = NavigationValidator()
    
    if '--fix' in sys.argv:
        print("Fixing navigation issues...")
        fixed = validator.fix_all()
        print(f"\nFixed {fixed} files")
    else:
        print("Validating navigation structure...")
        results = validator.validate_all()
        
        print(f"\nTotal issues found: {results['total']}")
        print(f"Files affected: {results['files_affected']}")
        
        print("\nIssues by type:")
        for issue_type, issues in results['by_type'].items():
            print(f"  {issue_type}: {len(issues)}")
            # Show first few examples
            for issue in issues[:3]:
                print(f"    - {issue['file']}: {issue.get('found', 'N/A')}")
            if len(issues) > 3:
                print(f"    ... and {len(issues) - 3} more")
        
        print("\nRun with --fix to automatically fix these issues")

if __name__ == "__main__":
    main()