#!/usr/bin/env python3
"""
Comprehensive Navigation Fix Script for DStudio Documentation
Fixes all broken links identified in production deployment
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
import sys

class ComprehensiveNavigationFixer:
    def __init__(self, base_dir="/home/deepak/DStudio"):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.fixes_applied = 0
        self.files_modified = set()
        self.created_files = []
        self.stats = defaultdict(int)
        
    def fix_broken_links_in_file(self, file_path):
        """Fix all broken link patterns in a single file"""
        full_path = self.docs_dir / file_path
        if not full_path.exists():
            return 0
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original = content
        fixes = 0
        
        # Pattern 1: Fix wrong path prefixes (core-principles/pattern-library should be pattern-library)
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*core-principles/pattern-library/([^)]+)\)',
            r'[\1](../pattern-library/\2)',
            content
        )
        
        # Pattern 2: Fix inverted paths (pattern-library/core-principles should be core-principles)  
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*pattern-library/core-principles/([^)]+)\)',
            r'[\1](../core-principles/\2)',
            content
        )
        
        # Pattern 3: Fix architects-handbook/pattern-library paths
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*architects-handbook/pattern-library/([^)]+)\)',
            r'[\1](../pattern-library/\2)',
            content
        )
        
        # Pattern 4: Fix redundant pattern-library/coordination/pattern-library paths
        content = re.sub(
            r'pattern-library/([^/]+)/pattern-library/([^)]+)',
            r'pattern-library/\1/\2',
            content
        )
        
        # Pattern 5: Fix core-principles double nesting
        content = re.sub(
            r'core-principles/core-principles/([^)]+)',
            r'core-principles/\1',
            content
        )
        
        # Pattern 6: Remove trailing slashes that should be index.md
        content = re.sub(
            r'\[([^\]]+)\]\(([^)]+)/\)',
            r'[\1](\2/index.md)',
            content
        )
        
        # Pattern 7: Fix quantitative-analysis paths (missing architects-handbook prefix)
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*quantitative-analysis/([^)]+)\)',
            r'[\1](../architects-handbook/quantitative-analysis/\2)',
            content
        )
        
        # Pattern 8: Fix excellence/index.md references
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*excellence/index\.md\)',
            r'[\1](../architects-handbook/implementation-playbooks/index.md)',
            content
        )
        
        # Pattern 9: Fix human-factors references without architects-handbook
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*human-factors/([^)]+)\)',
            r'[\1](../architects-handbook/human-factors/\2)',
            content
        )
        
        # Pattern 10: Fix case-studies references without architects-handbook
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*case-studies/([^)]+)\)',
            r'[\1](../architects-handbook/case-studies/\2)',
            content
        )
        
        # Pattern 11: Fix learning-paths references
        content = re.sub(
            r'\[([^\]]+)\]\([\./]*learning-paths/([^)]+)\)',
            r'[\1](../architects-handbook/learning-paths/\2)',
            content
        )
        
        # Pattern 12: Fix broken .md references (add missing extension)
        # Match links that don't end in .md, /, or start with http/https
        content = re.sub(
            r'\[([^\]]+)\]\(([^)#]+[^/.md#)])(\)|#)',
            lambda m: f'[{m.group(1)}]({m.group(2)}.md{m.group(3)})' 
                if not m.group(2).startswith(('http://', 'https://', 'mailto:', '../', './'))
                else m.group(0),
            content
        )
        
        # Count fixes
        if content != original:
            fixes = content.count('](') - original.count('](')
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_modified.add(str(file_path))
            self.fixes_applied += abs(fixes)
            
        return fixes
        
    def create_missing_directories(self):
        """Create missing implementation-playbooks directories"""
        missing_dirs = [
            'architects-handbook/implementation-playbooks/monolith-decomposition',
            'architects-handbook/implementation-playbooks/zero-downtime',
            'architects-handbook/implementation-playbooks/global-expansion',
            'architects-handbook/implementation-playbooks/pattern-selection-wizard',
            'architects-handbook/implementation-playbooks/migration-checklist',
            'architects-handbook/implementation-playbooks/monolith-to-microservices',
        ]
        
        for dir_path in missing_dirs:
            full_dir = self.docs_dir / dir_path
            full_dir.mkdir(parents=True, exist_ok=True)
            
            # Create index.md for each directory
            index_file = full_dir / 'index.md'
            if not index_file.exists():
                dir_name = Path(dir_path).name
                title = dir_name.replace('-', ' ').title()
                
                content = f"""# {title}

## Overview

This playbook provides comprehensive guidance for {title.lower()}.

## Quick Start

1. Assess current state
2. Define target architecture
3. Plan migration approach
4. Execute incrementally
5. Validate and optimize

## Key Patterns

Related patterns for this playbook:

- [Pattern Library](../../../pattern-library/index.md)
- [Case Studies](../../case-studies/index.md)
- [Quantitative Analysis](../../quantitative-analysis/index.md)

## Tools & Resources

- Assessment checklists
- Migration templates
- Automation scripts
- Monitoring dashboards

## Best Practices

1. Start small and iterate
2. Maintain backward compatibility
3. Automate rollback procedures
4. Monitor key metrics
5. Document decisions

## Case Studies

Learn from real implementations:

- Industry examples
- Common pitfalls
- Success patterns
- Lessons learned

## Next Steps

- Review prerequisites
- Complete assessment
- Create implementation plan
- Begin pilot project

---

*This playbook is part of the [Implementation Playbooks](../index.md) collection.*
"""
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.created_files.append(str(index_file.relative_to(self.base_dir)))
                print(f"Created: {index_file.relative_to(self.base_dir)}")
                
    def update_redirects_in_mkdocs(self):
        """Update mkdocs.yml with comprehensive redirects"""
        mkdocs_path = self.base_dir / 'mkdocs.yml'
        
        # Additional redirects to add for broken URLs
        new_redirects = {
            # Root redirects
            'index.html': 'index.md',
            '': 'index.md',
            
            # Pattern library ML infrastructure
            'pattern-library/ml-infrastructure/': 'pattern-library/ml-infrastructure/index.md',
            
            # Implementation playbooks
            'architects-handbook/implementation-playbooks/monolith-decomposition': 'architects-handbook/implementation-playbooks/monolith-decomposition/index.md',
            'architects-handbook/implementation-playbooks/zero-downtime': 'architects-handbook/implementation-playbooks/zero-downtime/index.md',
            'architects-handbook/implementation-playbooks/global-expansion': 'architects-handbook/implementation-playbooks/global-expansion/index.md',
            'architects-handbook/implementation-playbooks/pattern-selection-wizard': 'architects-handbook/implementation-playbooks/pattern-selection-wizard/index.md',
            'architects-handbook/implementation-playbooks/migration-checklist': 'architects-handbook/implementation-playbooks/migration-checklist/index.md',
            'architects-handbook/implementation-playbooks/monolith-to-microservices': 'architects-handbook/implementation-playbooks/monolith-to-microservices/index.md',
            
            # Common broken patterns
            'coordination-costs.md': 'architects-handbook/quantitative-analysis/coordination-costs.md',
            'zoom-scaling.md': 'architects-handbook/case-studies/infrastructure/zoom-scaling.md',
            'redis-architecture.md': 'architects-handbook/case-studies/databases/redis-architecture.md',
            'monolith-to-microservices.md': 'architects-handbook/case-studies/infrastructure/monolith-to-microservices.md',
            'progress.md': 'start-here/index.md',
            
            # Pattern library redirects for wrong paths
            'pattern-library/resilience/circuit-breaker.md': 'pattern-library/resilience/circuit-breaker-transformed.md',
            'core-principles/pattern-library/': 'pattern-library/',
            'pattern-library/core-principles/': 'core-principles/',
            'architects-handbook/pattern-library/': 'pattern-library/',
            
            # Quantitative redirects
            'quantitative-analysis/': 'architects-handbook/quantitative-analysis/',
            'quantitative-analysis/queueing-models.md': 'architects-handbook/quantitative-analysis/queueing-models.md',
            'quantitative-analysis/littles-law.md': 'architects-handbook/quantitative-analysis/littles-law.md',
            'quantitative-analysis/cap-theorem.md': 'architects-handbook/quantitative-analysis/cap-theorem.md',
            
            # Human factors redirects
            'human-factors.md': 'architects-handbook/human-factors/index.md',
            'incident-response.md': 'architects-handbook/human-factors/incident-response.md',
            'performance-testing.md': 'architects-handbook/quantitative-analysis/performance-testing.md',
            'latency-calculator.md': 'architects-handbook/tools/latency-calculator.md',
            
            # Excellence redirects
            'excellence/': 'architects-handbook/implementation-playbooks/',
            'excellence/index.md': 'architects-handbook/implementation-playbooks/index.md',
            'excellence/tools/': 'architects-handbook/tools/',
            'excellence/case-studies/': 'architects-handbook/case-studies/',
            'excellence/migrations/MIGRATION_GUIDES_COMPLETE.md': 'excellence/migrations/index.md',
        }
        
        # Read current mkdocs.yml
        with open(mkdocs_path, 'r') as f:
            lines = f.readlines()
            
        # Find redirect_maps section
        redirect_section_start = -1
        for i, line in enumerate(lines):
            if 'redirect_maps:' in line:
                redirect_section_start = i
                break
                
        if redirect_section_start >= 0:
            # Find where redirect_maps section ends
            indent_level = len(lines[redirect_section_start]) - len(lines[redirect_section_start].lstrip())
            redirect_section_end = len(lines)
            
            for i in range(redirect_section_start + 1, len(lines)):
                line_indent = len(lines[i]) - len(lines[i].lstrip())
                if lines[i].strip() and line_indent <= indent_level:
                    redirect_section_end = i
                    break
                    
            # Add new redirects
            new_lines = []
            for old_url, new_url in new_redirects.items():
                redirect_line = f"      {old_url}: {new_url}\n"
                # Check if redirect already exists
                exists = False
                for j in range(redirect_section_start, redirect_section_end):
                    if old_url + ':' in lines[j]:
                        exists = True
                        break
                if not exists:
                    new_lines.append(redirect_line)
                    
            # Insert new redirects
            if new_lines:
                lines[redirect_section_end:redirect_section_end] = new_lines
                with open(mkdocs_path, 'w') as f:
                    f.writelines(lines)
                print(f"Added {len(new_lines)} new redirects to mkdocs.yml")
                self.stats['redirects_added'] = len(new_lines)
                
    def fix_all_files(self):
        """Process all markdown files"""
        md_files = list(self.docs_dir.rglob('*.md'))
        total = len(md_files)
        
        print(f"Processing {total} markdown files...")
        
        for i, file_path in enumerate(md_files, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{total} files processed")
                
            rel_path = file_path.relative_to(self.docs_dir)
            self.fix_broken_links_in_file(rel_path)
            
        print(f"Processed {total} files")
        
    def generate_report(self):
        """Generate summary report"""
        report = f"""
==============================================
COMPREHENSIVE NAVIGATION FIX REPORT
==============================================

Files Modified: {len(self.files_modified)}
Total Fixes Applied: {self.fixes_applied}
Files Created: {len(self.created_files)}
Redirects Added: {self.stats.get('redirects_added', 0)}

Created Files:
{chr(10).join('  - ' + f for f in self.created_files[:10])}
{f'  ... and {len(self.created_files) - 10} more' if len(self.created_files) > 10 else ''}

Top Modified Files:
{chr(10).join('  - ' + f for f in list(self.files_modified)[:10])}
{f'  ... and {len(self.files_modified) - 10} more' if len(self.files_modified) > 10 else ''}

Fix Categories Applied:
- Wrong path prefixes (core-principles/pattern-library)
- Inverted paths (pattern-library/core-principles)
- Missing architects-handbook prefix
- Redundant path segments
- Missing .md extensions
- Trailing slashes converted to index.md
- Quantitative analysis path corrections
- Excellence to implementation-playbooks mapping
- Human factors path corrections
- Case studies path corrections

Next Steps:
1. Run: mkdocs build --strict
2. Test locally: mkdocs serve
3. Deploy to production
4. Monitor 404 errors

==============================================
"""
        print(report)
        
        # Save report
        report_file = self.base_dir / 'navigation_fix_report.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {report_file}")
        
    def run(self):
        """Run comprehensive navigation fix"""
        print("Starting Comprehensive Navigation Fix...")
        print("=" * 50)
        
        # Step 1: Create missing directories
        print("\n1. Creating missing directories...")
        self.create_missing_directories()
        
        # Step 2: Fix broken links in all files
        print("\n2. Fixing broken links in all files...")
        self.fix_all_files()
        
        # Step 3: Update redirects
        print("\n3. Updating mkdocs.yml redirects...")
        self.update_redirects_in_mkdocs()
        
        # Step 4: Generate report
        print("\n4. Generating report...")
        self.generate_report()
        
        print("\n✅ Navigation fix complete!")
        return self.fixes_applied > 0

if __name__ == "__main__":
    fixer = ComprehensiveNavigationFixer()
    success = fixer.run()
    sys.exit(0 if success else 1)