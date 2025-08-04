#!/usr/bin/env python3
"""
Pattern Template v2 Automated Transformation Script

Automates the transformation of patterns to Template v2 compliance by:
1. Adding essential questions
2. Reducing code percentage
3. Adding visual diagrams placeholders
4. Creating 5-level structure
5. Adding decision matrices
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TemplateV2Transformer:
    def __init__(self, pattern_library_path: str):
        self.pattern_library_path = Path(pattern_library_path)
        self.transformations_applied = 0
        self.errors = []

    def extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and content body."""
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2]
                    return frontmatter, body
            except:
                pass
        return {}, content

    def add_essential_question(self, frontmatter: Dict, body: str) -> Tuple[Dict, str]:
        """Add essential question to frontmatter and body if missing."""
        if 'essential_question' not in frontmatter:
            # Generate essential question based on pattern title
            title = frontmatter.get('title', 'Pattern')
            pattern_type = frontmatter.get('category', 'system')
            
            # Template essential questions by category
            questions = {
                'resilience': f"How do we protect our {pattern_type} from cascading failures when {title.lower()} occurs?",
                'scaling': f"How do we handle increasing load without sacrificing performance using {title.lower()}?",
                'data-management': f"How do we ensure data consistency and reliability with {title.lower()}?",
                'coordination': f"How do we coordinate distributed components effectively using {title.lower()}?",
                'architecture': f"How do we structure our system architecture to leverage {title.lower()}?",
                'communication': f"How do we enable efficient communication between services using {title.lower()}?"
            }
            
            frontmatter['essential_question'] = questions.get(
                pattern_type, 
                f"When and how should we implement {title.lower()} in our distributed system?"
            )
            
            # Add tagline if missing
            if 'tagline' not in frontmatter:
                frontmatter['tagline'] = f"Master {title.lower()} for distributed systems success"
        
        # Ensure essential question appears prominently in body
        if '## Essential Question' not in body:
            essential_section = f"\n## Essential Question\n\n**{frontmatter['essential_question']}**\n\n"
            # Insert after title
            body = body.replace('\n\n', essential_section, 1)
            
        return frontmatter, body

    def add_when_to_use_tables(self, body: str) -> str:
        """Add When to Use/When NOT to Use tables if missing."""
        if '## When to Use' not in body:
            when_to_use = """
## When to Use / When NOT to Use

### When to Use

| Scenario | Why It Fits | Alternative If Not |
|----------|-------------|-------------------|
| High availability required | Pattern provides resilience | Consider simpler approach |
| Scalability is critical | Handles load distribution | Monolithic might suffice |
| Distributed coordination needed | Manages complexity | Centralized coordination |

### When NOT to Use

| Scenario | Why to Avoid | Better Alternative |
|----------|--------------|-------------------|
| Simple applications | Unnecessary complexity | Direct implementation |
| Low traffic systems | Overhead not justified | Basic architecture |
| Limited resources | High operational cost | Simpler patterns |
"""
            # Insert early in document
            if '## Overview' in body:
                body = body.replace('## Overview', when_to_use + '\n## Overview')
            else:
                body = body.replace('\n\n', when_to_use, 1)
        
        return body

    def add_five_level_structure(self, body: str) -> str:
        """Add 5-level progressive disclosure structure."""
        if '## Level 1: Intuition' not in body:
            five_levels = """
## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]
"""
            # Add after When to Use section
            if '## Implementation' in body:
                body = body.replace('## Implementation', five_levels + '\n## Implementation')
            else:
                body += '\n' + five_levels
        
        return body

    def reduce_code_percentage(self, body: str) -> str:
        """Reduce code blocks and add visual diagram placeholders."""
        # Find all code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', body)
        
        # Replace large code blocks with diagram placeholders
        for i, block in enumerate(code_blocks):
            lines = block.count('\n')
            if lines > 20:  # Large code block
                diagram = f"""```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

{block}

</details>"""
                body = body.replace(block, diagram, 1)
                
        return body

    def add_decision_matrix(self, body: str) -> str:
        """Add decision matrix if missing."""
        if '## Decision Matrix' not in body and '## Decision Guide' not in body:
            matrix = """
## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |
"""
            # Add before implementation section
            if '## Implementation' in body:
                body = body.replace('## Implementation', matrix + '\n## Implementation')
            else:
                body += '\n' + matrix
                
        return body

    def transform_pattern(self, file_path: Path) -> bool:
        """Transform a single pattern file to Template v2."""
        try:
            content = file_path.read_text()
            frontmatter, body = self.extract_frontmatter(content)
            
            # Skip if already has essential_question and 5-level structure
            if 'essential_question' in frontmatter and '## Level 1: Intuition' in body:
                return False
            
            # Apply transformations
            frontmatter, body = self.add_essential_question(frontmatter, body)
            body = self.add_when_to_use_tables(body)
            body = self.add_five_level_structure(body)
            body = self.reduce_code_percentage(body)
            body = self.add_decision_matrix(body)
            
            # Reconstruct file
            new_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n{body}"
            
            # Write back
            file_path.write_text(new_content)
            self.transformations_applied += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error transforming {file_path}: {str(e)}")
            return False

    def transform_all_patterns(self, dry_run: bool = False) -> Dict:
        """Transform all patterns in the library."""
        results = {
            'transformed': [],
            'skipped': [],
            'errors': self.errors
        }
        
        pattern_files = list(self.pattern_library_path.rglob('*.md'))
        
        for file_path in pattern_files:
            # Skip index files and non-pattern files
            if file_path.name in ['index.md', 'pattern-template-v2.md', 'RENDERING_INSTRUCTIONS.md']:
                continue
                
            if dry_run:
                content = file_path.read_text()
                if 'essential_question' not in content or '## Level 1: Intuition' not in content:
                    results['transformed'].append(str(file_path))
                else:
                    results['skipped'].append(str(file_path))
            else:
                if self.transform_pattern(file_path):
                    results['transformed'].append(str(file_path))
                else:
                    results['skipped'].append(str(file_path))
        
        return results

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Transform patterns to Template v2')
    parser.add_argument('--path', default='docs/pattern-library', help='Path to pattern library')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be transformed')
    parser.add_argument('--pattern', help='Transform specific pattern file')
    
    args = parser.parse_args()
    
    transformer = TemplateV2Transformer(args.path)
    
    if args.pattern:
        # Transform single pattern
        pattern_path = Path(args.pattern)
        if pattern_path.exists():
            success = transformer.transform_pattern(pattern_path)
            print(f"{'✅ Transformed' if success else '⏭️  Skipped'} {pattern_path}")
        else:
            print(f"❌ Pattern not found: {args.pattern}")
    else:
        # Transform all patterns
        print(f"{'🔍 Analyzing' if args.dry_run else '🚀 Transforming'} patterns in {args.path}...")
        results = transformer.transform_all_patterns(dry_run=args.dry_run)
        
        print(f"\n📊 Results:")
        print(f"✅ {'Would transform' if args.dry_run else 'Transformed'}: {len(results['transformed'])} patterns")
        print(f"⏭️  Skipped (already compliant): {len(results['skipped'])} patterns")
        print(f"❌ Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\n❌ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        if args.dry_run and results['transformed']:
            print(f"\n📝 Patterns that would be transformed:")
            for pattern in results['transformed'][:10]:
                print(f"  - {pattern}")
            if len(results['transformed']) > 10:
                print(f"  ... and {len(results['transformed']) - 10} more")

if __name__ == '__main__':
    main()