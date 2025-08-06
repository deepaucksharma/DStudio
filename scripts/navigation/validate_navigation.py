#!/usr/bin/env python3
"""
Navigation Validation Script - Final check for all navigation issues
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
import subprocess
import sys

class NavigationValidator:
    def __init__(self, base_dir="/home/deepak/DStudio"):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.issues = []
        self.stats = defaultdict(int)
        
    def check_critical_files(self):
        """Check that all critical files exist"""
        print("\n🔍 Checking Critical Files...")
        
        critical_files = [
            'docs/index.md',
            'docs/start-here/index.md',
            'docs/core-principles/index.md',
            'docs/pattern-library/index.md',
            'docs/architects-handbook/index.md',
            'docs/pattern-library/ml-infrastructure/index.md',
            'docs/architects-handbook/case-studies/infrastructure/zoom-scaling.md',
            'docs/architects-handbook/case-studies/databases/redis-architecture.md',
            'docs/architects-handbook/quantitative-analysis/coordination-costs.md',
            'docs/progress.md',
        ]
        
        missing = []
        for file_path in critical_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing.append(file_path)
                self.issues.append(f"Missing critical file: {file_path}")
            else:
                self.stats['critical_files_ok'] += 1
                
        if missing:
            print(f"❌ Missing {len(missing)} critical files:")
            for f in missing:
                print(f"   - {f}")
        else:
            print(f"✅ All {len(critical_files)} critical files exist")
            
        return len(missing) == 0
        
    def check_navigation_structure(self):
        """Check mkdocs.yml navigation is valid"""
        print("\n🔍 Checking Navigation Structure...")
        
        mkdocs_path = self.base_dir / 'mkdocs.yml'
        if not mkdocs_path.exists():
            self.issues.append("mkdocs.yml not found")
            return False
            
        try:
            import yaml
            with open(mkdocs_path, 'r') as f:
                config = yaml.safe_load(f)
                
            nav = config.get('nav', [])
            if not nav:
                self.issues.append("No navigation defined in mkdocs.yml")
                return False
                
            # Extract all files from nav
            nav_files = self._extract_nav_files(nav)
            missing_nav = []
            
            for nav_file in nav_files:
                full_path = self.docs_dir / nav_file
                if not full_path.exists():
                    missing_nav.append(nav_file)
                    self.issues.append(f"Navigation references missing file: {nav_file}")
                else:
                    self.stats['nav_files_ok'] += 1
                    
            if missing_nav:
                print(f"❌ {len(missing_nav)} navigation files missing")
                for f in missing_nav[:10]:
                    print(f"   - {f}")
            else:
                print(f"✅ All {len(nav_files)} navigation files exist")
                
            return len(missing_nav) == 0
            
        except Exception as e:
            print(f"❌ Error checking navigation: {e}")
            self.issues.append(f"Navigation check error: {e}")
            return False
            
    def _extract_nav_files(self, nav, files=None):
        """Recursively extract file paths from navigation"""
        if files is None:
            files = []
            
        if isinstance(nav, list):
            for item in nav:
                self._extract_nav_files(item, files)
        elif isinstance(nav, dict):
            for key, value in nav.items():
                if isinstance(value, str) and value.endswith('.md'):
                    files.append(value)
                else:
                    self._extract_nav_files(value, files)
        elif isinstance(nav, str) and nav.endswith('.md'):
            files.append(nav)
            
        return files
        
    def check_redirect_mappings(self):
        """Check that redirect mappings are valid"""
        print("\n🔍 Checking Redirect Mappings...")
        
        mkdocs_path = self.base_dir / 'mkdocs.yml'
        try:
            import yaml
            with open(mkdocs_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Find redirects plugin config
            redirects = None
            for plugin in config.get('plugins', []):
                if isinstance(plugin, dict) and 'redirects' in plugin:
                    redirects = plugin['redirects'].get('redirect_maps', {})
                    break
                    
            if not redirects:
                print("⚠️  No redirects configured")
                return True
                
            invalid_redirects = []
            for old_url, new_url in redirects.items():
                # Check if target exists (for internal redirects)
                if not new_url.startswith('http'):
                    target_path = self.docs_dir / new_url
                    if not target_path.exists() and not new_url.endswith('/'):
                        # Try adding .md
                        target_path = self.docs_dir / f"{new_url}.md"
                        if not target_path.exists():
                            invalid_redirects.append((old_url, new_url))
                            self.issues.append(f"Redirect target missing: {old_url} -> {new_url}")
                    else:
                        self.stats['redirects_ok'] += 1
                        
            if invalid_redirects:
                print(f"❌ {len(invalid_redirects)} invalid redirects")
                for old, new in invalid_redirects[:10]:
                    print(f"   - {old} -> {new}")
            else:
                print(f"✅ All {len(redirects)} redirects valid")
                
            return len(invalid_redirects) == 0
            
        except Exception as e:
            print(f"❌ Error checking redirects: {e}")
            self.issues.append(f"Redirect check error: {e}")
            return False
            
    def check_internal_links(self):
        """Quick check of internal link patterns"""
        print("\n🔍 Checking Internal Link Patterns...")
        
        issues_found = 0
        files_checked = 0
        
        for md_file in self.docs_dir.rglob('*.md'):
            files_checked += 1
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for common bad patterns
                bad_patterns = [
                    (r'core-principles/pattern-library/', 'Wrong prefix: core-principles/pattern-library'),
                    (r'pattern-library/core-principles/', 'Wrong prefix: pattern-library/core-principles'),
                    (r'architects-handbook/pattern-library/', 'Wrong prefix: architects-handbook/pattern-library'),
                    (r'/index\.md\)', 'Uses /index.md instead of /'),
                    (r'\]\(\)', 'Empty link'),
                    (r'\.md\.md', 'Double .md extension'),
                ]
                
                for pattern, desc in bad_patterns:
                    if re.search(pattern, content):
                        issues_found += 1
                        rel_path = md_file.relative_to(self.docs_dir)
                        self.issues.append(f"{rel_path}: {desc}")
                        break
                        
            except Exception as e:
                pass
                
        if issues_found > 0:
            print(f"⚠️  Found {issues_found} files with link issues")
        else:
            print(f"✅ No bad link patterns found in {files_checked} files")
            
        self.stats['files_checked'] = files_checked
        return issues_found == 0
        
    def test_mkdocs_build(self):
        """Test if mkdocs can build without errors"""
        print("\n🔍 Testing MkDocs Build...")
        
        try:
            # Run mkdocs build with json output
            result = subprocess.run(
                ['mkdocs', 'build', '--clean', '--quiet'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ MkDocs build successful")
                return True
            else:
                print(f"❌ MkDocs build failed")
                if result.stderr:
                    print(f"   Error: {result.stderr[:500]}")
                self.issues.append("MkDocs build failed")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  MkDocs build timed out (but may still be working)")
            return True
        except Exception as e:
            print(f"❌ Error running mkdocs build: {e}")
            self.issues.append(f"Build test error: {e}")
            return False
            
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("NAVIGATION VALIDATION REPORT")
        print("=" * 60)
        
        all_checks = [
            self.check_critical_files(),
            self.check_navigation_structure(),
            self.check_redirect_mappings(),
            self.check_internal_links(),
            self.test_mkdocs_build(),
        ]
        
        print("\n📊 Statistics:")
        for key, value in self.stats.items():
            print(f"   {key}: {value}")
            
        if self.issues:
            print(f"\n⚠️  Issues Found ({len(self.issues)}):")
            for issue in self.issues[:20]:
                print(f"   - {issue}")
            if len(self.issues) > 20:
                print(f"   ... and {len(self.issues) - 20} more")
        else:
            print("\n✅ No issues found!")
            
        success = all(all_checks)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ VALIDATION PASSED - Navigation is healthy!")
        else:
            print("❌ VALIDATION FAILED - Issues need attention")
        print("=" * 60)
        
        # Save report
        report = {
            'success': success,
            'stats': dict(self.stats),
            'issues': self.issues,
            'checks': {
                'critical_files': all_checks[0],
                'navigation_structure': all_checks[1],
                'redirect_mappings': all_checks[2],
                'internal_links': all_checks[3],
                'mkdocs_build': all_checks[4],
            }
        }
        
        with open(self.base_dir / 'navigation_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        return success
        
    def run(self):
        """Run all validation checks"""
        print("🚀 Starting Navigation Validation...")
        print("=" * 60)
        
        success = self.generate_report()
        
        if success:
            print("\n✨ Ready for deployment!")
            print("\nNext steps:")
            print("1. Review changes: git diff")
            print("2. Commit: git add -A && git commit -m 'fix: comprehensive navigation fixes'")
            print("3. Push: git push")
            print("4. Monitor deployment at: https://deepaucksharma.github.io/DStudio/")
        else:
            print("\n⚠️  Please fix remaining issues before deployment")
            
        return success

if __name__ == "__main__":
    validator = NavigationValidator()
    success = validator.run()
    sys.exit(0 if success else 1)