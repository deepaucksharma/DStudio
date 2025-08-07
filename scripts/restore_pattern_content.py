#!/usr/bin/env python3
"""
Restore pattern content from transformed versions and fix redirect stubs
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class PatternContentRestorer:
    def __init__(self):
        self.base_dir = Path("/home/deepak/DStudio/docs/pattern-library")
        self.issues_found = []
        self.files_restored = []
        
    def find_redirect_stubs(self) -> List[Tuple[Path, str]]:
        """Find all files that are redirect stubs"""
        stubs = []
        
        for pattern_file in self.base_dir.rglob("*.md"):
            if pattern_file.name == "index.md":
                continue
                
            with open(pattern_file, 'r') as f:
                content = f.read()
                
            # Check if it's a redirect stub
            if "redirect_to:" in content or "redirect:" in content:
                lines = content.split('\n')
                if len(lines) < 20:  # Stub files are typically very short
                    # Find redirect target
                    redirect_target = None
                    for line in lines:
                        if "redirect_to:" in line or "redirect:" in line:
                            redirect_target = line.split(':')[-1].strip()
                            break
                    
                    if redirect_target:
                        stubs.append((pattern_file, redirect_target))
                        
        return stubs
        
    def check_transformed_versions(self) -> Dict[str, Path]:
        """Find all transformed versions of patterns"""
        transformed = {}
        
        for pattern_file in self.base_dir.rglob("*-transformed.md"):
            base_name = pattern_file.stem.replace('-transformed', '')
            transformed[base_name] = pattern_file
            
        return transformed
        
    def restore_content_from_transformed(self):
        """Restore content from transformed versions to original files"""
        print("🔍 Scanning for redirect stubs and transformed versions...")
        
        stubs = self.find_redirect_stubs()
        transformed = self.check_transformed_versions()
        
        print(f"Found {len(stubs)} redirect stubs")
        print(f"Found {len(transformed)} transformed pattern files")
        
        restored_count = 0
        
        for stub_file, redirect_target in stubs:
            stub_name = stub_file.stem
            
            # Check if transformed version exists
            if stub_name in transformed:
                transformed_file = transformed[stub_name]
                
                print(f"\n📝 Restoring: {stub_file.name}")
                print(f"   From: {transformed_file.name}")
                
                # Read transformed content
                with open(transformed_file, 'r') as f:
                    content = f.read()
                    
                # Write to original file
                with open(stub_file, 'w') as f:
                    f.write(content)
                    
                self.files_restored.append({
                    'original': str(stub_file.relative_to(self.base_dir)),
                    'source': str(transformed_file.relative_to(self.base_dir)),
                    'size': len(content)
                })
                
                restored_count += 1
                
                # Optionally remove the transformed version
                # os.remove(transformed_file)
                
            elif redirect_target and (self.base_dir / stub_file.parent / redirect_target).exists():
                # Check if redirect target has the content
                target_file = self.base_dir / stub_file.parent / redirect_target
                
                with open(target_file, 'r') as f:
                    target_content = f.read()
                    
                if len(target_content) > 1000:  # Substantial content
                    print(f"\n📝 Found content at redirect target: {redirect_target}")
                    print(f"   For stub: {stub_file.name}")
                    
                    self.issues_found.append({
                        'stub': str(stub_file.relative_to(self.base_dir)),
                        'target': redirect_target,
                        'action': 'Review redirect - content exists at target'
                    })
                    
        print(f"\n✅ Restored {restored_count} pattern files")
        
    def check_content_quality(self):
        """Check quality of all pattern files after restoration"""
        print("\n🔍 Checking pattern content quality...")
        
        quality_issues = []
        good_patterns = []
        
        for pattern_file in self.base_dir.rglob("*.md"):
            if pattern_file.name == "index.md" or "-transformed" in pattern_file.name:
                continue
                
            with open(pattern_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Quality checks
            line_count = len(lines)
            has_code = "```" in content
            has_mermaid = "```mermaid" in content
            has_examples = any(word in content.lower() for word in ['example', 'netflix', 'amazon', 'google', 'uber'])
            
            if line_count < 100:
                quality_issues.append({
                    'file': str(pattern_file.relative_to(self.base_dir)),
                    'lines': line_count,
                    'issue': 'Too short (< 100 lines)'
                })
            elif not has_code:
                quality_issues.append({
                    'file': str(pattern_file.relative_to(self.base_dir)),
                    'lines': line_count,
                    'issue': 'No code examples'
                })
            elif not has_mermaid:
                quality_issues.append({
                    'file': str(pattern_file.relative_to(self.base_dir)),
                    'lines': line_count,
                    'issue': 'No diagrams'
                })
            else:
                good_patterns.append(str(pattern_file.relative_to(self.base_dir)))
                
        print(f"✅ Good quality patterns: {len(good_patterns)}")
        print(f"⚠️  Quality issues found: {len(quality_issues)}")
        
        return quality_issues
        
    def generate_report(self):
        """Generate restoration report"""
        quality_issues = self.check_content_quality()
        
        report = f"""# Pattern Content Restoration Report

## Summary

- **Files Restored**: {len(self.files_restored)}
- **Issues Found**: {len(self.issues_found)}
- **Quality Issues**: {len(quality_issues)}

## Restored Files

"""
        if self.files_restored:
            for item in self.files_restored:
                report += f"### {item['original']}\n"
                report += f"- Source: {item['source']}\n"
                report += f"- Size: {item['size']} bytes\n\n"
        else:
            report += "No files needed restoration.\n\n"
            
        report += "## Redirect Issues\n\n"
        
        if self.issues_found:
            for issue in self.issues_found:
                report += f"### {issue['stub']}\n"
                report += f"- Target: {issue['target']}\n"
                report += f"- Action: {issue['action']}\n\n"
        else:
            report += "No redirect issues found.\n\n"
            
        report += "## Content Quality Issues\n\n"
        
        if quality_issues:
            report += "| File | Lines | Issue |\n"
            report += "|------|-------|-------|\n"
            for issue in quality_issues[:20]:  # Show first 20
                report += f"| {issue['file']} | {issue['lines']} | {issue['issue']} |\n"
                
            if len(quality_issues) > 20:
                report += f"\n... and {len(quality_issues) - 20} more issues\n"
        else:
            report += "No quality issues found.\n"
            
        report += """

## Recommendations

1. Review all restored files to ensure content completeness
2. Address quality issues in short/incomplete patterns
3. Remove `-transformed.md` files after verification
4. Update any remaining redirect stubs
5. Run link validation to ensure all references work

## Next Steps

```bash
# Validate all links
python3 scripts/validate_pattern_links.py

# Check pattern quality
python3 scripts/pattern_library_qa_dashboard.py

# Build search index
python3 scripts/build_pattern_search_index.py
```
"""
        
        return report
        
    def run(self):
        """Run the restoration process"""
        print("=" * 60)
        print("🔧 Pattern Content Restoration Tool")
        print("=" * 60)
        
        # Restore content
        self.restore_content_from_transformed()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_file = Path("/home/deepak/DStudio/PATTERN_RESTORATION_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"\n📄 Report saved to: {report_file}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("✨ Restoration Summary:")
        print(f"  - Files restored: {len(self.files_restored)}")
        print(f"  - Issues to review: {len(self.issues_found)}")
        print("=" * 60)

def main():
    restorer = PatternContentRestorer()
    restorer.run()

if __name__ == "__main__":
    main()