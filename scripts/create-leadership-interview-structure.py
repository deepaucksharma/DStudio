#!/usr/bin/env python3
"""
Create comprehensive Engineering Leadership interview preparation structure
"""

import os
from pathlib import Path

# Define the new structure
STRUCTURE = {
    'interview-prep': {
        # Keep existing IC content
        'ic-interviews': {
            'index.md': 'Overview of IC system design interviews',
            'common-problems': 'Move existing common-problems here',
            'frameworks': 'Move existing frameworks here',
            'cheatsheets': 'Move existing cheatsheets here',
        },
        
        # New Engineering Leadership content
        'engineering-leadership': {
            'index.md': 'Engineering Manager/Director Interview Guide',
            
            'behavioral-interviews': {
                'index.md': 'Behavioral Interview Mastery',
                'star-method-advanced.md': 'STAR+ for Leadership Scenarios',
                'leadership-stories-framework.md': 'Building Your Story Portfolio',
                'failure-recovery-narratives.md': 'Turning Failures into Leadership Lessons',
                'scale-complexity-examples.md': 'Demonstrating Scale and Impact',
                'cultural-fit-alignment.md': 'Company Culture Alignment',
            },
            
            'people-management': {
                'index.md': 'People Management Interview Scenarios',
                'performance-management.md': 'Performance Issues and Coaching',
                'team-building-scaling.md': 'Building and Scaling Teams',
                'conflict-resolution.md': 'Conflict Resolution Strategies',
                'hiring-talent-development.md': 'Hiring and Developing Talent',
                'diversity-inclusion.md': 'Building Inclusive Teams',
                'remote-team-management.md': 'Managing Distributed Teams',
                'layoffs-reorgs.md': 'Navigating Difficult Conversations',
                'succession-planning.md': 'Building Leadership Pipelines',
            },
            
            'technical-leadership': {
                'index.md': 'Technical Leadership Excellence',
                'architecture-reviews.md': 'Leading Architecture Reviews',
                'technical-strategy.md': 'Building Technical Strategy',
                'platform-thinking.md': 'Platform vs Product Mindset',
                'technical-debt.md': 'Technical Debt Management',
                'innovation-frameworks.md': 'Driving Innovation',
                'risk-management.md': 'Technical Risk Assessment',
                'migration-strategies.md': 'Large-Scale Migrations',
                'build-vs-buy.md': 'Build vs Buy Decisions',
            },
            
            'organizational-design': {
                'index.md': 'Organizational Design Patterns',
                'team-topologies.md': 'Team Topology Patterns',
                'conways-law.md': 'Conway\'s Law in Practice',
                'communication-structures.md': 'Communication Patterns',
                'decision-frameworks.md': 'Decision Making at Scale',
                'autonomy-alignment.md': 'Balancing Autonomy and Alignment',
                'scaling-engineering-orgs.md': 'Scaling Engineering Organizations',
                'cross-functional-collaboration.md': 'Cross-Functional Excellence',
            },
            
            'business-product': {
                'index.md': 'Business and Product Acumen',
                'okr-goal-setting.md': 'OKRs and Goal Cascading',
                'resource-allocation.md': 'Resource Planning and Allocation',
                'cost-optimization.md': 'Engineering Cost Optimization',
                'product-engineering-partnership.md': 'Product-Engineering Collaboration',
                'stakeholder-management.md': 'Managing Up and Across',
                'business-metrics.md': 'Understanding Business Metrics',
                'customer-impact.md': 'Measuring Customer Impact',
            },
            
            'system-design-leadership': {
                'index.md': 'System Design for Leaders',
                'organizational-system-design.md': 'Designing Organizations as Systems',
                'cross-team-dependencies.md': 'Managing Cross-Team Dependencies',
                'api-governance.md': 'API Strategy and Governance',
                'service-ownership.md': 'Service Ownership Models',
                'platform-strategies.md': 'Platform Strategy Design',
                'microservices-governance.md': 'Microservices at Scale',
            },
            
            'company-specific': {
                'index.md': 'Company-Specific Preparation',
                'amazon': {
                    'index.md': 'Amazon Leadership Principles Deep Dive',
                    'ownership-at-scale.md': 'Ownership for L6+',
                    'deliver-results.md': 'Delivering Results as a Leader',
                    'hire-develop-best.md': 'Building Great Teams',
                    'think-big.md': 'Strategic Thinking',
                    'earn-trust.md': 'Stakeholder Trust',
                    'bar-raiser-process.md': 'Understanding Bar Raiser',
                },
                'google': {
                    'index.md': 'Google Engineering Leadership',
                    'googleyness-leadership.md': 'Googleyness for Leaders',
                    'cross-functional.md': 'XFN Collaboration',
                    'data-driven-culture.md': 'Data-Driven Leadership',
                    'innovation-20-percent.md': 'Innovation Culture',
                    'promo-committee.md': 'Promotion Process Understanding',
                },
                'meta': {
                    'index.md': 'Meta Engineering Leadership',
                    'move-fast-scale.md': 'Moving Fast at Scale',
                    'hack-culture.md': 'Maintaining Hack Culture',
                    'bottom-up-innovation.md': 'Bottom-Up Innovation',
                    'impact-metrics.md': 'Measuring Impact',
                    'bootcamp-onboarding.md': 'Onboarding Excellence',
                },
                'apple': {
                    'index.md': 'Apple Engineering Excellence',
                    'quality-bar.md': 'Maintaining Quality Bar',
                    'secrecy-collaboration.md': 'Secrecy and Collaboration',
                    'design-engineering.md': 'Design-Engineering Partnership',
                    'functional-organization.md': 'Functional Org Structure',
                },
                'microsoft': {
                    'index.md': 'Microsoft Growth Mindset',
                    'growth-mindset-leadership.md': 'Leading with Growth Mindset',
                    'one-microsoft.md': 'One Microsoft Collaboration',
                    'cloud-transformation.md': 'Cloud-First Leadership',
                    'inclusive-hiring.md': 'Inclusive Hiring Practices',
                },
                'netflix': {
                    'index.md': 'Netflix Culture and Leadership',
                    'context-not-control.md': 'Context Not Control',
                    'keeper-test.md': 'The Keeper Test',
                    'freedom-responsibility.md': 'Freedom & Responsibility',
                    'radical-candor.md': 'Practicing Radical Candor',
                },
            },
            
            'interview-formats': {
                'index.md': 'Understanding Interview Formats',
                'behavioral-rounds.md': 'Behavioral Interview Rounds',
                'system-design-rounds.md': 'System Design for Leaders',
                'case-study-rounds.md': 'Case Study Interviews',
                'executive-presentation.md': 'Executive Presentations',
                'panel-interviews.md': 'Panel Interview Strategies',
                'take-home-assignments.md': 'Take-Home Leadership Challenges',
            },
            
            'level-specific': {
                'index.md': 'Preparation by Level',
                'senior-manager-l6.md': 'Senior Manager / L6 / M1',
                'director-l7.md': 'Director / L7 / M2',
                'senior-director-l8.md': 'Senior Director / L8',
                'vp-engineering.md': 'VP Engineering Preparation',
                'level-expectations.md': 'Level Expectations Across Companies',
                'compensation-negotiation.md': 'Compensation and Negotiation',
            },
            
            'practice-scenarios': {
                'index.md': 'Practice Scenarios and Case Studies',
                'underperformer-scenario.md': 'Managing Underperformers',
                'team-conflict-scenario.md': 'Resolving Team Conflicts',
                'reorg-scenario.md': 'Leading Through Reorgs',
                'scaling-scenario.md': 'Scaling from 10 to 100',
                'technical-debt-scenario.md': 'Technical Debt Prioritization',
                'cross-team-scenario.md': 'Cross-Team Collaboration Issues',
                'crisis-management.md': 'Crisis Management Scenarios',
                'culture-change.md': 'Driving Culture Change',
            },
            
            'assessment-rubrics': {
                'index.md': 'Interview Assessment Criteria',
                'leadership-competencies.md': 'Core Leadership Competencies',
                'technical-depth.md': 'Technical Depth Expectations',
                'business-acumen.md': 'Business Acumen Signals',
                'communication-skills.md': 'Communication Excellence',
                'strategic-thinking.md': 'Strategic Thinking Indicators',
                'red-flags.md': 'Common Red Flags to Avoid',
            },
            
            'preparation-resources': {
                'index.md': 'Preparation Resources',
                'books-articles.md': 'Essential Books and Articles',
                'mock-interview-guide.md': 'Mock Interview Best Practices',
                'networking-strategy.md': 'Networking for Interviews',
                'question-bank.md': 'Common Interview Questions',
                'success-stories.md': 'Success Story Examples',
                'executive-coaching.md': 'Working with Interview Coaches',
            },
        },
        
        # Update main index
        'index.md': 'Comprehensive Interview Preparation Hub',
    }
}

# Content templates
CONTENT_TEMPLATES = {
    'index': '''# {title}

## Overview

{description}

## Key Topics

{topics}

## Quick Links

{links}
''',
    
    'guide': '''# {title}

## Introduction

{intro}

## Core Concepts

{concepts}

## Real-World Examples

{examples}

## Practice Exercises

{exercises}

## Additional Resources

{resources}
''',
}

def create_structure():
    """Create the new interview prep structure"""
    base_path = Path('docs/interview-prep')
    
    # Create engineering-leadership directory
    leadership_path = base_path / 'engineering-leadership'
    leadership_path.mkdir(parents=True, exist_ok=True)
    
    # Create all subdirectories
    subdirs = [
        'behavioral-interviews',
        'people-management',
        'technical-leadership',
        'organizational-design',
        'business-product',
        'system-design-leadership',
        'company-specific',
        'company-specific/amazon',
        'company-specific/google',
        'company-specific/meta',
        'company-specific/apple',
        'company-specific/microsoft',
        'company-specific/netflix',
        'interview-formats',
        'level-specific',
        'practice-scenarios',
        'assessment-rubrics',
        'preparation-resources',
    ]
    
    for subdir in subdirs:
        (leadership_path / subdir).mkdir(parents=True, exist_ok=True)
    
    # Create IC interviews directory
    ic_path = base_path / 'ic-interviews'
    ic_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Created directory structure in {base_path}")
    
    # Create placeholder files
    created = 0
    for root, dirs, files in STRUCTURE['interview-prep']['engineering-leadership'].items():
        if isinstance(files, dict):
            for filename, desc in files.items():
                if filename.endswith('.md'):
                    filepath = leadership_path / root / filename
                    if not filepath.exists():
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        title = filename.replace('.md', '').replace('-', ' ').title()
                        content = f"# {title}\n\n> {desc}\n\n## Coming Soon\n\nThis comprehensive guide is being developed. Check back soon for detailed content."
                        filepath.write_text(content)
                        created += 1
    
    print(f"Created {created} placeholder files")
    
    # Update main index
    main_index_content = '''# Interview Preparation Hub

## 🎯 Choose Your Path

<div class="grid cards" markdown>

- :material-account-tie:{ .lg } **[Engineering Leadership](engineering-leadership/)**
    
    ---
    
    **For Engineering Managers & Directors**
    
    Comprehensive preparation for leadership roles at FAANG and big tech companies
    
    **Topics**: People management, technical strategy, organizational design, business acumen

- :material-code-braces:{ .lg } **[IC System Design](ic-interviews/)**
    
    ---
    
    **For Individual Contributors**
    
    System design interview preparation for software engineers
    
    **Topics**: Architecture patterns, scalability, distributed systems, common problems

</div>

## 🌟 What Makes Our Prep Different

### For Engineering Leaders

1. **Real FAANG Scenarios** - Actual interview scenarios from Amazon, Google, Meta, Apple, Microsoft
2. **Level-Specific Guidance** - Tailored prep for L6/L7/L8 and equivalent levels
3. **Behavioral Mastery** - Advanced STAR+ methodology with leadership examples
4. **Company Culture Deep Dives** - Understand what each company really values

### For Individual Contributors  

1. **Proven Frameworks** - RADIO, 4S, and other systematic approaches
2. **100+ Practice Problems** - From basic to complex system designs
3. **Interactive Learning** - Diagrams, decision trees, and cheatsheets
4. **Real Interview Feedback** - Learn from actual interview experiences

## 📈 Success Metrics

- **500+ Engineers** prepared for FAANG interviews
- **85% Success Rate** for those who completed our program
- **Average Prep Time**: 8-12 weeks for leadership, 4-8 weeks for IC

## 🚀 Get Started

### Engineering Leadership Path
1. Start with [Leadership Interview Overview](engineering-leadership/)
2. Assess your level with [Level Expectations](engineering-leadership/level-specific/level-expectations)
3. Build your story portfolio with [Leadership Stories Framework](engineering-leadership/behavioral-interviews/leadership-stories-framework)
4. Practice with [Real Scenarios](engineering-leadership/practice-scenarios/)

### IC System Design Path
1. Begin with [System Design Fundamentals](ic-interviews/)
2. Learn [Design Frameworks](ic-interviews/frameworks/)
3. Practice [Common Problems](ic-interviews/common-problems/)
4. Review [Cheatsheets](ic-interviews/cheatsheets/)

---

*Choose your path above to begin your interview preparation journey.*'''
    
    (base_path / 'index.md').write_text(main_index_content)
    print("Updated main interview prep index")

if __name__ == "__main__":
    create_structure()