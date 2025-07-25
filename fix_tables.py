#!/usr/bin/env python3
"""
Script to find and fix HTML tables in markdown files to add responsive classes and data-labels.
"""

import os
import re
from typing import List, Tuple
from pathlib import Path

def extract_headers_from_table(table_html: str) -> List[str]:
    """Extract header texts from table HTML."""
    headers = []
    
    # First try to find headers in thead
    thead_match = re.search(r'<thead>(.*?)</thead>', table_html, re.DOTALL | re.IGNORECASE)
    if thead_match:
        thead_content = thead_match.group(1)
        # Extract th tags from thead
        th_matches = re.findall(r'<th[^>]*>(.*?)</th>', thead_content, re.DOTALL | re.IGNORECASE)
        headers = [re.sub(r'<[^>]+>', '', th.strip()) for th in th_matches]
    
    # If no thead, look for th tags in first tr
    if not headers:
        first_tr_match = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        if first_tr_match:
            first_tr_content = first_tr_match.group(1)
            th_matches = re.findall(r'<th[^>]*>(.*?)</th>', first_tr_content, re.DOTALL | re.IGNORECASE)
            if th_matches:
                headers = [re.sub(r'<[^>]+>', '', th.strip()) for th in th_matches]
    
    return headers

def fix_table(table_html: str) -> Tuple[str, bool]:
    """Fix a single table to add responsive class and data-labels."""
    original_table = table_html
    modified = False
    
    # Check if table already has responsive-table class
    if 'responsive-table' in table_html:
        return table_html, False
    
    # Add responsive-table class
    if re.match(r'<table\s*>', table_html, re.IGNORECASE):
        table_html = re.sub(r'<table\s*>', '<table class="responsive-table">', table_html, count=1, flags=re.IGNORECASE)
        modified = True
    elif re.match(r'<table\s+', table_html, re.IGNORECASE):
        # Table already has attributes
        if 'class=' in table_html:
            # Add to existing class
            table_html = re.sub(r'class="([^"]*)"', r'class="\1 responsive-table"', table_html, count=1)
        else:
            # Add class attribute
            table_html = re.sub(r'<table(\s+[^>]*)>', r'<table class="responsive-table"\1>', table_html, count=1, flags=re.IGNORECASE)
        modified = True
    
    # Extract headers
    headers = extract_headers_from_table(table_html)
    
    if not headers:
        return table_html, modified
    
    # Check if table has thead/tbody structure
    has_thead = bool(re.search(r'<thead>', table_html, re.IGNORECASE))
    has_tbody = bool(re.search(r'<tbody>', table_html, re.IGNORECASE))
    
    if not has_thead and not has_tbody:
        # Need to add thead/tbody structure
        # Find all tr tags
        tr_pattern = r'<tr[^>]*>.*?</tr>'
        all_trs = list(re.finditer(tr_pattern, table_html, re.DOTALL | re.IGNORECASE))
        
        if all_trs and headers:
            # First tr contains headers
            header_tr = all_trs[0].group()
            body_trs = [tr.group() for tr in all_trs[1:]]
            
            # Construct new table with thead/tbody
            table_start = re.search(r'<table[^>]*>', table_html, re.IGNORECASE).group()
            table_end = '</table>'
            
            new_table_content = f"{table_start}\n  <thead>\n    {header_tr}\n  </thead>\n  <tbody>\n"
            
            # Process body rows and add data-labels
            for tr in body_trs:
                # Find all td tags in this row
                td_pattern = r'<td[^>]*>(.*?)</td>'
                tds = list(re.finditer(td_pattern, tr, re.DOTALL | re.IGNORECASE))
                
                new_tr = tr
                for i, td_match in enumerate(tds):
                    if i < len(headers):
                        old_td = td_match.group()
                        td_content = td_match.group(1)
                        # Check if td already has data-label
                        if 'data-label=' not in old_td:
                            new_td = f'<td data-label="{headers[i]}">{td_content}</td>'
                            new_tr = new_tr.replace(old_td, new_td, 1)
                
                new_table_content += f"    {new_tr}\n"
            
            new_table_content += f"  </tbody>\n{table_end}"
            table_html = new_table_content
            modified = True
    else:
        # Table already has structure, just add data-labels to td elements
        # Find tbody content
        tbody_match = re.search(r'<tbody>(.*?)</tbody>', table_html, re.DOTALL | re.IGNORECASE)
        if tbody_match:
            tbody_content = tbody_match.group(1)
            new_tbody_content = tbody_content
            
            # Process each tr in tbody
            tr_pattern = r'<tr[^>]*>.*?</tr>'
            for tr_match in re.finditer(tr_pattern, tbody_content, re.DOTALL | re.IGNORECASE):
                tr = tr_match.group()
                td_pattern = r'<td[^>]*>(.*?)</td>'
                tds = list(re.finditer(td_pattern, tr, re.DOTALL | re.IGNORECASE))
                
                new_tr = tr
                for i, td_match in enumerate(tds):
                    if i < len(headers):
                        old_td = td_match.group()
                        td_content = td_match.group(1)
                        # Check if td already has data-label
                        if 'data-label=' not in old_td:
                            new_td = f'<td data-label="{headers[i]}">{td_content}</td>'
                            new_tr = new_tr.replace(old_td, new_td, 1)
                
                new_tbody_content = new_tbody_content.replace(tr, new_tr)
            
            if new_tbody_content != tbody_content:
                table_html = table_html.replace(tbody_match.group(0), f'<tbody>{new_tbody_content}</tbody>')
                modified = True
    
    return table_html, modified

def process_markdown_file(filepath: Path) -> int:
    """Process a markdown file and fix all tables. Returns number of tables fixed."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    tables_fixed = 0
    
    # Find all HTML tables
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = list(re.finditer(table_pattern, content, re.DOTALL | re.IGNORECASE))
    
    # Process tables in reverse order to maintain positions
    for table_match in reversed(tables):
        table_html = table_match.group()
        fixed_table, was_modified = fix_table(table_html)
        
        if was_modified:
            content = content[:table_match.start()] + fixed_table + content[table_match.end():]
            tables_fixed += 1
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return tables_fixed

def main():
    """Main function to process all markdown files."""
    docs_dir = Path('/home/deepak/DStudio/docs')
    total_files = 0
    total_tables_fixed = 0
    files_modified = []
    
    # Process all markdown files
    for md_file in docs_dir.rglob('*.md'):
        tables_fixed = process_markdown_file(md_file)
        if tables_fixed > 0:
            total_tables_fixed += tables_fixed
            files_modified.append((md_file.relative_to(docs_dir), tables_fixed))
            total_files += 1
    
    # Report results
    print(f"\nTable Fix Report")
    print("=" * 50)
    print(f"Total files processed: {len(list(docs_dir.rglob('*.md')))}")
    print(f"Files modified: {total_files}")
    print(f"Tables fixed: {total_tables_fixed}")
    
    if files_modified:
        print("\nFiles modified:")
        for filepath, count in sorted(files_modified):
            print(f"  {filepath}: {count} table(s)")

if __name__ == "__main__":
    main()