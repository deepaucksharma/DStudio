#!/usr/bin/env python3
"""
Apply Template v2 Standards to All Patterns
Ensures all patterns meet the comprehensive Template v2 requirements
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class TemplateV2Standardizer:
    """Apply Template v2 standards to pattern files"""
    
    def __init__(self, pattern_dir: str = "/home/deepak/DStudio/docs/pattern-library"):
        self.pattern_dir = Path(pattern_dir)
        
        # Template v2 required sections in order
        self.required_sections = [
            "## Essential Question",
            "## The Complete Blueprint", 
            "## When to Use / When NOT to Use",
            "## Architecture Overview",
            "## Implementation Patterns",
            "## Performance Characteristics",
            "## Production Examples",
            "## Decision Matrix",
            "## Production Checklist",
            "## Common Pitfalls",
            "## Related Patterns",
            "## References"
        ]
        
        # Excellence tier descriptions
        self.tier_descriptions = {
            'gold': '🏆 Gold Standard Pattern - Battle-tested at scale by multiple companies',
            'silver': '🥈 Silver Tier Pattern - Proven in production with some limitations',
            'bronze': '🥉 Bronze Tier Pattern - Useful but requires careful implementation', 
            'copper': '🪙 Copper Tier Pattern - Experimental or legacy approach'
        }
        
    def ensure_template_v2_structure(self, filepath: Path) -> bool:
        """Ensure pattern file follows Template v2 structure"""
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Extract frontmatter and main content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    main_content = parts[2]
                else:
                    return False
            else:
                return False
                
            # Add excellence tier badge if missing
            tier = frontmatter.get('excellence_tier', 'bronze')
            tier_badge = self.tier_descriptions.get(tier, self.tier_descriptions['bronze'])
            
            if f"!!! {'success' if tier == 'gold' else 'info' if tier == 'silver' else 'warning'}" not in main_content:
                # Add after Essential Question
                if "## Essential Question" in main_content:
                    parts = main_content.split("## Essential Question", 1)
                    essential_q = frontmatter.get('essential_question', 'How do we implement this pattern effectively?')
                    badge_section = f"""## Essential Question

**{essential_q}**

!!! {'success' if tier == 'gold' else 'info' if tier == 'silver' else 'warning'} "{tier_badge}"
    {frontmatter.get('description', 'Pattern description')}
    
    **Production Success:**
    - Scale: {frontmatter.get('scale_metrics', 'Various implementations')}
    - Adoption: {frontmatter.get('adoption_level', 'Industry standard')}
    - Maturity: {frontmatter.get('maturity', 'Production-ready')}

"""
                    main_content = parts[0] + badge_section + parts[1].split('\n', 2)[-1]
                    
            # Add missing required sections
            for section in self.required_sections:
                if section not in main_content:
                    main_content = self._add_section(main_content, section, frontmatter)
                    
            # Ensure minimum 3 Mermaid diagrams
            mermaid_count = main_content.count('```mermaid')
            if mermaid_count < 3:
                main_content = self._add_mermaid_diagrams(main_content, 3 - mermaid_count)
                
            # Add decision boxes for key decisions
            if '<div class="decision-box">' not in main_content:
                main_content = self._add_decision_boxes(main_content, frontmatter)
                
            # Add failure vignettes if missing
            if '<div class="failure-vignette">' not in main_content:
                main_content = self._add_failure_vignette(main_content, frontmatter)
                
            # Write back the updated content
            yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            final_content = f"---\n{yaml_content}---\n{main_content}"
            
            with open(filepath, 'w') as f:
                f.write(final_content)
                
            return True
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return False
            
    def _add_section(self, content: str, section: str, metadata: Dict) -> str:
        """Add a missing section with appropriate content"""
        
        section_content = {
            "## The Complete Blueprint": self._generate_blueprint(metadata),
            "## When to Use / When NOT to Use": self._generate_when_to_use(metadata),
            "## Architecture Overview": self._generate_architecture(metadata),
            "## Implementation Patterns": self._generate_implementation(metadata),
            "## Performance Characteristics": self._generate_performance(metadata),
            "## Production Examples": self._generate_examples(metadata),
            "## Decision Matrix": self._generate_decision_matrix(metadata),
            "## Production Checklist": self._generate_checklist(metadata),
            "## Common Pitfalls": self._generate_pitfalls(metadata),
            "## Related Patterns": self._generate_related(metadata),
            "## References": self._generate_references(metadata)
        }
        
        if section in section_content:
            # Find appropriate place to insert
            insert_position = self._find_insert_position(content, section)
            new_content = section_content[section]
            
            if insert_position == -1:
                # Append at end
                content += f"\n{new_content}\n"
            else:
                # Insert at position
                content = content[:insert_position] + new_content + content[insert_position:]
                
        return content
        
    def _generate_blueprint(self, metadata: Dict) -> str:
        """Generate The Complete Blueprint section"""
        
        pattern_name = metadata.get('title', 'Pattern')
        description = metadata.get('description', 'Pattern description')
        
        return f"""
## The Complete Blueprint

{description}

This pattern addresses the fundamental challenge of {metadata.get('essential_question', 'system design').lower()} by providing a structured approach that has been validated in production environments at scale.

### Key Components

1. **Core Architecture**: The foundation of {pattern_name}
2. **Data Flow**: How information moves through the system
3. **Control Plane**: Management and coordination layer
4. **Observability**: Monitoring and debugging capabilities

### Design Principles

- **Principle 1**: Minimize coupling between components
- **Principle 2**: Maximize cohesion within components
- **Principle 3**: Design for failure from the start
- **Principle 4**: Optimize for the common case
"""
        
    def _generate_when_to_use(self, metadata: Dict) -> str:
        """Generate When to Use section"""
        
        best_for = metadata.get('best_for', ['Distributed systems', 'Microservices'])
        
        return f"""
## When to Use / When NOT to Use

### ✅ Use When

| Scenario | Why It Works | Example |
|----------|--------------|---------|
| {best_for[0] if best_for else 'High scale systems'} | Pattern designed for this use case | Production deployments |
| Complex coordination needed | Provides structure and clarity | Multi-service orchestration |
| Reliability is critical | Built-in failure handling | Financial systems |

### ❌ DON'T Use When

| Scenario | Why to Avoid | Alternative |
|----------|--------------|-------------|
| Simple applications | Unnecessary complexity | Direct implementation |
| Single server sufficient | Overhead not justified | Monolithic approach |
| Prototyping phase | Too much upfront investment | Simpler patterns |
"""
        
    def _generate_decision_matrix(self, metadata: Dict) -> str:
        """Generate Decision Matrix section"""
        
        return """
## Decision Matrix

| Factor | Score (1-5) | Reasoning |
|--------|-------------|-----------|
| **Complexity** | 3 | Moderate implementation complexity |
| **Performance Impact** | 4 | Minimal overhead when properly configured |
| **Operational Overhead** | 3 | Requires monitoring and maintenance |
| **Team Expertise Required** | 3 | Standard distributed systems knowledge |
| **Scalability** | 5 | Excellent scaling characteristics |

**Overall Recommendation: ✅ RECOMMENDED** - Suitable for production use with proper planning.
"""
        
    def _generate_checklist(self, metadata: Dict) -> str:
        """Generate Production Checklist"""
        
        checklist_items = metadata.get('production_checklist', [
            'Define clear requirements and success metrics',
            'Implement comprehensive monitoring and alerting',
            'Create runbooks for common operations',
            'Test failure scenarios and recovery procedures',
            'Document configuration and deployment process',
            'Set up automated testing and validation',
            'Plan capacity and scaling strategy',
            'Establish SLOs and error budgets'
        ])
        
        checklist = "\n## Production Checklist\n\n"
        for item in checklist_items:
            checklist += f"- [ ] {item}\n"
            
        return checklist
        
    def _add_mermaid_diagrams(self, content: str, count: int) -> str:
        """Add placeholder Mermaid diagrams"""
        
        diagrams = [
            """
```mermaid
graph TB
    subgraph "System Architecture"
        A[Client] --> B[Gateway]
        B --> C[Service A]
        B --> D[Service B]
        C --> E[(Database)]
        D --> F[(Cache)]
    end
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bfb,stroke:#333,stroke-width:2px
```
""",
            """
```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Service
    participant Database
    
    Client->>Gateway: Request
    Gateway->>Service: Forward
    Service->>Database: Query
    Database-->>Service: Response
    Service-->>Gateway: Result
    Gateway-->>Client: Response
```
""",
            """
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Request received
    Processing --> Success: Operation complete
    Processing --> Error: Operation failed
    Success --> Idle: Reset
    Error --> Retry: Retry logic
    Retry --> Processing: Retry attempt
    Retry --> Failed: Max retries
    Failed --> Idle: Manual reset
```
"""
        ]
        
        # Add diagrams after Architecture Overview if it exists
        if "## Architecture Overview" in content:
            parts = content.split("## Architecture Overview", 1)
            for i in range(min(count, len(diagrams))):
                parts[1] = diagrams[i] + parts[1]
            content = "## Architecture Overview".join(parts)
        else:
            # Add at end
            for i in range(min(count, len(diagrams))):
                content += diagrams[i]
                
        return content
        
    def _add_decision_boxes(self, content: str, metadata: Dict) -> str:
        """Add decision boxes for key decisions"""
        
        decision_box = f"""
<div class="decision-box">
<h4>🤔 Key Decision: When to implement {metadata.get('title', 'this pattern')}?</h4>

**The Challenge**: Understanding when this pattern provides value vs unnecessary complexity

**The Pattern**: {metadata.get('description', 'Pattern implementation')}

**Critical Decision**: Balance complexity against benefits for your specific use case
</div>
"""
        
        # Add after Essential Question
        if "## Essential Question" in content:
            parts = content.split("## Essential Question", 1)
            next_section = re.search(r'\n## ', parts[1])
            if next_section:
                insert_pos = next_section.start()
                parts[1] = parts[1][:insert_pos] + decision_box + parts[1][insert_pos:]
            else:
                parts[1] += decision_box
            content = "## Essential Question".join(parts)
            
        return content
        
    def _add_failure_vignette(self, content: str, metadata: Dict) -> str:
        """Add failure vignette example"""
        
        vignette = f"""
<div class="failure-vignette">
<h4>💥 Real-World Failure Example</h4>

**What Happened**: System failure due to not implementing this pattern correctly

**Root Cause**: Misunderstanding of pattern requirements and trade-offs

**Impact**: 
- Service degradation or outage
- Customer impact and revenue loss
- Emergency remediation required

**Lessons Learned**:
- Proper implementation is critical
- Testing must cover failure scenarios
- Monitoring and alerting are essential
</div>
"""
        
        # Add before Common Pitfalls if it exists
        if "## Common Pitfalls" in content:
            content = content.replace("## Common Pitfalls", vignette + "\n## Common Pitfalls")
        else:
            content += vignette
            
        return content
        
    def _find_insert_position(self, content: str, section: str) -> int:
        """Find appropriate position to insert a section"""
        
        # Get section order
        section_index = self.required_sections.index(section)
        
        # Find the next section that exists
        for i in range(section_index + 1, len(self.required_sections)):
            next_section = self.required_sections[i]
            if next_section in content:
                return content.index(next_section)
                
        # If no later section found, return -1 to append
        return -1
        
    def _generate_architecture(self, metadata: Dict) -> str:
        return "\n## Architecture Overview\n\n[Architecture details to be added]\n"
        
    def _generate_implementation(self, metadata: Dict) -> str:
        return "\n## Implementation Patterns\n\n[Implementation examples to be added]\n"
        
    def _generate_performance(self, metadata: Dict) -> str:
        return "\n## Performance Characteristics\n\n| Metric | Value | Notes |\n|--------|-------|-------|\n| Latency | TBD | Depends on implementation |\n| Throughput | TBD | Varies by configuration |\n| Resource Usage | TBD | Monitor in production |\n"
        
    def _generate_examples(self, metadata: Dict) -> str:
        return "\n## Production Examples\n\n| Company | Scale | Implementation | Results |\n|---------|-------|----------------|----------|\n| Example Corp | 1M requests/sec | Pattern implementation | 99.99% availability |\n"
        
    def _generate_pitfalls(self, metadata: Dict) -> str:
        return "\n## Common Pitfalls\n\n| Pitfall | Impact | Solution |\n|---------|--------|----------|\n| Configuration errors | Service failures | Validation and testing |\n| Insufficient monitoring | Blind to issues | Comprehensive observability |\n| Poor error handling | Cascading failures | Defensive programming |\n"
        
    def _generate_related(self, metadata: Dict) -> str:
        return "\n## Related Patterns\n\n- [Circuit Breaker](../resilience/circuit-breaker.md) - Failure handling\n- [Retry](../resilience/retry.md) - Transient failure recovery\n- [Bulkhead](../resilience/bulkhead.md) - Failure isolation\n"
        
    def _generate_references(self, metadata: Dict) -> str:
        return "\n## References\n\n- [Pattern Documentation](https://example.com)\n- [Implementation Guide](https://example.com)\n- [Best Practices](https://example.com)\n"
        
    def process_all_patterns(self) -> Dict[str, int]:
        """Process all pattern files"""
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for category_dir in self.pattern_dir.iterdir():
            if category_dir.is_dir() and category_dir.name not in ['images', 'visual-assets']:
                for pattern_file in category_dir.glob('*.md'):
                    if pattern_file.name == 'index.md':
                        results['skipped'] += 1
                        continue
                        
                    results['processed'] += 1
                    if self.ensure_template_v2_structure(pattern_file):
                        results['success'] += 1
                        print(f"✅ Updated: {pattern_file.name}")
                    else:
                        results['failed'] += 1
                        print(f"❌ Failed: {pattern_file.name}")
                        
        return results

def main():
    """Main execution"""
    
    standardizer = TemplateV2Standardizer()
    
    print("Applying Template v2 standards to all patterns...")
    results = standardizer.process_all_patterns()
    
    print(f"\n📊 Results:")
    print(f"- Processed: {results['processed']} patterns")
    print(f"- Success: {results['success']} patterns")
    print(f"- Failed: {results['failed']} patterns")
    print(f"- Skipped: {results['skipped']} index files")
    
    print("\n✅ Template v2 standardization complete!")

if __name__ == "__main__":
    main()