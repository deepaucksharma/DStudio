#!/usr/bin/env python3
"""
Comprehensive Pattern Metadata Validation Script

This script validates all pattern metadata against the excellence framework standards:
- Required fields presence
- Valid excellence_tier values (gold/silver/bronze)
- Valid pattern_status values (recommended/use-with-expertise/use-with-caution/legacy)
- Category consistency with folder location
- Field naming consistency (hyphens vs underscores)
- No null/undefined values
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

class PatternMetadataValidator:
    def __init__(self, base_path: str = "docs/pattern-library"):
        self.base_path = Path(base_path)
        self.validation_results = {
            "total_patterns": 0,
            "errors": [],
            "warnings": [],
            "fixes_needed": [],
            "summary": {}
        }
        
        # Standard values
        self.valid_tiers = {"gold", "silver", "bronze"}
        self.valid_statuses = {
            "recommended", 
            "use-with-expertise", 
            "use-with-caution", 
            "legacy"
        }
        
        # Required fields by tier
        self.required_base_fields = {
            "excellence_tier", "pattern_status", "introduced", 
            "current_relevance", "category", "description"
        }
        
        self.tier_specific_fields = {
            "gold": {"modern_examples", "production_checklist"},
            "silver": {"trade_offs", "best_for"}, 
            "bronze": {"modern_alternatives", "deprecation_reason"}
        }
        
        # Valid categories (folder names)
        self.valid_categories = {
            "architecture", "communication", "coordination", 
            "data-management", "resilience", "scaling"
        }
        
        # Valid relevance values
        self.valid_relevance = {"mainstream", "growing", "declining", "niche"}

    def extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return {}
        
        try:
            # Find the end of frontmatter
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                end_marker = content.find('\n---', 3)
                if end_marker == -1:
                    return {}
            
            frontmatter = content[3:end_marker].strip()
            return yaml.safe_load(frontmatter) or {}
        except yaml.YAMLError as e:
            return {"_yaml_error": str(e)}

    def validate_pattern_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single pattern file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                "file": str(file_path),
                "errors": [f"Could not read file: {e}"],
                "metadata": {}
            }
        
        metadata = self.extract_frontmatter(content)
        result = {
            "file": str(file_path),
            "errors": [],
            "warnings": [],
            "fixes_needed": [],
            "metadata": metadata
        }
        
        # Skip index files and special files
        if file_path.name in ['index.md'] or 'pattern-' in file_path.name:
            return result
        
        # Check for YAML parsing errors
        if "_yaml_error" in metadata:
            result["errors"].append(f"YAML parsing error: {metadata['_yaml_error']}")
            return result
        
        # Extract category from file path
        category_from_path = file_path.parent.name
        if category_from_path == "pattern-library":
            result["warnings"].append("Pattern file in root pattern-library directory")
            category_from_path = None
        
        # Validate required base fields
        for field in self.required_base_fields:
            if field not in metadata:
                result["errors"].append(f"Missing required field: {field}")
            elif metadata[field] is None or metadata[field] == "":
                result["errors"].append(f"Empty value for required field: {field}")
        
        # Validate excellence_tier
        if "excellence_tier" in metadata:
            tier = metadata["excellence_tier"]
            if tier not in self.valid_tiers:
                result["errors"].append(f"Invalid excellence_tier '{tier}'. Must be one of: {', '.join(self.valid_tiers)}")
            else:
                # Check tier-specific required fields
                tier_fields = self.tier_specific_fields.get(tier, set())
                for field in tier_fields:
                    if field not in metadata:
                        result["errors"].append(f"Missing required field for {tier} tier: {field}")
                    elif metadata[field] is None or metadata[field] == "":
                        result["errors"].append(f"Empty value for required {tier} tier field: {field}")
        
        # Validate pattern_status
        if "pattern_status" in metadata:
            status = metadata["pattern_status"]
            if status not in self.valid_statuses:
                result["errors"].append(f"Invalid pattern_status '{status}'. Must be one of: {', '.join(self.valid_statuses)}")
                result["fixes_needed"].append({
                    "field": "pattern_status",
                    "current_value": status,
                    "suggested_fix": self._suggest_status_fix(status)
                })
        
        # Validate category consistency
        if "category" in metadata and category_from_path:
            if metadata["category"] != category_from_path:
                result["errors"].append(f"Category mismatch: metadata says '{metadata['category']}' but file is in '{category_from_path}' folder")
        
        # Validate category value
        if "category" in metadata:
            if metadata["category"] not in self.valid_categories:
                result["errors"].append(f"Invalid category '{metadata['category']}'. Must be one of: {', '.join(self.valid_categories)}")
        
        # Validate current_relevance
        if "current_relevance" in metadata:
            relevance = metadata["current_relevance"]
            if relevance not in self.valid_relevance:
                result["errors"].append(f"Invalid current_relevance '{relevance}'. Must be one of: {', '.join(self.valid_relevance)}")
        
        # Check for field naming consistency (prefer hyphens)
        for field in metadata:
            if '_' in field and field not in ['excellence_tier', 'pattern_status', 'current_relevance']:
                suggested = field.replace('_', '-')
                result["warnings"].append(f"Field naming: prefer '{suggested}' over '{field}'")
                result["fixes_needed"].append({
                    "field": field,
                    "current_value": field,
                    "suggested_fix": suggested,
                    "type": "field_rename"
                })
        
        # Validate introduced date format
        if "introduced" in metadata:
            introduced = str(metadata["introduced"])
            if not re.match(r'^\d{4}-\d{2}$', introduced):
                result["warnings"].append(f"Introduced date '{introduced}' should be in YYYY-MM format")
        
        return result

    def _suggest_status_fix(self, invalid_status: str) -> str:
        """Suggest a valid status for invalid values."""
        mapping = {
            "educational-only": "use-with-caution",
            "use-with-context": "use-with-expertise",
            "deprecated": "legacy",
            "experimental": "use-with-caution",
            "beta": "use-with-expertise",
            "stable": "recommended"
        }
        return mapping.get(invalid_status, "use-with-expertise")

    def validate_all_patterns(self) -> Dict[str, Any]:
        """Validate all pattern files in the pattern library."""
        pattern_files = list(self.base_path.rglob("*.md"))
        
        all_results = []
        error_count = 0
        warning_count = 0
        fixes_count = 0
        
        for file_path in pattern_files:
            result = self.validate_pattern_file(file_path)
            all_results.append(result)
            
            error_count += len(result["errors"])
            warning_count += len(result["warnings"])
            fixes_count += len(result["fixes_needed"])
        
        # Compile summary
        self.validation_results.update({
            "total_patterns": len([r for r in all_results if not any(skip in r["file"] for skip in ["index.md", "pattern-"])]),
            "total_files_checked": len(pattern_files),
            "total_errors": error_count,
            "total_warnings": warning_count,
            "total_fixes_needed": fixes_count,
            "results": all_results
        })
        
        # Generate detailed summary
        self.validation_results["summary"] = self._generate_summary(all_results)
        
        return self.validation_results

    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate a detailed summary of validation results."""
        summary = {
            "patterns_with_errors": [],
            "patterns_missing_fields": defaultdict(list),
            "invalid_status_values": [],
            "category_mismatches": [],
            "field_naming_issues": [],
            "patterns_by_tier": defaultdict(list),
            "patterns_by_status": defaultdict(list)
        }
        
        for result in results:
            file_path = result["file"]
            
            # Skip index and special files
            if "index.md" in file_path or "pattern-" in Path(file_path).name:
                continue
            
            metadata = result["metadata"]
            
            if result["errors"]:
                summary["patterns_with_errors"].append({
                    "file": file_path,
                    "errors": result["errors"]
                })
            
            # Track missing fields
            for error in result["errors"]:
                if "Missing required field:" in error:
                    field = error.split("Missing required field: ")[1]
                    summary["patterns_missing_fields"][field].append(file_path)
                elif "Invalid pattern_status" in error:
                    summary["invalid_status_values"].append({
                        "file": file_path,
                        "error": error
                    })
                elif "Category mismatch" in error:
                    summary["category_mismatches"].append({
                        "file": file_path,
                        "error": error
                    })
            
            # Track field naming issues
            for fix in result["fixes_needed"]:
                if fix.get("type") == "field_rename":
                    summary["field_naming_issues"].append({
                        "file": file_path,
                        "field": fix["field"],
                        "suggested": fix["suggested_fix"]
                    })
            
            # Track patterns by tier and status
            if "excellence_tier" in metadata:
                summary["patterns_by_tier"][metadata["excellence_tier"]].append(file_path)
            if "pattern_status" in metadata:
                summary["patterns_by_status"][metadata["pattern_status"]].append(file_path)
        
        return summary

    def generate_fix_script(self) -> str:
        """Generate a Python script to fix the identified issues."""
        fixes = []
        
        for result in self.validation_results.get("results", []):
            file_path = result["file"]
            fixes_needed = result["fixes_needed"]
            
            if not fixes_needed:
                continue
            
            fixes.append(f"# Fixes for {file_path}")
            
            for fix in fixes_needed:
                if fix.get("type") == "field_rename":
                    fixes.append(f"rename_field('{file_path}', '{fix['field']}', '{fix['suggested_fix']}')")
                elif "pattern_status" in fix.get("field", ""):
                    fixes.append(f"update_field('{file_path}', 'pattern_status', '{fix['suggested_fix']}')")
        
        script_template = """#!/usr/bin/env python3
'''
Auto-generated script to fix pattern metadata issues
'''

import yaml
import re
from pathlib import Path

def update_field(file_path: str, field: str, new_value: str):
    '''Update a field value in the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"No frontmatter found in {{file_path}}")
            return
        
        end_marker = content.find('\\n---\\n', 3)
        if end_marker == -1:
            end_marker = content.find('\\n---', 3)
            if end_marker == -1:
                print(f"Could not find end of frontmatter in {{file_path}}")
                return
        
        frontmatter = content[3:end_marker].strip()
        body = content[end_marker + 4:]
        
        # Parse and update
        data = yaml.safe_load(frontmatter) or {{}}
        data[field] = new_value
        
        # Write back
        new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
        new_content = f"---\\n{{new_frontmatter}}---\\n{{body}}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {{field}} in {{file_path}}")
    
    except Exception as e:
        print(f"Error updating {{file_path}}: {{e}}")

def rename_field(file_path: str, old_field: str, new_field: str):
    '''Rename a field in the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"No frontmatter found in {{file_path}}")
            return
        
        end_marker = content.find('\\n---\\n', 3)
        if end_marker == -1:
            end_marker = content.find('\\n---', 3)
            if end_marker == -1:
                print(f"Could not find end of frontmatter in {{file_path}}")
                return
        
        frontmatter = content[3:end_marker].strip()
        body = content[end_marker + 4:]
        
        # Parse, rename, and update
        data = yaml.safe_load(frontmatter) or {{}}
        if old_field in data:
            data[new_field] = data.pop(old_field)
            
            # Write back
            new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
            new_content = f"---\\n{{new_frontmatter}}---\\n{{body}}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Renamed {{old_field}} to {{new_field}} in {{file_path}}")
    
    except Exception as e:
        print(f"Error renaming field in {{file_path}}: {{e}}")

def add_missing_field(file_path: str, field: str, value: str):
    '''Add a missing field to the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            # Add frontmatter if missing
            new_content = f"---\\n{{field}}: {{value}}\\n---\\n{{content}}"
        else:
            end_marker = content.find('\\n---\\n', 3)
            if end_marker == -1:
                end_marker = content.find('\\n---', 3)
                if end_marker == -1:
                    print(f"Could not find end of frontmatter in {{file_path}}")
                    return
            
            frontmatter = content[3:end_marker].strip()
            body = content[end_marker + 4:]
            
            # Parse and add field
            data = yaml.safe_load(frontmatter) or {{}}
            if field not in data:
                data[field] = value
                
                # Write back
                new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
                new_content = f"---\\n{{new_frontmatter}}---\\n{{body}}"
            else:
                print(f"Field {{field}} already exists in {{file_path}}")
                return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added {{field}} to {{file_path}}")
    
    except Exception as e:
        print(f"Error adding field to {{file_path}}: {{e}}")

if __name__ == "__main__":
    print("Starting pattern metadata fixes...")
    
    {fixes_code}
    
    print("Pattern metadata fixes completed!")
"""
        
        fixes_code = '\n    '.join(fixes) if fixes else '# No fixes needed'
        return script_template.format(fixes_code=fixes_code)

def main():
    """Main validation function."""
    print("🔍 Validating Pattern Metadata...")
    
    validator = PatternMetadataValidator()
    results = validator.validate_all_patterns()
    
    # Print summary
    print(f"\n📊 VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total patterns checked: {results['total_patterns']}")
    print(f"Total errors: {results['total_errors']}")
    print(f"Total warnings: {results['total_warnings']}")
    print(f"Total fixes needed: {results['total_fixes_needed']}")
    
    # Print detailed issues
    summary = results["summary"]
    
    if summary["patterns_with_errors"]:
        print(f"\n❌ PATTERNS WITH ERRORS ({len(summary['patterns_with_errors'])})")
        for pattern in summary["patterns_with_errors"]:
            print(f"  📁 {pattern['file']}")
            for error in pattern["errors"]:
                print(f"    • {error}")
    
    if summary["invalid_status_values"]:
        print(f"\n🚨 INVALID STATUS VALUES ({len(summary['invalid_status_values'])})")
        for item in summary["invalid_status_values"]:
            print(f"  📁 {item['file']}")
            print(f"    • {item['error']}")
    
    if summary["patterns_missing_fields"]:
        print(f"\n📝 MISSING FIELDS")
        for field, files in summary["patterns_missing_fields"].items():
            print(f"  🏷️  {field}: {len(files)} patterns")
            if len(files) <= 5:  # Show files if few
                for file in files:
                    print(f"    • {Path(file).name}")
    
    if summary["field_naming_issues"]:
        print(f"\n🔤 FIELD NAMING ISSUES ({len(summary['field_naming_issues'])})")
        for item in summary["field_naming_issues"]:
            print(f"  📁 {Path(item['file']).name}: {item['field']} → {item['suggested']}")
    
    # Tier and status distribution
    print(f"\n📈 PATTERN DISTRIBUTION")
    print(f"By Tier:")
    for tier, files in summary["patterns_by_tier"].items():
        print(f"  🎯 {tier}: {len(files)} patterns")
    
    print(f"By Status:")
    for status, files in summary["patterns_by_status"].items():
        print(f"  📊 {status}: {len(files)} patterns")
    
    # Save detailed results
    output_file = "pattern_metadata_validation_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Generate fix script
    fix_script = validator.generate_fix_script()
    with open("fix_pattern_metadata.py", 'w') as f:
        f.write(fix_script)
    
    print("🔧 Fix script generated: fix_pattern_metadata.py")
    
    return results

if __name__ == "__main__":
    main()