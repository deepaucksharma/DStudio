#!/usr/bin/env python3
"""
Get list of pages with broken links and their counts
"""

import subprocess
import re
from collections import defaultdict

# Run verify-links script
result = subprocess.run(
    ['python3', 'scripts/verify-links.py'],
    capture_output=True,
    text=True
)

# Parse stderr output
pages = defaultdict(int)
current_file = None

for line in result.stderr.split('\n'):
    if line and line.endswith('.md:'):
        current_file = line[:-1]
    elif current_file and '  Line ' in line and '->' in line:
        pages[current_file] += 1

# Sort by issue count
sorted_pages = sorted(pages.items(), key=lambda x: x[1], reverse=True)

# Print top 50 pages
print("Top 50 pages with broken links:")
print("="*80)

for i, (page, count) in enumerate(sorted_pages[:50]):
    page_short = page.replace('docs/', '')
    print(f"{i+1:3d}. {page_short:<60} {count:4d} issues")

print(f"\nTotal pages with issues: {len(pages)}")
print(f"Total broken links: {sum(pages.values())}")