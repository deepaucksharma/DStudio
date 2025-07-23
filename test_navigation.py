#!/usr/bin/env python3
"""
Automated navigation tests for DStudio documentation
"""

import os
import sys
import time
import yaml
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"
DOCS_DIR = Path("docs")

def load_mkdocs_config():
    """Load and parse mkdocs.yml"""
    with open("mkdocs.yml", "r") as f:
        return yaml.safe_load(f)

def extract_all_nav_items(nav, prefix=""):
    """Recursively extract all navigation items"""
    items = []
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    items.append((key, value))
                elif isinstance(value, list):
                    items.extend(extract_all_nav_items(value, f"{prefix}{key}/"))
        elif isinstance(item, str):
            items.append((item, item))
    return items

def test_all_pages_accessible():
    """Test that all pages in navigation are accessible"""
    config = load_mkdocs_config()
    nav_items = extract_all_nav_items(config.get("nav", []))
    
    failed = []
    for title, path in nav_items:
        if path.endswith(".md"):
            url_path = path.replace(".md", "/").replace("index/", "")
            url = urljoin(BASE_URL, url_path)
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    failed.append((title, url, response.status_code))
                else:
                    print(f"✓ {title}: {url}")
            except Exception as e:
                failed.append((title, url, str(e)))
                print(f"✗ {title}: {url} - {e}")
    
    return failed

def test_markdown_files_count():
    """Verify the expected number of markdown files"""
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"\nTotal markdown files found: {len(md_files)}")
    return len(md_files)

def test_specific_files():
    """Test specific files mentioned in requirements"""
    required_files = [
        "docs/introduction/getting-started.md",
        "docs/case-studies/prometheus-datadog-enhanced.md"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"✗ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    return missing

def test_search_functionality():
    """Test that search can find key pages"""
    test_queries = [
        ("getting started", "introduction/getting-started"),
        ("prometheus datadog", "case-studies/prometheus-datadog-enhanced"),
        ("circuit breaker", "patterns/circuit-breaker"),
        ("correlated failure", "part1-axioms/axiom1-failure")
    ]
    
    print("\nTesting search functionality...")
    search_issues = []
    
    # Note: This is a placeholder as MkDocs search requires JavaScript
    # In a real test, you'd use Selenium or similar for browser automation
    for query, expected_path in test_queries:
        print(f"  Would search for: '{query}' expecting to find: {expected_path}")
    
    return search_issues

def test_breadcrumb_navigation():
    """Test breadcrumb navigation on deep pages"""
    test_pages = [
        "/part1-axioms/axiom1-failure/examples/",
        "/patterns/circuit-breaker/",
        "/case-studies/uber-location/"
    ]
    
    breadcrumb_issues = []
    for page in test_pages:
        url = urljoin(BASE_URL, page)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                breadcrumbs = soup.find_all(class_='breadcrumb')
                if not breadcrumbs:
                    print(f"  No breadcrumbs found on: {page}")
                else:
                    print(f"✓ Breadcrumbs present on: {page}")
            else:
                breadcrumb_issues.append((page, f"Status: {response.status_code}"))
        except Exception as e:
            breadcrumb_issues.append((page, str(e)))
    
    return breadcrumb_issues

def count_patterns_by_category():
    """Count patterns in each category to verify completeness"""
    patterns_dir = DOCS_DIR / "patterns"
    
    categories = {
        "resilience": ["circuit-breaker", "retry-backoff", "bulkhead", "timeout", 
                      "health-check", "graceful-degradation", "backpressure", 
                      "rate-limiting", "load-shedding", "failover", "fault-tolerance",
                      "split-brain", "idempotent-receiver"],
        "caching": ["caching", "caching-strategies", "cache-aside", "read-through-cache",
                   "write-through-cache", "write-behind-cache", "tile-caching"],
        "data-management": ["sharding", "event-sourcing", "cqrs", "saga", "outbox",
                           "two-phase-commit", "distributed-transactions", "eventual-consistency",
                           "tunable-consistency", "cap-theorem", "cdc", "materialized-view",
                           "polyglot-persistence", "wal"],
        # Add other categories...
    }
    
    print("\nPattern counts by category:")
    for category, patterns in categories.items():
        found = sum(1 for p in patterns if (patterns_dir / f"{p}.md").exists())
        print(f"  {category}: {found}/{len(patterns)} patterns")

def run_all_tests():
    """Run all automated tests"""
    print("Starting DStudio Navigation Tests\n")
    
    # Test 1: File count
    print("Test 1: Markdown File Count")
    file_count = test_markdown_files_count()
    
    # Test 2: Specific files
    print("\nTest 2: Required Files")
    missing_files = test_specific_files()
    
    # Test 3: Navigation accessibility
    print("\nTest 3: Navigation Accessibility")
    failed_pages = test_all_pages_accessible()
    
    # Test 4: Search functionality (placeholder)
    print("\nTest 4: Search Functionality")
    search_issues = test_search_functionality()
    
    # Test 5: Breadcrumb navigation
    print("\nTest 5: Breadcrumb Navigation")
    breadcrumb_issues = test_breadcrumb_navigation()
    
    # Test 6: Pattern categorization
    print("\nTest 6: Pattern Categorization")
    count_patterns_by_category()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total markdown files: {file_count}")
    print(f"Expected files: 343")
    print(f"Missing required files: {len(missing_files)}")
    print(f"Failed page loads: {len(failed_pages)}")
    print(f"Breadcrumb issues: {len(breadcrumb_issues)}")
    
    if failed_pages:
        print("\nFailed pages:")
        for title, url, error in failed_pages:
            print(f"  - {title}: {error}")
    
    if missing_files:
        print("\nMissing files:")
        for file in missing_files:
            print(f"  - {file}")
    
    # Calculate pass/fail
    all_passed = (
        len(missing_files) == 0 and 
        len(failed_pages) == 0 and
        file_count >= 297  # Minimum expected based on navigation
    )
    
    print(f"\nOverall Result: {'PASS' if all_passed else 'FAIL'}")
    
    return all_passed

if __name__ == "__main__":
    # Ensure MkDocs is running
    try:
        response = requests.get(BASE_URL)
    except:
        print("ERROR: MkDocs server not running!")
        print("Please run 'mkdocs serve' first")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)