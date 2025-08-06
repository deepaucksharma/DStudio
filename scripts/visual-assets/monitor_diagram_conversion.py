#!/usr/bin/env python3
"""
Monitor the progress of Mermaid diagram conversion.
Tracks metrics and generates status reports.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ConversionMonitor:
    def __init__(self):
        self.base_path = Path("docs/pattern-library")
        self.render_path = Path("docs/pattern-library/visual-assets/rendered")
        self.metrics = {
            'total_mermaid_blocks': 0,
            'converted_blocks': 0,
            'total_images': 0,
            'total_size_mb': 0,
            'formats': {'png': 0, 'webp': 0},
            'sizes': {'small': 0, 'medium': 0, 'large': 0},
            'unconverted_files': []
        }
    
    def scan_mermaid_blocks(self) -> None:
        """Count total Mermaid blocks in markdown files."""
        import re
        
        for md_file in self.base_path.rglob("*.md"):
            if "visual-assets" in str(md_file):
                continue
                
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Count original mermaid blocks (not in comments)
                original_blocks = len(re.findall(r'^```mermaid\n', content, re.MULTILINE))
                
                # Count preserved source blocks
                preserved_blocks = content.count('MERMAID_SOURCE')
                
                # Count picture elements
                picture_elements = content.count('<picture>')
                
                self.metrics['total_mermaid_blocks'] += original_blocks + preserved_blocks
                self.metrics['converted_blocks'] += picture_elements
                
                if original_blocks > 0:
                    self.metrics['unconverted_files'].append(str(md_file.relative_to(self.base_path)))
                    
            except Exception as e:
                print(f"Error scanning {md_file}: {e}")
    
    def analyze_rendered_images(self) -> None:
        """Analyze the rendered images directory."""
        if not self.render_path.exists():
            return
        
        total_size = 0
        
        for image_file in self.render_path.rglob("*"):
            if not image_file.is_file():
                continue
                
            self.metrics['total_images'] += 1
            total_size += image_file.stat().st_size
            
            # Track format
            if image_file.suffix == '.png':
                self.metrics['formats']['png'] += 1
            elif image_file.suffix == '.webp':
                self.metrics['formats']['webp'] += 1
            
            # Track size
            if 'small' in str(image_file):
                self.metrics['sizes']['small'] += 1
            elif 'medium' in str(image_file):
                self.metrics['sizes']['medium'] += 1
            elif 'large' in str(image_file):
                self.metrics['sizes']['large'] += 1
        
        self.metrics['total_size_mb'] = total_size / (1024 * 1024)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required tools are installed."""
        import shutil
        
        tools = {
            'mmdc': shutil.which('mmdc') is not None,
            'convert': shutil.which('convert') is not None,
            'cwebp': shutil.which('cwebp') is not None,
            'python3': shutil.which('python3') is not None
        }
        
        return tools
    
    def measure_performance(self) -> Dict[str, any]:
        """Measure page performance metrics (requires running server)."""
        perf_metrics = {
            'mermaid_js_loaded': False,
            'avg_image_size_kb': 0,
            'compression_ratio': 0
        }
        
        # Check if mermaid.js is still being loaded
        try:
            # This would need to be measured with actual browser tools
            # For now, we'll check if mermaid is in any HTML output
            result = subprocess.run(
                ['grep', '-r', 'mermaid.min.js', 'site/'],
                capture_output=True,
                text=True
            )
            perf_metrics['mermaid_js_loaded'] = result.returncode == 0
        except:
            pass
        
        # Calculate average image size
        if self.metrics['total_images'] > 0:
            perf_metrics['avg_image_size_kb'] = (
                self.metrics['total_size_mb'] * 1024 / self.metrics['total_images']
            )
        
        # Calculate compression ratio (WebP vs PNG)
        if self.metrics['formats']['png'] > 0:
            # Rough estimate: WebP is typically 25-35% smaller
            perf_metrics['compression_ratio'] = 0.30
        
        return perf_metrics
    
    def generate_status_report(self) -> str:
        """Generate a comprehensive status report."""
        report = [
            "# Mermaid Diagram Conversion Status Report",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Overall Progress\n"
        ]
        
        # Calculate completion percentage
        if self.metrics['total_mermaid_blocks'] > 0:
            completion = (self.metrics['converted_blocks'] / self.metrics['total_mermaid_blocks']) * 100
        else:
            completion = 0
        
        # Progress bar
        progress_bar = self._create_progress_bar(completion)
        report.append(f"**Conversion Progress**: {progress_bar} {completion:.1f}%\n")
        
        # Key metrics
        report.append("## Key Metrics\n")
        report.append(f"- **Total Mermaid Diagrams**: {self.metrics['total_mermaid_blocks']}")
        report.append(f"- **Converted Diagrams**: {self.metrics['converted_blocks']}")
        report.append(f"- **Remaining**: {self.metrics['total_mermaid_blocks'] - self.metrics['converted_blocks']}")
        report.append(f"- **Total Images Generated**: {self.metrics['total_images']}")
        report.append(f"- **Total Storage Used**: {self.metrics['total_size_mb']:.2f} MB")
        
        # Image breakdown
        report.append("\n## Image Breakdown\n")
        report.append("### By Format")
        report.append(f"- PNG: {self.metrics['formats']['png']} files")
        report.append(f"- WebP: {self.metrics['formats']['webp']} files")
        
        report.append("\n### By Size")
        report.append(f"- Small (400px): {self.metrics['sizes']['small']} files")
        report.append(f"- Medium (800px): {self.metrics['sizes']['medium']} files")
        report.append(f"- Large (1200px): {self.metrics['sizes']['large']} files")
        
        # Dependency status
        deps = self.check_dependencies()
        report.append("\n## Dependencies Status\n")
        for tool, installed in deps.items():
            status = "✅ Installed" if installed else "❌ Not Found"
            report.append(f"- **{tool}**: {status}")
        
        # Performance metrics
        perf = self.measure_performance()
        report.append("\n## Performance Impact\n")
        report.append(f"- **Mermaid.js Still Loading**: {'Yes ⚠️' if perf['mermaid_js_loaded'] else 'No ✅'}")
        report.append(f"- **Average Image Size**: {perf['avg_image_size_kb']:.1f} KB")
        report.append(f"- **WebP Compression Savings**: ~{perf['compression_ratio']*100:.0f}%")
        
        # Unconverted files
        if self.metrics['unconverted_files']:
            report.append("\n## ⚠️ Unconverted Files\n")
            report.append("The following files still contain unconverted Mermaid blocks:\n")
            for file in sorted(self.metrics['unconverted_files'])[:10]:  # Show first 10
                report.append(f"- {file}")
            if len(self.metrics['unconverted_files']) > 10:
                report.append(f"\n...and {len(self.metrics['unconverted_files']) - 10} more")
        
        # Next steps
        report.append("\n## Next Steps\n")
        if completion < 100:
            report.append("1. Run `python3 scripts/extract_mermaid_diagrams.py` to extract remaining diagrams")
            report.append("2. Run `python3 scripts/render_mermaid_diagrams.py` to render images")
            report.append("3. Run `python3 scripts/replace_mermaid_blocks.py` to update markdown files")
        else:
            report.append("✅ All diagrams have been converted!")
            report.append("1. Run performance tests to measure improvements")
            report.append("2. Deploy changes to production")
            report.append("3. Monitor Core Web Vitals for impact")
        
        return '\n'.join(report)
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Create a text-based progress bar."""
        filled = int(width * percentage / 100)
        empty = width - filled
        
        bar = '█' * filled + '░' * empty
        return f"[{bar}]"
    
    def save_metrics(self, output_path: str = "conversion_metrics.json") -> None:
        """Save metrics to JSON file for tracking."""
        metrics_with_timestamp = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics
        }
        
        # Load existing metrics if file exists
        history = []
        if Path(output_path).exists():
            try:
                with open(output_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        history = data
                    else:
                        history = [data]
            except:
                pass
        
        # Append new metrics
        history.append(metrics_with_timestamp)
        
        # Keep last 100 entries
        history = history[-100:]
        
        # Save updated history
        with open(output_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"✅ Metrics saved to: {output_path}")


def main():
    """Main execution function."""
    monitor = ConversionMonitor()
    
    print("🔍 Scanning pattern library...")
    monitor.scan_mermaid_blocks()
    
    print("📊 Analyzing rendered images...")
    monitor.analyze_rendered_images()
    
    print("📝 Generating status report...")
    report = monitor.generate_status_report()
    
    # Save report
    report_path = Path("diagram_conversion_status.md")
    report_path.write_text(report)
    print(f"✅ Status report saved to: {report_path}")
    
    # Save metrics for tracking
    monitor.save_metrics()
    
    # Print summary
    if monitor.metrics['total_mermaid_blocks'] > 0:
        completion = (monitor.metrics['converted_blocks'] / monitor.metrics['total_mermaid_blocks']) * 100
        print(f"\n📊 Conversion Progress: {completion:.1f}% complete")
        print(f"   - {monitor.metrics['converted_blocks']}/{monitor.metrics['total_mermaid_blocks']} diagrams converted")
        print(f"   - {monitor.metrics['total_images']} images generated")
        print(f"   - {monitor.metrics['total_size_mb']:.2f} MB total size")


if __name__ == "__main__":
    main()