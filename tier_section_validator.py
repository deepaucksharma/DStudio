#!/usr/bin/env python3
"""
Validate tier-specific sections in patterns with excellence metadata.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

class TierSectionValidator:
    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        self.results = {
            'gold': {'total': 0, 'valid': 0, 'issues': []},
            'silver': {'total': 0, 'valid': 0, 'issues': []},
            'bronze': {'total': 0, 'valid': 0, 'issues': []}
        }
    
    def extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown content."""
        try:
            if content.startswith('---\n'):
                end_pos = content.find('\n---\n', 4)
                if end_pos != -1:
                    frontmatter_yaml = content[4:end_pos]
                    return yaml.safe_load(frontmatter_yaml)
        except yaml.YAMLError as e:
            return None
        return None
    
    def validate_gold_pattern(self, file_path: str, metadata: Dict[str, Any]) -> List[str]:
        """Validate Gold tier pattern requirements."""
        issues = []
        
        # Check modern_examples
        if 'modern_examples' not in metadata:
            issues.append("Missing 'modern_examples' section")
        else:
            examples = metadata['modern_examples']
            if not isinstance(examples, list) or len(examples) == 0:
                issues.append("'modern_examples' should be a non-empty list")
            else:
                for i, example in enumerate(examples):
                    if not isinstance(example, dict):
                        issues.append(f"modern_examples[{i}] should be a dictionary")
                        continue
                    required_keys = {'company', 'implementation', 'scale'}
                    missing_keys = required_keys - set(example.keys())
                    if missing_keys:
                        issues.append(f"modern_examples[{i}] missing: {', '.join(missing_keys)}")
        
        # Check production_checklist
        if 'production_checklist' not in metadata:
            issues.append("Missing 'production_checklist' section")
        else:
            checklist = metadata['production_checklist']
            if not isinstance(checklist, list) or len(checklist) == 0:
                issues.append("'production_checklist' should be a non-empty list")
        
        return issues
    
    def validate_silver_pattern(self, file_path: str, metadata: Dict[str, Any]) -> List[str]:
        """Validate Silver tier pattern requirements."""
        issues = []
        
        # Check trade_offs
        if 'trade_offs' not in metadata:
            issues.append("Missing 'trade_offs' section")
        else:
            trade_offs = metadata['trade_offs']
            if not isinstance(trade_offs, dict):
                issues.append("'trade_offs' should be a dictionary")
            else:
                if 'pros' not in trade_offs:
                    issues.append("'trade_offs' missing 'pros'")
                elif not isinstance(trade_offs['pros'], list):
                    issues.append("'trade_offs.pros' should be a list")
                
                if 'cons' not in trade_offs:
                    issues.append("'trade_offs' missing 'cons'")
                elif not isinstance(trade_offs['cons'], list):
                    issues.append("'trade_offs.cons' should be a list")
        
        # Check best_for
        if 'best_for' not in metadata:
            issues.append("Missing 'best_for' section")
        else:
            best_for = metadata['best_for']
            if not isinstance(best_for, list) or len(best_for) == 0:
                issues.append("'best_for' should be a non-empty list")
        
        return issues
    
    def validate_bronze_pattern(self, file_path: str, metadata: Dict[str, Any]) -> List[str]:
        """Validate Bronze tier pattern requirements."""
        issues = []
        
        # Check modern_alternatives
        if 'modern_alternatives' not in metadata:
            issues.append("Missing 'modern_alternatives' section")
        else:
            alternatives = metadata['modern_alternatives']
            if not isinstance(alternatives, list) or len(alternatives) == 0:
                issues.append("'modern_alternatives' should be a non-empty list")
        
        # Check deprecation_reason
        if 'deprecation_reason' not in metadata:
            issues.append("Missing 'deprecation_reason' section")
        else:
            reason = metadata['deprecation_reason']
            if not isinstance(reason, str) or len(reason.strip()) == 0:
                issues.append("'deprecation_reason' should be a non-empty string")
        
        return issues
    
    def validate_pattern_file(self, file_path: Path):
        """Validate a single pattern file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip non-pattern files
            if file_path.name in ['README.md', 'index.md', 'index-new.md', 'pattern-catalog.md', 
                                 'pattern-selector-tool.md', 'pattern-relationships.md', 
                                 'PATTERN_TEMPLATE.md']:
                return
            
            metadata = self.extract_frontmatter(content)
            if not metadata or 'excellence_tier' not in metadata:
                return
            
            tier = metadata['excellence_tier']
            if tier not in self.results:
                return
                
            self.results[tier]['total'] += 1
            
            issues = []
            if tier == 'gold':
                issues = self.validate_gold_pattern(str(file_path), metadata)
            elif tier == 'silver':
                issues = self.validate_silver_pattern(str(file_path), metadata)
            elif tier == 'bronze':
                issues = self.validate_bronze_pattern(str(file_path), metadata)
            
            if issues:
                self.results[tier]['issues'].append({
                    'file': file_path.name,
                    'issues': issues
                })
            else:
                self.results[tier]['valid'] += 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def validate_all_patterns(self):
        """Validate all pattern files."""
        pattern_files = list(self.patterns_dir.glob('*.md'))
        
        for file_path in sorted(pattern_files):
            self.validate_pattern_file(file_path)
    
    def generate_report(self) -> str:
        """Generate validation report."""
        report = []
        report.append("# Tier-Specific Section Validation Report")
        report.append("")
        
        for tier, data in self.results.items():
            if data['total'] == 0:
                continue
                
            report.append(f"## {tier.title()} Tier Patterns")
            report.append(f"- **Total patterns**: {data['total']}")
            report.append(f"- **Valid patterns**: {data['valid']}")
            report.append(f"- **Patterns with issues**: {len(data['issues'])}")
            report.append("")
            
            if data['issues']:
                report.append(f"### {tier.title()} Tier Issues")
                for issue_item in data['issues']:
                    report.append(f"#### {issue_item['file']}")
                    for issue in issue_item['issues']:
                        report.append(f"- {issue}")
                    report.append("")
        
        return "\n".join(report)

def main():
    patterns_dir = Path("docs/patterns")
    validator = TierSectionValidator(patterns_dir)
    validator.validate_all_patterns()
    
    report = validator.generate_report()
    print(report)
    
    with open("tier_section_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()