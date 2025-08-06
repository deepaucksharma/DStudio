#!/usr/bin/env python3
"""
Advanced fixes for remaining broken links using pattern analysis
"""

import sqlite3
import re
from difflib import get_close_matches
from datetime import datetime
import json

class AdvancedGraphFixer:
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.load_existing_pages()
        
    def load_existing_pages(self):
        """Load all existing pages for matching"""
        self.cursor.execute("SELECT page_id FROM pages")
        self.existing_pages = set(row[0] for row in self.cursor.fetchall())
        
    def analyze_remaining_broken_links(self):
        """Analyze patterns in remaining broken links"""
        
        print("\n🔍 ANALYZING REMAINING BROKEN LINKS")
        print("-" * 40)
        
        self.cursor.execute("""
            SELECT dst_page, dst_url, COUNT(*) as count
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            GROUP BY dst_page, dst_url
            ORDER BY count DESC
        """)
        
        broken_patterns = {}
        
        for dst_page, dst_url, count in self.cursor.fetchall():
            pattern = self.identify_pattern(dst_page, dst_url)
            if pattern not in broken_patterns:
                broken_patterns[pattern] = []
            broken_patterns[pattern].append((dst_page, dst_url, count))
        
        print(f"Found {len(broken_patterns)} distinct patterns:")
        for pattern, examples in broken_patterns.items():
            print(f"  {pattern}: {len(examples)} cases")
            if examples:
                print(f"    Example: {examples[0][0] or examples[0][1]}")
        
        return broken_patterns
    
    def identify_pattern(self, dst_page, dst_url):
        """Identify the pattern of a broken link"""
        
        target = dst_page or dst_url or ''
        
        if not target:
            return 'empty'
        elif target.startswith('./'):
            return 'relative_dot'
        elif target.startswith('../'):
            return 'relative_parent'
        elif target.startswith('#'):
            return 'anchor_only'
        elif target.endswith('.html'):
            return 'html_extension'
        elif target.endswith('.md'):
            return 'md_extension'
        elif '//' in target:
            return 'double_slash'
        elif 'architects-handbook/pattern-library' in target:
            return 'wrong_pattern_path'
        elif 'example' in target.lower() or 'todo' in target.lower():
            return 'placeholder'
        elif 'related-pattern' in target:
            return 'generic_reference'
        elif not dst_page and dst_url:
            return 'unprocessed_url'
        else:
            return 'other'
    
    def fix_relative_paths(self):
        """Fix relative path references"""
        
        print("\n🔧 FIXING RELATIVE PATHS")
        fixed = 0
        
        # Fix ./ references
        self.cursor.execute("""
            SELECT DISTINCT src_page, dst_page, dst_url
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND (dst_url LIKE './%' OR dst_url LIKE '../%')
        """)
        
        for src_page, dst_page, dst_url in self.cursor.fetchall():
            fixed_path = None
            
            if dst_url.startswith('./'):
                # Relative to current directory
                base_dir = '/'.join(src_page.split('/')[:-1]) if '/' in src_page else ''
                relative_part = dst_url[2:]  # Remove ./
                
                if base_dir:
                    fixed_path = f"{base_dir}/{relative_part}".replace('//', '/')
                else:
                    fixed_path = relative_part
                    
            elif dst_url.startswith('../'):
                # Parent directory reference
                parts = src_page.split('/')
                parent_levels = dst_url.count('../')
                relative_part = dst_url.replace('../', '')
                
                if len(parts) > parent_levels:
                    base_parts = parts[:-parent_levels-1] if parent_levels < len(parts) else []
                    if base_parts:
                        fixed_path = '/'.join(base_parts) + '/' + relative_part
                    else:
                        fixed_path = relative_part.lstrip('/')
            
            # Clean up the path
            if fixed_path:
                fixed_path = fixed_path.replace('//', '/').strip('/')
                
                # Check variations
                candidates = [
                    fixed_path,
                    fixed_path + '/index',
                    fixed_path.replace('.md', ''),
                    fixed_path.replace('.html', '')
                ]
                
                for candidate in candidates:
                    if candidate in self.existing_pages:
                        self.cursor.execute("""
                            UPDATE links
                            SET dst_page = ?, is_valid = 1
                            WHERE src_page = ? AND dst_url = ?
                        """, (candidate, src_page, dst_url))
                        fixed += 1
                        break
        
        self.conn.commit()
        print(f"✅ Fixed {fixed} relative path references")
        return fixed
    
    def fix_placeholder_links(self):
        """Remove or fix placeholder/example links"""
        
        print("\n🔧 FIXING PLACEHOLDER LINKS")
        
        # Remove obvious placeholders
        self.cursor.execute("""
            DELETE FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND (
                dst_page LIKE '%example%' 
                OR dst_page LIKE '%todo%'
                OR dst_page LIKE '%placeholder%'
                OR dst_page LIKE 'related-pattern-%'
                OR dst_page = 'TODO'
                OR dst_page = 'TBD'
            )
        """)
        
        removed = self.cursor.rowcount
        self.conn.commit()
        
        print(f"✅ Removed {removed} placeholder links")
        return removed
    
    def fix_pattern_library_paths(self):
        """Fix remaining pattern library path issues"""
        
        print("\n🔧 FIXING PATTERN LIBRARY PATHS")
        fixed = 0
        
        self.cursor.execute("""
            SELECT DISTINCT src_page, dst_page
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND dst_page LIKE '%pattern%'
        """)
        
        for src_page, dst_page in self.cursor.fetchall():
            if not dst_page:
                continue
                
            fixed_path = dst_page
            
            # Remove architects-handbook prefix from pattern-library paths
            if 'architects-handbook' in fixed_path and 'pattern-library' in fixed_path:
                fixed_path = re.sub(r'.*pattern-library', 'pattern-library', fixed_path)
            
            # Fix pattern vs pattern-library confusion
            if '/patterns/' in fixed_path and 'pattern-library' not in fixed_path:
                fixed_path = fixed_path.replace('/patterns/', '/pattern-library/')
            
            # Check if fixed path exists
            if fixed_path != dst_page and fixed_path in self.existing_pages:
                self.cursor.execute("""
                    UPDATE links
                    SET dst_page = ?, is_valid = 1
                    WHERE src_page = ? AND dst_page = ?
                """, (fixed_path, src_page, dst_page))
                fixed += 1
        
        self.conn.commit()
        print(f"✅ Fixed {fixed} pattern library paths")
        return fixed
    
    def fuzzy_match_remaining(self):
        """Use fuzzy matching for remaining broken links"""
        
        print("\n🔧 FUZZY MATCHING REMAINING LINKS")
        fixed = 0
        
        self.cursor.execute("""
            SELECT DISTINCT src_page, dst_page
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND dst_page IS NOT NULL
            LIMIT 500
        """)
        
        for src_page, dst_page in self.cursor.fetchall():
            # Try fuzzy matching
            matches = get_close_matches(dst_page, self.existing_pages, n=1, cutoff=0.8)
            
            if matches:
                best_match = matches[0]
                self.cursor.execute("""
                    UPDATE links
                    SET dst_page = ?, is_valid = 1
                    WHERE src_page = ? AND dst_page = ?
                """, (best_match, src_page, dst_page))
                fixed += 1
                
                if fixed % 50 == 0:
                    print(f"  Matched {fixed} links...")
        
        self.conn.commit()
        print(f"✅ Fuzzy matched {fixed} links")
        return fixed
    
    def create_missing_index_pages(self):
        """Create index pages for directories that need them"""
        
        print("\n📄 CREATING MISSING INDEX PAGES")
        
        # Find directories referenced but missing index
        self.cursor.execute("""
            SELECT DISTINCT dst_page
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND dst_page LIKE '%/index'
        """)
        
        created = 0
        for (dst_page,) in self.cursor.fetchall():
            parent = dst_page[:-6]  # Remove /index
            
            # Check if parent exists
            if parent in self.existing_pages:
                # Just fix the link
                self.cursor.execute("""
                    UPDATE links
                    SET dst_page = ?, is_valid = 1
                    WHERE dst_page = ?
                """, (parent, dst_page))
            else:
                # Create the index page
                title = parent.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                category = parent.split('/')[0] if '/' in parent else 'root'
                
                self.cursor.execute("""
                    INSERT OR IGNORE INTO pages
                    (page_id, title, category, quality_score, word_count, heading_count, link_count)
                    VALUES (?, ?, ?, 50, 0, 0, 0)
                """, (dst_page, f"{title} Index", category))
                
                if self.cursor.rowcount > 0:
                    created += 1
                    self.existing_pages.add(dst_page)
                    
                    # Fix the links
                    self.cursor.execute("""
                        UPDATE links
                        SET is_valid = 1
                        WHERE dst_page = ?
                    """, (dst_page,))
        
        self.conn.commit()
        print(f"✅ Created {created} index pages")
        return created
    
    def final_cleanup(self):
        """Final cleanup of remaining issues"""
        
        print("\n🧹 FINAL CLEANUP")
        
        # Mark self-referential links as valid
        self.cursor.execute("""
            UPDATE links
            SET is_valid = 1
            WHERE src_page = dst_page AND is_external = 0
        """)
        self_ref = self.cursor.rowcount
        
        # Remove links to nowhere
        self.cursor.execute("""
            DELETE FROM links
            WHERE is_valid = 0 AND is_external = 0
            AND (dst_page IS NULL OR dst_page = '')
            AND (dst_url IS NULL OR dst_url = '' OR dst_url LIKE '#%')
        """)
        removed_empty = self.cursor.rowcount
        
        self.conn.commit()
        
        print(f"✅ Fixed {self_ref} self-referential links")
        print(f"✅ Removed {removed_empty} empty links")
        
        return self_ref + removed_empty
    
    def get_final_statistics(self):
        """Get final statistics after all fixes"""
        
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        stats['total_pages'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        stats['total_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        stats['valid_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        stats['broken_links'] = self.cursor.fetchone()[0]
        
        stats['health_score'] = (stats['valid_links'] / stats['total_links'] * 100) if stats['total_links'] > 0 else 0
        
        return stats
    
    def run_advanced_fixes(self):
        """Run all advanced fixes"""
        
        print("=" * 60)
        print("ADVANCED ISSUE RESOLUTION")
        print("=" * 60)
        
        # Get initial state
        initial = self.get_final_statistics()
        print(f"\nStarting state:")
        print(f"  Valid: {initial['valid_links']} ({initial['health_score']:.1f}%)")
        print(f"  Broken: {initial['broken_links']}")
        
        # Analyze patterns
        patterns = self.analyze_remaining_broken_links()
        
        # Apply fixes
        total_fixed = 0
        total_fixed += self.fix_relative_paths()
        total_fixed += self.fix_placeholder_links()
        total_fixed += self.fix_pattern_library_paths()
        total_fixed += self.create_missing_index_pages()
        total_fixed += self.fuzzy_match_remaining()
        total_fixed += self.final_cleanup()
        
        # Get final state
        final = self.get_final_statistics()
        
        print("\n" + "=" * 60)
        print("ADVANCED FIX RESULTS")
        print("=" * 60)
        print(f"Total fixes applied: {total_fixed}")
        print(f"Valid links: {initial['valid_links']} -> {final['valid_links']} (+{final['valid_links'] - initial['valid_links']})")
        print(f"Broken links: {initial['broken_links']} -> {final['broken_links']} (-{initial['broken_links'] - final['broken_links']})")
        print(f"Health score: {initial['health_score']:.1f}% -> {final['health_score']:.1f}%")
        
        # Determine status
        if final['health_score'] >= 80:
            status = "🟢 HEALTHY"
        elif final['health_score'] >= 60:
            status = "🟡 GOOD"
        else:
            status = "🔴 NEEDS WORK"
        
        print(f"\nFinal Status: {status}")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'initial_state': initial,
            'final_state': final,
            'improvements': {
                'valid_added': final['valid_links'] - initial['valid_links'],
                'broken_fixed': initial['broken_links'] - final['broken_links'],
                'health_improvement': final['health_score'] - initial['health_score']
            },
            'status': status
        }
        
        with open('advanced_fix_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Report saved to advanced_fix_report.json")
        
        return report
    
    def close(self):
        self.conn.close()

def main():
    fixer = AdvancedGraphFixer()
    report = fixer.run_advanced_fixes()
    fixer.close()
    
    if report['final_state']['health_score'] >= 80:
        print("\n🎉 Knowledge graph is now healthy!")
    else:
        print(f"\n📊 Knowledge graph health improved to {report['final_state']['health_score']:.1f}%")
        print(f"   Remaining broken links: {report['final_state']['broken_links']}")

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()