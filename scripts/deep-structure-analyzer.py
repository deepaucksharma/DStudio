#!/usr/bin/env python3
"""Deep structural analysis of the entire documentation system."""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class DeepStructureAnalyzer:
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = docs_dir
        self.issues = defaultdict(list)
        self.statistics = defaultdict(int)
        
    def analyze_frontmatter_consistency(self):
        """Analyze all frontmatter for consistency issues."""
        print("\n🔍 ANALYZING FRONTMATTER CONSISTENCY...")
        
        frontmatter_keys = defaultdict(list)
        no_frontmatter = []
        inconsistent_keys = defaultdict(list)
        
        for md_file in self.docs_dir.glob("**/*.md"):
            rel_path = md_file.relative_to(self.docs_dir)
            content = md_file.read_text()
            
            if not content.startswith('---'):
                no_frontmatter.append(str(rel_path))
                self.issues['no_frontmatter'].append(str(rel_path))
                continue
                
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if fm:
                        # Track all keys used
                        for key in fm.keys():
                            frontmatter_keys[key].append(str(rel_path))
                            
                        # Check for inconsistent key formats
                        if 'best-for' in fm:
                            inconsistent_keys['best-for'].append(str(rel_path))
                        if 'best_for' in fm:
                            inconsistent_keys['best_for'].append(str(rel_path))
                            
                        # Check law references in tags
                        if 'tags' in fm and isinstance(fm['tags'], list):
                            for tag in fm['tags']:
                                if re.match(r'law\d-', tag):
                                    self.issues['old_law_tags'].append({
                                        'file': str(rel_path),
                                        'tag': tag
                                    })
            except:
                self.issues['invalid_yaml'].append(str(rel_path))
        
        # Report findings
        print(f"\n📊 Frontmatter Statistics:")
        print(f"  - Files without frontmatter: {len(no_frontmatter)}")
        print(f"  - Files with 'best-for': {len(inconsistent_keys['best-for'])}")
        print(f"  - Files with 'best_for': {len(inconsistent_keys['best_for'])}")
        
        if no_frontmatter:
            print(f"\n❌ Files missing frontmatter:")
            for f in no_frontmatter[:5]:
                print(f"    - {f}")
            if len(no_frontmatter) > 5:
                print(f"    ... and {len(no_frontmatter) - 5} more")
                
        self.statistics['frontmatter_issues'] = len(no_frontmatter) + len(inconsistent_keys['best-for']) + len(inconsistent_keys['best_for'])
        
    def analyze_law_references(self):
        """Analyze all law references for consistency."""
        print("\n🔍 ANALYZING LAW REFERENCES...")
        
        old_patterns = [
            r'law1-failure',
            r'law2-asynchrony', 
            r'law3-chaos',
            r'law4-tradeoffs',
            r'law5-epistemology',
            r'law6-load',
            r'law7-economics',
            r'part1-axioms',
            r'/axioms/',
        ]
        
        for md_file in self.docs_dir.glob("**/*.md"):
            rel_path = md_file.relative_to(self.docs_dir)
            content = md_file.read_text()
            
            for pattern in old_patterns:
                if re.search(pattern, content):
                    self.issues['old_law_references'].append({
                        'file': str(rel_path),
                        'pattern': pattern,
                        'count': len(re.findall(pattern, content))
                    })
                    
        print(f"\n📊 Law Reference Issues:")
        print(f"  - Files with old law references: {len(self.issues['old_law_references'])}")
        
        self.statistics['law_reference_issues'] = len(self.issues['old_law_references'])
        
    def analyze_path_consistency(self):
        """Analyze path references for consistency."""
        print("\n🔍 ANALYZING PATH CONSISTENCY...")
        
        # Check for actual file structure
        actual_structure = {
            'laws': list((self.docs_dir / "core-principles" / "laws").glob("*.md")),
            'pillars': list((self.docs_dir / "core-principles" / "pillars").glob("*.md")),
            'patterns': list((self.docs_dir / "pattern-library").glob("**/*.md"))
        }
        
        # Common path issues
        path_issues = {
            '../patterns/': [],
            '/pillars/work/': [],
            '/pillars/state/': [],
            '../quantitative/': [],
            'law[0-9]-[a-z]+/': []
        }
        
        for md_file in self.docs_dir.glob("**/*.md"):
            rel_path = md_file.relative_to(self.docs_dir)
            content = md_file.read_text()
            
            for pattern, files in path_issues.items():
                if re.search(pattern, content):
                    files.append(str(rel_path))
                    
        # Check pillar references
        pillar_confusion = {
            'work': 'work-distribution',
            'state': 'state-distribution',
            'truth': 'truth-distribution',
            'control': 'control-distribution',
            'intelligence': 'intelligence-distribution'
        }
        
        for short, full in pillar_confusion.items():
            pattern = f'/pillars/{short}/'
            for md_file in self.docs_dir.glob("**/*.md"):
                content = md_file.read_text()
                if pattern in content:
                    self.issues['pillar_path_confusion'].append({
                        'file': str(md_file.relative_to(self.docs_dir)),
                        'wrong': pattern,
                        'correct': f'/pillars/{full}/'
                    })
                    
        print(f"\n📊 Path Consistency Issues:")
        for pattern, files in path_issues.items():
            if files:
                print(f"  - '{pattern}' found in {len(files)} files")
                
        self.statistics['path_issues'] = sum(len(files) for files in path_issues.values())
        
    def analyze_mkdocs_alignment(self):
        """Check if mkdocs.yml aligns with actual file structure."""
        print("\n🔍 ANALYZING MKDOCS.YML ALIGNMENT...")
        
        # Custom YAML loader that ignores MkDocs-specific tags
        class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
            pass
        
        def constructor_undefined(loader, node):
            if isinstance(node, yaml.ScalarNode):
                value = loader.construct_scalar(node)
                return f"tag:{node.tag}:{value}"
            elif isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node)
            elif isinstance(node, yaml.MappingNode):
                return loader.construct_mapping(node)
            return None
        
        SafeLoaderIgnoreUnknown.add_constructor(None, constructor_undefined)
        
        mkdocs_path = self.docs_dir.parent / "mkdocs.yml"
        with open(mkdocs_path) as f:
            mkdocs_config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
            
        # Extract all referenced files from navigation
        nav_files = set()
        
        def extract_files(nav_item):
            if isinstance(nav_item, str):
                nav_files.add(nav_item)
            elif isinstance(nav_item, dict):
                for value in nav_item.values():
                    extract_files(value)
            elif isinstance(nav_item, list):
                for item in nav_item:
                    extract_files(item)
                    
        extract_files(mkdocs_config.get('nav', []))
        
        # Check if files exist
        missing_files = []
        for nav_file in nav_files:
            if nav_file.endswith('.md'):
                full_path = self.docs_dir / nav_file
                if not full_path.exists():
                    missing_files.append(nav_file)
                    
        # Check for orphaned files
        all_md_files = set(str(f.relative_to(self.docs_dir)) for f in self.docs_dir.glob("**/*.md"))
        orphaned_files = all_md_files - nav_files
        
        print(f"\n📊 MkDocs Alignment:")
        print(f"  - Files in nav but missing: {len(missing_files)}")
        print(f"  - Files exist but not in nav: {len(orphaned_files)}")
        
        self.statistics['mkdocs_issues'] = len(missing_files) + len(orphaned_files)
        
    def analyze_empty_directories(self):
        """Check for empty or confusing directories."""
        print("\n🔍 ANALYZING DIRECTORY STRUCTURE...")
        
        # Check patterns directory
        patterns_dir = self.docs_dir / "patterns"
        if patterns_dir.exists():
            if patterns_dir.is_symlink():
                print(f"  - /patterns/ is a symlink to {patterns_dir.readlink()}")
            else:
                files = list(patterns_dir.glob("**/*.md"))
                print(f"  - /patterns/ contains {len(files)} files")
                if len(files) == 0:
                    self.issues['empty_patterns_dir'] = True
                    
    def generate_report(self):
        """Generate comprehensive report."""
        print("\n" + "="*80)
        print("🚨 DEEP STRUCTURE ANALYSIS REPORT")
        print("="*80)
        
        total_issues = sum(self.statistics.values())
        
        print(f"\n📊 TOTAL ISSUES FOUND: {total_issues}")
        print(f"\n🔥 CRITICAL ISSUES BY CATEGORY:")
        
        categories = [
            ("Frontmatter Chaos", self.statistics['frontmatter_issues']),
            ("Law Reference Breakdown", self.statistics['law_reference_issues']),
            ("Path Consistency Failures", self.statistics['path_issues']),
            ("MkDocs Misalignment", self.statistics['mkdocs_issues'])
        ]
        
        for category, count in categories:
            if count > 0:
                print(f"  - {category}: {count} issues")
                
        # Write detailed issues to file
        with open("DEEP_STRUCTURE_ISSUES.json", "w") as f:
            json.dump(dict(self.issues), f, indent=2)
            
        print(f"\n📄 Detailed issues written to DEEP_STRUCTURE_ISSUES.json")
        
        return total_issues > 0
        
    def run_analysis(self):
        """Run complete deep structure analysis."""
        print("🔬 RUNNING DEEP STRUCTURE ANALYSIS...")
        print("="*80)
        
        self.analyze_frontmatter_consistency()
        self.analyze_law_references()
        self.analyze_path_consistency()
        self.analyze_mkdocs_alignment()
        self.analyze_empty_directories()
        
        has_issues = self.generate_report()
        
        if has_issues:
            print("\n❌ VERDICT: SYSTEMATIC STRUCTURAL BREAKDOWN CONFIRMED")
            print("The documentation has fundamental organizational issues that require architectural fixes.")
        else:
            print("\n✅ VERDICT: Structure is consistent")
            
        return has_issues

def main():
    analyzer = DeepStructureAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()