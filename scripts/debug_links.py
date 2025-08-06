#!/usr/bin/env python3
"""Debug specific link issues"""

import sqlite3
from pathlib import Path

conn = sqlite3.connect("knowledge_graph_ultimate.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("DEBUGGING LINK ISSUES")
print("=" * 60)

# Check a specific broken link pattern
print("\nSample broken '../../core-principles/laws/asynchronous-reality.md' links:")
cursor.execute("""
    SELECT src_page, dst_url, dst_page, is_valid
    FROM links
    WHERE dst_url = '../../core-principles/laws/asynchronous-reality.md'
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"\nSource: {row['src_page']}")
    print(f"  Original link: {row['dst_url']}")
    print(f"  Normalized to: {row['dst_page']}")
    print(f"  Valid: {row['is_valid']}")
    
    # Check if the file actually exists
    expected_files = [
        f"docs/{row['dst_page']}.md",
        f"docs/{row['dst_page']}/index.md",
    ]
    
    for f in expected_files:
        if Path(f).exists():
            print(f"  ✓ File exists: {f}")
            break
    else:
        print(f"  ✗ No file found at expected locations")

# Check what files actually exist for core-principles/laws
print("\n" + "-" * 40)
print("Files in core-principles/laws/:")
laws_path = Path("docs/core-principles/laws")
if laws_path.exists():
    for f in laws_path.glob("*.md"):
        print(f"  - {f.name}")

# Check a page that should have these links
print("\n" + "-" * 40)
print("Checking pattern-library pages that link to laws:")

cursor.execute("""
    SELECT DISTINCT src_page
    FROM links
    WHERE src_page LIKE 'pattern-library/%'
    AND dst_url LIKE '%core-principles/laws/%'
    LIMIT 3
""")

for row in cursor.fetchall():
    print(f"\n{row['src_page']}:")
    
    # Get all law links from this page
    cursor.execute("""
        SELECT dst_url, dst_page, is_valid
        FROM links
        WHERE src_page = ?
        AND dst_url LIKE '%laws/%'
    """, (row['src_page'],))
    
    for link in cursor.fetchall():
        status = "✓" if link['is_valid'] else "✗"
        print(f"  {status} {link['dst_url']} -> {link['dst_page']}")

conn.close()