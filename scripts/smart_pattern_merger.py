#!/usr/bin/env python3
"""
Smart Pattern Merger - Carefully merges duplicate patterns preserving all important content
"""

import os
import re
import yaml
import difflib
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class SmartPatternMerger:
    def __init__(self):
        self.base_dir = Path("/home/deepak/DStudio/docs/pattern-library")
        self.backup_dir = Path("/home/deepak/DStudio/pattern_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        
    def backup_patterns(self):
        """Create backup of all patterns before merging"""
        print(f"📦 Creating backup at {self.backup_dir}")
        import shutil
        if not self.backup_dir.exists():
            shutil.copytree(self.base_dir, self.backup_dir)
        print("  ✅ Backup created")
        
    def analyze_duplicates(self, file1: Path, file2: Path) -> Dict:
        """Analyze two files to identify unique content in each"""
        with open(file1, 'r') as f:
            content1 = f.read()
        with open(file2, 'r') as f:
            content2 = f.read()
            
        # Parse frontmatter and content
        fm1, body1 = self._parse_markdown(content1)
        fm2, body2 = self._parse_markdown(content2)
        
        # Extract sections from both files
        sections1 = self._extract_sections(body1)
        sections2 = self._extract_sections(body2)
        
        analysis = {
            'file1': str(file1),
            'file2': str(file2),
            'frontmatter_diff': self._compare_frontmatter(fm1, fm2),
            'unique_sections_file1': [],
            'unique_sections_file2': [],
            'common_sections': [],
            'examples_file1': self._extract_examples(body1),
            'examples_file2': self._extract_examples(body2),
            'code_blocks_file1': self._extract_code_blocks(body1),
            'code_blocks_file2': self._extract_code_blocks(body2),
            'references_file1': self._extract_references(body1),
            'references_file2': self._extract_references(body2)
        }
        
        # Find unique and common sections
        for section in sections1:
            if section not in sections2:
                analysis['unique_sections_file1'].append(section)
            else:
                analysis['common_sections'].append(section)
                
        for section in sections2:
            if section not in sections1:
                analysis['unique_sections_file2'].append(section)
                
        return analysis
        
    def merge_zero_trust_patterns(self):
        """Carefully merge zero-trust patterns preserving all unique content"""
        print("\n🔧 Merging Zero Trust patterns...")
        
        arch_file = self.base_dir / "security" / "zero-trust-architecture.md"
        sec_file = self.base_dir / "security" / "zero-trust-security.md"
        
        if not (arch_file.exists() and sec_file.exists()):
            print("  ⚠️  One or both zero-trust files not found")
            return
            
        # Analyze differences
        analysis = self.analyze_duplicates(arch_file, sec_file)
        
        # Read both files
        with open(arch_file, 'r') as f:
            arch_content = f.read()
        with open(sec_file, 'r') as f:
            sec_content = f.read()
            
        # Parse content
        arch_fm, arch_body = self._parse_markdown(arch_content)
        sec_fm, sec_body = self._parse_markdown(sec_content)
        
        # Merge frontmatter - keep best of both
        merged_fm = self._merge_frontmatter(arch_fm, sec_fm)
        merged_fm['title'] = 'Zero Trust Architecture'
        merged_fm['description'] = merged_fm.get('description', '') or 'Never trust, always verify - comprehensive security model eliminating implicit trust'
        
        # Merge body content preserving unique sections
        merged_body = arch_body
        
        # Add unique sections from security file
        for section in analysis['unique_sections_file2']:
            print(f"  📝 Adding unique section from zero-trust-security.md: {section[:50]}...")
            merged_body += f"\n\n{section}"
            
        # Add unique examples from security file
        if analysis['examples_file2']:
            existing_examples = analysis['examples_file1']
            for example in analysis['examples_file2']:
                if example not in existing_examples:
                    print(f"  📝 Adding unique example: {example[:50]}...")
                    # Find appropriate place to add example
                    if "## Production Examples" in merged_body:
                        pos = merged_body.find("## Production Examples")
                        next_section = merged_body.find("\n## ", pos + 1)
                        if next_section == -1:
                            merged_body += f"\n{example}"
                        else:
                            merged_body = merged_body[:next_section] + f"\n{example}\n" + merged_body[next_section:]
                            
        # Add unique code blocks
        unique_code = []
        for code in analysis['code_blocks_file2']:
            if code not in analysis['code_blocks_file1']:
                unique_code.append(code)
                
        if unique_code:
            print(f"  📝 Adding {len(unique_code)} unique code examples")
            # Add code examples in implementation section
            if "## Implementation" in merged_body:
                pos = merged_body.find("## Implementation")
                for code in unique_code:
                    merged_body = merged_body[:pos] + code + "\n" + merged_body[pos:]
                    
        # Save merged file
        yaml_content = yaml.dump(merged_fm, default_flow_style=False, sort_keys=False)
        final_content = f"---\n{yaml_content}---\n\n{merged_body}"
        
        with open(arch_file, 'w') as f:
            f.write(final_content)
            
        # Create redirect from old file
        redirect_content = f"""---
title: Zero Trust Security
description: Redirect to Zero Trust Architecture
---

# Zero Trust Security

This page has been merged with [Zero Trust Architecture](./zero-trust-architecture.md).

Please update your bookmarks.
"""
        with open(sec_file, 'w') as f:
            f.write(redirect_content)
            
        print("  ✅ Merged zero-trust patterns successfully")
        
    def merge_sharding_patterns(self):
        """Carefully merge sharding patterns"""
        print("\n🔧 Merging Sharding patterns...")
        
        general_file = self.base_dir / "scaling" / "sharding.md"
        db_file = self.base_dir / "scaling" / "database-sharding.md"
        
        if not (general_file.exists() and db_file.exists()):
            print("  ⚠️  One or both sharding files not found")
            return
            
        # Analyze differences
        analysis = self.analyze_duplicates(general_file, db_file)
        
        with open(general_file, 'r') as f:
            general_content = f.read()
        with open(db_file, 'r') as f:
            db_content = f.read()
            
        # Parse content
        general_fm, general_body = self._parse_markdown(general_content)
        db_fm, db_body = self._parse_markdown(db_content)
        
        # Merge frontmatter
        merged_fm = self._merge_frontmatter(general_fm, db_fm)
        merged_fm['title'] = 'Sharding (Data Partitioning)'
        merged_fm['description'] = 'Horizontal partitioning strategy for distributing data across multiple database instances'
        
        # Keep general sharding as base (it's more comprehensive)
        merged_body = general_body
        
        # Add unique content from database-sharding
        for section in analysis['unique_sections_file2']:
            if "database" in section.lower() or "sql" in section.lower():
                print(f"  📝 Adding database-specific section: {section[:50]}...")
                merged_body += f"\n\n{section}"
                
        # Add any unique examples from database-sharding
        if analysis['examples_file2']:
            for example in analysis['examples_file2']:
                if "database" in example.lower() and example not in analysis['examples_file1']:
                    print(f"  📝 Adding database example: {example[:50]}...")
                    if "## Database-Specific Considerations" not in merged_body:
                        merged_body += "\n\n## Database-Specific Considerations\n"
                    merged_body += f"\n{example}"
                    
        # Save merged file
        yaml_content = yaml.dump(merged_fm, default_flow_style=False, sort_keys=False)
        final_content = f"---\n{yaml_content}---\n\n{merged_body}"
        
        with open(general_file, 'w') as f:
            f.write(final_content)
            
        # Create redirect
        redirect_content = f"""---
title: Database Sharding
description: Redirect to Sharding pattern
---

# Database Sharding

This page has been merged with [Sharding (Data Partitioning)](./sharding.md).

Please update your bookmarks.
"""
        with open(db_file, 'w') as f:
            f.write(redirect_content)
            
        print("  ✅ Merged sharding patterns successfully")
        
    def _parse_markdown(self, content: str) -> Tuple[Dict, str]:
        """Parse markdown file into frontmatter and body"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except:
                    frontmatter = {}
                body = parts[2].strip()
            else:
                frontmatter = {}
                body = content
        else:
            frontmatter = {}
            body = content
            
        return frontmatter, body
        
    def _extract_sections(self, body: str) -> List[str]:
        """Extract all sections from markdown body"""
        sections = []
        lines = body.split('\n')
        current_section = []
        
        for line in lines:
            if line.startswith('## '):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            elif current_section:
                current_section.append(line)
                
        if current_section:
            sections.append('\n'.join(current_section))
            
        return sections
        
    def _extract_examples(self, body: str) -> List[str]:
        """Extract production examples from body"""
        examples = []
        # Look for example patterns
        patterns = [
            r'### .+Example',
            r'### .+Case Study',
            r'### Netflix',
            r'### Amazon',
            r'### Google',
            r'### Uber',
            r'### Microsoft'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, body, re.MULTILINE)
            for match in matches:
                # Extract the example section
                start = match.start()
                end = body.find('\n### ', start + 1)
                if end == -1:
                    end = body.find('\n## ', start + 1)
                if end == -1:
                    end = len(body)
                examples.append(body[start:end])
                
        return examples
        
    def _extract_code_blocks(self, body: str) -> List[str]:
        """Extract code blocks from body"""
        code_blocks = []
        pattern = r'```[\s\S]*?```'
        matches = re.finditer(pattern, body)
        for match in matches:
            code_blocks.append(match.group())
        return code_blocks
        
    def _extract_references(self, body: str) -> List[str]:
        """Extract references and links"""
        references = []
        # Extract markdown links
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.finditer(link_pattern, body)
        for match in matches:
            references.append(f"[{match.group(1)}]({match.group(2)})")
        return references
        
    def _compare_frontmatter(self, fm1: Dict, fm2: Dict) -> Dict:
        """Compare two frontmatter dictionaries"""
        diff = {
            'only_in_file1': {},
            'only_in_file2': {},
            'different_values': {}
        }
        
        for key in fm1:
            if key not in fm2:
                diff['only_in_file1'][key] = fm1[key]
            elif fm1[key] != fm2[key]:
                diff['different_values'][key] = {'file1': fm1[key], 'file2': fm2[key]}
                
        for key in fm2:
            if key not in fm1:
                diff['only_in_file2'][key] = fm2[key]
                
        return diff
        
    def _merge_frontmatter(self, fm1: Dict, fm2: Dict) -> Dict:
        """Merge two frontmatter dictionaries, keeping the best of both"""
        merged = fm1.copy()
        
        # Add any missing fields from fm2
        for key, value in fm2.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge lists
                for item in value:
                    if item not in merged[key]:
                        merged[key].append(item)
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                # Merge dictionaries
                for subkey, subvalue in value.items():
                    if subkey not in merged[key]:
                        merged[key][subkey] = subvalue
                        
        return merged
        
    def generate_merge_report(self) -> str:
        """Generate a report of what will be merged"""
        report = "# Pattern Merge Analysis Report\n\n"
        
        # Analyze Zero Trust patterns
        arch_file = self.base_dir / "security" / "zero-trust-architecture.md"
        sec_file = self.base_dir / "security" / "zero-trust-security.md"
        
        if arch_file.exists() and sec_file.exists():
            report += "## Zero Trust Patterns\n\n"
            analysis = self.analyze_duplicates(arch_file, sec_file)
            report += f"- **Primary file**: zero-trust-architecture.md\n"
            report += f"- **Secondary file**: zero-trust-security.md\n"
            report += f"- **Unique sections in architecture**: {len(analysis['unique_sections_file1'])}\n"
            report += f"- **Unique sections in security**: {len(analysis['unique_sections_file2'])}\n"
            report += f"- **Unique examples to preserve**: {len(analysis['examples_file2'])}\n"
            report += f"- **Unique code blocks to preserve**: {len([c for c in analysis['code_blocks_file2'] if c not in analysis['code_blocks_file1']])}\n\n"
            
        # Analyze Sharding patterns
        general_file = self.base_dir / "scaling" / "sharding.md"
        db_file = self.base_dir / "scaling" / "database-sharding.md"
        
        if general_file.exists() and db_file.exists():
            report += "## Sharding Patterns\n\n"
            analysis = self.analyze_duplicates(general_file, db_file)
            report += f"- **Primary file**: sharding.md\n"
            report += f"- **Secondary file**: database-sharding.md\n"
            report += f"- **Unique sections in general**: {len(analysis['unique_sections_file1'])}\n"
            report += f"- **Unique sections in database**: {len(analysis['unique_sections_file2'])}\n"
            report += f"- **Database-specific content to preserve**: {len([s for s in analysis['unique_sections_file2'] if 'database' in s.lower()])}\n\n"
            
        return report
        
    def run_safe_merge(self):
        """Run the merge process with safety checks"""
        print("🔍 Smart Pattern Merger - Preserving all unique content")
        
        # 1. Create backup
        self.backup_patterns()
        
        # 2. Generate analysis report
        report = self.generate_merge_report()
        report_path = Path("/home/deepak/DStudio/pattern_merge_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"  📊 Analysis report saved to {report_path}")
        
        # 3. Perform merges
        self.merge_zero_trust_patterns()
        self.merge_sharding_patterns()
        
        print(f"\n✅ Merge complete! Backup saved at {self.backup_dir}")
        print("  Review the merged files and the merge report for details")

def main():
    merger = SmartPatternMerger()
    merger.run_safe_merge()

if __name__ == "__main__":
    main()