# MkDocs Material Features for Navigation Analysis

## Built-in Features You Can Use

### 1. **Search Index (search_index.json)**
When MkDocs builds, it creates a search index that contains all content:
```bash
cat site/search/search_index.json
```
This contains every page's content, headings, and metadata.

### 2. **MkDocs Material Navigation Features**

Add these to your `mkdocs.yml` for better navigation analysis:

```yaml
theme:
  features:
    - navigation.instant      # Instant loading
    - navigation.tracking     # Track active page
    - navigation.tabs         # Top-level navigation tabs
    - navigation.sections     # Collapsible sections
    - navigation.expand       # Expand all sections by default
    - navigation.path         # Show breadcrumb path
    - navigation.indexes      # Section index pages
    - navigation.top          # Back to top button
    - toc.follow             # Follow scrolling in ToC
    - toc.integrate          # Integrate ToC into navigation
    
    # For better structure visibility:
    - navigation.prune       # Only render visible navigation items
    - header.autohide        # Hide header on scroll
    
plugins:
  - search:
      lang: en
      separator: '[\s\-\.]+'
  
  # Additional useful plugins:
  - tags:                    # Tag pages for categorization
      tags_file: tags.md
  
  - meta:                    # Read metadata from files
  
  - awesome-pages:           # Enhanced navigation control
      filename: .pages
      collapse_single_pages: false
      strict: false
  
  - print-site:              # Generate single-page view of entire site
      add_to_navigation: true
      print_page_title: 'Print Site'
      add_full_urls: false
      enumerate_headings: true
      enumerate_figures: true
      add_cover_page: true
      cover_page_template: "docs/assets/templates/cover_page.tpl"
  
  - mkdocs-nav-enhancements: # Better navigation
  
  - git-revision-date-localized: # Show last updated dates
      enable_creation_date: true
```

### 3. **Generate Site Map Programmatically**

MkDocs exposes its navigation through Python:

```python
from mkdocs.config import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

# Load MkDocs configuration
config = load_config('mkdocs.yml')

# Get all files
files = get_files(config)

# Get navigation structure
nav = get_navigation(files, config)

# Access navigation items
for item in nav:
    if item.is_page:
        print(f"Page: {item.title} -> {item.file.src_path}")
    elif item.is_section:
        print(f"Section: {item.title}")
        for child in item.children:
            print(f"  - {child.title}")
```

### 4. **Use MkDocs Macros Plugin**

The macros plugin can generate dynamic content:

```python
# docs/macros.py
def define_env(env):
    """Hook for defining variables, macros and filters"""
    
    @env.macro
    def generate_site_tree():
        """Generate a tree of all pages"""
        pages = []
        for page in env.conf['nav']:
            # Process navigation
            pass
        return pages
    
    @env.macro
    def list_all_pages():
        """List all pages with metadata"""
        return env.conf['pages']
```

Then in your markdown:
```markdown
{{ generate_site_tree() }}
```

### 5. **MkDocs Commands for Analysis**

```bash
# Build site with verbose output
mkdocs build --verbose

# Serve with live reload (shows all file changes)
mkdocs serve --dirtyreload

# Get info about the build
mkdocs build --strict --verbose 2>&1 | grep "Page"

# Use Python API
python -c "
import mkdocs
from mkdocs.config import load_config
config = load_config('mkdocs.yml')
print('Total pages:', len(config['nav']))
"
```

### 6. **Extract from Built Site**

After building, you can analyze:

```bash
# All HTML files (represents all pages)
find site -name "*.html" -type f | wc -l

# Extract all headings
grep -h "<h[1-6]" site/**/*.html | sed 's/<[^>]*>//g' | sort | uniq

# Get all internal links
grep -ho 'href="[^"]*"' site/**/*.html | grep -v "http" | sort | uniq
```

### 7. **Browser Developer Tools**

When serving the site:
1. Open browser console
2. Access MkDocs navigation object:
```javascript
// If using instant loading
console.log(document.querySelector('.md-nav__list'))

// Get all navigation items
document.querySelectorAll('.md-nav__item').forEach(item => {
    console.log(item.textContent.trim())
})
```

### 8. **Export Tools**

Some useful MkDocs plugins for export:
- `mkdocs-pdf-export-plugin` - Export to PDF with ToC
- `mkdocs-print-site-plugin` - Single page with everything
- `mkdocs-with-pdf` - Generate PDF with cover, ToC
- `mkdocs-combine` - Combine all pages into one

### 9. **Analytics Integration**

Add to understand usage:
```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
    
# Or custom
extra_javascript:
  - javascripts/analytics.js
```

Then analyze which pages are most visited.

### 10. **API Documentation Generation**

For comprehensive documentation:
```bash
# Generate JSON representation
python -c "
import json
import mkdocs.config
config = mkdocs.config.load_config('mkdocs.yml')
nav_dict = {item: str(config['nav'][item]) for item in range(len(config['nav']))}
print(json.dumps(nav_dict, indent=2))
"
```

## Quick Commands Summary

```bash
# 1. Build search index
mkdocs build

# 2. Extract navigation as JSON
python analyze_site_structure.py

# 3. Generate visual tree
python generate_ultra_detailed_tree.py

# 4. View in browser with dev tools
mkdocs serve
# Then: http://localhost:8000

# 5. Single command site analysis
find docs -name "*.md" | xargs grep "^#" | cut -d: -f2- | sort | uniq -c | sort -nr
```

## Recommended Approach

For the most detailed tree, combine:
1. **Our Python scripts** (already created)
2. **MkDocs search index** (contains all content)
3. **Built site analysis** (actual output)
4. **Navigation configuration** (intended structure)

This gives you:
- Intended structure (mkdocs.yml)
- Actual files (file system)
- Content details (headings, links, topics)
- Relationships (cross-references)
- Search data (indexed content)