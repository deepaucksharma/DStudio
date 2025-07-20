#!/usr/bin/env python3
"""
Targeted Broken Link Fixer

This script focuses on fixing the specific types of broken links found:
1. Placeholder links (../../placeholder.md, ../../patterns/placeholder.md)
2. Missing .md extensions
3. Wrong relative paths
4. Non-existent files that should exist

Uses a more aggressive approach with better heuristics.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class TargetedLinkFixer:
    def __init__(self, docs_dir="/Users/deepaksharma/syc/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.all_files = set()
        self.path_mappings = {}
        self.fixed_links = []
        self.unfixable_links = []
        self.placeholder_replacements = {}
        
        # Build comprehensive file index
        self._build_file_index()
        self._build_path_mappings()
        self._build_placeholder_replacements()

    def _build_file_index(self):
        """Build index of all markdown files"""
        for file_path in self.docs_dir.rglob("*.md"):
            if file_path.is_file():
                # Store both absolute and relative paths
                rel_path = file_path.relative_to(self.docs_dir)
                self.all_files.add(str(rel_path))
                self.all_files.add(str(rel_path.with_suffix('')))  # Without .md
                
                # Also add directory-relative paths
                self.all_files.add(file_path.name)
                self.all_files.add(file_path.stem)

    def _build_path_mappings(self):
        """Build mappings for common path patterns"""
        # Map file stems to their full paths
        stem_to_paths = defaultdict(list)
        
        for file_path in self.docs_dir.rglob("*.md"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.docs_dir)
                stem = file_path.stem
                stem_to_paths[stem].append(str(rel_path))
        
        # Store mappings where there's a unique match
        for stem, paths in stem_to_paths.items():
            if len(paths) == 1:
                self.path_mappings[stem] = paths[0]
            elif len(paths) > 1:
                # Prefer index files
                index_paths = [p for p in paths if 'index.md' in p]
                if index_paths:
                    self.path_mappings[stem] = index_paths[0]
                else:
                    self.path_mappings[stem] = paths[0]  # Take first

    def _build_placeholder_replacements(self):
        """Build replacements for known placeholder patterns"""
        self.placeholder_replacements = {
            # Pattern placeholders to real patterns
            "../../patterns/placeholder.md": self._find_best_pattern_match,
            "../../patterns/circuit-breaker.md": "../../patterns/circuit-breaker.md",
            "../../patterns/retry-backoff.md": "../../patterns/retry-backoff.md",
            
            # Axiom placeholders
            "../../part1-axioms/placeholder.md": self._find_best_axiom_match,
            
            # Case study placeholders
            "../../case-studies/placeholder.md": self._find_best_case_study_match,
            
            # Quantitative placeholders
            "../../quantitative/placeholder.md": self._find_best_quantitative_match,
            
            # Generic placeholder
            "../../placeholder.md": self._find_best_generic_match,
            "../placeholder.md": self._find_best_generic_match,
            "placeholder.md": self._find_best_generic_match,
        }

    def _find_best_pattern_match(self, context_file, link_text=""):
        """Find best pattern replacement based on context"""
        patterns = list(self.docs_dir.glob("patterns/*.md"))
        pattern_names = [p.stem for p in patterns if p.stem != "index"]
        
        # Look for context clues in surrounding text
        if "circuit" in link_text.lower() or "breaker" in link_text.lower():
            return "../../patterns/circuit-breaker.md"
        elif "retry" in link_text.lower() or "backoff" in link_text.lower():
            return "../../patterns/retry-backoff.md"
        elif "cache" in link_text.lower() or "caching" in link_text.lower():
            return "../../patterns/caching-strategies.md"
        elif "load" in link_text.lower() and "balanc" in link_text.lower():
            return "../../patterns/load-balancing.md"
        elif "timeout" in link_text.lower():
            return "../../patterns/timeout.md"
        
        # Default to most common pattern
        return "../../patterns/circuit-breaker.md"

    def _find_best_axiom_match(self, context_file, link_text=""):
        """Find best axiom replacement"""
        if "latency" in link_text.lower() or "speed" in link_text.lower():
            return "../../part1-axioms/axiom1-latency/index.md"
        elif "capacity" in link_text.lower() or "finite" in link_text.lower():
            return "../../part1-axioms/axiom2-capacity/index.md"
        elif "failure" in link_text.lower() or "fail" in link_text.lower():
            return "../../part1-axioms/axiom3-failure/index.md"
        
        return "../../part1-axioms/axiom1-latency/index.md"

    def _find_best_case_study_match(self, context_file, link_text=""):
        """Find best case study replacement"""
        if "uber" in link_text.lower() or "location" in link_text.lower():
            return "../../case-studies/uber-location.md"
        elif "amazon" in link_text.lower() or "dynamo" in link_text.lower():
            return "../../case-studies/amazon-dynamo.md"
        elif "spotify" in link_text.lower() or "recommend" in link_text.lower():
            return "../../case-studies/spotify-recommendations.md"
        
        return "../../case-studies/uber-location.md"

    def _find_best_quantitative_match(self, context_file, link_text=""):
        """Find best quantitative replacement"""
        if "capacity" in link_text.lower() or "planning" in link_text.lower():
            return "../../quantitative/capacity-planning.md"
        elif "queue" in link_text.lower() or "latency" in link_text.lower():
            return "../../quantitative/queueing-models.md"
        elif "scale" in link_text.lower() or "universal" in link_text.lower():
            return "../../quantitative/universal-scalability.md"
        
        return "../../quantitative/capacity-planning.md"

    def _find_best_generic_match(self, context_file, link_text=""):
        """Find best generic replacement"""
        # Based on the context file location, guess appropriate section
        context_str = str(context_file)
        
        if "patterns" in context_str:
            return self._find_best_pattern_match(context_file, link_text)
        elif "axioms" in context_str:
            return self._find_best_axiom_match(context_file, link_text)
        elif "case-studies" in context_str:
            return self._find_best_case_study_match(context_file, link_text)
        elif "quantitative" in context_str:
            return self._find_best_quantitative_match(context_file, link_text)
        
        return "../../patterns/circuit-breaker.md"  # Safe default

    def find_all_links(self, content):
        """Find all markdown links in content"""
        # Match [text](link) and [text](link "title")
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        return re.findall(link_pattern, content)

    def is_broken_link(self, link_url, from_file):
        """Check if a link is broken"""
        # Skip external links, anchors, and special protocols
        if any(link_url.startswith(prefix) for prefix in ['http://', 'https://', 'mailto:', 'tel:', '#']):
            return False
        
        # Check for placeholder patterns
        if 'placeholder' in link_url:
            return True
        
        # Resolve the link relative to the file
        try:
            from_dir = from_file.parent
            target_path = (from_dir / link_url).resolve()
            
            # Check if target exists
            if not target_path.exists():
                return True
                
        except Exception:
            return True
        
        return False

    def fix_link(self, link_url, link_text, from_file):
        """Attempt to fix a broken link with improved heuristics"""
        original_url = link_url
        
        # Handle placeholder patterns first
        if 'placeholder' in link_url:
            if link_url in self.placeholder_replacements:
                if callable(self.placeholder_replacements[link_url]):
                    return self.placeholder_replacements[link_url](from_file, link_text)
                else:
                    return self.placeholder_replacements[link_url]
        
        # Handle missing .md extension
        if not link_url.endswith('.md') and not link_url.startswith('#'):
            # Check if adding .md makes it valid
            md_url = link_url + '.md'
            if not self.is_broken_link(md_url, from_file):
                return md_url
            
            # Check if it's a directory that should point to index.md
            index_url = link_url + '/index.md'
            if not self.is_broken_link(index_url, from_file):
                return index_url
        
        # Try to find the file by name
        link_basename = Path(link_url).name
        if link_basename.endswith('.md'):
            file_stem = link_basename[:-3]
        else:
            file_stem = link_basename
        
        # Look for exact match
        if file_stem in self.path_mappings:
            target_path = self.path_mappings[file_stem]
            
            # Calculate relative path from current file to target
            try:
                from_dir = from_file.parent
                relative_path = os.path.relpath(
                    self.docs_dir / target_path,
                    from_dir
                )
                return relative_path.replace('\\', '/')  # Use forward slashes
            except Exception:
                pass
        
        # Try intelligent pattern matching
        link_lower = link_url.lower()
        
        # Pattern-specific fixes
        if 'circuit' in link_lower and 'breaker' in link_lower:
            return self._calculate_relative_path(from_file, "patterns/circuit-breaker.md")
        elif 'retry' in link_lower:
            return self._calculate_relative_path(from_file, "patterns/retry-backoff.md")
        elif 'cache' in link_lower:
            return self._calculate_relative_path(from_file, "patterns/caching-strategies.md")
        elif 'load' in link_lower and 'balanc' in link_lower:
            return self._calculate_relative_path(from_file, "patterns/load-balancing.md")
        elif 'timeout' in link_lower:
            return self._calculate_relative_path(from_file, "patterns/timeout.md")
        
        # Axiom-specific fixes
        elif 'latency' in link_lower or 'axiom1' in link_lower:
            return self._calculate_relative_path(from_file, "part1-axioms/axiom1-latency/index.md")
        elif 'capacity' in link_lower or 'axiom2' in link_lower:
            return self._calculate_relative_path(from_file, "part1-axioms/axiom2-capacity/index.md")
        elif 'failure' in link_lower or 'axiom3' in link_lower:
            return self._calculate_relative_path(from_file, "part1-axioms/axiom3-failure/index.md")
        
        # Case study fixes
        elif 'uber' in link_lower:
            return self._calculate_relative_path(from_file, "case-studies/uber-location.md")
        elif 'amazon' in link_lower or 'dynamo' in link_lower:
            return self._calculate_relative_path(from_file, "case-studies/amazon-dynamo.md")
        elif 'spotify' in link_lower:
            return self._calculate_relative_path(from_file, "case-studies/spotify-recommendations.md")
        
        return None  # Could not fix

    def _calculate_relative_path(self, from_file, target_relative_path):
        """Calculate relative path from one file to another"""
        try:
            from_dir = from_file.parent
            target_path = self.docs_dir / target_relative_path
            
            if target_path.exists():
                relative_path = os.path.relpath(target_path, from_dir)
                return relative_path.replace('\\', '/')
        except Exception:
            pass
        return None

    def process_file(self, file_path):
        """Process a single file to fix broken links"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            links = self.find_all_links(content)
            
            changes_made = False
            
            for link_text, link_url in links:
                if self.is_broken_link(link_url, file_path):
                    fixed_url = self.fix_link(link_url, link_text, file_path)
                    
                    if fixed_url and fixed_url != link_url:
                        # Replace the specific link in content
                        old_link = f'[{link_text}]({link_url})'
                        new_link = f'[{link_text}]({fixed_url})'
                        
                        if old_link in content:
                            content = content.replace(old_link, new_link, 1)
                            changes_made = True
                            
                            self.fixed_links.append({
                                'file': str(file_path),
                                'old_url': link_url,
                                'new_url': fixed_url,
                                'link_text': link_text
                            })
                    else:
                        self.unfixable_links.append({
                            'file': str(file_path),
                            'url': link_url,
                            'text': link_text
                        })
            
            # Write back if changes were made
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
        
        return False

    def run(self):
        """Main execution function"""
        print("=== Targeted Broken Link Fixer ===\n")
        
        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"Processing {len(md_files)} markdown files...\n")
        
        processed_files = 0
        
        for file_path in md_files:
            if self.process_file(file_path):
                processed_files += 1
                print(f"✓ Fixed links in: {file_path.relative_to(self.docs_dir)}")
        
        # Generate report
        self.generate_report(processed_files, len(md_files))

    def generate_report(self, processed_files, total_files):
        """Generate detailed report"""
        print("\n" + "="*60)
        print("TARGETED LINK FIXING REPORT")
        print("="*60)
        
        print(f"\n📁 FILES PROCESSED:")
        print(f"   • Total files scanned: {total_files}")
        print(f"   • Files with fixes: {processed_files}")
        
        print(f"\n✅ LINKS FIXED: {len(self.fixed_links)}")
        if self.fixed_links:
            for fix in self.fixed_links[:10]:  # Show first 10
                print(f"   • {Path(fix['file']).name}: '{fix['old_url']}' → '{fix['new_url']}'")
            if len(self.fixed_links) > 10:
                print(f"   ... and {len(self.fixed_links) - 10} more")
        
        print(f"\n❌ UNFIXABLE LINKS: {len(self.unfixable_links)}")
        if self.unfixable_links:
            # Group by URL for cleaner output
            url_counts = defaultdict(list)
            for link in self.unfixable_links:
                url_counts[link['url']].append(link['file'])
            
            for url, files in list(url_counts.items())[:10]:  # Show first 10
                print(f"   • '{url}' (in {len(files)} files)")
            if len(url_counts) > 10:
                print(f"   ... and {len(url_counts) - 10} more unique URLs")
        
        # Save detailed results
        results = {
            'fixed_links': self.fixed_links,
            'unfixable_links': self.unfixable_links,
            'summary': {
                'total_files': total_files,
                'files_with_fixes': processed_files,
                'links_fixed': len(self.fixed_links),
                'links_unfixable': len(self.unfixable_links)
            }
        }
        
        with open('link_fixing_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: link_fixing_results.json")
        
        if len(self.fixed_links) > 0:
            print(f"\n🎉 SUCCESS: Fixed {len(self.fixed_links)} broken links!")
        else:
            print(f"\n⚠️  No links were automatically fixable.")

if __name__ == "__main__":
    fixer = TargetedLinkFixer()
    fixer.run()