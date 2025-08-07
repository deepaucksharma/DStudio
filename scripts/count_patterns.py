#!/usr/bin/env python3
"""Count patterns in the library by category"""

from pathlib import Path
import json

pattern_dir = Path("/home/deepak/DStudio/docs/pattern-library")
categories = {}
total_patterns = 0

for category_dir in pattern_dir.iterdir():
    if category_dir.is_dir() and category_dir.name not in ['visual-assets', 'images']:
        patterns = []
        for pattern_file in category_dir.glob("*.md"):
            if pattern_file.name != "index.md":
                patterns.append(pattern_file.name)
                total_patterns += 1
        if patterns:
            categories[category_dir.name] = {
                'count': len(patterns),
                'patterns': sorted(patterns)
            }

# Sort categories by count
sorted_categories = dict(sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True))

print(f"Total patterns: {total_patterns}\n")
print("Patterns by category:")
for cat, info in sorted_categories.items():
    print(f"  {cat}: {info['count']} patterns")

# Save detailed info
with open('/home/deepak/DStudio/pattern_count_audit.json', 'w') as f:
    json.dump({
        'total': total_patterns,
        'categories': sorted_categories
    }, f, indent=2)

print(f"\nDetailed audit saved to pattern_count_audit.json")