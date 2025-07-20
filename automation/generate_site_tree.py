#!/usr/bin/env python3
"""
Generate a detailed tree of the entire MkDocs site structure including:
- Navigation hierarchy
- All content files
- Topics and headings
- Metadata from frontmatter
"""

import yaml
import os
import re
from pathlib import Path
import json
from typing import Dict, List, Any, Optional

class SiteTreeGenerator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.mkdocs_config = self._load_mkdocs_config()
        self.site_tree = {
            "title": self.mkdocs_config.get("site_name", "Site"),
            "navigation": [],
            "all_files": {},
            "topics": {},
            "statistics": {}
        }
        
    def _load_mkdocs_config(self) -> dict:
        """Load mkdocs.yml configuration"""
        config_path = self.base_dir / "mkdocs.yml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _extract_frontmatter(self, file_path: Path) -> Optional[dict]:
        """Extract YAML frontmatter from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if content.startswith('---'):
                # Find the closing ---
                match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    return yaml.safe_load(match.group(1))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        return None
    
    def _extract_headings(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract all headings from markdown file"""
        headings = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Remove frontmatter
            content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            
            # Find all headings
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            for match in re.finditer(heading_pattern, content, re.MULTILINE):
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({
                    "level": level,
                    "title": title,
                    "slug": self._slugify(title)
                })
        except Exception as e:
            print(f"Error extracting headings from {file_path}: {e}")
        return headings
    
    def _slugify(self, text: str) -> str:
        """Convert heading to URL slug"""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces with hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _process_nav_item(self, item: Any, parent_path: str = "") -> Dict[str, Any]:
        """Process a navigation item from mkdocs.yml"""
        if isinstance(item, dict):
            # Single key-value pair
            title = list(item.keys())[0]
            value = item[title]
            
            if isinstance(value, str):
                # It's a file reference
                file_path = self.docs_dir / value
                return {
                    "type": "file",
                    "title": title,
                    "path": value,
                    "full_path": str(file_path),
                    "metadata": self._extract_frontmatter(file_path),
                    "headings": self._extract_headings(file_path) if file_path.exists() else []
                }
            elif isinstance(value, list):
                # It's a section with children
                return {
                    "type": "section",
                    "title": title,
                    "children": [self._process_nav_item(child, f"{parent_path}/{title}") for child in value]
                }
        elif isinstance(item, str):
            # Direct file reference
            file_path = self.docs_dir / item
            return {
                "type": "file",
                "title": Path(item).stem.replace('-', ' ').title(),
                "path": item,
                "full_path": str(file_path),
                "metadata": self._extract_frontmatter(file_path),
                "headings": self._extract_headings(file_path) if file_path.exists() else []
            }
        
        return {"type": "unknown", "item": str(item)}
    
    def _scan_all_files(self) -> Dict[str, Any]:
        """Scan all markdown files in docs directory"""
        all_files = {}
        for md_file in self.docs_dir.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_dir)
            all_files[str(relative_path)] = {
                "path": str(relative_path),
                "size": md_file.stat().st_size,
                "metadata": self._extract_frontmatter(md_file),
                "headings": self._extract_headings(md_file),
                "line_count": sum(1 for _ in open(md_file, 'r', encoding='utf-8'))
            }
        return all_files
    
    def _extract_topics(self) -> Dict[str, List[str]]:
        """Extract and categorize all topics from the documentation"""
        topics = {
            "axioms": [],
            "pillars": [],
            "patterns": [],
            "case_studies": [],
            "tools": [],
            "human_factors": [],
            "quantitative": [],
            "other": []
        }
        
        for file_path, file_info in self.site_tree["all_files"].items():
            category = self._categorize_file(file_path)
            topics[category].append({
                "file": file_path,
                "title": file_info.get("metadata", {}).get("title", Path(file_path).stem),
                "headings": [h["title"] for h in file_info.get("headings", []) if h["level"] <= 3]
            })
        
        return topics
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize a file based on its path"""
        if "axioms" in file_path or "part1-axioms" in file_path:
            return "axioms"
        elif "pillars" in file_path or "part2-pillars" in file_path:
            return "pillars"
        elif "patterns" in file_path:
            return "patterns"
        elif "case-studies" in file_path:
            return "case_studies"
        elif "tools" in file_path:
            return "tools"
        elif "human-factors" in file_path:
            return "human_factors"
        elif "quantitative" in file_path:
            return "quantitative"
        else:
            return "other"
    
    def generate_tree(self) -> Dict[str, Any]:
        """Generate the complete site tree"""
        # Process navigation from mkdocs.yml
        nav_config = self.mkdocs_config.get("nav", [])
        self.site_tree["navigation"] = [self._process_nav_item(item) for item in nav_config]
        
        # Scan all files
        self.site_tree["all_files"] = self._scan_all_files()
        
        # Extract topics
        self.site_tree["topics"] = self._extract_topics()
        
        # Calculate statistics
        self.site_tree["statistics"] = {
            "total_files": len(self.site_tree["all_files"]),
            "total_lines": sum(f["line_count"] for f in self.site_tree["all_files"].values()),
            "total_size_bytes": sum(f["size"] for f in self.site_tree["all_files"].values()),
            "files_with_frontmatter": sum(1 for f in self.site_tree["all_files"].values() if f["metadata"]),
            "category_counts": {cat: len(files) for cat, files in self.site_tree["topics"].items()},
            "largest_files": sorted(
                [(path, info["line_count"]) for path, info in self.site_tree["all_files"].items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return self.site_tree
    
    def print_tree(self, item: Any = None, indent: int = 0):
        """Print navigation tree in a readable format"""
        if item is None:
            print(f"📚 {self.site_tree['title']}")
            print("=" * 50)
            for nav_item in self.site_tree["navigation"]:
                self.print_tree(nav_item, 0)
            return
        
        prefix = "  " * indent
        if isinstance(item, dict):
            if item.get("type") == "section":
                print(f"{prefix}📁 {item['title']}")
                for child in item.get("children", []):
                    self.print_tree(child, indent + 1)
            elif item.get("type") == "file":
                print(f"{prefix}📄 {item['title']} ({item['path']})")
                if item.get("headings"):
                    for heading in item["headings"][:3]:  # Show first 3 headings
                        h_prefix = "  " * (indent + 1) + "  " * (heading["level"] - 1)
                        print(f"{h_prefix}→ {heading['title']}")
    
    def save_json(self, output_path: str = "site_tree.json"):
        """Save the tree as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.site_tree, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved detailed site tree to {output_path}")
    
    def generate_markdown_report(self, output_path: str = "site_structure_report.md"):
        """Generate a markdown report of the site structure"""
        report = []
        report.append(f"# {self.site_tree['title']} - Site Structure Report\n")
        report.append(f"Generated from mkdocs.yml configuration\n")
        
        # Statistics
        stats = self.site_tree["statistics"]
        report.append("## 📊 Statistics\n")
        report.append(f"- **Total Files**: {stats['total_files']}")
        report.append(f"- **Total Lines**: {stats['total_lines']:,}")
        report.append(f"- **Total Size**: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
        report.append(f"- **Files with Metadata**: {stats['files_with_frontmatter']}\n")
        
        # Category breakdown
        report.append("### Files by Category\n")
        for category, count in stats["category_counts"].items():
            report.append(f"- **{category.replace('_', ' ').title()}**: {count} files")
        report.append("")
        
        # Largest files
        report.append("### Largest Files\n")
        for file_path, line_count in stats["largest_files"]:
            report.append(f"- `{file_path}`: {line_count:,} lines")
        report.append("")
        
        # Navigation structure
        report.append("## 🧭 Navigation Structure\n")
        self._add_nav_to_report(self.site_tree["navigation"], report)
        
        # Topics by category
        report.append("\n## 📚 Topics by Category\n")
        for category, files in self.site_tree["topics"].items():
            if files:
                report.append(f"\n### {category.replace('_', ' ').title()}\n")
                for file_info in files:
                    report.append(f"- **{file_info['title']}** (`{file_info['file']}`)")
                    if file_info["headings"]:
                        for heading in file_info["headings"][:5]:
                            report.append(f"  - {heading}")
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        print(f"✅ Saved markdown report to {output_path}")
    
    def _add_nav_to_report(self, nav_items: List[Dict], report: List[str], indent: int = 0):
        """Add navigation structure to markdown report"""
        for item in nav_items:
            prefix = "  " * indent
            if item.get("type") == "section":
                report.append(f"{prefix}- **{item['title']}**")
                self._add_nav_to_report(item.get("children", []), report, indent + 1)
            elif item.get("type") == "file":
                metadata = item.get("metadata", {})
                description = metadata.get("description", "")
                report.append(f"{prefix}- {item['title']} - {description}" if description else f"{prefix}- {item['title']}")


def main():
    """Generate comprehensive site tree"""
    generator = SiteTreeGenerator()
    
    print("🔍 Analyzing MkDocs site structure...")
    site_tree = generator.generate_tree()
    
    print("\n📋 Navigation Tree:")
    print("-" * 50)
    generator.print_tree()
    
    print("\n📊 Site Statistics:")
    print("-" * 50)
    stats = site_tree["statistics"]
    print(f"Total files: {stats['total_files']}")
    print(f"Total lines: {stats['total_lines']:,}")
    print(f"Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
    
    # Save outputs
    generator.save_json("site_tree.json")
    generator.generate_markdown_report("site_structure_report.md")
    
    print("\n✨ Analysis complete! Check site_tree.json and site_structure_report.md for details.")


if __name__ == "__main__":
    main()