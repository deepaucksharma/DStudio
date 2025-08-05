#!/usr/bin/env python3
"""Add missing pattern redirects to mkdocs.yml"""

import yaml
import re

# Read all pattern URLs from the JavaScript file
with open('/home/deepak/DStudio/docs/javascripts/pattern-filtering.js', 'r') as f:
    js_content = f.read()

# Extract all pattern URLs
pattern_urls = re.findall(r'url: "/DStudio/pattern-library/([^"]+)"', js_content)
# Remove trailing slashes and make unique
pattern_urls = sorted(set(url.rstrip('/') for url in pattern_urls))

# Create redirect mappings
redirects = []
for url in pattern_urls:
    # Create the old pattern URL and new pattern-library URL
    pattern_name = url.split('/')[-1]
    old_url = f"patterns/{pattern_name}.md"
    new_url = f"pattern-library/{url}.md"
    redirects.append(f"      {old_url}: {new_url}")

# Read mkdocs.yml
with open('/home/deepak/DStudio/mkdocs.yml', 'r') as f:
    content = f.read()

# Find the redirect section
redirect_start = content.find('- redirects:\n    redirect_maps:')
if redirect_start == -1:
    print("Could not find redirect section!")
    exit(1)

# Find where to insert (after the existing pattern redirects)
insert_pos = content.find('      patterns/chaos-engineering.md:')
if insert_pos == -1:
    print("Could not find insertion point!")
    exit(1)

# Find the end of that line
line_end = content.find('\n', insert_pos)
if line_end == -1:
    line_end = len(content)

# Insert all the new redirects
new_redirects = "\n" + "\n".join(redirects)
new_content = content[:line_end + 1] + new_redirects + content[line_end + 1:]

# Write back
with open('/home/deepak/DStudio/mkdocs.yml', 'w') as f:
    f.write(new_content)

print(f"Added {len(redirects)} pattern redirects to mkdocs.yml")