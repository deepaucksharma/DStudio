#!/usr/bin/env python3
"""
Fix the link validation logic issue
"""

import sqlite3

def fix_link_validation(db_path="knowledge_graph_ultimate.db"):
    """Fix the validation status of links that are incorrectly marked as broken"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Fixing link validation...")
    print("=" * 60)
    
    # First, let's see the current state
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
    broken_before = cursor.fetchone()[0]
    print(f"Broken internal links before fix: {broken_before}")
    
    # Get all internal links that are marked as invalid
    cursor.execute("""
        SELECT DISTINCT dst_page
        FROM links
        WHERE is_external = 0 AND is_valid = 0
    """)
    
    invalid_destinations = [row[0] for row in cursor.fetchall()]
    
    # Check which of these actually exist in the pages table
    fixed_count = 0
    for dst in invalid_destinations:
        if dst:  # Skip None/NULL values
            cursor.execute("SELECT page_id FROM pages WHERE page_id = ?", (dst,))
            if cursor.fetchone():
                # This page exists! Update all links to it as valid
                cursor.execute("""
                    UPDATE links
                    SET is_valid = 1
                    WHERE dst_page = ? AND is_external = 0
                """, (dst,))
                fixed_count += cursor.rowcount
                print(f"  Fixed {cursor.rowcount} links to {dst}")
    
    conn.commit()
    
    # Check the result
    cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
    broken_after = cursor.fetchone()[0]
    print(f"\nBroken internal links after fix: {broken_after}")
    print(f"Fixed {broken_before - broken_after} links")
    
    # Show remaining broken links
    if broken_after > 0:
        print("\n" + "-" * 40)
        print("Sample remaining broken links:")
        cursor.execute("""
            SELECT src_page, dst_url, dst_page
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]} -> {row[1]}")
            print(f"    (looking for: {row[2]})")
    
    # Update the issues table
    print("\n" + "-" * 40)
    print("Updating issues table...")
    
    # Remove old broken link issues
    cursor.execute("DELETE FROM issues WHERE issue_type = 'broken_internal_link'")
    removed = cursor.rowcount
    print(f"Removed {removed} old broken link issues")
    
    # Add new broken link issues for truly broken links
    cursor.execute("""
        INSERT INTO issues (page_id, issue_type, severity, details, suggested_fix)
        SELECT 
            src_page,
            'broken_internal_link',
            'error',
            'Link to non-existent page: ' || dst_url,
            'Create page ' || dst_page || '.md or fix the link'
        FROM links
        WHERE is_valid = 0 AND is_external = 0
    """)
    added = cursor.rowcount
    print(f"Added {added} updated broken link issues")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Validation fix complete!")
    
    return broken_before, broken_after

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    fix_link_validation()