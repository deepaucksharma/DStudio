# Immediate YAML Fixes Required

**Generated**: 2025-07-20  
**Priority**: CRITICAL - These errors block MkDocs builds

## 🚨 Files Requiring Immediate YAML Fixes

### 1. part2-pillars/decision-tree.md
```yaml
# CURRENT (BROKEN):
description: "Mitigation:
- Read models for complex queries
- Archival strategy for old events
- Clear SLAs on consistency windows
```"

# FIXED:
description: "Interactive decision tree walkthrough for choosing distributed architectures based on requirements and constraints"
```

### 2. Pattern Files (Already Fixed in Previous Session)
✅ **COMPLETED**: caching-strategies.md, cdc.md, edge-computing.md, finops.md, geo-replication.md, graphql-federation.md, observability.md, saga.md, sharding.md, tunable-consistency.md

### 3. Empty/Missing Descriptions
**Files with empty description fields**:
- axiom1-latency/exercises.md
- Several other exercise files

**Quick Fix**:
```yaml
# CURRENT:
description: ""

# FIXED:
description: "Hands-on exercises and labs for understanding latency constraints in distributed systems"
```

## 🔍 Detection Script

```bash
#!/bin/bash
# find_yaml_issues.sh

echo "=== Files with potential multiline YAML issues ==="
grep -r "description: \"" docs/ | grep -v "\"$" | grep -v ".py:" | head -20

echo -e "\n=== Files with empty descriptions ==="
grep -r 'description: ""' docs/ | head -20

echo -e "\n=== Files with unclosed quotes ==="
grep -r 'description: "[^"]*$' docs/ | grep -v ".py:" | head -20

echo -e "\n=== Small files marked complete ==="
find docs -name "*.md" -exec grep -l "status: complete" {} \; | \
xargs wc -l | awk '$1 < 100 {print $2 " has only " $1 " lines"}' | sort -k5 -n
```

## ⚡ Quick Fix Script

```python
#!/usr/bin/env python3
# fix_yaml_frontmatter.py

import os
import re
import yaml

def fix_yaml_frontmatter(filepath):
    """Fix common YAML frontmatter issues"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "No valid frontmatter found"
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Fix multiline descriptions
    if 'description: "' in frontmatter and not re.search(r'description: "[^"]*"', frontmatter):
        # Extract the broken description
        desc_match = re.search(r'description: "(.*)', frontmatter, re.DOTALL)
        if desc_match:
            # Find the content up to the next field
            broken_desc = desc_match.group(1)
            next_field = re.search(r'\n\w+:', broken_desc)
            if next_field:
                actual_desc = broken_desc[:next_field.start()].strip()
                # Clean up the description
                actual_desc = re.sub(r'[\n\r]+', ' ', actual_desc)
                actual_desc = re.sub(r'["`]+$', '', actual_desc)
                actual_desc = actual_desc[:200]  # Truncate if too long
                
                # Create proper description
                new_desc = f'description: "{actual_desc}"'
                frontmatter = re.sub(r'description: ".*', new_desc, frontmatter, flags=re.DOTALL)
    
    # Fix empty descriptions
    frontmatter = re.sub(r'description: ""', 'description: "Documentation for distributed systems concepts"', frontmatter)
    
    # Reconstruct file
    new_content = f"---{frontmatter}---{body}"
    
    # Validate YAML
    try:
        yaml_content = yaml.safe_load(frontmatter)
        if yaml_content and isinstance(yaml_content.get('description'), str):
            with open(filepath, 'w') as f:
                f.write(new_content)
            return True, "Fixed successfully"
        else:
            return False, "YAML validation failed"
    except Exception as e:
        return False, f"YAML error: {e}"

# Run fixes
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        success, message = fix_yaml_frontmatter(filepath)
        print(f"{filepath}: {message}")
    else:
        print("Usage: python fix_yaml_frontmatter.py <file.md>")
```

## 📋 Manual Review Checklist

For each file with YAML issues:

1. **Check frontmatter boundaries**: Ensure `---` markers are correct
2. **Validate description field**: 
   - Must be on one line
   - Must be properly quoted
   - Must be meaningful (not empty)
3. **Update status if needed**:
   - If <100 lines: `status: stub`
   - If 100-300 lines: `status: in-progress`
   - If >300 lines with complete content: `status: complete`
4. **Add completion percentage** for non-complete files:
   ```yaml
   status: in-progress
   completion_percentage: 60
   ```

## ⚠️ Common Patterns to Fix

### Pattern 1: Multiline Description
```yaml
# WRONG:
description: "This is a long description that
spans multiple lines and breaks
YAML parsing"

# RIGHT:
description: "This is a long description that spans one line"
```

### Pattern 2: Unescaped Quotes
```yaml
# WRONG:
description: "Using "quotes" breaks parsing"

# RIGHT:
description: "Using 'quotes' works fine"
# OR:
description: "Using \"quotes\" with escaping"
```

### Pattern 3: Lists in Description
```yaml
# WRONG:
description: "Features:
- Feature 1
- Feature 2"

# RIGHT:
description: "Features include Feature 1 and Feature 2"
```

## 🎯 Action Items

1. **NOW**: Run detection script to find all issues
2. **TODAY**: Fix all YAML syntax errors
3. **TOMORROW**: Update all false "complete" statuses
4. **THIS WEEK**: Complete stub files with actual content

Remember: **Broken YAML = Broken builds = Broken user experience**

Fix these first before any other improvements!