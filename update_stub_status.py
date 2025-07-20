#!/usr/bin/env python3
"""
Update status for stub files that are falsely marked as complete
"""

import os
import re

stub_files = [
    ("docs/part1-axioms/axiom1-latency/examples.md", 39),
    ("docs/part1-axioms/axiom4-concurrency/examples.md", 41),
    ("docs/part1-axioms/axiom5-coordination/examples.md", 41),
    ("docs/part1-axioms/axiom3-failure/exercises.md", 42),
    ("docs/part1-axioms/axiom2-capacity/examples.md", 45),
    ("docs/part1-axioms/axiom3-failure/examples.md", 45),
    ("docs/part1-axioms/axiom4-concurrency/exercises.md", 47),
    ("docs/part1-axioms/axiom5-coordination/exercises.md", 47),
    ("docs/part1-axioms/axiom6-observability/examples.md", 48),
    ("docs/part1-axioms/axiom7-human/examples.md", 48),
    ("docs/part1-axioms/axiom6-observability/exercises.md", 50),
    ("docs/part1-axioms/axiom7-human/exercises.md", 50),
    ("docs/part1-axioms/axiom8-economics/examples.md", 51),
    ("docs/part1-axioms/axiom2-capacity/exercises.md", 52),
    ("docs/part1-axioms/axiom8-economics/exercises.md", 56),
    ("docs/part2-pillars/transition-part3.md", 76),
    ("docs/tools/index.md", 87),
    ("docs/reference/index.md", 88),
]

def update_stub_status(filepath, line_count):
    """Update status from complete to stub"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Calculate completion percentage based on line count
        # Assume 300+ lines is complete
        completion_percentage = min(30, int((line_count / 300) * 100))
        
        # Replace status
        if 'status: complete' in content:
            content = content.replace(
                'status: complete',
                f'status: stub\ncompletion_percentage: {completion_percentage}'
            )
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            return True, f"Updated to stub ({completion_percentage}%)"
        else:
            return False, "Already updated or different status"
            
    except Exception as e:
        return False, str(e)

def main():
    print("=== Updating Stub File Status ===\n")
    
    updated = 0
    for filepath, line_count in stub_files:
        # Skip the one we already updated
        if filepath == "docs/part1-axioms/axiom1-latency/examples.md":
            print(f"✓ {filepath}: Already updated")
            updated += 1
            continue
            
        success, message = update_stub_status(filepath, line_count)
        if success:
            print(f"✓ {filepath}: {message}")
            updated += 1
        else:
            print(f"✗ {filepath}: {message}")
    
    print(f"\n=== Summary ===")
    print(f"Total stub files: {len(stub_files)}")
    print(f"Updated: {updated}")

if __name__ == "__main__":
    main()