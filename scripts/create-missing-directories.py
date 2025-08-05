#!/usr/bin/env python3
"""Create missing directories and index files for MkDocs."""

from pathlib import Path

def main():
    """Create missing directories that are referenced in links."""
    docs_dir = Path("docs")
    
    # Critical missing directories based on common broken links
    missing_dirs = [
        "company-specific",
        "company-specific/amazon",
        "company-specific/google",
        "company-specific/meta",
        "company-specific/apple",
        "company-specific/microsoft",
        "company-specific/netflix",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/story-portfolio",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/interview-timer",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/self-assessment",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/decision-trees",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/star-matcher",
        "interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/question-bank",
        "interview-prep/engineering-leadership/level-3-applications/technical-leadership/technical-strategy",
        "interview-prep/engineering-leadership/level-3-applications/people-management/hiring-interviewing",
        "interview-prep/engineering-leadership/level-3-applications/people-management/team-building-culture",
        "interview-prep/engineering-leadership/level-3-applications/organizational-design/team-topologies",
        "interview-prep/engineering-leadership/level-3-applications/business-acumen/business-metrics",
        "interview-prep/engineering-leadership/practice-scenarios/team-conflict-scenario",
        "interview-prep/engineering-leadership/practice-scenarios/underperformer-scenario",
        "interview-prep/engineering-leadership/practice-scenarios/stakeholder-negotiation-scenario",
        "interview-prep/engineering-leadership/company-specific/amazon",
        "interview-prep/engineering-leadership/company-specific/google",
        "interview-prep/engineering-leadership/company-specific/meta",
        "interview-prep/engineering-leadership/company-specific/apple",
        "interview-prep/engineering-leadership/company-specific/microsoft",
        "interview-prep/engineering-leadership/company-specific/netflix",
        "interview-prep/ic-interviews/cheatsheets/system-design-checklist",
    ]
    
    created_count = 0
    
    for dir_path in missing_dirs:
        full_path = docs_dir / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Create index.md
            index_file = full_path / "index.md"
            if not index_file.exists():
                # Generate appropriate title
                title = dir_path.split('/')[-1].replace('-', ' ').title()
                
                # Special handling for company names
                if title in ['Amazon', 'Google', 'Meta', 'Apple', 'Microsoft', 'Netflix']:
                    content = f"""# {title} Interview Guide

> **Note**: This company-specific guide is under construction.

## Overview

This guide will provide detailed insights into {title}'s engineering leadership interview process.

## Coming Soon

- Leadership principles and culture
- Interview format and structure
- Example questions and scenarios
- Preparation tips specific to {title}

---

**Related Resources:**
- [Engineering Leadership Framework](/interview-prep/engineering-leadership/)
- [Interview Execution Guide](/interview-prep/engineering-leadership/level-4-interview-execution/)
- [Practice Scenarios](/interview-prep/engineering-leadership/practice-scenarios/)
"""
                elif 'tools/interactive' in dir_path:
                    tool_name = title
                    content = f"""# {tool_name}

> **Note**: This interactive tool is under development.

## Overview

The {tool_name} tool will help you practice and prepare for engineering leadership interviews.

## Features (Coming Soon)

- Interactive practice interface
- Real-time feedback
- Progress tracking
- Customizable scenarios

---

**Related Tools:**
- [All Interactive Tools](/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/)
- [STAR Framework](/interview-prep/engineering-leadership/level-4-interview-execution/tools/star-framework/)
- [Practice Scenarios](/interview-prep/engineering-leadership/practice-scenarios/)
"""
                else:
                    content = f"""# {title}

> **Note**: This section is under construction.

## Overview

This page will provide comprehensive coverage of {title.lower()}.

## Topics to be Covered

- Core concepts and principles
- Best practices and frameworks
- Real-world examples
- Implementation guides

## Coming Soon

Check back soon for detailed content on this topic.

---

**Related Resources:**
- [Engineering Leadership Home](/interview-prep/engineering-leadership/)
- [Framework Overview](/interview-prep/engineering-leadership/framework-index/)
"""
                
                index_file.write_text(content)
                print(f"Created: {index_file.relative_to(docs_dir)}")
                created_count += 1
    
    print(f"\nTotal directories and index files created: {created_count}")

if __name__ == "__main__":
    main()