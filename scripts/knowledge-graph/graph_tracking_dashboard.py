#!/usr/bin/env python3
"""
Comprehensive tracking dashboard for the knowledge graph
Shows all 627 pages with health metrics and issue tracking
"""

import sqlite3
import json
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

class GraphTrackingDashboard:
    def __init__(self, db_path="knowledge_graph_ultimate.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def generate_complete_dashboard(self):
        """Generate comprehensive dashboard with all metrics"""
        
        print("=" * 100)
        print(" " * 30 + "KNOWLEDGE GRAPH TRACKING DASHBOARD")
        print("=" * 100)
        
        # 1. Overall Statistics
        self.display_overall_stats()
        
        # 2. Category Breakdown
        self.display_category_breakdown()
        
        # 3. Link Health Analysis
        self.display_link_health()
        
        # 4. Top Pages Analysis
        self.display_top_pages()
        
        # 5. Issue Tracking
        self.display_issue_tracking()
        
        # 6. Fix History
        self.display_fix_history()
        
        # 7. Connectivity Analysis
        self.display_connectivity()
        
        # 8. Generate visual reports
        self.generate_visual_reports()
        
        # 9. Export comprehensive data
        self.export_tracking_data()
        
    def display_overall_stats(self):
        """Display overall statistics"""
        
        print("\n" + "─" * 100)
        print("📊 OVERALL STATISTICS")
        print("─" * 100)
        
        # Page statistics
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        total_pages = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT AVG(quality_score), MIN(quality_score), MAX(quality_score) FROM pages")
        avg_quality, min_quality, max_quality = self.cursor.fetchone()
        
        self.cursor.execute("SELECT SUM(word_count), AVG(word_count) FROM pages")
        total_words, avg_words = self.cursor.fetchone()
        
        # Link statistics
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        total_internal = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        valid_links = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 0 AND is_external = 0")
        broken_links = self.cursor.fetchone()[0]
        
        health_score = (valid_links / total_internal * 100) if total_internal > 0 else 0
        
        # Determine status
        if health_score >= 80:
            status = "🟢 HEALTHY"
            status_color = "green"
        elif health_score >= 60:
            status = "🟡 ACCEPTABLE"
            status_color = "yellow"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
            status_color = "red"
        
        print(f"\n{'Pages:':<20} {total_pages:>10,} total pages")
        print(f"{'Quality:':<20} {avg_quality:>10.1f} average (min: {min_quality:.0f}, max: {max_quality:.0f})")
        print(f"{'Content:':<20} {total_words:>10,} total words ({avg_words:.0f} avg per page)")
        print(f"\n{'Links:':<20} {total_internal:>10,} total internal links")
        print(f"{'Valid:':<20} {valid_links:>10,} ({health_score:.1f}%)")
        print(f"{'Broken:':<20} {broken_links:>10,} ({100-health_score:.1f}%)")
        print(f"\n{'Health Status:':<20} {status}")
        print(f"{'Health Score:':<20} {health_score:>10.1f}%")
        
    def display_category_breakdown(self):
        """Display breakdown by category"""
        
        print("\n" + "─" * 100)
        print("📁 CATEGORY BREAKDOWN (All 627 Pages)")
        print("─" * 100)
        
        self.cursor.execute("""
            SELECT 
                category,
                COUNT(*) as page_count,
                AVG(quality_score) as avg_quality,
                SUM(word_count) as total_words,
                COUNT(CASE WHEN quality_score < 50 THEN 1 END) as low_quality
            FROM pages
            GROUP BY category
            ORDER BY page_count DESC
        """)
        
        categories = self.cursor.fetchall()
        
        print(f"\n{'Category':<30} {'Pages':>8} {'Avg Quality':>12} {'Total Words':>12} {'Low Quality':>12}")
        print("─" * 75)
        
        for cat, count, quality, words, low in categories:
            category = cat or 'root'
            print(f"{category:<30} {count:>8} {quality:>12.1f} {words:>12,} {low:>12}")
        
    def display_link_health(self):
        """Display link health by source category"""
        
        print("\n" + "─" * 100)
        print("🔗 LINK HEALTH BY CATEGORY")
        print("─" * 100)
        
        self.cursor.execute("""
            SELECT 
                p.category,
                COUNT(DISTINCT l.src_page) as pages_with_links,
                COUNT(l.src_page) as total_links,
                SUM(CASE WHEN l.is_valid = 1 THEN 1 ELSE 0 END) as valid_links,
                SUM(CASE WHEN l.is_valid = 0 THEN 1 ELSE 0 END) as broken_links
            FROM pages p
            LEFT JOIN links l ON p.page_id = l.src_page AND l.is_external = 0
            WHERE l.src_page IS NOT NULL
            GROUP BY p.category
            ORDER BY broken_links DESC
        """)
        
        print(f"\n{'Category':<30} {'Pages':>8} {'Total Links':>12} {'Valid':>8} {'Broken':>8} {'Health %':>10}")
        print("─" * 80)
        
        for cat, pages, total, valid, broken in self.cursor.fetchall():
            category = cat or 'root'
            health = (valid / total * 100) if total > 0 else 100
            print(f"{category:<30} {pages:>8} {total:>12} {valid:>8} {broken:>8} {health:>10.1f}%")
    
    def display_top_pages(self):
        """Display top pages by various metrics"""
        
        print("\n" + "─" * 100)
        print("🌟 TOP PAGES ANALYSIS")
        print("─" * 100)
        
        # Most referenced pages
        print("\n📥 Most Referenced Pages (Incoming Links):")
        self.cursor.execute("""
            SELECT dst_page, COUNT(*) as incoming
            FROM links
            WHERE is_valid = 1 AND is_external = 0 AND dst_page IS NOT NULL
            GROUP BY dst_page
            ORDER BY incoming DESC
            LIMIT 10
        """)
        
        for page, count in self.cursor.fetchall():
            print(f"  {count:4} <- {page[:70]}")
        
        # Pages with most outgoing links
        print("\n📤 Pages with Most Outgoing Links:")
        self.cursor.execute("""
            SELECT src_page, COUNT(*) as outgoing
            FROM links
            WHERE is_external = 0
            GROUP BY src_page
            ORDER BY outgoing DESC
            LIMIT 10
        """)
        
        for page, count in self.cursor.fetchall():
            print(f"  {count:4} -> {page[:70]}")
        
        # Pages with most broken links
        print("\n⚠️ Pages with Most Broken Links:")
        self.cursor.execute("""
            SELECT src_page, COUNT(*) as broken
            FROM links
            WHERE is_valid = 0 AND is_external = 0
            GROUP BY src_page
            ORDER BY broken DESC
            LIMIT 10
        """)
        
        for page, count in self.cursor.fetchall():
            print(f"  {count:4} ❌ {page[:70]}")
    
    def display_issue_tracking(self):
        """Display issue tracking statistics"""
        
        print("\n" + "─" * 100)
        print("🔍 ISSUE TRACKING")
        print("─" * 100)
        
        # Issue summary
        self.cursor.execute("""
            SELECT issue_type, severity, COUNT(*) as count
            FROM issues
            GROUP BY issue_type, severity
            ORDER BY 
                CASE severity 
                    WHEN 'error' THEN 1 
                    WHEN 'warning' THEN 2 
                    ELSE 3 
                END,
                count DESC
        """)
        
        issues = self.cursor.fetchall()
        
        print(f"\n{'Issue Type':<35} {'Severity':<10} {'Count':>10}")
        print("─" * 60)
        
        total_issues = 0
        for issue_type, severity, count in issues:
            total_issues += count
            severity_icon = "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
            print(f"{issue_type:<35} {severity_icon} {severity:<8} {count:>10}")
        
        print(f"\n{'Total Issues:':<46} {total_issues:>10}")
    
    def display_fix_history(self):
        """Display fix history"""
        
        print("\n" + "─" * 100)
        print("🔧 FIX HISTORY")
        print("─" * 100)
        
        # Check if fix_tracking table exists
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='fix_tracking'
        """)
        
        if not self.cursor.fetchone():
            print("\nNo fix history available")
            return
        
        # Fix summary
        self.cursor.execute("""
            SELECT 
                fix_type,
                COUNT(*) as total_fixes,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                MAX(timestamp) as last_applied
            FROM fix_tracking
            GROUP BY fix_type
            ORDER BY total_fixes DESC
        """)
        
        fixes = self.cursor.fetchall()
        
        if fixes:
            print(f"\n{'Fix Type':<25} {'Total':>8} {'Success':>8} {'Last Applied':<20}")
            print("─" * 65)
            
            for fix_type, total, success, last_time in fixes:
                last_date = last_time.split('T')[0] if last_time else 'N/A'
                print(f"{fix_type:<25} {total:>8} {success:>8} {last_date:<20}")
        
        # Version history
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='graph_versions'
        """)
        
        if self.cursor.fetchone():
            self.cursor.execute("""
                SELECT timestamp, valid_links, broken_links, notes
                FROM graph_versions
                ORDER BY version_id DESC
                LIMIT 5
            """)
            
            versions = self.cursor.fetchall()
            
            if versions:
                print("\n📈 Recent Version History:")
                for timestamp, valid, broken, notes in versions:
                    date = timestamp.split('T')[0]
                    health = (valid / (valid + broken) * 100) if (valid + broken) > 0 else 0
                    print(f"  {date}: {valid} valid, {broken} broken ({health:.1f}% health) - {notes or 'No notes'}")
    
    def display_connectivity(self):
        """Display connectivity analysis"""
        
        print("\n" + "─" * 100)
        print("🌐 CONNECTIVITY ANALYSIS")
        print("─" * 100)
        
        # Count unreachable pages
        self.cursor.execute("""
            SELECT COUNT(*) FROM pages p
            WHERE p.page_id != 'index'
            AND NOT EXISTS (
                SELECT 1 FROM links l 
                WHERE l.dst_page = p.page_id 
                AND l.is_valid = 1
            )
        """)
        unreachable = self.cursor.fetchone()[0]
        
        # Count isolated pages
        self.cursor.execute("""
            SELECT COUNT(*) FROM pages p
            WHERE NOT EXISTS (
                SELECT 1 FROM links l1 WHERE l1.src_page = p.page_id
            ) AND NOT EXISTS (
                SELECT 1 FROM links l2 WHERE l2.dst_page = p.page_id
            )
        """)
        isolated = self.cursor.fetchone()[0]
        
        # Count pages with no outgoing links
        self.cursor.execute("""
            SELECT COUNT(*) FROM pages p
            WHERE NOT EXISTS (
                SELECT 1 FROM links l WHERE l.src_page = p.page_id
            )
        """)
        no_outgoing = self.cursor.fetchone()[0]
        
        print(f"\n{'Unreachable Pages:':<30} {unreachable:>10} ({unreachable/627*100:.1f}%)")
        print(f"{'Isolated Pages:':<30} {isolated:>10} ({isolated/627*100:.1f}%)")
        print(f"{'Pages with No Outgoing Links:':<30} {no_outgoing:>10} ({no_outgoing/627*100:.1f}%)")
    
    def generate_visual_reports(self):
        """Generate visual reports"""
        
        print("\n" + "─" * 100)
        print("📊 GENERATING VISUAL REPORTS")
        print("─" * 100)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Category distribution
        self.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM pages
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """)
        
        categories = self.cursor.fetchall()
        cats = [c[0] or 'root' for c in categories]
        counts = [c[1] for c in categories]
        
        axes[0, 0].bar(range(len(cats)), counts, color='skyblue')
        axes[0, 0].set_xticks(range(len(cats)))
        axes[0, 0].set_xticklabels(cats, rotation=45, ha='right')
        axes[0, 0].set_title('Pages by Category')
        axes[0, 0].set_ylabel('Number of Pages')
        
        # 2. Quality distribution
        self.cursor.execute("SELECT quality_score FROM pages")
        quality_scores = [row[0] for row in self.cursor.fetchall()]
        
        axes[0, 1].hist(quality_scores, bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Quality Score Distribution')
        axes[0, 1].set_xlabel('Quality Score')
        axes[0, 1].set_ylabel('Number of Pages')
        axes[0, 1].axvline(x=50, color='red', linestyle='--', label='Low Quality Threshold')
        axes[0, 1].axvline(x=90, color='gold', linestyle='--', label='High Quality Threshold')
        axes[0, 1].legend()
        
        # 3. Link health over time (if version history exists)
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='graph_versions'
        """)
        
        if self.cursor.fetchone():
            self.cursor.execute("""
                SELECT timestamp, valid_links, broken_links
                FROM graph_versions
                ORDER BY version_id
            """)
            
            versions = self.cursor.fetchall()
            if versions:
                timestamps = [v[0].split('T')[0] for v in versions]
                valid = [v[1] for v in versions]
                broken = [v[2] for v in versions]
                
                axes[1, 0].plot(range(len(timestamps)), valid, 'g-', label='Valid Links', marker='o')
                axes[1, 0].plot(range(len(timestamps)), broken, 'r-', label='Broken Links', marker='x')
                axes[1, 0].set_xticks(range(len(timestamps)))
                axes[1, 0].set_xticklabels(timestamps, rotation=45, ha='right')
                axes[1, 0].set_title('Link Health Over Time')
                axes[1, 0].set_ylabel('Number of Links')
                axes[1, 0].legend()
                axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Issue severity distribution
        self.cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM issues
            GROUP BY severity
        """)
        
        severities = self.cursor.fetchall()
        if severities:
            sev_labels = [s[0] for s in severities]
            sev_counts = [s[1] for s in severities]
            colors = ['red' if s == 'error' else 'yellow' if s == 'warning' else 'blue' for s in sev_labels]
            
            axes[1, 1].pie(sev_counts, labels=sev_labels, colors=colors, autopct='%1.1f%%')
            axes[1, 1].set_title('Issues by Severity')
        
        plt.suptitle('Knowledge Graph Analytics Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('graph_tracking_dashboard.png', dpi=150, bbox_inches='tight')
        
        print("\n✅ Visual dashboard saved to graph_tracking_dashboard.png")
    
    def export_tracking_data(self):
        """Export comprehensive tracking data"""
        
        # Collect all data
        tracking_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'categories': [],
            'top_pages': {},
            'issues': [],
            'fixes': [],
            'connectivity': {}
        }
        
        # Summary
        self.cursor.execute("SELECT COUNT(*) FROM pages")
        tracking_data['summary']['total_pages'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_external = 0")
        total_links = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE is_valid = 1 AND is_external = 0")
        valid_links = self.cursor.fetchone()[0]
        
        tracking_data['summary']['total_links'] = total_links
        tracking_data['summary']['valid_links'] = valid_links
        tracking_data['summary']['broken_links'] = total_links - valid_links
        tracking_data['summary']['health_score'] = (valid_links / total_links * 100) if total_links > 0 else 0
        
        # Categories
        self.cursor.execute("""
            SELECT category, COUNT(*) as count, AVG(quality_score) as avg_quality
            FROM pages
            GROUP BY category
        """)
        
        for cat, count, quality in self.cursor.fetchall():
            tracking_data['categories'].append({
                'name': cat or 'root',
                'page_count': count,
                'avg_quality': round(quality, 1)
            })
        
        # Save to JSON
        with open('graph_tracking_data.json', 'w') as f:
            json.dump(tracking_data, f, indent=2)
        
        print("✅ Tracking data exported to graph_tracking_data.json")
        
        # Generate markdown report
        self.generate_markdown_report(tracking_data)
    
    def generate_markdown_report(self, data):
        """Generate markdown report"""
        
        with open('GRAPH_TRACKING_REPORT.md', 'w') as f:
            f.write("# Knowledge Graph Tracking Report\n\n")
            f.write(f"Generated: {data['generated_at']}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Pages**: {data['summary']['total_pages']}\n")
            f.write(f"- **Total Links**: {data['summary']['total_links']}\n")
            f.write(f"- **Valid Links**: {data['summary']['valid_links']} ({data['summary']['health_score']:.1f}%)\n")
            f.write(f"- **Broken Links**: {data['summary']['broken_links']}\n")
            f.write(f"- **Health Score**: {data['summary']['health_score']:.1f}%\n\n")
            
            f.write("## Categories\n\n")
            f.write("| Category | Pages | Avg Quality |\n")
            f.write("|----------|-------|-------------|\n")
            
            for cat in data['categories'][:10]:
                f.write(f"| {cat['name']} | {cat['page_count']} | {cat['avg_quality']} |\n")
            
            f.write("\n## Recommendations\n\n")
            
            if data['summary']['health_score'] < 80:
                f.write("1. Continue fixing broken links to reach 80% health target\n")
            if data['summary']['broken_links'] > 1000:
                f.write("2. Focus on pages with highest broken link counts\n")
            
            f.write("\n---\n")
            f.write("*This report tracks all 627 pages in the DStudio knowledge graph*\n")
        
        print("✅ Markdown report saved to GRAPH_TRACKING_REPORT.md")
    
    def close(self):
        self.conn.close()

def main():
    dashboard = GraphTrackingDashboard()
    dashboard.generate_complete_dashboard()
    dashboard.close()
    
    print("\n" + "=" * 100)
    print(" " * 35 + "✅ TRACKING DASHBOARD COMPLETE")
    print("=" * 100)
    print("\nGenerated Files:")
    print("  📊 graph_tracking_dashboard.png - Visual analytics")
    print("  📄 graph_tracking_data.json - Complete tracking data")
    print("  📝 GRAPH_TRACKING_REPORT.md - Markdown report")
    print("\nThe knowledge graph now tracks all 627 pages with comprehensive metrics!")

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    main()