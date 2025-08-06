#\!/usr/bin/env python3
"""Fix learning path references and create missing files"""

from pathlib import Path

def create_learning_path(base_dir: Path, filename: str, title: str, description: str):
    """Create a learning path file"""
    file_path = base_dir / 'docs' / 'architects-handbook' / 'learning-paths' / filename
    
    if file_path.exists():
        return False
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
title: {title}
description: {description}
---

# {title}

{description}

## Prerequisites

- Foundation 1
- Foundation 2
- Foundation 3

## Learning Objectives

By completing this learning path, you will:

1. Understand core concepts
2. Apply patterns in practice
3. Build production systems

## Module 1: Foundations

### Topics Covered
- Topic 1
- Topic 2
- Topic 3

### Hands-on Labs
- Lab 1: Description
- Lab 2: Description

## Module 2: Advanced Concepts

### Topics Covered
- Advanced topic 1
- Advanced topic 2

### Projects
- Project 1: Build a sample system
- Project 2: Optimize performance

## Module 3: Real-world Applications

### Case Studies
- Case study 1
- Case study 2

### Capstone Project
Build a complete distributed system

## Resources

### Books
- Book 1
- Book 2

### Papers
- Paper 1
- Paper 2

### Tools
- Tool 1
- Tool 2

## Certification Path

Steps to validate your knowledge

## Next Steps

- Advanced path 1
- Advanced path 2
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {filename}")
    return True

def main():
    base_dir = Path('/home/deepak/DStudio')
    
    # Learning paths that might be missing
    learning_paths = [
        ('blockchain-systems.md', 'Blockchain Systems Architecture', 'Learn to design and build blockchain-based distributed systems'),
        ('data-engineer.md', 'Data Engineering Path', 'Master data pipelines and processing at scale'),
        ('devops-sre.md', 'DevOps & SRE Path', 'Site reliability and operations excellence'),
        ('edge-computing.md', 'Edge Computing Architecture', 'Design systems for edge and IoT'),
        ('ml-infrastructure.md', 'ML Infrastructure Path', 'Build scalable machine learning systems'),
        ('platform-engineer.md', 'Platform Engineering Path', 'Design and build developer platforms'),
        ('quantum-resilient.md', 'Quantum-Resilient Systems', 'Future-proof cryptographic systems'),
        ('real-time-systems.md', 'Real-Time Systems Path', 'Build low-latency real-time systems'),
        ('security-architect.md', 'Security Architecture Path', 'Design secure distributed systems'),
    ]
    
    created_count = 0
    for filename, title, desc in learning_paths:
        if create_learning_path(base_dir, filename, title, desc):
            created_count += 1
    
    # Also check if index exists
    index_path = base_dir / 'docs' / 'architects-handbook' / 'learning-paths' / 'index.md'
    if not index_path.exists():
        content = """---
title: Learning Paths
description: Structured learning paths for distributed systems mastery
---

# Learning Paths

Choose your path to distributed systems mastery.

## Available Paths

### Foundation Paths
- [Data Engineering](data-engineer/)
- [Platform Engineering](platform-engineer/)
- [DevOps & SRE](devops-sre/)

### Specialized Paths
- [Blockchain Systems](blockchain-systems/)
- [ML Infrastructure](ml-infrastructure/)
- [Edge Computing](edge-computing/)
- [Real-Time Systems](real-time-systems/)

### Advanced Paths
- [Security Architecture](security-architect/)
- [Quantum-Resilient Systems](quantum-resilient/)

## How to Use These Paths

1. **Choose Your Path**: Select based on your goals
2. **Follow the Modules**: Work through sequentially
3. **Complete Projects**: Apply what you learn
4. **Get Certified**: Validate your knowledge

## Prerequisites

Basic understanding of:
- Programming fundamentals
- Networking concepts
- Database basics
- System design principles
"""
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Created: learning-paths/index.md")
        created_count += 1
    
    print(f"\nTotal learning path files created: {created_count}")

if __name__ == '__main__':
    main()
