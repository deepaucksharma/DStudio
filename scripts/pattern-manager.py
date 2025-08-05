#!/usr/bin/env python3
"""
Pattern Manager - Tools for managing pattern library

This script provides comprehensive tools for managing patterns:
- Adding new patterns with correct metadata
- Bulk updating pattern metadata  
- Generating pattern statistics
- Checking pattern quality
- Auto-fixing common issues

Usage:
    python3 scripts/pattern-manager.py [command] [options]

Commands:
    add         Add new pattern with template
    update      Update existing pattern metadata
    bulk-update Bulk update multiple patterns
    stats       Generate pattern statistics
    quality     Check pattern quality
    fix         Auto-fix common issues
    template    Generate pattern template
"""

import os
import sys
import yaml
import json
import re
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class PatternTemplate:
    """Pattern template structure"""
    title: str
    category: str
    excellence_tier: str
    pattern_status: str
    description: str
    problem: str
    solution: str
    use_cases: List[str]
    trade_offs: Dict[str, List[str]]
    examples: List[str]

class PatternManager:
    """Pattern library management tools"""
    
    VALID_CATEGORIES = {
        'architecture', 'communication', 'coordination', 
        'data-management', 'resilience', 'scaling'
    }
    
    VALID_TIERS = {'gold', 'silver', 'bronze'}
    
    VALID_STATUS = {
        'recommended', 'stable', 'use-with-expertise', 
        'use-with-caution', 'legacy', 'deprecated', 'experimental'
    }
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.docs_path = project_root / "docs"
        self.pattern_lib_path = self.docs_path / "pattern-library"
        
    def add_pattern(self, name: str, category: str, tier: str = 'silver', 
                   status: str = 'stable', interactive: bool = True) -> bool:
        """Add new pattern with template"""
        self.log(f"🔨 Adding new pattern: {name}")
        
        # Validate inputs
        if category not in self.VALID_CATEGORIES:
            print(f"❌ Invalid category. Choose from: {', '.join(self.VALID_CATEGORIES)}")
            return False
            
        if tier not in self.VALID_TIERS:
            print(f"❌ Invalid tier. Choose from: {', '.join(self.VALID_TIERS)}")
            return False
            
        if status not in self.VALID_STATUS:
            print(f"❌ Invalid status. Choose from: {', '.join(self.VALID_STATUS)}")
            return False
        
        # Create filename
        filename = name.lower().replace(' ', '-').replace('_', '-')
        filename = re.sub(r'[^a-z0-9-]', '', filename)
        
        # Check if pattern exists
        pattern_path = self.pattern_lib_path / category / f"{filename}.md"
        if pattern_path.exists():
            print(f"❌ Pattern already exists: {pattern_path}")
            return False
        
        # Create category directory if needed
        category_path = self.pattern_lib_path / category
        category_path.mkdir(exist_ok=True)
        
        # Gather pattern information
        if interactive:
            pattern_info = self._gather_pattern_info(name, category, tier, status)
        else:
            pattern_info = PatternTemplate(
                title=name,
                category=category,
                excellence_tier=tier,
                pattern_status=status,
                description="",
                problem="",
                solution="",
                use_cases=[],
                trade_offs={"pros": [], "cons": []},
                examples=[]
            )
        
        # Generate pattern content
        content = self._generate_pattern_content(pattern_info)
        
        # Write pattern file
        try:
            with open(pattern_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.log(f"✅ Pattern created: {pattern_path}")
            
            # Update navigation hint
            print(f"\n📝 Don't forget to add to navigation in mkdocs.yml:")
            print(f"   - {pattern_info.title}: pattern-library/{category}/{filename}.md")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create pattern: {e}")
            return False
    
    def _gather_pattern_info(self, name: str, category: str, tier: str, status: str) -> PatternTemplate:
        """Interactively gather pattern information"""
        print(f"\n📝 Creating pattern: {name}")
        print("="*50)
        
        # Basic info
        title = input(f"Title [{name}]: ").strip() or name
        description = input("Short description: ").strip()
        
        # Problem and solution
        print(f"\n🎯 Problem & Solution:")
        problem = input("What problem does this pattern solve? ").strip()
        solution = input("How does it solve the problem? ").strip()
        
        # Use cases
        print(f"\n💡 Use Cases (press Enter when done):")
        use_cases = []
        while True:
            use_case = input(f"Use case {len(use_cases)+1}: ").strip()
            if not use_case:
                break
            use_cases.append(use_case)
        
        # Trade-offs
        print(f"\n⚖️ Trade-offs:")
        print("Pros (press Enter when done):")
        pros = []
        while True:
            pro = input(f"Pro {len(pros)+1}: ").strip()
            if not pro:
                break
            pros.append(pro)
        
        print("Cons (press Enter when done):")
        cons = []
        while True:
            con = input(f"Con {len(cons)+1}: ").strip()
            if not con:
                break
            cons.append(con)
        
        # Examples
        print(f"\n🏢 Examples (companies/systems):")
        examples = []
        while True:
            example = input(f"Example {len(examples)+1}: ").strip()
            if not example:
                break
            examples.append(example)
        
        return PatternTemplate(
            title=title,
            category=category,
            excellence_tier=tier,
            pattern_status=status,
            description=description,
            problem=problem,
            solution=solution,
            use_cases=use_cases,
            trade_offs={"pros": pros, "cons": cons},
            examples=examples
        )
    
    def _generate_pattern_content(self, pattern: PatternTemplate) -> str:
        """Generate pattern markdown content"""
        content = f"""---
title: {pattern.title}
category: {pattern.category}
excellence_tier: {pattern.excellence_tier}
pattern_status: {pattern.pattern_status}
introduced: {datetime.now().strftime('%Y-%m')}
current_relevance: mainstream
---

# {pattern.title}

{self._generate_tier_badge(pattern.excellence_tier)}

{pattern.description}

[Home](/) > [Pattern Library](../) > [{pattern.category.title()} Patterns](./) > {pattern.title}

## Pattern Summary

| Aspect | Detail |
|--------|--------|
| **Problem Solved** | {pattern.problem} |
| **When to Use** | {', '.join(pattern.use_cases[:3]) if pattern.use_cases else 'TBD'} |
| **Key Benefits** | {', '.join(pattern.trade_offs['pros'][:3]) if pattern.trade_offs['pros'] else 'TBD'} |
| **Trade-offs** | {', '.join(pattern.trade_offs['cons'][:3]) if pattern.trade_offs['cons'] else 'TBD'} |
| **Implementation** | Intermediate difficulty |

## The Essential Question

**{pattern.problem}**

> *{pattern.solution}*

## Problem Context

### What Challenge Does This Solve?

{pattern.problem}

### Why Is This Important?

- Performance implications
- Scalability considerations  
- Reliability requirements
- Operational complexity

## Solution Approach

### Core Concept

{pattern.solution}

### Architecture Diagram

```mermaid
graph TB
    A[Client] --> B[Component 1]
    B --> C[Component 2]
    C --> D[Result]
    
    style A fill:#e1f5fe
    style D fill:#e8f5e8
```

## Implementation Details

### Basic Implementation

```python
# Basic implementation example
class {pattern.title.replace(' ', '').replace('-', '')}:
    def __init__(self):
        pass
        
    def execute(self):
        # Implementation details
        pass
```

### Key Components

1. **Component 1**: Description
2. **Component 2**: Description  
3. **Component 3**: Description

## Trade-offs Analysis

### Pros ✅

{chr(10).join(f'- {pro}' for pro in pattern.trade_offs['pros']) if pattern.trade_offs['pros'] else '- TBD'}

### Cons ❌

{chr(10).join(f'- {con}' for con in pattern.trade_offs['cons']) if pattern.trade_offs['cons'] else '- TBD'}

## When to Use

### Ideal Scenarios

{chr(10).join(f'- {use_case}' for use_case in pattern.use_cases) if pattern.use_cases else '- TBD'}

### Avoid When

- Small scale systems
- Simple requirements
- Limited resources

## Real-World Examples

{chr(10).join(f'### {example}' + chr(10) + 'Implementation details and lessons learned.' + chr(10) for example in pattern.examples) if pattern.examples else '### Example Company' + chr(10) + 'Implementation details coming soon.' + chr(10)}

{self._generate_tier_specific_sections(pattern.excellence_tier)}

## Related Patterns

- **Complements**: [Pattern A](../category/pattern-a.md)
- **Alternatives**: [Pattern B](../category/pattern-b.md)
- **Composes with**: [Pattern C](../category/pattern-c.md)

## References

- [External Resource 1](https://example.com)
- [External Resource 2](https://example.com)

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        return content
    
    def _generate_tier_badge(self, tier: str) -> str:
        """Generate tier badge"""
        badges = {
            'gold': '!!! success "🏆 Gold Standard Pattern"\n    **Production-Ready Foundation** • Battle-tested at scale\n    \n    This pattern has proven itself in high-traffic production environments and is considered an industry standard for solving this specific problem.',
            'silver': '!!! info "🥈 Silver Specialized Pattern"\n    **Domain-Specific Solution** • Use with expertise\n    \n    This pattern excels in specific scenarios but requires careful consideration of trade-offs and proper implementation.',
            'bronze': '!!! warning "🥉 Bronze Legacy Pattern"\n    **Legacy with Modern Alternatives** • Consider alternatives first\n    \n    This pattern has historical significance but modern alternatives may be more suitable for new systems.'
        }
        return badges.get(tier, '')
    
    def _generate_tier_specific_sections(self, tier: str) -> str:
        """Generate tier-specific sections"""
        if tier == 'gold':
            return """
## Production Checklist

### Pre-Implementation
- [ ] Requirements clearly defined
- [ ] Team has necessary expertise
- [ ] Infrastructure capacity verified

### Implementation
- [ ] Monitoring and alerting configured
- [ ] Error handling implemented
- [ ] Performance benchmarks established

### Post-Implementation
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Runbooks created

## Modern Examples

### Company A
- **Scale**: X requests/second
- **Implementation**: Brief description
- **Results**: Performance metrics

### Company B  
- **Scale**: X requests/second
- **Implementation**: Brief description
- **Results**: Performance metrics
"""
        elif tier == 'silver':
            return """
## Usage Guidelines

### Best For
- Scenario 1
- Scenario 2
- Scenario 3

### Consider Alternatives When
- Condition 1
- Condition 2
- Condition 3

## Implementation Considerations

### Prerequisites
- Technical requirement 1
- Technical requirement 2
- Team expertise level

### Common Pitfalls
- Pitfall 1 and how to avoid
- Pitfall 2 and how to avoid
"""
        elif tier == 'bronze':
            return """
## Modern Alternatives

### Recommended Instead
- [Modern Pattern A](../category/modern-pattern.md) - Why it's better
- [Modern Pattern B](../category/modern-pattern.md) - Use cases

### Migration Path
1. Assessment phase
2. Incremental replacement
3. Validation and rollout

### Why This Pattern Became Legacy
- Technology evolution
- Better solutions emerged
- Limitations discovered
"""
        return ""
    
    def update_metadata(self, pattern_path: str, **kwargs) -> bool:
        """Update pattern metadata"""
        self.log(f"📝 Updating metadata for: {pattern_path}")
        
        file_path = Path(self.project_root / pattern_path)
        if not file_path.exists():
            print(f"❌ Pattern not found: {file_path}")
            return False
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            if not content.startswith('---'):
                print(f"❌ No frontmatter found in: {file_path}")
                return False
            
            end_marker = content.find('---', 3)
            if end_marker == -1:
                print(f"❌ Invalid frontmatter in: {file_path}")
                return False
            
            frontmatter = content[3:end_marker].strip()
            body = content[end_marker + 3:]
            
            # Parse and update metadata
            metadata = yaml.safe_load(frontmatter) or {}
            
            for key, value in kwargs.items():
                if value is not None:
                    metadata[key] = value
                    self.log(f"  Updated {key}: {value}")
            
            # Write updated content
            new_frontmatter = yaml.dump(metadata, default_flow_style=False)
            new_content = f"---\n{new_frontmatter}---{body}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.log(f"✅ Updated: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update metadata: {e}")
            return False
    
    def bulk_update(self, pattern_filter: str = "*", **kwargs) -> int:
        """Bulk update patterns matching filter"""
        self.log(f"🔄 Bulk updating patterns: {pattern_filter}")
        
        updated_count = 0
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir():
                continue
                
            for pattern_file in category_dir.glob(pattern_filter):
                if pattern_file.name == 'index.md':
                    continue
                    
                relative_path = str(pattern_file.relative_to(self.project_root))
                if self.update_metadata(relative_path, **kwargs):
                    updated_count += 1
        
        self.log(f"✅ Updated {updated_count} patterns")
        return updated_count
    
    def generate_stats(self) -> Dict[str, Any]:
        """Generate pattern library statistics"""
        self.log("📊 Generating pattern statistics...")
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_patterns': 0,
            'by_category': {},
            'by_tier': {'gold': 0, 'silver': 0, 'bronze': 0},
            'by_status': {},
            'quality_metrics': {}
        }
        
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir():
                continue
                
            category = category_dir.name
            category_count = 0
            
            for pattern_file in category_dir.glob("*.md"):
                if pattern_file.name == 'index.md':
                    continue
                    
                stats['total_patterns'] += 1
                category_count += 1
                
                # Extract metadata for stats
                try:
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith('---'):
                        end_marker = content.find('---', 3)
                        if end_marker != -1:
                            frontmatter = content[3:end_marker].strip()
                            metadata = yaml.safe_load(frontmatter) or {}
                            
                            tier = metadata.get('excellence_tier', 'unknown')
                            status = metadata.get('pattern_status', 'unknown')
                            
                            if tier in stats['by_tier']:
                                stats['by_tier'][tier] += 1
                            
                            if status not in stats['by_status']:
                                stats['by_status'][status] = 0
                            stats['by_status'][status] += 1
                            
                except Exception:
                    pass
            
            stats['by_category'][category] = category_count
        
        return stats
    
    def check_quality(self, pattern_path: Optional[str] = None) -> Dict[str, Any]:
        """Check pattern quality metrics"""
        self.log(f"🔍 Checking pattern quality...")
        
        if pattern_path:
            patterns = [Path(self.project_root / pattern_path)]
        else:
            patterns = []
            for category_dir in self.pattern_lib_path.iterdir():
                if category_dir.is_dir():
                    patterns.extend(category_dir.glob("*.md"))
        
        quality_report = {
            'total_checked': len(patterns),
            'scores': {},
            'issues': []
        }
        
        for pattern_file in patterns:
            if pattern_file.name == 'index.md':
                continue
                
            score = self._calculate_quality_score(pattern_file)
            relative_path = str(pattern_file.relative_to(self.project_root))
            quality_report['scores'][relative_path] = score
        
        return quality_report
    
    def _calculate_quality_score(self, pattern_file: Path) -> Dict[str, Any]:
        """Calculate quality score for a pattern"""
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            has_diagram = 'mermaid' in content
            has_code = '```' in content
            has_examples = 'example' in content.lower()
            
            # Metadata quality
            metadata_score = 0
            if content.startswith('---'):
                end_marker = content.find('---', 3)
                if end_marker != -1:
                    frontmatter = content[3:end_marker].strip()
                    metadata = yaml.safe_load(frontmatter) or {}
                    
                    required_fields = ['title', 'category', 'excellence_tier', 'pattern_status']
                    present_fields = sum(1 for field in required_fields if metadata.get(field))
                    metadata_score = (present_fields / len(required_fields)) * 100
            
            # Content quality indicators
            content_score = 0
            content_indicators = [
                ('Has examples', has_examples, 20),
                ('Has diagrams', has_diagram, 20),
                ('Has code samples', has_code, 15),
                ('Adequate length', word_count > 500, 25),
                ('Well structured', '##' in content, 20)
            ]
            
            for name, present, weight in content_indicators:
                if present:
                    content_score += weight
            
            total_score = (metadata_score * 0.3) + (content_score * 0.7)
            
            return {
                'total_score': round(total_score, 2),
                'metadata_score': round(metadata_score, 2),
                'content_score': round(content_score, 2),
                'word_count': word_count,
                'has_diagram': has_diagram,
                'has_code': has_code,
                'has_examples': has_examples
            }
            
        except Exception as e:
            return {'error': str(e), 'total_score': 0}
    
    def auto_fix(self, dry_run: bool = True) -> int:
        """Auto-fix common issues"""
        self.log(f"🔧 Auto-fixing common issues (dry_run={dry_run})...")
        
        fix_count = 0
        
        # Fix category mismatches
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir():
                continue
                
            category = category_dir.name
            
            for pattern_file in category_dir.glob("*.md"):
                if pattern_file.name == 'index.md':
                    continue
                
                try:
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith('---'):
                        end_marker = content.find('---', 3)
                        if end_marker != -1:
                            frontmatter = content[3:end_marker].strip()
                            metadata = yaml.safe_load(frontmatter) or {}
                            
                            # Fix category mismatch
                            if metadata.get('category') != category:
                                self.log(f"  Fixing category mismatch in {pattern_file.name}")
                                if not dry_run:
                                    metadata['category'] = category
                                    new_frontmatter = yaml.dump(metadata, default_flow_style=False)
                                    new_content = f"---\n{new_frontmatter}---{content[end_marker + 3:]}"
                                    
                                    with open(pattern_file, 'w', encoding='utf-8') as f:
                                        f.write(new_content)
                                
                                fix_count += 1
                        
                except Exception as e:
                    self.log(f"  Error fixing {pattern_file}: {e}")
        
        self.log(f"✅ {'Would fix' if dry_run else 'Fixed'} {fix_count} issues")
        return fix_count
    
    def generate_template(self, output_path: str = "pattern-template.md") -> bool:
        """Generate a pattern template file"""
        template = PatternTemplate(
            title="Example Pattern",
            category="architecture", 
            excellence_tier="silver",
            pattern_status="stable",
            description="Brief description of what this pattern does",
            problem="What problem does this pattern solve?",
            solution="How does it solve the problem?",
            use_cases=["Use case 1", "Use case 2"],
            trade_offs={"pros": ["Pro 1", "Pro 2"], "cons": ["Con 1", "Con 2"]},
            examples=["Company A", "Company B"]
        )
        
        content = self._generate_pattern_content(template)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"✅ Template generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate template: {e}")
            return False
    
    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(message)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Pattern Library Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Common arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new pattern')
    add_parser.add_argument('name', help='Pattern name')
    add_parser.add_argument('category', choices=['architecture', 'communication', 'coordination', 'data-management', 'resilience', 'scaling'])
    add_parser.add_argument('--tier', choices=['gold', 'silver', 'bronze'], default='silver')
    add_parser.add_argument('--status', default='stable')
    add_parser.add_argument('--batch', action='store_true', help='Non-interactive mode')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update pattern metadata')
    update_parser.add_argument('pattern', help='Pattern file path')
    update_parser.add_argument('--tier', choices=['gold', 'silver', 'bronze'])
    update_parser.add_argument('--status', choices=['recommended', 'stable', 'use-with-expertise', 'use-with-caution', 'legacy', 'deprecated'])
    update_parser.add_argument('--category', choices=['architecture', 'communication', 'coordination', 'data-management', 'resilience', 'scaling'])
    
    # Bulk update command
    bulk_parser = subparsers.add_parser('bulk-update', help='Bulk update patterns')
    bulk_parser.add_argument('--filter', default='*.md', help='Pattern filter')
    bulk_parser.add_argument('--tier', choices=['gold', 'silver', 'bronze'])
    bulk_parser.add_argument('--status')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Generate statistics')
    stats_parser.add_argument('--format', choices=['json', 'yaml', 'table'], default='table')
    stats_parser.add_argument('--output', '-o', help='Output file')
    
    # Quality command
    quality_parser = subparsers.add_parser('quality', help='Check pattern quality')
    quality_parser.add_argument('--pattern', help='Specific pattern to check')
    quality_parser.add_argument('--format', choices=['json', 'yaml', 'table'], default='table')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Auto-fix common issues')
    fix_parser.add_argument('--dry-run', action='store_true', default=True, help='Show what would be fixed')
    fix_parser.add_argument('--apply', action='store_true', help='Actually apply fixes')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Generate pattern template')
    template_parser.add_argument('--output', '-o', default='pattern-template.md')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = PatternManager(PROJECT_ROOT, verbose=args.verbose)
    
    try:
        if args.command == 'add':
            success = manager.add_pattern(
                args.name, args.category, args.tier, args.status, 
                interactive=not args.batch
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'update':
            kwargs = {}
            if args.tier:
                kwargs['excellence_tier'] = args.tier
            if args.status:
                kwargs['pattern_status'] = args.status
            if args.category:
                kwargs['category'] = args.category
            
            success = manager.update_metadata(args.pattern, **kwargs)
            sys.exit(0 if success else 1)
            
        elif args.command == 'bulk-update':
            kwargs = {}
            if args.tier:
                kwargs['excellence_tier'] = args.tier
            if args.status:
                kwargs['pattern_status'] = args.status
            
            count = manager.bulk_update(args.filter, **kwargs)
            print(f"Updated {count} patterns")
            
        elif args.command == 'stats':
            stats = manager.generate_stats()
            
            if args.format == 'json':
                output = json.dumps(stats, indent=2)
            elif args.format == 'yaml':
                output = yaml.dump(stats, default_flow_style=False)
            else:
                # Table format
                output = f"""Pattern Library Statistics
Generated: {stats['timestamp']}

Total Patterns: {stats['total_patterns']}

By Category:
{chr(10).join(f'  {cat}: {count}' for cat, count in sorted(stats['by_category'].items()))}

By Excellence Tier:
  Gold: {stats['by_tier']['gold']}
  Silver: {stats['by_tier']['silver']}  
  Bronze: {stats['by_tier']['bronze']}

By Status:
{chr(10).join(f'  {status}: {count}' for status, count in sorted(stats['by_status'].items()))}
"""
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Stats written to: {args.output}")
            else:
                print(output)
                
        elif args.command == 'quality':
            quality = manager.check_quality(args.pattern)
            
            if args.format == 'json':
                print(json.dumps(quality, indent=2))
            elif args.format == 'yaml':
                print(yaml.dump(quality, default_flow_style=False))
            else:
                print(f"Quality Report - {quality['total_checked']} patterns checked")
                print("="*50)
                for path, score in sorted(quality['scores'].items()):
                    if isinstance(score, dict) and 'total_score' in score:
                        print(f"{score['total_score']:6.1f} - {path}")
                    else:
                        print(f"ERROR  - {path}")
        
        elif args.command == 'fix':
            dry_run = not args.apply
            count = manager.auto_fix(dry_run=dry_run)
            if dry_run:
                print(f"Would fix {count} issues. Use --apply to apply fixes.")
            else:
                print(f"Fixed {count} issues.")
                
        elif args.command == 'template':
            success = manager.generate_template(args.output)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()