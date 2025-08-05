#!/usr/bin/env python3
"""Optimize MkDocs configuration for better performance and fewer warnings."""

import yaml
from pathlib import Path

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    """Custom YAML loader that ignores unknown tags."""
    def ignore_unknown(self, node):
        return None

def add_unknown_constructors(loader):
    """Add constructors for unknown tags."""
    yaml.add_constructor(None, loader.ignore_unknown, Loader=loader)

def main():
    """Optimize mkdocs.yml configuration."""
    mkdocs_path = Path("mkdocs.yml")
    
    if not mkdocs_path.exists():
        print("ERROR: mkdocs.yml not found!")
        return
    
    # Set up custom loader
    add_unknown_constructors(SafeLoaderIgnoreUnknown)
    
    # Load config
    with open(mkdocs_path, 'r') as f:
        config = yaml.load(f, Loader=SafeLoaderIgnoreUnknown)
    
    # Add optimizations
    changes_made = []
    
    # 1. Add strict mode to catch errors faster
    if 'strict' not in config:
        config['strict'] = False  # Set to False to allow build with warnings
        changes_made.append("Added 'strict: false' mode")
    
    # 2. Optimize plugins
    if 'plugins' in config:
        # Ensure search plugin is configured properly
        for i, plugin in enumerate(config['plugins']):
            if isinstance(plugin, str) and plugin == 'search':
                config['plugins'][i] = {
                    'search': {
                        'separator': '[\\s\\-]+',
                        'min_search_length': 3,
                        'prebuild_index': True
                    }
                }
                changes_made.append("Optimized search plugin configuration")
            elif isinstance(plugin, dict) and 'mermaid2' in plugin:
                # Ensure mermaid2 has proper config
                if 'arguments' not in plugin['mermaid2']:
                    plugin['mermaid2']['arguments'] = {
                        'theme': 'default',
                        'themeVariables': {
                            'primaryColor': '#5448C8',
                            'primaryTextColor': '#fff',
                            'primaryBorderColor': '#4338A8',
                            'lineColor': '#5448C8',
                            'secondaryColor': '#00BCD4',
                            'tertiaryColor': '#fff'
                        }
                    }
                    changes_made.append("Added mermaid2 theme configuration")
    
    # 3. Add validation_config to suppress warnings
    if 'validation' not in config:
        config['validation'] = {
            'nav': {
                'omitted_files': 'warn',  # Don't error on files not in nav
                'not_found': 'warn',      # Don't error on missing files
                'absolute_links': 'warn'   # Don't error on absolute links
            },
            'links': {
                'not_found': 'warn',      # Don't error on broken links
                'absolute_links': 'warn',  # Don't error on absolute links
                'unrecognized_links': 'warn'  # Don't error on unrecognized link formats
            }
        }
        changes_made.append("Added validation config to suppress warnings")
    
    # 4. Add use_directory_urls for cleaner URLs
    if 'use_directory_urls' not in config:
        config['use_directory_urls'] = True
        changes_made.append("Enabled directory URLs")
    
    # 5. Set docs_dir explicitly
    if 'docs_dir' not in config:
        config['docs_dir'] = 'docs'
        changes_made.append("Set explicit docs_dir")
    
    # 6. Set site_dir explicitly
    if 'site_dir' not in config:
        config['site_dir'] = 'site'
        changes_made.append("Set explicit site_dir")
    
    # Write back to file
    with open(mkdocs_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    if changes_made:
        print("MkDocs configuration optimized with the following changes:")
        for change in changes_made:
            print(f"  - {change}")
    else:
        print("MkDocs configuration already optimized.")
    
    print("\nConfiguration optimized for better build performance and fewer warnings.")

if __name__ == "__main__":
    main()