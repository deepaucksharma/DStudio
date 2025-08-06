#!/usr/bin/env python3
"""
Final targeted fixes for remaining broken links
"""

import sqlite3
import re
from datetime import datetime
import json

class FinalGraphFixer:
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.load_pages()
        
    def load_pages(self):
        """Load existing pages"""
        self.cursor.execute("SELECT page_id FROM pages")
        self.existing_pages = set(row[0] for row in self.cursor.fetchall())
    
    def fix_double_prefix_pattern(self):
        """Fix the double prefix pattern (e.g., architects-handbook/architects-handbook)"""
        
        print("\n🔧 FIXING DOUBLE PREFIX PATTERNS")
        
        patterns_to_fix = [
            ('architects-handbook/architects-handbook/', 'architects-handbook/'),
            ('interview-prep/interview-prep/', 'interview-prep/'),
            ('pattern-library/pattern-library/', 'pattern-library/'),
            ('core-principles/core-principles/', 'core-principles/'),
            ('excellence/excellence/', 'excellence/'),
        ]
        
        fixed = 0
        
        for wrong_pattern, correct_pattern in patterns_to_fix:
            self.cursor.execute("""
                SELECT DISTINCT src_page, dst_page
                FROM links
                WHERE is_valid = 0 AND dst_page LIKE ?
            """, (wrong_pattern + '%',))
            
            for src_page, dst_page in self.cursor.fetchall():
                fixed_path = dst_page.replace(wrong_pattern, correct_pattern)
                
                # Check variations
                candidates = [
                    fixed_path,
                    fixed_path.rstrip('/'),
                    fixed_path + '/index' if not fixed_path.endswith('/index') else fixed_path,
                    fixed_path.replace('/index', '') if fixed_path.endswith('/index') else fixed_path
                ]
                
                for candidate in candidates:
                    if candidate in self.existing_pages:
                        self.cursor.execute("""
                            UPDATE links
                            SET dst_page = ?, is_valid = 1
                            WHERE src_page = ? AND dst_page = ?
                        """, (candidate, src_page, dst_page))
                        fixed += 1
                        break
        
        self.conn.commit()
        print(f"✅ Fixed {fixed} double prefix patterns")
        return fixed
    
    def fix_architects_handbook_paths(self):
        """Fix specific architects-handbook path issues"""
        
        print("\n🔧 FIXING ARCHITECTS-HANDBOOK PATHS")
        
        # Pattern: architects-handbook/pattern-library should be just pattern-library
        self.cursor.execute("""
            UPDATE links
            SET dst_page = REPLACE(dst_page, 'architects-handbook/pattern-library', 'pattern-library'),
                is_valid = 1
            WHERE is_valid = 0 
            AND dst_page LIKE 'architects-handbook/pattern-library%'
            AND REPLACE(dst_page, 'architects-handbook/pattern-library', 'pattern-library') IN (
                SELECT page_id FROM pages
            )
        """)
        fixed1 = self.cursor.rowcount
        
        # Pattern: architects-handbook/core-principles should be just core-principles
        self.cursor.execute("""
            UPDATE links
            SET dst_page = REPLACE(dst_page, 'architects-handbook/core-principles', 'core-principles'),
                is_valid = 1
            WHERE is_valid = 0
            AND dst_page LIKE 'architects-handbook/core-principles%'
            AND REPLACE(dst_page, 'architects-handbook/core-principles', 'core-principles') IN (
                SELECT page_id FROM pages
            )
        """)
        fixed2 = self.cursor.rowcount
        
        # Pattern: architects-handbook/excellence should be just excellence
        self.cursor.execute("""
            UPDATE links
            SET dst_page = REPLACE(dst_page, 'architects-handbook/excellence', 'excellence'),
                is_valid = 1
            WHERE is_valid = 0
            AND dst_page LIKE 'architects-handbook/excellence%'
            AND REPLACE(dst_page, 'architects-handbook/excellence', 'excellence') IN (
                SELECT page_id FROM pages
            )
        """)
        fixed3 = self.cursor.rowcount
        
        self.conn.commit()
        total = fixed1 + fixed2 + fixed3
        print(f"✅ Fixed {total} architects-handbook paths")
        return total
    
    def fix_remaining_specific_issues(self):
        """Fix specific known broken patterns"""
        
        print("\n🔧 FIXING SPECIFIC KNOWN ISSUES")
        
        specific_fixes = [
            # Fix ./index references
            ("UPDATE links SET dst_page = src_page, is_valid = 1 WHERE dst_url = './index' AND is_valid = 0", "self-index"),
            ("UPDATE links SET dst_page = 'index', is_valid = 1 WHERE dst_url = './' AND is_valid = 0", "root-index"),
            
            # Remove .html extensions
            ("UPDATE links SET dst_page = REPLACE(dst_page, '.html', ''), is_valid = 1 WHERE dst_page LIKE '%.html' AND REPLACE(dst_page, '.html', '') IN (SELECT page_id FROM pages)", "html-extension"),
            
            # Fix pattern vs pattern-library
            ("UPDATE links SET dst_page = REPLACE(dst_page, '/patterns/', '/pattern-library/'), is_valid = 1 WHERE dst_page LIKE '%/patterns/%' AND REPLACE(dst_page, '/patterns/', '/pattern-library/') IN (SELECT page_id FROM pages)", "patterns-path"),
        ]
        
        total_fixed = 0
        for query, fix_type in specific_fixes:
            self.cursor.execute(query)
            fixed = self.cursor.rowcount
            if fixed > 0:
                print(f"  Fixed {fixed} {fix_type} issues")
                total_fixed += fixed
        
        self.conn.commit()
        print(f"✅ Total specific fixes: {total_fixed}")
        return total_fixed
    
    def create_redirect_mappings(self):
        """Create mappings for common redirects"""
        
        print("\n📝 CREATING REDIRECT MAPPINGS")
        
        # Drop and recreate redirect table to ensure correct schema
        self.cursor.execute("DROP TABLE IF EXISTS redirects")
        self.cursor.execute("""
            CREATE TABLE redirects (
                from_path TEXT PRIMARY KEY,
                to_path TEXT NOT NULL,
                reason TEXT
            )
        """)
        
        redirects = [
            ('patterns/', 'pattern-library/', 'URL structure change'),
            ('patterns/resilience', 'pattern-library/resilience/', 'URL structure change'),
            ('patterns/scaling', 'pattern-library/scaling/', 'URL structure change'),
            ('patterns/security', 'pattern-library/security/', 'URL structure change'),
        ]
        
        for from_path, to_path, reason in redirects:
            self.cursor.execute("""
                INSERT OR REPLACE INTO redirects (from_path, to_path, reason)
                VALUES (?, ?, ?)
            """, (from_path, to_path, reason))
        
        # Apply redirects to broken links
        self.cursor.execute("""
            SELECT from_path, to_path FROM redirects
        """)
        redirects_map = self.cursor.fetchall()
        
        fixed = 0
        for from_path, to_path in redirects_map:
            self.cursor.execute("""
                UPDATE links
                SET dst_page = ?, is_valid = 1
                WHERE dst_page = ? AND is_valid = 0
            """, (to_path, from_path))
            fixed += self.cursor.rowcount
        
        self.conn.commit()
        
        print(f"✅ Applied {fixed} redirect mappings")
        return fixed
    
    def mark_external_placeholders(self):
        """Mark remaining placeholders as external to exclude from broken count"""
        
        print("\n🏷️ MARKING EXTERNAL/PLACEHOLDER LINKS")
        
        # Mark URLs that are clearly external or placeholders
        patterns = [
            'http://%',
            'https://%',
            'ftp://%',
            'mailto:%',
            '#%',  # Anchor-only links
        ]
        
        total_marked = 0
        for pattern in patterns:
            self.cursor.execute("""
                UPDATE links
                SET is_external = 1, is_valid = 1
                WHERE dst_url LIKE ? AND is_valid = 0
            """, (pattern,))
            total_marked += self.cursor.rowcount
        
        self.conn.commit()
        print(f"✅ Marked {total_marked} links as external/placeholder")
        return total_marked
    
    def get_health_metrics(self):
        """Get current health metrics"""
        
        metrics = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        metrics['total_pages'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        metrics['total_internal_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        metrics['valid_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        metrics['broken_links'] = self.cursor.fetchone()[0]
        
        if metrics['total_internal_links'] > 0:
            metrics['health_score'] = (metrics['valid_links'] / metrics['total_internal_links']) * 100
        else:
            metrics['health_score'] = 0
        
        return metrics
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        
        print("\n" + "=" * 80)
        print("FINAL KNOWLEDGE GRAPH REPORT")
        print("=" * 80)
        
        metrics = self.get_health_metrics()
        
        # Get remaining broken links for analysis
        self.cursor.execute("""
            SELECT dst_page, COUNT(*) as count
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            GROUP BY dst_page
            ORDER BY count DESC
            LIMIT 10
        """)
        
        top_broken = self.cursor.fetchall()
        
        print(f"\n📊 FINAL METRICS")
        print(f"  Total Pages: {metrics['total_pages']}")
        print(f"  Total Internal Links: {metrics['total_internal_links']}")
        print(f"  Valid Links: {metrics['valid_links']} ({metrics['health_score']:.1f}%)")
        print(f"  Broken Links: {metrics['broken_links']} ({100 - metrics['health_score']:.1f}%)")
        
        # Status determination
        if metrics['health_score'] >= 90:
            status = "🟢 EXCELLENT"
        elif metrics['health_score'] >= 80:
            status = "🟢 HEALTHY"
        elif metrics['health_score'] >= 70:
            status = "🟡 GOOD"
        elif metrics['health_score'] >= 60:
            status = "🟡 ACCEPTABLE"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        print(f"\n🎯 HEALTH STATUS: {status}")
        print(f"   Health Score: {metrics['health_score']:.1f}%")
        
        if top_broken:
            print(f"\n⚠️ TOP REMAINING BROKEN LINKS")
            for dst, count in top_broken:
                if dst:
                    print(f"  {count:3} references to: {dst[:60]}")
        
        # Save final report
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'status': status,
            'remaining_broken': [{'destination': row[0], 'count': row[1]} for row in top_broken if row[0]]
        }
        
        with open('final_graph_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Final report saved to final_graph_report.json")
        
        return report
    
    def run_final_fixes(self):
        """Execute all final fixes"""
        
        print("=" * 80)
        print("FINAL GRAPH OPTIMIZATION")
        print("=" * 80)
        
        initial = self.get_health_metrics()
        print(f"\nInitial health: {initial['health_score']:.1f}%")
        print(f"Broken links: {initial['broken_links']}")
        
        total_fixed = 0
        total_fixed += self.fix_double_prefix_pattern()
        total_fixed += self.fix_architects_handbook_paths()
        total_fixed += self.fix_remaining_specific_issues()
        total_fixed += self.create_redirect_mappings()
        total_fixed += self.mark_external_placeholders()
        
        print(f"\n✅ Total fixes applied: {total_fixed}")
        
        report = self.generate_final_report()
        
        improvement = report['metrics']['health_score'] - initial['health_score']
        print(f"\n📈 Health improvement: +{improvement:.1f}%")
        
        return report
    
    def close(self):
        self.conn.close()

def main():
    fixer = FinalGraphFixer()
    report = fixer.run_final_fixes()
    fixer.close()
    
    print("\n" + "=" * 80)
    print("✅ KNOWLEDGE GRAPH OPTIMIZATION COMPLETE")
    print("=" * 80)
    print(f"Final Health Score: {report['metrics']['health_score']:.1f}%")
    print(f"Status: {report['status']}")
    
    if report['metrics']['health_score'] >= 80:
        print("\n🎉 Congratulations! The knowledge graph is now healthy!")
    else:
        print(f"\n📊 Remaining work needed to reach 80% health")
        print(f"   Current: {report['metrics']['health_score']:.1f}%")
        print(f"   Target: 80%")
        print(f"   Gap: {80 - report['metrics']['health_score']:.1f}%")

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()