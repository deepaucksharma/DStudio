#!/usr/bin/env python3
"""Check for category mismatches between folder and metadata."""

import os
import re

mismatches = []

for root, dirs, files in os.walk('docs/pattern-library'):
    for file in files:
        if file.endswith('.md') and file != 'index.md' and not file.startswith('pattern-'):
            file_path = os.path.join(root, file)
            folder_category = os.path.basename(os.path.dirname(file_path))
            
            # Extract category from file
            with open(file_path, 'r') as f:
                content = f.read()
                match = re.search(r'^category:\s*(.+)$', content, re.MULTILINE)
                if match:
                    file_category = match.group(1).strip()
                    if file_category != folder_category:
                        mismatches.append(f'{file}: folder={folder_category}, metadata={file_category}')

print(f'Found {len(mismatches)} category mismatches:')
for m in sorted(mismatches):
    print(f'  {m}')