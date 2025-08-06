#!/usr/bin/env python3
"""
Fixed link normalization logic
"""

import os
from pathlib import Path

def normalize_internal_link(link_path: str, source_page_id: str) -> str:
    """
    Correctly normalize internal link paths
    
    Args:
        link_path: The raw link from markdown (e.g., "../core-principles/", "../../laws/cap.md")
        source_page_id: The page ID where link appears (e.g., "pattern-library/resilience/circuit-breaker")
    
    Returns:
        Normalized page ID (e.g., "core-principles/index", "core-principles/laws/cap")
    """
    # Handle anchors - remove them but keep the base path
    if '#' in link_path:
        link_path = link_path.split('#')[0]
        if not link_path:  # Just an anchor like "#overview"
            return source_page_id
    
    # Remove query parameters
    if '?' in link_path:
        link_path = link_path.split('?')[0]
    
    if not link_path:
        return source_page_id
    
    # Handle absolute paths (starting with /)
    if link_path.startswith('/'):
        # Remove leading slash - these are relative to docs root
        normalized = link_path[1:]
    else:
        # Handle relative paths
        # Convert source page ID to directory path
        source_dir = os.path.dirname(source_page_id) if source_page_id else ""
        
        # Build the full path
        if link_path.startswith('../'):
            # Go up directories
            parts = link_path.split('/')
            source_parts = source_dir.split('/') if source_dir else []
            
            # Process each ../ to go up one directory
            while parts and parts[0] == '..':
                parts.pop(0)
                if source_parts:
                    source_parts.pop()
            
            # Combine remaining parts
            if source_parts:
                normalized = '/'.join(source_parts + parts)
            else:
                normalized = '/'.join(parts)
                
        elif link_path.startswith('./'):
            # Same directory
            normalized = os.path.join(source_dir, link_path[2:]) if source_dir else link_path[2:]
        else:
            # Relative to current directory
            normalized = os.path.join(source_dir, link_path) if source_dir else link_path
    
    # Clean up the path
    # Convert to Path for normalization, then back to string
    normalized = str(Path(normalized))
    normalized = normalized.replace('\\', '/')  # Ensure forward slashes
    
    # Remove trailing slashes
    normalized = normalized.rstrip('/')
    
    # Check if this was originally a .md file
    was_md_file = normalized.endswith('.md')
    
    # Remove .md extension if present
    if was_md_file:
        normalized = normalized[:-3]
    
    # Handle directory references - add index
    # Only add /index if:
    # 1. The original link ended with / (explicit directory)
    # 2. OR it's not a .md file AND doesn't already end with index
    if link_path.endswith('/'):
        # Explicit directory reference
        if not normalized.endswith('index'):
            normalized = f"{normalized}/index"
    elif not was_md_file and normalized:
        # Not a .md file, might be a directory
        if '.' not in os.path.basename(normalized) and not normalized.endswith('index'):
            # No extension, assume directory
            normalized = f"{normalized}/index"
    
    return normalized

def test_normalization():
    """Test the fixed normalization logic"""
    test_cases = [
        # (source_page, link, expected_result)
        ("index", "core-principles/", "core-principles/index"),
        ("index", "./core-principles/", "core-principles/index"),
        ("index", "core-principles/laws/", "core-principles/laws/index"),
        ("pattern-library/index", "../core-principles/", "core-principles/index"),
        ("pattern-library/resilience/circuit-breaker", "../../core-principles/laws/correlated-failure.md", "core-principles/laws/correlated-failure"),
        ("pattern-library/resilience/circuit-breaker", "../scaling/auto-scaling.md", "pattern-library/scaling/auto-scaling"),
        ("architects-handbook/case-studies/databases/redis", "../../../pattern-library/", "pattern-library/index"),
        ("docs/index", "#overview", "docs/index"),
        ("start-here/index", "/core-principles/", "core-principles/index"),
        ("pattern-library/resilience/circuit-breaker", "timeout.md", "pattern-library/resilience/timeout"),
        ("pattern-library/resilience/circuit-breaker", "./retry-backoff.md", "pattern-library/resilience/retry-backoff"),
        ("interview-prep/index", "ic-interviews/common-problems/", "interview-prep/ic-interviews/common-problems/index"),
        ("", "core-principles/", "core-principles/index"),
        ("excellence/index", "../architects-handbook/", "architects-handbook/index"),
    ]
    
    print("Testing fixed link normalization:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for source, link, expected in test_cases:
        result = normalize_internal_link(link, source)
        if result == expected:
            print(f"✓ {source:40} + {link:40} = {result}")
            passed += 1
        else:
            print(f"✗ {source:40} + {link:40}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return failed == 0

if __name__ == "__main__":
    test_normalization()