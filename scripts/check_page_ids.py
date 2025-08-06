#!/usr/bin/env python3
"""Check how page IDs are stored vs how links resolve"""

import sqlite3

conn = sqlite3.connect("knowledge_graph_ultimate.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Checking page ID storage issues:")
print("=" * 60)

# Check how core-principles/laws pages are stored
print("\nPages in core-principles/laws:")
cursor.execute("""
    SELECT page_id, path
    FROM pages
    WHERE page_id LIKE 'core-principles/laws/%'
    ORDER BY page_id
""")

laws_pages = {}
for row in cursor.fetchall():
    laws_pages[row['page_id']] = row['path']
    print(f"  {row['page_id']:<50} -> {row['path']}")

# Now check what links are looking for
print("\nWhat links are trying to find:")
cursor.execute("""
    SELECT DISTINCT dst_page, COUNT(*) as count
    FROM links
    WHERE dst_page LIKE 'core-principles/laws/%'
    AND is_valid = 0
    GROUP BY dst_page
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    exists = "✓ EXISTS" if row['dst_page'] in laws_pages else "✗ MISSING"
    print(f"  {row['dst_page']:<50} ({row['count']:3} links) {exists}")

# The problem analysis
print("\n" + "=" * 60)
print("PROBLEM IDENTIFIED:")
print("=" * 60)

print("\nThe issue is that links are resolving to 'core-principles/laws/asynchronous-reality'")
print("but the page_id in the database is likely different.")
print("\nLet's verify:")

# Check if the exact page exists
test_id = "core-principles/laws/asynchronous-reality"
cursor.execute("SELECT page_id FROM pages WHERE page_id = ?", (test_id,))
result = cursor.fetchone()
if result:
    print(f"✓ Page '{test_id}' exists in database")
else:
    print(f"✗ Page '{test_id}' NOT in database")
    
    # Try to find what it's actually stored as
    cursor.execute("SELECT page_id FROM pages WHERE page_id LIKE '%asynchronous-reality%'")
    actual = cursor.fetchall()
    if actual:
        print(f"  Actually stored as: {actual[0]['page_id']}")

conn.close()