# Navigation Test Plan for DStudio

## Test Plan Overview

This comprehensive test plan verifies that all navigation improvements are working correctly in the DStudio documentation site. The plan covers manual testing procedures and expected results for all navigation enhancements.

**Total Pages Expected**: 343 markdown files (as per file count)
**Test Coverage**: 100% of navigation paths and user flows

## 1. Prerequisites

### Environment Setup
- [ ] Python environment with all dependencies installed (`pip install -r requirements.txt`)
- [ ] Local development server running (`mkdocs serve`)
- [ ] Access to http://127.0.0.1:8000
- [ ] Modern web browser (Chrome, Firefox, Safari, or Edge)

### Test Data Verification
- [ ] Verify 343 .md files exist in docs directory: `find docs -name "*.md" | wc -l`
- [ ] Verify mkdocs.yml is properly formatted: `python -m yaml mkdocs.yml`
- [ ] No build errors when running: `mkdocs build --strict`

## 2. Navigation Structure Tests

### 2.1 Main Navigation Bar
**Test ID**: NAV-001
**Objective**: Verify main navigation tabs are visible and functional

**Steps**:
1. Navigate to http://127.0.0.1:8000
2. Check that the following tabs appear in navigation:
   - Home
   - Foundations
   - Patterns
   - Quantitative Toolkit
   - Human Factors
   - Case Studies
   - Reference

**Expected Results**:
- [ ] All 7 main navigation tabs are visible
- [ ] Each tab is clickable
- [ ] Active tab is highlighted
- [ ] Navigation persists across page loads

### 2.2 Section Index Pages
**Test ID**: NAV-002
**Objective**: Verify all section index pages provide complete navigation

**Test Cases**:

#### 2.2.1 Foundations Index
**URL**: `/foundations/`
- [ ] Links to "The 7 Laws" overview
- [ ] Links to "The 5 Pillars" overview
- [ ] Expandable "Laws (Detailed)" section with all 7 laws
- [ ] Expandable "Pillars (Detailed)" section with all 5 pillars
- [ ] All links are clickable and lead to correct pages

#### 2.2.2 Patterns Index
**URL**: `/patterns/`
- [ ] Pattern Library link works
- [ ] Pattern Finder tool accessible
- [ ] Pattern Comparison tool accessible
- [ ] Pattern Quiz accessible
- [ ] Pattern Combinations accessible
- [ ] All category sections visible:
  - Resilience & Reliability (13 patterns)
  - Caching Patterns (8 patterns)
  - Data Management (15 patterns)
  - Distributed Coordination (12 patterns)
  - Communication Patterns (14 patterns)
  - Architectural Patterns (11 patterns)
  - Performance & Scaling (13 patterns)
  - Geographic Distribution (10 patterns)
  - Security Patterns (5 patterns)
  - Data Structures (6 patterns)
  - Operations & Monitoring (4 patterns)
  - Specialized Patterns (12 patterns)

#### 2.2.3 Quantitative Toolkit Index
**URL**: `/quantitative/`
- [ ] All 9 quantitative tools listed
- [ ] Each tool has a working link
- [ ] Problem Set link works

#### 2.2.4 Human Factors Index
**URL**: `/human-factors/`
- [ ] All 6 essential practices listed
- [ ] Each practice has a working link

#### 2.2.5 Case Studies Index
**URL**: `/case-studies/`
- [ ] All 15 case studies listed
- [ ] Each case study has a working link
- [ ] Enhanced versions clearly marked

#### 2.2.6 Reference Index
**URL**: `/reference/`
- [ ] All 5 reference resources listed
- [ ] Each resource has a working link

## 3. Deep Navigation Tests

### 3.1 Law Navigation Flow
**Test ID**: NAV-003
**Objective**: Test navigation from main page to specific law content

**Test Flow**:
1. Start at homepage
2. Click "Foundations" in main nav
3. Click "Laws (Detailed)"
4. Click "Law 1: Correlated Failure ⛓️"
5. Verify breadcrumb: Home → Foundations → Laws → Law 1

**Expected Results**:
- [ ] Each click leads to correct page
- [ ] Breadcrumb navigation shows correct path
- [ ] Can navigate back using breadcrumbs
- [ ] Left sidebar shows current location

**Repeat for all 7 laws**:
- [ ] Law 1: Correlated Failure
- [ ] Law 2: Asynchronous Reality
- [ ] Law 3: Emergent Chaos
- [ ] Law 4: Multidimensional Optimization
- [ ] Law 5: Distributed Knowledge
- [ ] Law 6: Cognitive Load
- [ ] Law 7: Economic Reality

### 3.2 Pattern Category Navigation
**Test ID**: NAV-004
**Objective**: Test navigation within pattern categories

**Test Case**: Navigate to Circuit Breaker pattern
1. Click "Patterns" in main nav
2. Click "Resilience & Reliability"
3. Click "Circuit Breaker"
4. Verify page loads correctly
5. Check for related pattern links

**Expected Results**:
- [ ] Pattern page loads with correct content
- [ ] Related patterns section visible
- [ ] Can navigate to other patterns in category
- [ ] Back navigation works correctly

### 3.3 Cross-Reference Navigation
**Test ID**: NAV-005
**Objective**: Test cross-references between sections

**Test Cases**:
1. From any Law page, click reference to a Pattern
   - [ ] Pattern page loads correctly
   - [ ] Can navigate back to Law page

2. From Pattern page, click reference to Law
   - [ ] Law page loads correctly
   - [ ] Can navigate back to Pattern page

3. From Case Study, click reference to Pattern
   - [ ] Pattern page loads correctly
   - [ ] Can navigate back to Case Study

## 4. Specific File Tests

### 4.1 Getting Started Integration
**Test ID**: NAV-006
**Objective**: Verify getting-started.md is properly integrated

**Steps**:
1. Navigate to `/introduction/getting-started/`
2. Verify page loads correctly
3. Check all internal links:
   - [ ] Links to all 7 Laws work
   - [ ] Links to learning paths work
   - [ ] Links to pattern catalog work
   - [ ] Links to case studies work

**Expected Results**:
- [ ] Page is accessible from introduction section
- [ ] All learning path recommendations have working links
- [ ] Quick navigation guide links all work
- [ ] Next/Previous navigation buttons work

### 4.2 Prometheus & Datadog Case Study
**Test ID**: NAV-007
**Objective**: Verify prometheus-datadog-enhanced.md is accessible

**Steps**:
1. Navigate to `/case-studies/`
2. Find "Prometheus & Datadog (Enhanced)" in list
3. Click the link
4. Verify page loads at `/case-studies/prometheus-datadog-enhanced/`

**Expected Results**:
- [ ] Page loads correctly with full content
- [ ] All code examples render properly
- [ ] Mermaid diagrams display correctly
- [ ] Internal navigation (TOC) works

## 5. Search Functionality Tests

### 5.1 Global Search
**Test ID**: SEARCH-001
**Objective**: Verify search can find all pages

**Test Cases**:
1. Search for "getting started"
   - [ ] Results include getting-started.md

2. Search for "prometheus datadog"
   - [ ] Results include prometheus-datadog-enhanced.md

3. Search for each Law name
   - [ ] Each law page appears in results

4. Search for pattern names
   - [ ] Pattern pages appear in results

**Expected Results**:
- [ ] Search returns relevant results
- [ ] Clicking results navigates to correct page
- [ ] Search highlighting works on result pages

## 6. Mobile Navigation Tests

### 6.1 Responsive Navigation
**Test ID**: MOB-001
**Objective**: Test navigation on mobile devices

**Steps**:
1. Resize browser to mobile width (< 768px)
2. Check hamburger menu appears
3. Click hamburger menu
4. Verify all navigation items accessible

**Expected Results**:
- [ ] Navigation collapses to hamburger menu
- [ ] All sections accessible via mobile menu
- [ ] Touch targets are appropriately sized
- [ ] Navigation drawer can be closed

## 7. Performance Tests

### 7.1 Navigation Speed
**Test ID**: PERF-001
**Objective**: Verify navigation performs well

**Test Cases**:
1. Time navigation between main sections
2. Time navigation within patterns (should use instant navigation)
3. Check for any slow-loading pages

**Expected Results**:
- [ ] Section navigation < 500ms
- [ ] Within-section navigation < 200ms (instant navigation)
- [ ] No pages take > 2s to load

## 8. Accessibility Tests

### 8.1 Keyboard Navigation
**Test ID**: ACC-001
**Objective**: Verify keyboard navigation works

**Steps**:
1. Use Tab key to navigate through main navigation
2. Use Enter to select navigation items
3. Use arrow keys in expanded menus

**Expected Results**:
- [ ] All navigation items reachable via keyboard
- [ ] Focus indicators visible
- [ ] Skip navigation link available
- [ ] Logical tab order maintained

## 9. Edge Cases

### 9.1 Deep Linking
**Test ID**: EDGE-001
**Objective**: Test direct URL access

**Test Cases**:
1. Direct access to deep pages:
   - [ ] `/part1-axioms/law1-failure/examples/`
   - [ ] `/patterns/circuit-breaker#implementation`
   - [ ] `/case-studies/uber-location/`

**Expected Results**:
- [ ] Pages load correctly via direct URL
- [ ] Navigation state reflects current location
- [ ] Breadcrumbs show correct path

### 9.2 404 Handling
**Test ID**: EDGE-002
**Objective**: Test non-existent page handling

**Steps**:
1. Navigate to `/this-page-does-not-exist/`
2. Check 404 page displays
3. Verify navigation still works from 404 page

**Expected Results**:
- [ ] 404 page displays with helpful message
- [ ] Navigation remains functional
- [ ] Can return to valid pages

## 10. Regression Tests

### 10.1 Previous Issues
**Test ID**: REG-001
**Objective**: Ensure previous navigation issues don't recur

**Known Issues to Test**:
- [ ] Duplicate "Circuit Breaker" entries (should only appear once)
- [ ] Missing pattern pages (all should be accessible)
- [ ] Broken cross-references (all should work)

## Test Execution Checklist

### Phase 1: Structure Tests (30 min)
- [ ] Complete all Navigation Structure Tests (Section 2)
- [ ] Document any issues found

### Phase 2: Flow Tests (45 min)
- [ ] Complete Deep Navigation Tests (Section 3)
- [ ] Complete Specific File Tests (Section 4)
- [ ] Document navigation paths that fail

### Phase 3: Feature Tests (30 min)
- [ ] Complete Search Functionality Tests (Section 5)
- [ ] Complete Mobile Navigation Tests (Section 6)
- [ ] Document any search or mobile issues

### Phase 4: Quality Tests (30 min)
- [ ] Complete Performance Tests (Section 7)
- [ ] Complete Accessibility Tests (Section 8)
- [ ] Complete Edge Cases (Section 9)
- [ ] Document any quality issues

### Phase 5: Final Verification (15 min)
- [ ] Run Regression Tests (Section 10)
- [ ] Verify all 343 pages are accessible
- [ ] Create summary report

## Automated Test Script

Save this as `test_navigation.py` for automated testing:

```python
# !/usr/bin/env python3
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
    
# Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total markdown files: {file_count}")
    print(f"Missing required files: {len(missing_files)}")
    print(f"Failed page loads: {len(failed_pages)}")
    
    if failed_pages:
        print("\nFailed pages:")
        for title, url, error in failed_pages:
            print(f"  - {title}: {error}")
    
    return len(missing_files) == 0 and len(failed_pages) == 0

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
```

## Success Criteria

The navigation improvements are considered successful when:

1. **All 343 pages are accessible** through navigation
2. **No broken links** in navigation or cross-references
3. **Search finds all content** including new files
4. **Mobile navigation works** correctly
5. **Performance targets met** (< 500ms navigation)
6. **No duplicate entries** in navigation
7. **Breadcrumbs accurate** for all pages
8. **Getting-started.md** properly integrated
9. **prometheus-datadog-enhanced.md** accessible

## Issue Reporting Template

When issues are found, document them using this template:

```markdown
### Issue: [Brief Description]
**Test ID**: [e.g., NAV-003]
**Severity**: High/Medium/Low
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Result**:

**Actual Result**:

**Screenshot/Error**: [if applicable]

**Suggested Fix**:
```

## Post-Test Actions

1. **Document all issues** found during testing
2. **Prioritize fixes** based on severity
3. **Re-test failed cases** after fixes
4. **Update test plan** with any new test cases discovered
5. **Create automation** for critical test paths

---

This test plan ensures comprehensive coverage of all navigation improvements. Execute systematically and document results for tracking progress.