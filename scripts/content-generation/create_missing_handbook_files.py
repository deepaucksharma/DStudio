#\!/usr/bin/env python3
"""Create missing architects handbook files"""

from pathlib import Path

def create_handbook_file(base_dir: Path, path: str, title: str, description: str):
    """Create a handbook file"""
    file_path = base_dir / 'docs' / 'architects-handbook' / path
    
    if file_path.exists():
        return False
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine the type of content based on path
    if 'tools' in path:
        content = f"""---
title: {title}
description: {description}
---

# {title}

{description}

## Tool Overview

This tool helps architects calculate and optimize {title.lower()}.

## How to Use

1. **Input Parameters**
   - Parameter 1: Description
   - Parameter 2: Description

2. **Calculations**
   - Formula or method used

3. **Output**
   - Result interpretation

## Example Scenarios

### Scenario 1
- Input: Values
- Output: Results

### Scenario 2
- Input: Values
- Output: Results

## Best Practices

- Tip 1
- Tip 2
- Tip 3
"""
    elif 'quantitative-analysis' in path:
        content = f"""---
title: {title}
description: {description}
---

# {title}

{description}

## Mathematical Foundation

### Formula

Mathematical formula or theorem

### Key Variables

- Variable 1: Description
- Variable 2: Description

## Application to Distributed Systems

How this applies to system design

## Examples

### Example 1
Detailed example

### Example 2
Detailed example

## Common Pitfalls

- Pitfall 1
- Pitfall 2
"""
    else:
        content = f"""---
title: {title}
description: {description}
---

# {title}

{description}

## Overview

Comprehensive overview of {title.lower()}.

## Key Concepts

1. **Concept 1**: Description
2. **Concept 2**: Description
3. **Concept 3**: Description

## Implementation

### Step 1: Planning
Details

### Step 2: Execution
Details

### Step 3: Validation
Details

## Best Practices

- Practice 1
- Practice 2
- Practice 3

## Case Studies

### Case Study 1
Description

### Case Study 2
Description

## Resources

- Resource 1
- Resource 2
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: architects-handbook/{path}")
    return True

def main():
    base_dir = Path('/home/deepak/DStudio')
    
    handbook_files = [
        ('tools/capacity-calculator.md', 'Capacity Calculator', 'Calculate system capacity requirements'),
        ('tools/throughput-calculator.md', 'Throughput Calculator', 'Estimate system throughput'),
        ('tools/cost-optimizer.md', 'Cost Optimizer', 'Optimize cloud infrastructure costs'),
        ('tools/consistency-calculator.md', 'Consistency Calculator', 'Analyze consistency guarantees'),
        ('quantitative-analysis/queueing-models.md', 'Queueing Models', 'Mathematical models for system queues'),
    ]
    
    created_count = 0
    for path, title, desc in handbook_files:
        if create_handbook_file(base_dir, path, title, desc):
            created_count += 1
    
    print(f"\nTotal handbook files created: {created_count}")

if __name__ == '__main__':
    main()
