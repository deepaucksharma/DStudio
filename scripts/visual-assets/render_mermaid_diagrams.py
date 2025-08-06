#!/usr/bin/env python3
"""
Render Mermaid diagrams to multiple image formats using Mermaid CLI.
Generates responsive images with multiple sizes and formats.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import shutil

class MermaidRenderer:
    def __init__(self, manifest_path: str = "diagram_manifest.json"):
        self.manifest = self._load_manifest(manifest_path)
        self.output_base = Path("docs/pattern-library/visual-assets/rendered")
        self.sizes = {
            'small': 400,
            'medium': 800,
            'large': 1200
        }
        self.formats = ['png', 'webp']
        self.failed_renders = []
        
    def _load_manifest(self, path: str) -> Dict:
        """Load the diagram manifest."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def setup_directories(self) -> None:
        """Create output directory structure."""
        categories = set(d['category'] for d in self.manifest['diagrams'])
        
        for category in categories:
            for size in self.sizes:
                dir_path = self.output_base / category / size
                dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created directory structure under {self.output_base}")
    
    def render_diagram(self, diagram: Dict) -> Dict[str, any]:
        """Render a single diagram to multiple formats and sizes."""
        results = {'id': diagram['id'], 'renders': []}
        
        # Create temporary mermaid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(diagram['content'])
            temp_mmd = f.name
        
        try:
            # First render to SVG at full size
            svg_path = self._render_svg(temp_mmd, diagram)
            
            if svg_path and svg_path.exists():
                # Convert SVG to multiple formats and sizes
                for size_name, width in self.sizes.items():
                    for format in self.formats:
                        output_path = self._convert_image(
                            svg_path, diagram, size_name, width, format
                        )
                        if output_path:
                            results['renders'].append({
                                'size': size_name,
                                'format': format,
                                'path': str(output_path.relative_to(self.output_base))
                            })
                
                # Clean up SVG
                svg_path.unlink()
            else:
                results['error'] = 'SVG rendering failed'
                self.failed_renders.append(diagram['id'])
                
        except Exception as e:
            results['error'] = str(e)
            self.failed_renders.append(diagram['id'])
        finally:
            # Clean up temp file
            Path(temp_mmd).unlink(missing_ok=True)
        
        return results
    
    def _render_svg(self, mmd_path: str, diagram: Dict) -> Path:
        """Render Mermaid to SVG using mermaid-cli."""
        output_path = Path(tempfile.gettempdir()) / f"{diagram['id']}.svg"
        
        cmd = [
            'mmdc',
            '-i', mmd_path,
            '-o', str(output_path),
            '-t', 'default',  # Can be customized
            '-b', 'transparent'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return output_path
            else:
                print(f"❌ Mermaid CLI error for {diagram['id']}: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout rendering {diagram['id']}")
            return None
        except FileNotFoundError:
            print("❌ mermaid-cli (mmdc) not found. Please install with: npm install -g @mermaid-js/mermaid-cli")
            raise
    
    def _convert_image(self, svg_path: Path, diagram: Dict, 
                      size_name: str, width: int, format: str) -> Path:
        """Convert SVG to specified format and size."""
        output_dir = self.output_base / diagram['category'] / size_name
        output_path = output_dir / f"{diagram['id']}.{format}"
        
        if format == 'png':
            cmd = [
                'convert',
                str(svg_path),
                '-resize', f'{width}x',
                '-background', 'transparent',
                str(output_path)
            ]
        elif format == 'webp':
            # First convert to PNG, then to WebP for better quality
            temp_png = Path(tempfile.gettempdir()) / f"{diagram['id']}_temp.png"
            
            # SVG to PNG
            subprocess.run([
                'convert',
                str(svg_path),
                '-resize', f'{width}x',
                '-background', 'transparent',
                str(temp_png)
            ], check=True)
            
            # PNG to WebP
            cmd = [
                'cwebp',
                '-q', '85',
                '-alpha_q', '100',
                str(temp_png),
                '-o', str(output_path)
            ]
            
            # Clean up temp PNG
            temp_png.unlink(missing_ok=True)
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Conversion error for {diagram['id']} to {format}: {e}")
            return None
        except FileNotFoundError:
            print(f"❌ ImageMagick (convert) or cwebp not found. Please install these tools.")
            raise
    
    def generate_picture_elements(self) -> Dict[str, str]:
        """Generate HTML picture elements for all rendered diagrams."""
        picture_elements = {}
        
        for diagram in self.manifest['diagrams']:
            picture_html = self._create_picture_element(diagram)
            if picture_html:
                picture_elements[diagram['id']] = picture_html
        
        return picture_elements
    
    def _create_picture_element(self, diagram: Dict) -> str:
        """Create responsive picture element HTML."""
        base_path = f"/pattern-library/visual-assets/rendered/{diagram['category']}"
        
        html = ['<picture>']
        
        # Large WebP
        html.append(f'  <source media="(min-width: 1200px)" '
                   f'srcset="{base_path}/large/{diagram["id"]}.webp" '
                   f'type="image/webp">')
        
        # Large PNG fallback
        html.append(f'  <source media="(min-width: 1200px)" '
                   f'srcset="{base_path}/large/{diagram["id"]}.png" '
                   f'type="image/png">')
        
        # Medium WebP
        html.append(f'  <source media="(min-width: 768px)" '
                   f'srcset="{base_path}/medium/{diagram["id"]}.webp" '
                   f'type="image/webp">')
        
        # Medium PNG fallback
        html.append(f'  <source media="(min-width: 768px)" '
                   f'srcset="{base_path}/medium/{diagram["id"]}.png" '
                   f'type="image/png">')
        
        # Small WebP
        html.append(f'  <source srcset="{base_path}/small/{diagram["id"]}.webp" '
                   f'type="image/webp">')
        
        # Default img tag with small PNG
        alt_text = self._generate_alt_text(diagram)
        html.append(f'  <img src="{base_path}/small/{diagram["id"]}.png" '
                   f'alt="{alt_text}" loading="lazy">')
        
        html.append('</picture>')
        
        return '\n'.join(html)
    
    def _generate_alt_text(self, diagram: Dict) -> str:
        """Generate descriptive alt text for diagram."""
        type_descriptions = {
            'graph': 'Architecture diagram',
            'sequence': 'Sequence diagram',
            'state': 'State machine diagram',
            'flowchart': 'Process flow diagram',
            'gantt': 'Timeline diagram',
            'mindmap': 'Mind map diagram'
        }
        
        base_desc = type_descriptions.get(diagram['type'], 'Diagram')
        pattern_name = Path(diagram['file']).stem.replace('-', ' ').title()
        
        return f"{base_desc} for {pattern_name} pattern"
    
    def render_batch(self, max_workers: int = 4) -> None:
        """Render all diagrams in parallel."""
        total = len(self.manifest['diagrams'])
        completed = 0
        
        print(f"🚀 Starting batch rendering of {total} diagrams...")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_diagram = {
                executor.submit(self.render_diagram, diagram): diagram 
                for diagram in self.manifest['diagrams']
            }
            
            for future in as_completed(future_to_diagram):
                diagram = future_to_diagram[future]
                try:
                    result = future.result()
                    completed += 1
                    
                    if 'error' in result:
                        print(f"❌ Failed: {diagram['id']} - {result['error']}")
                    else:
                        renders = len(result['renders'])
                        print(f"✅ Rendered: {diagram['id']} ({renders} files) - {completed}/{total}")
                        
                except Exception as e:
                    print(f"❌ Exception rendering {diagram['id']}: {e}")
                    completed += 1
        
        print(f"\n📊 Rendering complete: {completed - len(self.failed_renders)}/{total} successful")
        if self.failed_renders:
            print(f"❌ Failed renders: {len(self.failed_renders)}")
    
    def generate_report(self) -> str:
        """Generate a rendering report."""
        report = ["# Mermaid Diagram Rendering Report\n"]
        
        total = len(self.manifest['diagrams'])
        successful = total - len(self.failed_renders)
        
        report.append(f"**Total Diagrams**: {total}")
        report.append(f"**Successfully Rendered**: {successful}")
        report.append(f"**Failed**: {len(self.failed_renders)}\n")
        
        if self.failed_renders:
            report.append("## Failed Renders\n")
            for diagram_id in self.failed_renders:
                report.append(f"- {diagram_id}")
        
        # Calculate output size
        total_size = 0
        file_count = 0
        
        for path in self.output_base.rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size
                file_count += 1
        
        report.append(f"\n## Output Statistics\n")
        report.append(f"**Total Files Generated**: {file_count}")
        report.append(f"**Total Size**: {total_size / (1024*1024):.2f} MB")
        report.append(f"**Average Size per File**: {total_size / file_count / 1024:.2f} KB")
        
        return '\n'.join(report)


def check_dependencies():
    """Check if required tools are installed."""
    tools = {
        'mmdc': 'mermaid-cli - Install with: npm install -g @mermaid-js/mermaid-cli',
        'convert': 'ImageMagick - Install with: apt-get install imagemagick or brew install imagemagick',
        'cwebp': 'WebP tools - Install with: apt-get install webp or brew install webp'
    }
    
    missing = []
    for tool, install_info in tools.items():
        if shutil.which(tool) is None:
            missing.append(f"{tool} ({install_info})")
    
    if missing:
        print("❌ Missing required tools:")
        for tool in missing:
            print(f"   - {tool}")
        return False
    
    print("✅ All required tools are installed")
    return True


def main():
    """Main execution function."""
    if not check_dependencies():
        print("\n⚠️  Please install missing tools before running the renderer.")
        return
    
    renderer = MermaidRenderer()
    
    print("📁 Setting up directories...")
    renderer.setup_directories()
    
    print("🎨 Starting rendering process...")
    renderer.render_batch(max_workers=4)
    
    print("📝 Generating picture elements...")
    picture_elements = renderer.generate_picture_elements()
    
    with open("picture_elements.json", "w") as f:
        json.dump(picture_elements, f, indent=2)
    
    print("📊 Generating report...")
    report = renderer.generate_report()
    
    with open("rendering_report.md", "w") as f:
        f.write(report)
    
    print(f"✅ Rendering complete! Report saved to: rendering_report.md")


if __name__ == "__main__":
    main()