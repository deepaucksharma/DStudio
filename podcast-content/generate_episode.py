#!/usr/bin/env python3
"""
Podcast Episode Generator for DStudio Content
============================================

This script automates the creation of podcast episodes by concatenating 
related markdown files with intelligent narrative bridges and formatting.

Usage:
    python generate_episode.py --config episode_configs/episode-02.yaml
    python generate_episode.py --series foundational --episode 2
    python generate_episode.py --interactive  # Interactive mode
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime


class PodcastEpisodeGenerator:
    """Generates podcast episodes by concatenating and formatting content files."""
    
    def __init__(self, base_path: str = "\\wsl.localhost\\Ubuntu\\home\\deepak\\DStudio"):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs"
        self.output_path = self.base_path / "podcast-content"
        
        # Ensure output directories exist
        self.ensure_output_structure()
    
    def ensure_output_structure(self):
        """Create the podcast content directory structure."""
        series_dirs = [
            "01-foundational-series",
            "02-pattern-mastery", 
            "03-case-studies",
            "04-quantitative-mastery",
            "05-operational-excellence",
            "06-interview-prep"
        ]
        
        for series_dir in series_dirs:
            (self.output_path / series_dir).mkdir(parents=True, exist_ok=True)
    
    def read_file_content(self, file_path: str) -> str:
        """Read content from a markdown file, handling errors gracefully."""
        try:
            full_path = self.docs_path / file_path.lstrip('/')
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove front matter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()
                
                return content
            else:
                return f"<!-- FILE NOT FOUND: {file_path} -->"
                
        except Exception as e:
            return f"<!-- ERROR READING {file_path}: {str(e)} -->"
    
    def create_narrative_bridge(self, from_topic: str, to_topic: str, context: str = "") -> str:
        """Generate narrative bridges between content sections."""
        bridges = {
            ("failure", "time"): "Now that we understand how systems fail together, let's explore another fundamental constraint: the nature of time itself in distributed systems.",
            ("time", "latency"): "Time synchronization issues lead us naturally to the physics of latency - the hard constraints that govern every distributed system.",
            ("latency", "network"): "Understanding latency numbers helps us appreciate why network topology and communication patterns are so critical.",
            ("patterns", "cases"): "These patterns become clearer when we see them applied in real-world systems at massive scale.",
            ("theory", "practice"): "Let's see how these theoretical concepts play out in production systems.",
            ("concepts", "implementation"): "Now that we have the conceptual foundation, let's explore how these ideas are implemented in practice."
        }
        
        # Try to find a specific bridge
        key = (from_topic.lower(), to_topic.lower())
        if key in bridges:
            return f"\n\n---\n\n### Transition: From {from_topic.title()} to {to_topic.title()}\n\n{bridges[key]}\n\n---\n\n"
        
        # Generic bridge
        return f"\n\n---\n\n### Moving from {from_topic.title()} to {to_topic.title()}\n\nBuilding on our understanding of {from_topic.lower()}, let's now explore {to_topic.lower()} and how these concepts interconnect.\n\n---\n\n"
    
    def estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes (assumes 200 words per minute)."""
        word_count = len(content.split())
        return max(1, round(word_count / 200))
    
    def create_episode_header(self, config: Dict[str, Any]) -> str:
        """Create standardized episode header."""
        return f"""# PODCAST EPISODE {config['episode_number']}: {config['title']}
## {config['series_name']}
**Estimated Duration: {config['duration']}**
**Target Audience: {config.get('audience', 'Engineers, Architects, Technical Leaders')}**

---

## EPISODE INTRODUCTION

{config['introduction']}

---

"""
    
    def create_part_header(self, part_number: int, title: str, duration: str, description: str = "") -> str:
        """Create standardized part header within episodes."""
        header = f"""## PART {part_number}: {title.upper()}
*Estimated Duration: {duration}*

"""
        if description:
            header += f"{description}\n\n"
        
        return header
    
    def create_episode_conclusion(self, config: Dict[str, Any]) -> str:
        """Create standardized episode conclusion."""
        return f"""
---

## EPISODE CONCLUSION: {config.get('conclusion_theme', 'Key Takeaways')}

### Key Takeaways

{config['key_takeaways']}

### What's Next

{config.get('next_episode_preview', 'In our next episode, we\'ll continue exploring distributed systems concepts.')}

---

*Total Episode Length: ~{config['duration']}*
*Next Episode: {config.get('next_episode_title', 'TBD')}*
"""
    
    def process_file_content(self, content: str, file_config: Dict[str, Any]) -> str:
        """Process file content with custom introductions and formatting."""
        processed = content
        
        # Add custom introduction if provided
        if 'intro' in file_config:
            processed = f"{file_config['intro']}\n\n{processed}"
        
        # Add section markers for audio production
        if 'audio_markers' in file_config:
            for marker in file_config['audio_markers']:
                processed = processed.replace(marker['text'], f"<!-- AUDIO: {marker['instruction']} -->\n{marker['text']}")
        
        return processed
    
    def generate_episode(self, config: Dict[str, Any]) -> str:
        """Generate a complete episode from configuration."""
        episode_content = []
        
        # Add episode header
        episode_content.append(self.create_episode_header(config))
        
        # Process each part
        for part_idx, part in enumerate(config['parts'], 1):
            # Add part header
            episode_content.append(self.create_part_header(
                part_idx, 
                part['title'], 
                part['duration'],
                part.get('description', '')
            ))
            
            # Process files in this part
            for file_idx, file_config in enumerate(part['files']):
                # Read file content
                content = self.read_file_content(file_config['path'])
                
                # Process content with custom configuration
                processed_content = self.process_file_content(content, file_config)
                
                episode_content.append(processed_content)
                
                # Add narrative bridge to next file if not last
                if file_idx < len(part['files']) - 1:
                    next_file = part['files'][file_idx + 1]
                    bridge = self.create_narrative_bridge(
                        file_config.get('topic', 'previous topic'),
                        next_file.get('topic', 'next topic')
                    )
                    episode_content.append(bridge)
        
        # Add episode conclusion
        episode_content.append(self.create_episode_conclusion(config))
        
        return '\n'.join(episode_content)
    
    def save_episode(self, content: str, series: str, episode_number: int, title: str):
        """Save episode content to appropriate file."""
        # Create filename
        filename = f"episode-{episode_number:02d}-{title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '')}.md"
        
        # Determine series directory
        series_mapping = {
            'foundational': '01-foundational-series',
            'patterns': '02-pattern-mastery',
            'cases': '03-case-studies', 
            'quantitative': '04-quantitative-mastery',
            'operations': '05-operational-excellence',
            'interviews': '06-interview-prep'
        }
        
        series_dir = series_mapping.get(series, f"0{episode_number//10 + 1}-{series}")
        output_file = self.output_path / series_dir / filename
        
        # Write content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Episode saved: {output_file}")
        return output_file
    
    def load_episode_config(self, config_file: str) -> Dict[str, Any]:
        """Load episode configuration from YAML file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def interactive_mode(self):
        """Interactive mode for creating episodes."""
        print("🎙️ Podcast Episode Generator - Interactive Mode")
        print("=" * 50)
        
        # Get basic episode info
        series = input("Series (foundational/patterns/cases/quantitative/operations/interviews): ")
        episode_num = int(input("Episode number: "))
        title = input("Episode title: ")
        duration = input("Estimated duration (e.g., 2.5h): ")
        
        print(f"\n📝 Creating Episode {episode_num}: {title}")
        
        # Get files to include
        files = []
        print("\nEnter file paths (relative to docs/). Press Enter with empty input to finish:")
        while True:
            file_path = input(f"File {len(files)+1}: ")
            if not file_path:
                break
                
            topic = input(f"Topic/theme for this file: ")
            duration_min = input(f"Estimated duration (e.g., 45 min): ")
            
            files.append({
                'path': file_path,
                'topic': topic,
                'duration': duration_min
            })
        
        # Create basic config
        config = {
            'episode_number': episode_num,
            'title': title,
            'series_name': series.title() + " Series",
            'duration': duration,
            'introduction': f"Welcome to Episode {episode_num} of our {series} series on distributed systems.",
            'key_takeaways': "Key insights from this episode will be summarized here.",
            'parts': [{
                'title': title,
                'duration': duration,
                'files': files
            }]
        }
        
        # Generate and save episode
        content = self.generate_episode(config)
        output_file = self.save_episode(content, series, episode_num, title)
        
        print(f"\n🎉 Episode created successfully!")
        print(f"📁 File: {output_file}")
        print(f"📊 Content length: {len(content)} characters")
        print(f"⏱️ Estimated reading time: {self.estimate_reading_time(content)} minutes")


def main():
    parser = argparse.ArgumentParser(description='Generate podcast episodes from DStudio content')
    parser.add_argument('--config', help='YAML configuration file for episode')
    parser.add_argument('--series', help='Series name (foundational/patterns/cases/etc.)')
    parser.add_argument('--episode', type=int, help='Episode number')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--base-path', default="\\wsl.localhost\\Ubuntu\\home\\deepak\\DStudio", 
                       help='Base path to DStudio repository')
    
    args = parser.parse_args()
    
    generator = PodcastEpisodeGenerator(args.base_path)
    
    if args.interactive:
        generator.interactive_mode()
    elif args.config:
        config = generator.load_episode_config(args.config)
        content = generator.generate_episode(config)
        generator.save_episode(content, args.series or 'custom', 
                             config['episode_number'], config['title'])
    else:
        print("Please specify --config, --interactive, or provide --series and --episode")
        parser.print_help()


if __name__ == "__main__":
    main()
