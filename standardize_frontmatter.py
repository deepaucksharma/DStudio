#!/usr/bin/env python3
"""
Standardize frontmatter across all documentation files
"""

import os
import re
from pathlib import Path
from datetime import datetime

class FrontmatterStandardizer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.processed_count = 0
        self.updated_count = 0
        
    def get_content_type(self, file_path):
        """Determine content type from file path"""
        path_str = str(file_path)
        
        if 'axiom' in path_str:
            return 'axiom'
        elif 'pillar' in path_str:
            return 'pillar'
        elif 'patterns' in path_str:
            return 'pattern'
        elif 'case-studies' in path_str:
            return 'case-study'
        elif 'human-factors' in path_str:
            return 'human-factors'
        elif 'quantitative' in path_str:
            return 'quantitative'
        elif 'reference' in path_str:
            return 'reference'
        elif 'introduction' in path_str:
            return 'introduction'
        else:
            return 'general'
    
    def estimate_difficulty(self, content):
        """Estimate difficulty based on content"""
        content_lower = content.lower()
        
        # Check for complexity indicators
        advanced_terms = ['byzantine', 'paxos', 'raft', 'linearizable', 'consensus', 'quorum']
        intermediate_terms = ['replication', 'sharding', 'consistency', 'partition']
        
        advanced_count = sum(1 for term in advanced_terms if term in content_lower)
        intermediate_count = sum(1 for term in intermediate_terms if term in content_lower)
        
        if advanced_count >= 2:
            return 'advanced'
        elif intermediate_count >= 2 or advanced_count >= 1:
            return 'intermediate'
        else:
            return 'beginner'
    
    def calculate_reading_time(self, content):
        """Calculate reading time based on word count"""
        # Remove code blocks for more accurate count
        content_no_code = re.sub(r'```[\s\S]*?```', '', content)
        
        # Count words
        words = len(content_no_code.split())
        
        # Average reading speed: 200 words per minute
        # Add time for code blocks
        code_blocks = len(re.findall(r'```', content)) // 2
        
        minutes = (words / 200) + (code_blocks * 2)  # 2 min per code block
        
        return max(5, int(round(minutes / 5) * 5))  # Round to nearest 5 min
    
    def extract_existing_frontmatter(self, content):
        """Extract existing frontmatter if present"""
        if content.startswith('---'):
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                fm_text = match.group(1)
                frontmatter = {}
                
                for line in fm_text.split('\n'):
                    if ':' in line and not line.strip().startswith('-'):
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')
                
                return frontmatter, content[match.end():]
        
        return {}, content
    
    def extract_title(self, content, file_path):
        """Extract title from content or filename"""
        # Try to find first H1
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Fall back to filename
        name = Path(file_path).stem
        if name == 'index':
            # Use parent directory name
            name = Path(file_path).parent.name
        
        # Convert to title case
        return name.replace('-', ' ').replace('_', ' ').title()
    
    def extract_description(self, content):
        """Extract description from first paragraph"""
        # Remove frontmatter
        content_no_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # Remove title
        content_no_title = re.sub(r'^# .+\n', '', content_no_fm)
        
        # Find first non-empty paragraph
        paragraphs = content_no_title.strip().split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith(('#', '-', '*', '```', '>')):
                # Clean and truncate
                desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', para)  # Remove links
                desc = desc.replace('**', '').replace('*', '')  # Remove emphasis
                if len(desc) > 150:
                    desc = desc[:147] + '...'
                return desc
        
        return "Documentation for distributed systems concepts"
    
    def extract_prerequisites(self, content):
        """Extract prerequisites from content"""
        prerequisites = []
        
        # Look for prerequisite section
        prereq_match = re.search(r'(?:Prerequisites?|Required Knowledge)[:\s]*\n((?:[-*]\s*.+\n?)+)', 
                                content, re.IGNORECASE | re.MULTILINE)
        
        if prereq_match:
            prereq_text = prereq_match.group(1)
            for line in prereq_text.split('\n'):
                if line.strip().startswith(('-', '*')):
                    prereq = line.strip()[1:].strip()
                    prerequisites.append(prereq)
        
        return prerequisites
    
    def create_frontmatter(self, file_path, content):
        """Create standardized frontmatter"""
        existing_fm, content_body = self.extract_existing_frontmatter(content)
        
        # Base frontmatter
        frontmatter = {
            'title': existing_fm.get('title') or self.extract_title(content_body, file_path),
            'description': existing_fm.get('description') or self.extract_description(content_body),
            'type': existing_fm.get('type') or self.get_content_type(file_path),
            'difficulty': existing_fm.get('difficulty') or self.estimate_difficulty(content_body),
            'reading_time': f"{self.calculate_reading_time(content_body)} min",
            'prerequisites': existing_fm.get('prerequisites', []),
            'status': existing_fm.get('status', 'complete'),
            'last_updated': existing_fm.get('last_updated', datetime.now().strftime('%Y-%m-%d'))
        }
        
        # Add type-specific fields
        if frontmatter['type'] == 'pattern':
            frontmatter['pattern_type'] = existing_fm.get('pattern_type', 'general')
            frontmatter['when_to_use'] = existing_fm.get('when_to_use', '')
            frontmatter['when_not_to_use'] = existing_fm.get('when_not_to_use', '')
        
        # Build YAML
        yaml_lines = ['---']
        
        # Required fields first
        for key in ['title', 'description', 'type', 'difficulty', 'reading_time']:
            value = frontmatter[key]
            if isinstance(value, str) and (':' in value or '"' in value):
                yaml_lines.append(f'{key}: "{value}"')
            else:
                yaml_lines.append(f'{key}: {value}')
        
        # Prerequisites
        if frontmatter['prerequisites']:
            yaml_lines.append('prerequisites:')
            for prereq in frontmatter['prerequisites']:
                yaml_lines.append(f'  - {prereq}')
        else:
            yaml_lines.append('prerequisites: []')
        
        # Optional fields
        for key in ['pattern_type', 'when_to_use', 'when_not_to_use']:
            if key in frontmatter and frontmatter[key]:
                yaml_lines.append(f'{key}: "{frontmatter[key]}"')
        
        # Status and date
        yaml_lines.append(f'status: {frontmatter["status"]}')
        yaml_lines.append(f'last_updated: {frontmatter["last_updated"]}')
        yaml_lines.append('---')
        
        return '\n'.join(yaml_lines) + '\n'
    
    def process_file(self, file_path):
        """Process a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already has good frontmatter
            if content.startswith('---'):
                existing_fm, _ = self.extract_existing_frontmatter(content)
                required_fields = ['title', 'description', 'type', 'difficulty', 'reading_time']
                
                if all(field in existing_fm for field in required_fields):
                    print(f"  ✓ Already has complete frontmatter")
                    return
            
            # Create new frontmatter
            new_frontmatter = self.create_frontmatter(file_path, content)
            
            # Remove existing frontmatter if present
            if content.startswith('---'):
                content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_frontmatter)
                f.write('\n')
                f.write(content.lstrip())
            
            self.updated_count += 1
            print(f"  ✅ Added/updated frontmatter")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def process_all(self):
        """Process all markdown files"""
        print("📝 Standardizing frontmatter across all files...")
        
        for md_file in sorted(self.docs_dir.rglob("*.md")):
            # Skip templates and internal docs
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE', 'SOLUTION']):
                continue
            
            print(f"\nProcessing {md_file.relative_to(self.docs_dir)}...")
            self.process_file(md_file)
            self.processed_count += 1
        
        print(f"\n✅ Processed {self.processed_count} files")
        print(f"📝 Updated {self.updated_count} files with frontmatter")


if __name__ == "__main__":
    standardizer = FrontmatterStandardizer()
    standardizer.process_all()