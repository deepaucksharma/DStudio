#!/usr/bin/env python3
"""
Extract all Mermaid diagrams from pattern library markdown files.
Generates a manifest for batch rendering and tracks diagram metadata.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class MermaidExtractor:
    def __init__(self, base_path: str = "docs/pattern-library"):
        self.base_path = Path(base_path)
        self.diagrams = []
        self.stats = defaultdict(int)
        
    def extract_diagrams(self) -> List[Dict]:
        """Extract all Mermaid diagrams from markdown files."""
        for md_file in self.base_path.rglob("*.md"):
            if "visual-assets" in str(md_file):
                continue  # Skip already processed assets
                
            self._process_file(md_file)
            
        return self.diagrams
    
    def _process_file(self, file_path: Path) -> None:
        """Process a single markdown file for Mermaid diagrams."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Find all mermaid code blocks
            mermaid_pattern = r'```mermaid\n(.*?)\n```'
            matches = re.findall(mermaid_pattern, content, re.DOTALL)
            
            for idx, diagram_content in enumerate(matches):
                diagram_info = self._analyze_diagram(diagram_content, file_path, idx)
                self.diagrams.append(diagram_info)
                self.stats[diagram_info['type']] += 1
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def _analyze_diagram(self, content: str, file_path: Path, index: int) -> Dict:
        """Analyze a single diagram and extract metadata."""
        # Determine diagram type
        diagram_type = self._get_diagram_type(content)
        
        # Generate unique ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        relative_path = file_path.relative_to(self.base_path)
        diagram_id = f"{relative_path.stem}-{index}-{content_hash}"
        
        # Count nodes/complexity
        node_count = len(re.findall(r'\b\w+\[', content))
        line_count = len(content.split('\n'))
        
        return {
            'id': diagram_id,
            'file': str(relative_path),
            'index': index,
            'type': diagram_type,
            'content': content,
            'line_count': line_count,
            'node_count': node_count,
            'complexity': self._calculate_complexity(node_count, line_count),
            'category': relative_path.parts[0] if relative_path.parts else 'root'
        }
    
    def _get_diagram_type(self, content: str) -> str:
        """Determine the type of Mermaid diagram."""
        first_line = content.strip().split('\n')[0].lower()
        
        if 'graph' in first_line:
            return 'graph'
        elif 'sequencediagram' in first_line:
            return 'sequence'
        elif 'statediagram' in first_line:
            return 'state'
        elif 'flowchart' in first_line:
            return 'flowchart'
        elif 'gantt' in first_line:
            return 'gantt'
        elif 'mindmap' in first_line:
            return 'mindmap'
        else:
            return 'unknown'
    
    def _calculate_complexity(self, nodes: int, lines: int) -> str:
        """Calculate diagram complexity level."""
        if nodes > 50 or lines > 100:
            return 'high'
        elif nodes > 20 or lines > 50:
            return 'medium'
        else:
            return 'low'
    
    def generate_manifest(self, output_path: str = "diagram_manifest.json") -> None:
        """Generate a manifest file for batch processing."""
        manifest = {
            'total_diagrams': len(self.diagrams),
            'statistics': dict(self.stats),
            'diagrams': self.diagrams
        }
        
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Extracted {len(self.diagrams)} diagrams")
        print(f"📊 Types: {dict(self.stats)}")
        print(f"📁 Manifest saved to: {output_path}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of extracted diagrams."""
        report = ["# Mermaid Diagram Extraction Report\n"]
        report.append(f"**Total Diagrams**: {len(self.diagrams)}\n")
        
        # Type distribution
        report.append("## Diagram Type Distribution\n")
        for diagram_type, count in sorted(self.stats.items()):
            report.append(f"- **{diagram_type}**: {count} diagrams")
        
        # Complexity distribution
        complexity_stats = defaultdict(int)
        for diagram in self.diagrams:
            complexity_stats[diagram['complexity']] += 1
        
        report.append("\n## Complexity Distribution\n")
        for level, count in sorted(complexity_stats.items()):
            report.append(f"- **{level}**: {count} diagrams")
        
        # Category distribution
        category_stats = defaultdict(int)
        for diagram in self.diagrams:
            category_stats[diagram['category']] += 1
        
        report.append("\n## Category Distribution\n")
        for category, count in sorted(category_stats.items()):
            report.append(f"- **{category}**: {count} diagrams")
        
        # High complexity diagrams
        high_complexity = [d for d in self.diagrams if d['complexity'] == 'high']
        if high_complexity:
            report.append("\n## High Complexity Diagrams (Top 10)\n")
            for diagram in sorted(high_complexity, key=lambda x: x['node_count'], reverse=True)[:10]:
                report.append(f"- {diagram['file']} (index {diagram['index']}): {diagram['node_count']} nodes")
        
        return '\n'.join(report)


def main():
    """Main execution function."""
    extractor = MermaidExtractor()
    
    print("🔍 Scanning for Mermaid diagrams...")
    diagrams = extractor.extract_diagrams()
    
    print("📝 Generating manifest...")
    extractor.generate_manifest()
    
    print("📊 Generating report...")
    report = extractor.generate_summary_report()
    
    with open("diagram_extraction_report.md", "w") as f:
        f.write(report)
    
    print(f"✅ Report saved to: diagram_extraction_report.md")


if __name__ == "__main__":
    main()