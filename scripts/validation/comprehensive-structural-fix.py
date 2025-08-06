#!/usr/bin/env python3
"""Comprehensive structural fix for all systemic issues discovered."""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import argparse

class ComprehensiveStructuralFix:
    def __init__(self, docs_dir: Path = Path("docs"), fix: bool = False):
        self.docs_dir = docs_dir
        self.fix = fix
        self.changes_made = []
        self.errors = []
        
        # Define all mappings and standards
        self.pillar_mappings = {
            '/pillars/work/': '/core-principles/pillars/work-distribution/',
            '/pillars/state/': '/core-principles/pillars/state-distribution/',
            '/pillars/truth/': '/core-principles/pillars/truth-distribution/',
            '/pillars/control/': '/core-principles/pillars/control-distribution/',
            '/pillars/intelligence/': '/core-principles/pillars/intelligence-distribution/',
            '../../core-principles/pillars/work/index': '../../core-principles/pillars/work-distribution/',
            '../../core-principles/pillars/state/index': '../../core-principles/pillars/state-distribution/',
            '../../core-principles/pillars/truth/index': '../../core-principles/pillars/truth-distribution/',
            '../../core-principles/pillars/control/index': '../../core-principles/pillars/control-distribution/',
            '../../core-principles/pillars/intelligence/index': '../../core-principles/pillars/intelligence-distribution/',
        }
        
        self.law_mappings = {
            'law1-failure': 'correlated-failure',
            'law2-asynchrony': 'asynchronous-reality',
            'law3-chaos': 'emergent-chaos',
            'law3-emergence': 'emergent-chaos',
            'law4-tradeoffs': 'multidimensional-optimization',
            'law5-epistemology': 'distributed-knowledge',
            'law6-load': 'cognitive-load',
            'law7-economics': 'economic-reality',
        }
        
        self.path_fixes = {
            '../patterns/': '../pattern-library/',
            '../quantitative/': '../quantitative-analysis/',
            '/quantitative/': '/quantitative-analysis/',
            '../../quantitative/': '../../quantitative-analysis/',
        }
        
    def fix_frontmatter_consistency(self):
        """Fix all frontmatter consistency issues."""
        print("\n🔧 FIXING FRONTMATTER CONSISTENCY...")
        
        fixed_count = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            if self.fix_file_frontmatter(md_file):
                fixed_count += 1
                
        print(f"✅ Fixed frontmatter in {fixed_count} files")
        
    def fix_file_frontmatter(self, file_path: Path) -> bool:
        """Fix frontmatter in a single file."""
        try:
            content = file_path.read_text()
            original_content = content
            changed = False
            
            # Extract frontmatter if exists
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm_text = parts[1]
                    body = parts[2]
                    
                    # Parse and fix frontmatter
                    try:
                        fm = yaml.safe_load(fm_text)
                        if fm:
                            # Fix best-for to best_for
                            if 'best-for' in fm:
                                fm['best_for'] = fm.pop('best-for')
                                changed = True
                                
                            # Fix law references in tags
                            if 'tags' in fm and isinstance(fm['tags'], list):
                                new_tags = []
                                for tag in fm['tags']:
                                    new_tag = tag
                                    for old, new in self.law_mappings.items():
                                        if tag == old:
                                            new_tag = new
                                            changed = True
                                            break
                                    new_tags.append(new_tag)
                                fm['tags'] = new_tags
                                
                            # Fix related_laws
                            if 'related_laws' in fm and isinstance(fm['related_laws'], list):
                                new_laws = []
                                for law in fm['related_laws']:
                                    new_law = self.law_mappings.get(law, law)
                                    if new_law != law:
                                        changed = True
                                    new_laws.append(new_law)
                                fm['related_laws'] = new_laws
                                
                            # Reconstruct content if changed
                            if changed:
                                new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False)
                                content = f"---\n{new_fm}---{body}"
                                
                    except yaml.YAMLError:
                        pass
            else:
                # Add frontmatter for critical files that need it
                rel_path = file_path.relative_to(self.docs_dir)
                if self.should_have_frontmatter(rel_path):
                    fm = self.generate_default_frontmatter(rel_path)
                    if fm:
                        fm_text = yaml.dump(fm, default_flow_style=False, sort_keys=False)
                        content = f"---\n{fm_text}---\n\n{content}"
                        changed = True
                        
            # Write back if changed
            if changed and self.fix:
                file_path.write_text(content)
                self.changes_made.append(f"Fixed frontmatter: {file_path.relative_to(self.docs_dir)}")
                return True
            elif changed:
                print(f"  Would fix frontmatter: {file_path.relative_to(self.docs_dir)}")
                
        except Exception as e:
            self.errors.append(f"Error fixing {file_path}: {e}")
            
        return False
        
    def should_have_frontmatter(self, rel_path: Path) -> bool:
        """Determine if a file should have frontmatter."""
        # Pattern files should have frontmatter
        if 'pattern-library' in str(rel_path):
            return True
        # Index files in key directories
        if rel_path.name == 'index.md' and any(part in str(rel_path) for part in [
            'interview-prep', 'core-principles', 'excellence', 'architects-handbook'
        ]):
            return True
        return False
        
    def generate_default_frontmatter(self, rel_path: Path) -> Dict:
        """Generate appropriate default frontmatter."""
        fm = {}
        
        # For pattern files
        if 'pattern-library' in str(rel_path):
            category = rel_path.parent.name
            fm.update({
                'type': 'pattern',
                'category': category,
                'title': rel_path.stem.replace('-', ' ').title(),
                'description': 'TODO: Add description',
            })
            
        # For index files
        elif rel_path.name == 'index.md':
            title = rel_path.parent.name.replace('-', ' ').title()
            fm.update({
                'title': title,
                'description': f'{title} overview and navigation',
            })
            
        return fm
        
    def fix_path_references(self):
        """Fix all path reference issues."""
        print("\n🔧 FIXING PATH REFERENCES...")
        
        fixed_count = 0
        
        for md_file in self.docs_dir.glob("**/*.md"):
            content = md_file.read_text()
            original_content = content
            
            # Fix pillar paths
            for old_path, new_path in self.pillar_mappings.items():
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    
            # Fix pattern paths
            for old_path, new_path in self.path_fixes.items():
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    
            # Fix law references in content
            for old_law, new_law in self.law_mappings.items():
                # Fix in links
                content = re.sub(f'/laws/{old_law}/', f'/laws/{new_law}/', content)
                content = re.sub(f'/{old_law}/', f'/{new_law}/', content)
                
            if content != original_content:
                if self.fix:
                    md_file.write_text(content)
                    self.changes_made.append(f"Fixed paths: {md_file.relative_to(self.docs_dir)}")
                    fixed_count += 1
                else:
                    print(f"  Would fix paths: {md_file.relative_to(self.docs_dir)}")
                    
        print(f"✅ Fixed path references in {fixed_count} files")
        
    def validate_mkdocs_structure(self):
        """Ensure mkdocs.yml matches actual file structure."""
        print("\n🔧 VALIDATING MKDOCS STRUCTURE...")
        
        # This would require parsing mkdocs.yml and checking against actual files
        # For now, just report the symlink status
        patterns_dir = self.docs_dir / "patterns"
        if patterns_dir.exists():
            if patterns_dir.is_symlink():
                print("✅ /patterns/ is correctly symlinked to pattern-library")
            else:
                print("❌ /patterns/ exists but is not a symlink")
                if self.fix:
                    # Would remove and create symlink
                    print("  Would remove /patterns/ directory and create symlink")
                    
    def generate_report(self):
        """Generate summary report."""
        print("\n" + "="*80)
        print("🔧 COMPREHENSIVE STRUCTURAL FIX SUMMARY")
        print("="*80)
        
        if self.fix:
            print(f"\n✅ CHANGES MADE: {len(self.changes_made)}")
            if self.changes_made:
                print("\nSample changes:")
                for change in self.changes_made[:10]:
                    print(f"  - {change}")
                if len(self.changes_made) > 10:
                    print(f"  ... and {len(self.changes_made) - 10} more")
        else:
            print("\n🔍 DRY RUN MODE - No changes made")
            print("Run with --fix to apply changes")
            
        if self.errors:
            print(f"\n❌ ERRORS: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"  - {error}")
                
    def run(self):
        """Run all fixes."""
        print("🔧 RUNNING COMPREHENSIVE STRUCTURAL FIXES...")
        print("="*80)
        
        self.fix_frontmatter_consistency()
        self.fix_path_references()
        self.validate_mkdocs_structure()
        self.generate_report()

def main():
    parser = argparse.ArgumentParser(description='Fix all structural issues in documentation')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default: dry run)')
    args = parser.parse_args()
    
    fixer = ComprehensiveStructuralFix(fix=args.fix)
    fixer.run()

if __name__ == "__main__":
    main()