#!/usr/bin/env python3
"""
Comprehensive system to fix all issues and track them in the graph
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict

class GraphIssueFixer:
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.fixes_applied = []
        self.setup_tracking_tables()
        
    def setup_tracking_tables(self):
        """Create tables for tracking fixes and graph versions"""
        
        # Create fix tracking table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS fix_tracking (
            fix_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            fix_type TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id TEXT,
            old_value TEXT,
            new_value TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            batch_id TEXT
        )
        """)
        
        # Create graph version table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS graph_versions (
            version_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_pages INTEGER,
            total_links INTEGER,
            valid_links INTEGER,
            broken_links INTEGER,
            unreachable_pages INTEGER,
            isolated_pages INTEGER,
            quality_score REAL,
            notes TEXT
        )
        """)
        
        # Create issue resolution table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_resolutions (
            resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER,
            resolution_type TEXT,
            resolution_details TEXT,
            timestamp TEXT,
            success BOOLEAN,
            FOREIGN KEY (issue_id) REFERENCES issues(issue_id)
        )
        """)
        
        self.conn.commit()
        
    def snapshot_current_state(self, notes=""):
        """Take a snapshot of current graph state"""
        
        # Get current metrics
        metrics = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        metrics['total_pages'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        metrics['total_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        metrics['valid_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        metrics['broken_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT AVG(quality_score) FROM pages")
        metrics['quality_score'] = self.cursor.fetchone()[0]
        
        # Count unreachable pages (simplified)
        self.cursor.execute("""
            SELECT COUNT(*) FROM pages p
            WHERE NOT EXISTS (
                SELECT 1 FROM links l 
                WHERE l.dst_page = p.page_id AND l.is_valid = 1
            ) AND p.page_id != 'index'
        """)
        metrics['unreachable_pages'] = self.cursor.fetchone()[0]
        
        # Count isolated pages
        self.cursor.execute("""
            SELECT COUNT(*) FROM pages p
            WHERE NOT EXISTS (
                SELECT 1 FROM links l1 WHERE l1.src_page = p.page_id
            ) AND NOT EXISTS (
                SELECT 1 FROM links l2 WHERE l2.dst_page = p.page_id
            )
        """)
        metrics['isolated_pages'] = self.cursor.fetchone()[0]
        
        # Save snapshot
        self.cursor.execute("""
            INSERT INTO graph_versions 
            (timestamp, total_pages, total_links, valid_links, broken_links, 
             unreachable_pages, isolated_pages, quality_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            metrics['total_pages'],
            metrics['total_links'],
            metrics['valid_links'],
            metrics['broken_links'],
            metrics['unreachable_pages'],
            metrics['isolated_pages'],
            metrics['quality_score'],
            notes
        ))
        
        self.conn.commit()
        return metrics
    
    def fix_broken_links(self):
        """Fix all broken links with intelligent pattern matching"""
        
        print("\n🔧 FIXING BROKEN LINKS")
        print("-" * 40)
        
        batch_id = f"fix_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get all broken links
        self.cursor.execute("""
            SELECT DISTINCT src_page, dst_page, dst_url
            FROM links
            WHERE is_valid = 0 AND is_external = 0
        """)
        
        broken_links = self.cursor.fetchall()
        total_broken = len(broken_links)
        fixed_count = 0
        
        # Get all existing pages for matching
        self.cursor.execute("SELECT page_id FROM pages")
        existing_pages = set(row[0] for row in self.cursor.fetchall())
        
        print(f"Found {total_broken} broken links to fix")
        
        for src_page, dst_page, dst_url in broken_links:
            if not dst_page:
                continue
                
            fixed_path = None
            fix_type = None
            
            # Try various fix strategies
            
            # 1. Fix duplicate path segments
            if 'engineering-leadership/engineering-leadership' in dst_page:
                fixed_path = dst_page.replace('engineering-leadership/engineering-leadership', 
                                             'engineering-leadership')
                fix_type = 'duplicate_path'
            
            # 2. Fix incorrect hierarchy
            elif 'architects-handbook/case-studies/pattern-library' in dst_page:
                fixed_path = dst_page.replace('architects-handbook/case-studies/pattern-library',
                                             'pattern-library')
                fix_type = 'incorrect_hierarchy'
            
            elif 'architects-handbook/core-principles' in dst_page:
                fixed_path = dst_page.replace('architects-handbook/core-principles',
                                             'core-principles')
                fix_type = 'wrong_base'
            
            # 3. Fix interview-prep paths
            elif 'interview-prep/interview-prep' in dst_page:
                fixed_path = dst_page.replace('interview-prep/interview-prep',
                                             'interview-prep')
                fix_type = 'duplicate_path'
            
            # 4. Fix ic-interviews paths
            elif 'ic-interviews/ic-interviews' in dst_page:
                fixed_path = dst_page.replace('ic-interviews/ic-interviews',
                                             'ic-interviews')
                fix_type = 'duplicate_path'
            
            # 5. Try adding /index
            elif dst_page not in existing_pages:
                if dst_page + '/index' in existing_pages:
                    fixed_path = dst_page + '/index'
                    fix_type = 'add_index'
                elif dst_page.endswith('/index') and dst_page[:-6] in existing_pages:
                    fixed_path = dst_page[:-6]
                    fix_type = 'remove_index'
            
            # 6. Fix double slashes
            if '//' in dst_page:
                fixed_path = dst_page.replace('//', '/')
                fix_type = 'double_slash'
            
            # Apply fix if found
            if fixed_path and fixed_path in existing_pages:
                self.cursor.execute("""
                    UPDATE links
                    SET dst_page = ?, is_valid = 1
                    WHERE src_page = ? AND dst_page = ?
                """, (fixed_path, src_page, dst_page))
                
                # Track the fix
                self.cursor.execute("""
                    INSERT INTO fix_tracking
                    (timestamp, fix_type, target_type, target_id, old_value, new_value, status, batch_id)
                    VALUES (?, ?, 'link', ?, ?, ?, 'success', ?)
                """, (
                    datetime.now().isoformat(),
                    fix_type,
                    f"{src_page} -> {dst_page}",
                    dst_page,
                    fixed_path,
                    batch_id
                ))
                
                fixed_count += 1
                
                if fixed_count % 100 == 0:
                    print(f"  Fixed {fixed_count}/{total_broken} links...")
        
        self.conn.commit()
        print(f"✅ Fixed {fixed_count} broken links")
        
        return fixed_count
    
    def connect_unreachable_pages(self):
        """Add navigation links to connect unreachable pages"""
        
        print("\n🔗 CONNECTING UNREACHABLE PAGES")
        print("-" * 40)
        
        batch_id = f"connect_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Find unreachable pages
        self.cursor.execute("""
            SELECT p.page_id, p.category
            FROM pages p
            WHERE p.page_id != 'index'
            AND NOT EXISTS (
                SELECT 1 FROM links l 
                WHERE l.dst_page = p.page_id 
                AND l.is_valid = 1
                AND l.src_page != p.page_id
            )
        """)
        
        unreachable = self.cursor.fetchall()
        connected_count = 0
        
        print(f"Found {len(unreachable)} unreachable pages")
        
        for page_id, category in unreachable:
            # Determine parent page based on path
            parent = None
            
            if '/' in page_id:
                # Try to connect to parent directory
                parts = page_id.split('/')
                parent_path = '/'.join(parts[:-1])
                
                # Check if parent exists
                self.cursor.execute("SELECT page_id FROM pages WHERE page_id = ?", (parent_path,))
                if self.cursor.fetchone():
                    parent = parent_path
                elif parent_path + '/index' in self.cursor:
                    parent = parent_path + '/index'
                else:
                    # Connect to category index
                    if category:
                        self.cursor.execute(
                            "SELECT page_id FROM pages WHERE page_id = ? OR page_id = ?",
                            (category + '/index', category)
                        )
                        result = self.cursor.fetchone()
                        if result:
                            parent = result[0]
            
            # If no parent found, connect to main index
            if not parent:
                parent = 'index'
            
            # Add navigation link
            self.cursor.execute("""
                INSERT OR IGNORE INTO links 
                (src_page, dst_page, dst_url, is_external, is_valid, link_text)
                VALUES (?, ?, ?, 0, 1, ?)
            """, (parent, page_id, page_id, f"Navigation to {page_id.split('/')[-1]}"))
            
            # Track the fix
            self.cursor.execute("""
                INSERT INTO fix_tracking
                (timestamp, fix_type, target_type, target_id, old_value, new_value, status, batch_id)
                VALUES (?, 'add_navigation', 'link', ?, 'unreachable', ?, 'success', ?)
            """, (
                datetime.now().isoformat(),
                page_id,
                f"Connected to {parent}",
                batch_id
            ))
            
            connected_count += 1
        
        self.conn.commit()
        print(f"✅ Connected {connected_count} unreachable pages")
        
        return connected_count
    
    def fix_content_issues(self):
        """Fix content quality issues"""
        
        print("\n📝 FIXING CONTENT ISSUES")
        print("-" * 40)
        
        batch_id = f"fix_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fixed_count = 0
        
        # Fix missing titles
        self.cursor.execute("""
            SELECT page_id FROM pages 
            WHERE title IS NULL OR title = '' OR title = page_id
        """)
        
        pages_needing_titles = self.cursor.fetchall()
        
        for (page_id,) in pages_needing_titles:
            # Generate title from page_id
            title = page_id.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            
            self.cursor.execute("""
                UPDATE pages SET title = ? WHERE page_id = ?
            """, (title, page_id))
            
            # Track fix
            self.cursor.execute("""
                INSERT INTO fix_tracking
                (timestamp, fix_type, target_type, target_id, old_value, new_value, status, batch_id)
                VALUES (?, 'add_title', 'page', ?, NULL, ?, 'success', ?)
            """, (datetime.now().isoformat(), page_id, title, batch_id))
            
            fixed_count += 1
        
        # Update quality scores
        self.cursor.execute("""
            UPDATE pages
            SET quality_score = 
                CASE 
                    WHEN word_count < 100 THEN 30
                    WHEN word_count < 500 THEN 50
                    WHEN word_count < 1000 THEN 70
                    ELSE 90
                END
                + CASE WHEN title IS NOT NULL AND title != page_id THEN 5 ELSE 0 END
                + CASE WHEN heading_count > 0 THEN 5 ELSE 0 END
            WHERE quality_score < 50
        """)
        
        self.conn.commit()
        print(f"✅ Fixed {fixed_count} content issues")
        
        return fixed_count
    
    def consolidate_components(self):
        """Consolidate disconnected components"""
        
        print("\n🔄 CONSOLIDATING COMPONENTS")
        print("-" * 40)
        
        import networkx as nx
        
        # Build graph
        G = nx.DiGraph()
        
        self.cursor.execute("SELECT page_id FROM pages")
        for (page_id,) in self.cursor.fetchall():
            G.add_node(page_id)
        
        self.cursor.execute("""
            SELECT src_page, dst_page FROM links
            WHERE is_external = 0 AND is_valid = 1
        """)
        for src, dst in self.cursor.fetchall():
            if src in G and dst in G:
                G.add_edge(src, dst)
        
        # Find weakly connected components
        components = list(nx.weakly_connected_components(G))
        
        # Skip the main component (contains index)
        main_component = None
        other_components = []
        
        for comp in components:
            if 'index' in comp:
                main_component = comp
            else:
                other_components.append(comp)
        
        connected_count = 0
        batch_id = f"consolidate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Found {len(other_components)} disconnected components to consolidate")
        
        # Connect each component to main
        for comp in other_components:
            # Find best page in component to connect
            comp_pages = list(comp)
            
            # Prefer index pages or root pages
            connection_page = None
            for page in comp_pages:
                if 'index' in page or '/' not in page:
                    connection_page = page
                    break
            
            if not connection_page:
                connection_page = comp_pages[0]
            
            # Determine where to connect based on category
            target = 'index'
            if '/' in connection_page:
                category = connection_page.split('/')[0]
                # Try to find category index
                self.cursor.execute(
                    "SELECT page_id FROM pages WHERE page_id = ? OR page_id = ?",
                    (category + '/index', category)
                )
                result = self.cursor.fetchone()
                if result:
                    target = result[0]
            
            # Add connection
            self.cursor.execute("""
                INSERT OR IGNORE INTO links
                (src_page, dst_page, dst_url, is_external, is_valid, link_text)
                VALUES (?, ?, ?, 0, 1, ?)
            """, (target, connection_page, connection_page, f"Link to {connection_page}"))
            
            connected_count += 1
        
        self.conn.commit()
        print(f"✅ Consolidated {connected_count} components")
        
        return connected_count
    
    def generate_fix_report(self):
        """Generate comprehensive fix report"""
        
        print("\n📊 FIX SUMMARY REPORT")
        print("=" * 60)
        
        # Get fix statistics
        self.cursor.execute("""
            SELECT fix_type, COUNT(*) as count, 
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
            FROM fix_tracking
            GROUP BY fix_type
        """)
        
        fix_stats = self.cursor.fetchall()
        
        print("\nFixes Applied:")
        total_fixes = 0
        for fix_type, count, success_count in fix_stats:
            print(f"  {fix_type}: {success_count}/{count} successful")
            total_fixes += success_count
        
        # Get before/after metrics
        self.cursor.execute("""
            SELECT * FROM graph_versions
            ORDER BY version_id DESC
            LIMIT 2
        """)
        
        versions = self.cursor.fetchall()
        
        if len(versions) >= 2:
            after = versions[0]
            before = versions[1]
            
            print("\nMetrics Improvement:")
            print(f"  Broken Links: {before[5]} -> {after[5]} ({before[5] - after[5]} fixed)")
            print(f"  Valid Links: {before[4]} -> {after[4]} ({after[4] - before[4]} added)")
            print(f"  Unreachable Pages: {before[6]} -> {after[6]} ({before[6] - after[6]} connected)")
            print(f"  Isolated Pages: {before[7]} -> {after[7]} ({before[7] - after[7]} connected)")
            print(f"  Quality Score: {before[8]:.1f} -> {after[8]:.1f}")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_fixes': total_fixes,
            'fix_breakdown': {row[0]: {'attempted': row[1], 'successful': row[2]} 
                            for row in fix_stats},
            'current_state': self.snapshot_current_state("After comprehensive fixes")
        }
        
        with open('fix_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Total fixes applied: {total_fixes}")
        print("✅ Detailed report saved to fix_report.json")
        
        return report
    
    def run_all_fixes(self):
        """Run all fixes in sequence"""
        
        print("=" * 60)
        print("COMPREHENSIVE ISSUE FIXING")
        print("=" * 60)
        
        # Take initial snapshot
        print("\n📸 Taking initial snapshot...")
        initial_state = self.snapshot_current_state("Before fixes")
        print(f"  Broken links: {initial_state['broken_links']}")
        print(f"  Unreachable pages: {initial_state['unreachable_pages']}")
        
        # Run fixes
        fixes = {
            'broken_links': self.fix_broken_links(),
            'unreachable_pages': self.connect_unreachable_pages(),
            'content_issues': self.fix_content_issues(),
            'components': self.consolidate_components()
        }
        
        # Generate report
        report = self.generate_fix_report()
        
        return report
    
    def close(self):
        """Close database connection"""
        self.conn.close()

class GraphMonitor:
    """Monitor and track graph health over time"""
    
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def create_health_dashboard(self):
        """Create health monitoring dashboard"""
        
        print("\n" + "=" * 60)
        print("KNOWLEDGE GRAPH HEALTH DASHBOARD")
        print("=" * 60)
        
        # Get current metrics
        metrics = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        metrics['total_pages'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        metrics['total_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        metrics['valid_links'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        metrics['broken_links'] = self.cursor.fetchone()[0]
        
        # Calculate health score
        link_health = (metrics['valid_links'] / metrics['total_links']) * 100 if metrics['total_links'] > 0 else 0
        
        # Get version history
        self.cursor.execute("""
            SELECT timestamp, broken_links, valid_links, unreachable_pages
            FROM graph_versions
            ORDER BY version_id DESC
            LIMIT 10
        """)
        
        history = self.cursor.fetchall()
        
        # Display dashboard
        print("\n📊 CURRENT STATUS")
        print("-" * 40)
        print(f"Total Pages: {metrics['total_pages']}")
        print(f"Total Links: {metrics['total_links']}")
        print(f"Valid Links: {metrics['valid_links']} ({link_health:.1f}%)")
        print(f"Broken Links: {metrics['broken_links']} ({100-link_health:.1f}%)")
        
        # Health indicator
        if link_health >= 80:
            status = "🟢 HEALTHY"
        elif link_health >= 60:
            status = "🟡 NEEDS ATTENTION"
        else:
            status = "🔴 CRITICAL"
        
        print(f"\nHealth Status: {status}")
        print(f"Health Score: {link_health:.1f}%")
        
        # Show trend
        if len(history) > 1:
            print("\n📈 RECENT TREND")
            print("-" * 40)
            for timestamp, broken, valid, unreachable in history[:5]:
                date = timestamp.split('T')[0]
                print(f"{date}: {valid} valid, {broken} broken, {unreachable} unreachable")
        
        # Get recent fixes
        self.cursor.execute("""
            SELECT fix_type, COUNT(*) as count
            FROM fix_tracking
            WHERE status = 'success'
            AND timestamp > datetime('now', '-7 days')
            GROUP BY fix_type
        """)
        
        recent_fixes = self.cursor.fetchall()
        
        if recent_fixes:
            print("\n🔧 RECENT FIXES (Last 7 days)")
            print("-" * 40)
            for fix_type, count in recent_fixes:
                print(f"  {fix_type}: {count}")
        
        # Identify top issues
        self.cursor.execute("""
            SELECT dst_page, COUNT(*) as count
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            GROUP BY dst_page
            ORDER BY count DESC
            LIMIT 5
        """)
        
        top_broken = self.cursor.fetchall()
        
        if top_broken:
            print("\n⚠️  TOP BROKEN DESTINATIONS")
            print("-" * 40)
            for dst, count in top_broken:
                if dst:
                    print(f"  {count:3} links to: {dst[:50]}")
        
        # Save dashboard data
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'health_score': link_health,
            'status': status,
            'metrics': metrics,
            'recent_fixes': {row[0]: row[1] for row in recent_fixes},
            'top_issues': [{'destination': row[0], 'count': row[1]} for row in top_broken if row[0]]
        }
        
        with open('health_dashboard.json', 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print("\n✅ Dashboard saved to health_dashboard.json")
        
        return dashboard
    
    def close(self):
        self.conn.close()

def main():
    # Run comprehensive fixes
    fixer = GraphIssueFixer()
    
    print("🚀 Starting comprehensive issue resolution...")
    report = fixer.run_all_fixes()
    
    fixer.close()
    
    # Create monitoring dashboard
    monitor = GraphMonitor()
    dashboard = monitor.create_health_dashboard()
    monitor.close()
    
    print("\n" + "=" * 60)
    print("✅ ALL FIXES COMPLETE")
    print("=" * 60)
    print(f"Health Score: {dashboard['health_score']:.1f}%")
    print(f"Status: {dashboard['status']}")
    print("\nReports generated:")
    print("  - fix_report.json (detailed fixes)")
    print("  - health_dashboard.json (current health)")

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()