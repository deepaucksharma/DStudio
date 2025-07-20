#!/usr/bin/env python3
"""
Analyze site structure using basic Python (no external dependencies)
Works directly with the mkdocs.yml file structure
"""

import os
import re
from pathlib import Path
import json

class SiteAnalyzer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.results = {
            "file_tree": {},
            "statistics": {},
            "patterns": {},
            "axioms": {},
            "pillars": {},
            "case_studies": {},
            "navigation_structure": []
        }
    
    def parse_mkdocs_yml(self):
        """Parse mkdocs.yml manually to extract navigation"""
        nav_items = []
        with open(self.base_dir / "mkdocs.yml", 'r') as f:
            lines = f.readlines()
        
        in_nav = False
        nav_lines = []
        
        for line in lines:
            if line.strip() == "nav:":
                in_nav = True
                continue
            elif in_nav and line and not line[0].isspace():
                break
            elif in_nav:
                nav_lines.append(line)
        
        # Parse navigation structure
        current_section = None
        for line in nav_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Count indentation
            indent = len(line) - len(line.lstrip())
            
            if stripped.startswith('- '):
                item = stripped[2:].strip()
                if ':' in item:
                    title, path = item.split(':', 1)
                    title = title.strip()
                    path = path.strip()
                    
                    if indent == 2:  # Top level
                        current_section = {"title": title, "items": []}
                        nav_items.append(current_section)
                    else:  # Sub item
                        if current_section:
                            current_section["items"].append({
                                "title": title,
                                "path": path
                            })
        
        return nav_items
    
    def scan_directory(self, path, prefix=""):
        """Recursively scan directory and build file tree"""
        tree = {}
        
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                    
                item_path = path / item
                relative_path = item_path.relative_to(self.docs_dir)
                
                if item_path.is_dir():
                    tree[item] = {
                        "type": "directory",
                        "path": str(relative_path),
                        "children": self.scan_directory(item_path, prefix + "  ")
                    }
                elif item.endswith('.md'):
                    file_info = self.analyze_markdown_file(item_path)
                    tree[item] = {
                        "type": "file",
                        "path": str(relative_path),
                        "info": file_info
                    }
        except PermissionError:
            pass
            
        return tree
    
    def analyze_markdown_file(self, file_path):
        """Extract information from a markdown file"""
        info = {
            "size": os.path.getsize(file_path),
            "lines": 0,
            "headings": [],
            "has_frontmatter": False,
            "frontmatter": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                info["lines"] = len(lines)
                
                # Check for frontmatter
                if content.startswith('---'):
                    end_marker = content.find('\n---\n', 4)
                    if end_marker > 0:
                        info["has_frontmatter"] = True
                        # Extract basic frontmatter info
                        fm_content = content[4:end_marker]
                        for line in fm_content.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                info["frontmatter"][key.strip()] = value.strip().strip('"\'')
                
                # Extract headings
                heading_pattern = r'^(#{1,6})\s+(.+)$'
                for line in lines:
                    match = re.match(heading_pattern, line)
                    if match:
                        level = len(match.group(1))
                        title = match.group(2).strip()
                        info["headings"].append({
                            "level": level,
                            "title": title
                        })
        except Exception as e:
            info["error"] = str(e)
            
        return info
    
    def categorize_files(self, tree, path=""):
        """Categorize files by their path patterns"""
        for name, item in tree.items():
            if item["type"] == "directory":
                self.categorize_files(item["children"], os.path.join(path, name))
            elif item["type"] == "file":
                full_path = os.path.join(path, name)
                
                # Categorize based on path
                if "patterns" in path:
                    self.results["patterns"][full_path] = item["info"]
                elif "axiom" in path:
                    self.results["axioms"][full_path] = item["info"]
                elif "pillar" in path:
                    self.results["pillars"][full_path] = item["info"]
                elif "case-studies" in path:
                    self.results["case_studies"][full_path] = item["info"]
    
    def calculate_statistics(self, tree):
        """Calculate statistics about the documentation"""
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_lines": 0,
            "total_size": 0,
            "files_with_frontmatter": 0,
            "largest_files": [],
            "files_by_category": {}
        }
        
        def traverse(node, path=""):
            for name, item in node.items():
                if item["type"] == "directory":
                    stats["total_directories"] += 1
                    traverse(item["children"], os.path.join(path, name))
                elif item["type"] == "file":
                    stats["total_files"] += 1
                    info = item["info"]
                    stats["total_lines"] += info["lines"]
                    stats["total_size"] += info["size"]
                    
                    if info["has_frontmatter"]:
                        stats["files_with_frontmatter"] += 1
                    
                    # Track largest files
                    stats["largest_files"].append({
                        "path": os.path.join(path, name),
                        "lines": info["lines"],
                        "size": info["size"]
                    })
        
        traverse(tree)
        
        # Sort largest files
        stats["largest_files"].sort(key=lambda x: x["lines"], reverse=True)
        stats["largest_files"] = stats["largest_files"][:20]  # Top 20
        
        return stats
    
    def generate_report(self):
        """Generate a text report of the analysis"""
        report = []
        report.append("=" * 80)
        report.append("DISTRIBUTED SYSTEMS DOCUMENTATION STRUCTURE ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Statistics
        stats = self.results["statistics"]
        report.append("STATISTICS:")
        report.append(f"  Total Files: {stats['total_files']}")
        report.append(f"  Total Directories: {stats['total_directories']}")
        report.append(f"  Total Lines: {stats['total_lines']:,}")
        report.append(f"  Total Size: {stats['total_size'] / 1024 / 1024:.2f} MB")
        report.append(f"  Files with Frontmatter: {stats['files_with_frontmatter']}")
        report.append("")
        
        # Navigation structure
        report.append("NAVIGATION STRUCTURE (from mkdocs.yml):")
        for section in self.results["navigation_structure"]:
            report.append(f"\n  📁 {section['title']}")
            for item in section.get("items", []):
                report.append(f"    📄 {item['title']} → {item['path']}")
        report.append("")
        
        # Largest files
        report.append("\nLARGEST FILES (by line count):")
        for i, file in enumerate(stats["largest_files"][:10], 1):
            report.append(f"  {i}. {file['path']} ({file['lines']:,} lines)")
        report.append("")
        
        # Category counts
        report.append("\nFILES BY CATEGORY:")
        report.append(f"  Patterns: {len(self.results['patterns'])}")
        report.append(f"  Axioms: {len(self.results['axioms'])}")
        report.append(f"  Pillars: {len(self.results['pillars'])}")
        report.append(f"  Case Studies: {len(self.results['case_studies'])}")
        
        return "\n".join(report)
    
    def print_tree(self, tree, prefix="", is_last=True):
        """Print directory tree in a visual format"""
        items = list(tree.items())
        for i, (name, item) in enumerate(items):
            is_last_item = i == len(items) - 1
            
            # Print current item
            connector = "└── " if is_last_item else "├── "
            print(prefix + connector + name)
            
            # If directory, recurse
            if item["type"] == "directory":
                extension = "    " if is_last_item else "│   "
                self.print_tree(item["children"], prefix + extension, is_last_item)
    
    def run(self):
        """Run the complete analysis"""
        print("🔍 Analyzing documentation structure...")
        
        # Parse navigation
        print("📋 Parsing mkdocs.yml navigation...")
        self.results["navigation_structure"] = self.parse_mkdocs_yml()
        
        # Scan file system
        print("📁 Scanning documentation files...")
        self.results["file_tree"] = self.scan_directory(self.docs_dir)
        
        # Categorize files
        print("🏷️  Categorizing files...")
        self.categorize_files(self.results["file_tree"])
        
        # Calculate statistics
        print("📊 Calculating statistics...")
        self.results["statistics"] = self.calculate_statistics(self.results["file_tree"])
        
        # Generate report
        print("\n" + "=" * 80)
        print("DOCUMENTATION TREE STRUCTURE:")
        print("=" * 80)
        self.print_tree(self.results["file_tree"])
        
        # Print summary report
        print("\n" + self.generate_report())
        
        # Save results
        with open("site_analysis.json", "w") as f:
            # Convert Path objects to strings for JSON serialization
            json.dump(self.results, f, indent=2, default=str)
        print("\n✅ Full analysis saved to site_analysis.json")
        
        # Save text report
        with open("site_analysis_report.txt", "w") as f:
            f.write(self.generate_report())
        print("✅ Report saved to site_analysis_report.txt")


if __name__ == "__main__":
    analyzer = SiteAnalyzer()
    analyzer.run()