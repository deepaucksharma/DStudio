#!/usr/bin/env python3
"""
Generate an ultra-detailed tree of the entire documentation site
Combines multiple approaches to extract maximum information
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

class UltraDetailedTreeGenerator:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.site_dir = self.base_dir / "site"
        
        self.tree = {
            "metadata": {
                "site_name": "The Compendium of Distributed Systems",
                "total_files": 0,
                "total_sections": 0,
                "total_topics": 0
            },
            "navigation_hierarchy": {},
            "content_map": {},
            "topic_index": defaultdict(list),
            "cross_references": defaultdict(list),
            "detailed_structure": {}
        }
    
    def extract_all_content_details(self, file_path):
        """Extract comprehensive details from a markdown file"""
        details = {
            "path": str(file_path),
            "title": None,
            "description": None,
            "frontmatter": {},
            "headings": [],
            "topics": [],
            "links": [],
            "code_blocks": [],
            "key_concepts": [],
            "statistics": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Extract frontmatter
            if content.startswith('---'):
                end_idx = content.find('\n---\n', 4)
                if end_idx > 0:
                    fm_content = content[4:end_idx]
                    for line in fm_content.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            details["frontmatter"][key] = value
                            
                            if key == "title":
                                details["title"] = value
                            elif key == "description":
                                details["description"] = value
            
            # If no title in frontmatter, use first H1
            if not details["title"]:
                for line in lines:
                    if line.startswith('# ') and not line.startswith('##'):
                        details["title"] = line[2:].strip()
                        break
            
            # Extract all headings with hierarchy
            heading_stack = []
            for i, line in enumerate(lines):
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if heading_match:
                    level = len(heading_match.group(1))
                    title = heading_match.group(2).strip()
                    
                    heading_info = {
                        "level": level,
                        "title": title,
                        "line": i + 1,
                        "id": self._slugify(title),
                        "children": []
                    }
                    
                    # Build hierarchy
                    while heading_stack and heading_stack[-1]["level"] >= level:
                        heading_stack.pop()
                    
                    if heading_stack:
                        heading_stack[-1]["children"].append(heading_info)
                    else:
                        details["headings"].append(heading_info)
                    
                    heading_stack.append(heading_info)
            
            # Extract topics and concepts
            topics_found = set()
            
            # Common distributed systems topics
            topic_patterns = {
                "latency": r'\b(latency|delay|response time|RTT)\b',
                "capacity": r'\b(capacity|throughput|bandwidth|scale)\b',
                "failure": r'\b(failure|fault|resilience|recovery)\b',
                "consistency": r'\b(consistency|consensus|CAP|ACID)\b',
                "concurrency": r'\b(concurrency|parallel|race condition|lock)\b',
                "coordination": r'\b(coordination|synchronization|distributed)\b',
                "replication": r'\b(replication|replica|backup|redundancy)\b',
                "partitioning": r'\b(partition|shard|split|segment)\b',
                "caching": r'\b(cache|caching|TTL|eviction)\b',
                "messaging": r'\b(message|queue|publish|subscribe|event)\b'
            }
            
            content_lower = content.lower()
            for topic, pattern in topic_patterns.items():
                if re.search(pattern, content_lower, re.IGNORECASE):
                    topics_found.add(topic)
            
            details["topics"] = list(topics_found)
            
            # Extract internal links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_text = match.group(1)
                link_url = match.group(2)
                
                if not link_url.startswith(('http://', 'https://', '#')):
                    details["links"].append({
                        "text": link_text,
                        "url": link_url,
                        "type": "internal"
                    })
            
            # Extract code blocks
            code_pattern = r'```(\w*)\n(.*?)```'
            for match in re.finditer(code_pattern, content, re.DOTALL):
                language = match.group(1) or 'text'
                details["code_blocks"].append({
                    "language": language,
                    "lines": len(match.group(2).split('\n'))
                })
            
            # Statistics
            details["statistics"] = {
                "total_lines": len(lines),
                "total_words": len(content.split()),
                "total_characters": len(content),
                "heading_count": len(heading_stack),
                "link_count": len(details["links"]),
                "code_block_count": len(details["code_blocks"])
            }
            
        except Exception as e:
            details["error"] = str(e)
        
        return details
    
    def _slugify(self, text):
        """Convert text to URL-friendly slug"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def parse_sitemap(self):
        """Parse sitemap.xml to get all URLs"""
        sitemap_path = self.site_dir / "sitemap.xml"
        urls = []
        
        if sitemap_path.exists():
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            
            # Handle namespace
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            for url in root.findall('.//sm:url', ns):
                loc = url.find('sm:loc', ns)
                if loc is not None:
                    urls.append(loc.text)
        
        return urls
    
    def build_navigation_from_mkdocs(self):
        """Parse mkdocs.yml to build navigation structure"""
        nav_structure = []
        
        with open(self.base_dir / "mkdocs.yml", 'r') as f:
            lines = f.readlines()
        
        # Find nav section
        nav_start = None
        for i, line in enumerate(lines):
            if line.strip() == "nav:":
                nav_start = i + 1
                break
        
        if nav_start:
            current_depth = 0
            stack = [nav_structure]
            
            for line in lines[nav_start:]:
                if line and not line[0].isspace():
                    break
                
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Calculate depth
                depth = (len(line) - len(line.lstrip())) // 2
                
                # Parse item
                if stripped.startswith('- '):
                    item_text = stripped[2:].strip()
                    
                    # Adjust stack to current depth
                    while len(stack) > depth + 1:
                        stack.pop()
                    
                    if ':' in item_text and not item_text.endswith(':'):
                        # It's a page link
                        parts = item_text.split(':', 1)
                        title = parts[0].strip().strip('"')
                        path = parts[1].strip()
                        
                        item = {
                            "type": "page",
                            "title": title,
                            "path": path,
                            "depth": depth
                        }
                        
                        stack[-1].append(item)
                    else:
                        # It's a section
                        title = item_text.rstrip(':').strip('"')
                        item = {
                            "type": "section",
                            "title": title,
                            "depth": depth,
                            "children": []
                        }
                        
                        stack[-1].append(item)
                        stack.append(item["children"])
        
        return nav_structure
    
    def analyze_directory_structure(self, path=None, depth=0):
        """Recursively analyze directory structure with content"""
        if path is None:
            path = self.docs_dir
        
        structure = {}
        
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.') or item.startswith('_'):
                    continue
                
                item_path = Path(path) / item
                
                if item_path.is_dir():
                    structure[item] = {
                        "type": "directory",
                        "path": str(item_path.relative_to(self.docs_dir)),
                        "children": self.analyze_directory_structure(item_path, depth + 1)
                    }
                elif item.endswith('.md'):
                    details = self.extract_all_content_details(item_path)
                    structure[item] = {
                        "type": "file",
                        "path": str(item_path.relative_to(self.docs_dir)),
                        "details": details
                    }
                    
                    # Update indices
                    self.tree["content_map"][str(item_path.relative_to(self.docs_dir))] = details
                    
                    # Update topic index
                    for topic in details["topics"]:
                        self.tree["topic_index"][topic].append({
                            "file": str(item_path.relative_to(self.docs_dir)),
                            "title": details["title"]
                        })
                    
                    # Track cross-references
                    for link in details["links"]:
                        self.tree["cross_references"][link["url"]].append({
                            "from": str(item_path.relative_to(self.docs_dir)),
                            "text": link["text"]
                        })
                    
                    self.tree["metadata"]["total_files"] += 1
        
        except PermissionError:
            pass
        
        return structure
    
    def generate_visual_tree(self, structure, prefix="", is_last=True):
        """Generate a visual tree representation"""
        lines = []
        items = list(structure.items())
        
        for i, (name, info) in enumerate(items):
            is_last_item = i == len(items) - 1
            
            # Connector
            connector = "└── " if is_last_item else "├── "
            
            # Icon based on type
            if info["type"] == "directory":
                icon = "📁"
                item_count = len(info.get("children", {}))
                suffix = f" ({item_count} items)"
            else:
                icon = "📄"
                details = info.get("details", {})
                title = details.get("title", "")
                suffix = f" - {title}" if title else ""
            
            lines.append(f"{prefix}{connector}{icon} {name}{suffix}")
            
            # Recurse for directories
            if info["type"] == "directory" and info.get("children"):
                extension = "    " if is_last_item else "│   "
                child_lines = self.generate_visual_tree(
                    info["children"], 
                    prefix + extension,
                    is_last_item
                )
                lines.extend(child_lines)
        
        return lines
    
    def generate_topic_summary(self):
        """Generate a summary of topics across the documentation"""
        summary = []
        
        summary.append("\n📚 TOPIC DISTRIBUTION:")
        summary.append("=" * 50)
        
        # Sort topics by frequency
        topic_freq = [(topic, len(files)) for topic, files in self.tree["topic_index"].items()]
        topic_freq.sort(key=lambda x: x[1], reverse=True)
        
        for topic, count in topic_freq:
            summary.append(f"\n🔖 {topic.upper()} ({count} files):")
            for file_info in self.tree["topic_index"][topic][:5]:  # Show first 5
                summary.append(f"   - {file_info['title']} ({file_info['file']})")
            
            if count > 5:
                summary.append(f"   ... and {count - 5} more")
        
        return summary
    
    def generate_navigation_outline(self, nav_items, depth=0):
        """Generate navigation outline from parsed structure"""
        lines = []
        
        for item in nav_items:
            indent = "  " * depth
            
            if item["type"] == "section":
                lines.append(f"{indent}📂 {item['title']}")
                if item.get("children"):
                    lines.extend(self.generate_navigation_outline(item["children"], depth + 1))
            else:
                lines.append(f"{indent}📄 {item['title']} → {item['path']}")
        
        return lines
    
    def generate_comprehensive_report(self):
        """Generate the ultra-detailed report"""
        report = []
        
        # Header
        report.append("=" * 100)
        report.append("ULTRA-DETAILED DOCUMENTATION TREE")
        report.append("=" * 100)
        report.append("")
        
        # Metadata
        meta = self.tree["metadata"]
        report.append("📊 OVERVIEW:")
        report.append(f"  Site: {meta['site_name']}")
        report.append(f"  Total Files: {meta['total_files']}")
        report.append(f"  Total Topics: {len(self.tree['topic_index'])}")
        report.append(f"  Cross-references: {len(self.tree['cross_references'])}")
        report.append("")
        
        # Navigation structure from mkdocs.yml
        report.append("\n🧭 NAVIGATION STRUCTURE (mkdocs.yml):")
        report.append("=" * 50)
        nav_outline = self.generate_navigation_outline(self.tree["navigation_hierarchy"])
        report.extend(nav_outline)
        
        # File system structure
        report.append("\n\n📁 FILE SYSTEM STRUCTURE:")
        report.append("=" * 50)
        visual_tree = self.generate_visual_tree(self.tree["detailed_structure"])
        report.extend(visual_tree)
        
        # Topic summary
        topic_summary = self.generate_topic_summary()
        report.extend(topic_summary)
        
        # Cross-reference analysis
        report.append("\n\n🔗 CROSS-REFERENCE ANALYSIS:")
        report.append("=" * 50)
        
        # Most referenced files
        ref_count = defaultdict(int)
        for target, refs in self.tree["cross_references"].items():
            ref_count[target] = len(refs)
        
        most_referenced = sorted(ref_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report.append("\nMost Referenced Files:")
        for target, count in most_referenced:
            report.append(f"  - {target}: {count} references")
        
        return "\n".join(report)
    
    def save_results(self):
        """Save all results in multiple formats"""
        # Save JSON with full details
        with open("ultra_detailed_tree.json", "w") as f:
            json.dump(self.tree, f, indent=2, default=str)
        
        # Save text report
        report = self.generate_comprehensive_report()
        with open("ultra_detailed_report.txt", "w") as f:
            f.write(report)
        
        # Save topic index
        with open("topic_index.json", "w") as f:
            json.dump(dict(self.tree["topic_index"]), f, indent=2)
        
        # Save cross-reference map
        with open("cross_references.json", "w") as f:
            json.dump(dict(self.tree["cross_references"]), f, indent=2)
        
        print("\n✅ Generated files:")
        print("  - ultra_detailed_tree.json (complete data)")
        print("  - ultra_detailed_report.txt (human-readable)")
        print("  - topic_index.json (topics across files)")
        print("  - cross_references.json (link relationships)")


def main():
    print("🚀 Generating ultra-detailed documentation tree...")
    
    generator = UltraDetailedTreeGenerator()
    
    # Parse navigation from mkdocs.yml
    print("📋 Parsing navigation structure...")
    generator.tree["navigation_hierarchy"] = generator.build_navigation_from_mkdocs()
    
    # Analyze directory structure with content
    print("📁 Analyzing file system and content...")
    generator.tree["detailed_structure"] = generator.analyze_directory_structure()
    
    # Parse sitemap if available
    print("🗺️  Parsing sitemap...")
    urls = generator.parse_sitemap()
    generator.tree["sitemap_urls"] = urls
    
    # Generate and save results
    print("💾 Saving results...")
    generator.save_results()
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print(f"Total files analyzed: {generator.tree['metadata']['total_files']}")
    print(f"Total topics found: {len(generator.tree['topic_index'])}")
    print(f"Total cross-references: {len(generator.tree['cross_references'])}")
    
    print("\n✨ Analysis complete!")


if __name__ == "__main__":
    main()