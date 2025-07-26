#!/usr/bin/env python3
"""
Pattern Health Dashboard

Generates pattern health metrics dashboard:
- GitHub stars trends
- Stack Overflow activity
- Conference mentions
- Visual dashboard
- Quarterly review data
"""

import os
import json
import requests
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PatternHealth:
    """Health metrics for a pattern"""
    pattern_name: str
    health_score: float
    tier: str
    github_stars: int
    stack_overflow_questions: int
    conference_talks: int
    job_postings: int
    trend: str  # 'rising', 'stable', 'declining'
    last_updated: str

@dataclass 
class HealthTrend:
    """Historical health data point"""
    date: str
    health_score: float
    github_stars: int
    stack_overflow_questions: int

class PatternHealthDashboard:
    """Generates health metrics and visualizations for patterns"""
    
    def __init__(self, patterns_dir: Path, data_dir: Optional[Path] = None):
        self.patterns_dir = patterns_dir
        self.data_dir = data_dir or patterns_dir.parent.parent / 'health-data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load historical data
        self.history_file = self.data_dir / 'pattern_health_history.json'
        self.history = self._load_history()
        
        # Load current metrics
        self.metrics_file = patterns_dir / 'pattern_metadata.json'
        self.current_metrics = self._load_current_metrics()
    
    def _load_history(self) -> Dict[str, List[HealthTrend]]:
        """Load historical health data"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                # Convert to HealthTrend objects
                history = {}
                for pattern, trends in data.items():
                    history[pattern] = [HealthTrend(**trend) for trend in trends]
                return history
        return {}
    
    def _save_history(self):
        """Save historical health data"""
        # Convert to serializable format
        data = {}
        for pattern, trends in self.history.items():
            data[pattern] = [asdict(trend) for trend in trends]
        
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_current_metrics(self) -> Dict[str, Dict]:
        """Load current pattern metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {}
    
    def calculate_trend(self, pattern_name: str) -> str:
        """Calculate trend for a pattern based on historical data"""
        if pattern_name not in self.history or len(self.history[pattern_name]) < 2:
            return 'stable'
        
        trends = self.history[pattern_name]
        recent_trends = trends[-3:]  # Last 3 data points
        
        if len(recent_trends) < 2:
            return 'stable'
        
        # Calculate average change in health score
        score_changes = []
        for i in range(1, len(recent_trends)):
            change = recent_trends[i].health_score - recent_trends[i-1].health_score
            score_changes.append(change)
        
        avg_change = sum(score_changes) / len(score_changes)
        
        if avg_change > 2:
            return 'rising'
        elif avg_change < -2:
            return 'declining'
        else:
            return 'stable'
    
    def update_health_metrics(self, pattern_name: str, metrics: Dict):
        """Update health metrics for a pattern"""
        # Create health trend entry
        trend = HealthTrend(
            date=datetime.now().isoformat(),
            health_score=metrics.get('health_score', 0),
            github_stars=metrics.get('github_stars', 0),
            stack_overflow_questions=metrics.get('stack_overflow_questions', 0)
        )
        
        # Add to history
        if pattern_name not in self.history:
            self.history[pattern_name] = []
        
        # Check if we already have an entry for today
        today = datetime.now().date().isoformat()
        existing_today = [t for t in self.history[pattern_name] if t.date.startswith(today)]
        
        if existing_today:
            # Update existing entry
            idx = self.history[pattern_name].index(existing_today[0])
            self.history[pattern_name][idx] = trend
        else:
            # Add new entry
            self.history[pattern_name].append(trend)
            # Keep only last 90 days
            if len(self.history[pattern_name]) > 90:
                self.history[pattern_name] = self.history[pattern_name][-90:]
        
        self._save_history()
    
    def get_pattern_health(self, pattern_name: str) -> Optional[PatternHealth]:
        """Get current health metrics for a pattern"""
        # Check if we have metrics
        cache_key = f"{pattern_name}_metrics"
        if cache_key not in self.current_metrics:
            return None
        
        metrics = self.current_metrics[cache_key].get('metrics', {})
        
        return PatternHealth(
            pattern_name=pattern_name,
            health_score=metrics.get('health_score', 0),
            tier=metrics.get('recommended_tier', 'bronze'),
            github_stars=metrics.get('github_stars', 0),
            stack_overflow_questions=metrics.get('stack_overflow_questions', 0),
            conference_talks=metrics.get('conference_talks', 0),
            job_postings=metrics.get('job_postings', 0),
            trend=self.calculate_trend(pattern_name),
            last_updated=self.current_metrics[cache_key].get('timestamp', '')
        )
    
    def get_all_pattern_health(self) -> List[PatternHealth]:
        """Get health metrics for all patterns"""
        health_data = []
        
        for cache_key in self.current_metrics:
            if cache_key.endswith('_metrics'):
                pattern_name = cache_key[:-8]  # Remove '_metrics' suffix
                health = self.get_pattern_health(pattern_name)
                if health:
                    health_data.append(health)
        
        return sorted(health_data, key=lambda x: x.health_score, reverse=True)
    
    def generate_tier_distribution_chart(self, output_path: Path):
        """Generate pie chart of tier distribution"""
        health_data = self.get_all_pattern_health()
        
        # Count by tier
        tier_counts = {'gold': 0, 'silver': 0, 'bronze': 0}
        for pattern in health_data:
            if pattern.tier in tier_counts:
                tier_counts[pattern.tier] += 1
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Gold', 'Silver', 'Bronze']
        sizes = [tier_counts['gold'], tier_counts['silver'], tier_counts['bronze']]
        colors = ['#FFD700', '#C0C0C0', '#CD7F32']
        explode = (0.05, 0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, 
                                          colors=colors, autopct='%1.1f%%',
                                          shadow=True, startangle=90)
        
        # Enhance text
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title('Pattern Tier Distribution', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Tier distribution chart saved to {output_path}")
    
    def generate_health_score_histogram(self, output_path: Path):
        """Generate histogram of health scores"""
        health_data = self.get_all_pattern_health()
        scores = [p.health_score for p in health_data]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create histogram
        n, bins, patches = ax.hist(scores, bins=20, range=(0, 100), 
                                  edgecolor='black', alpha=0.7)
        
        # Color bars by score range
        for i, patch in enumerate(patches):
            if bins[i] >= 80:
                patch.set_facecolor('#FFD700')  # Gold
            elif bins[i] >= 60:
                patch.set_facecolor('#C0C0C0')  # Silver
            else:
                patch.set_facecolor('#CD7F32')  # Bronze
        
        ax.set_xlabel('Health Score', fontsize=12)
        ax.set_ylabel('Number of Patterns', fontsize=12)
        ax.set_title('Distribution of Pattern Health Scores', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.1f}')
        ax.axvline(median_score, color='blue', linestyle='--', linewidth=2, label=f'Median: {median_score:.1f}')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Health score histogram saved to {output_path}")
    
    def generate_top_patterns_chart(self, output_path: Path, top_n: int = 20):
        """Generate bar chart of top patterns by health score"""
        health_data = self.get_all_pattern_health()[:top_n]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        patterns = [p.pattern_name for p in health_data]
        scores = [p.health_score for p in health_data]
        tiers = [p.tier for p in health_data]
        
        # Create color map
        colors = []
        for tier in tiers:
            if tier == 'gold':
                colors.append('#FFD700')
            elif tier == 'silver':
                colors.append('#C0C0C0')
            else:
                colors.append('#CD7F32')
        
        # Create horizontal bar chart
        y_pos = np.arange(len(patterns))
        bars = ax.barh(y_pos, scores, color=colors, edgecolor='black')
        
        # Add pattern names
        ax.set_yticks(y_pos)
        ax.set_yticklabels(patterns)
        ax.invert_yaxis()
        
        # Add score labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   f'{score:.1f}', va='center')
        
        ax.set_xlabel('Health Score', fontsize=12)
        ax.set_title(f'Top {top_n} Patterns by Health Score', fontsize=16, fontweight='bold')
        ax.set_xlim(0, 105)
        ax.grid(True, axis='x', alpha=0.3)
        
        # Add legend
        gold_patch = mpatches.Patch(color='#FFD700', label='Gold')
        silver_patch = mpatches.Patch(color='#C0C0C0', label='Silver')
        bronze_patch = mpatches.Patch(color='#CD7F32', label='Bronze')
        ax.legend(handles=[gold_patch, silver_patch, bronze_patch], loc='lower right')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Top patterns chart saved to {output_path}")
    
    def generate_trend_chart(self, pattern_name: str, output_path: Path):
        """Generate trend chart for a specific pattern"""
        if pattern_name not in self.history or len(self.history[pattern_name]) < 2:
            logger.warning(f"Not enough historical data for {pattern_name}")
            return
        
        trends = self.history[pattern_name]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Prepare data
        dates = [datetime.fromisoformat(t.date) for t in trends]
        health_scores = [t.health_score for t in trends]
        github_stars = [t.github_stars for t in trends]
        so_questions = [t.stack_overflow_questions for t in trends]
        
        # Health score trend
        ax1.plot(dates, health_scores, 'b-', linewidth=2, marker='o', markersize=6)
        ax1.set_ylabel('Health Score', fontsize=12)
        ax1.set_title(f'{pattern_name} - Health Trend', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)
        
        # Add trend indicator
        trend = self.calculate_trend(pattern_name)
        trend_color = {'rising': 'green', 'stable': 'blue', 'declining': 'red'}[trend]
        ax1.text(0.02, 0.95, f'Trend: {trend.upper()}', transform=ax1.transAxes,
                fontsize=12, fontweight='bold', color=trend_color,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Activity metrics
        ax2_twin = ax2.twinx()
        
        line1 = ax2.plot(dates, github_stars, 'g-', linewidth=2, marker='s', 
                        markersize=6, label='GitHub Stars')
        line2 = ax2_twin.plot(dates, so_questions, 'r-', linewidth=2, marker='^', 
                             markersize=6, label='Stack Overflow Q')
        
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('GitHub Stars', fontsize=12, color='g')
        ax2_twin.set_ylabel('Stack Overflow Questions', fontsize=12, color='r')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2_twin.tick_params(axis='y', labelcolor='r')
        ax2.grid(True, alpha=0.3)
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left')
        
        # Format x-axis
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Trend chart for {pattern_name} saved to {output_path}")
    
    def generate_dashboard(self, output_dir: Path):
        """Generate complete dashboard with all visualizations"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate charts
        self.generate_tier_distribution_chart(output_dir / 'tier_distribution.png')
        self.generate_health_score_histogram(output_dir / 'health_histogram.png')
        self.generate_top_patterns_chart(output_dir / 'top_patterns.png')
        
        # Generate trend charts for top 5 patterns
        health_data = self.get_all_pattern_health()[:5]
        trends_dir = output_dir / 'trends'
        trends_dir.mkdir(exist_ok=True)
        
        for pattern in health_data:
            self.generate_trend_chart(pattern.pattern_name, 
                                    trends_dir / f'{pattern.pattern_name}_trend.png')
        
        # Generate summary report
        self.generate_summary_report(output_dir / 'health_summary.md')
        
        logger.info(f"Dashboard generated in {output_dir}")
    
    def generate_summary_report(self, output_path: Path):
        """Generate markdown summary report"""
        health_data = self.get_all_pattern_health()
        
        # Calculate statistics
        total_patterns = len(health_data)
        avg_health = np.mean([p.health_score for p in health_data]) if health_data else 0
        
        # Count by tier and trend
        tier_counts = {'gold': 0, 'silver': 0, 'bronze': 0}
        trend_counts = {'rising': 0, 'stable': 0, 'declining': 0}
        
        for pattern in health_data:
            if pattern.tier in tier_counts:
                tier_counts[pattern.tier] += 1
            if pattern.trend in trend_counts:
                trend_counts[pattern.trend] += 1
        
        report_lines = [
            "# Pattern Health Dashboard Summary",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overall Statistics",
            f"- **Total Patterns**: {total_patterns}",
            f"- **Average Health Score**: {avg_health:.1f}",
            "",
            "## Tier Distribution",
            f"- **Gold**: {tier_counts['gold']} ({tier_counts['gold']/total_patterns*100:.1f}%)",
            f"- **Silver**: {tier_counts['silver']} ({tier_counts['silver']/total_patterns*100:.1f}%)",
            f"- **Bronze**: {tier_counts['bronze']} ({tier_counts['bronze']/total_patterns*100:.1f}%)",
            "",
            "## Trend Analysis",
            f"- **Rising**: {trend_counts['rising']} patterns",
            f"- **Stable**: {trend_counts['stable']} patterns",
            f"- **Declining**: {trend_counts['declining']} patterns",
            "",
            "## Top 10 Healthiest Patterns",
            ""
        ]
        
        # Add top patterns
        for i, pattern in enumerate(health_data[:10], 1):
            tier_emoji = {'gold': '🏆', 'silver': '🥈', 'bronze': '🥉'}[pattern.tier]
            trend_emoji = {'rising': '📈', 'stable': '↔️', 'declining': '📉'}[pattern.trend]
            
            report_lines.append(
                f"{i}. **{pattern.pattern_name}** {tier_emoji} {trend_emoji} - "
                f"Score: {pattern.health_score:.1f}"
            )
        
        report_lines.extend([
            "",
            "## Patterns Needing Attention",
            ""
        ])
        
        # Find patterns with low health or declining trend
        attention_patterns = [p for p in health_data 
                            if p.health_score < 40 or p.trend == 'declining']
        
        if attention_patterns:
            for pattern in attention_patterns[:10]:
                reason = []
                if pattern.health_score < 40:
                    reason.append(f"Low health score: {pattern.health_score:.1f}")
                if pattern.trend == 'declining':
                    reason.append("Declining trend")
                
                report_lines.append(
                    f"- **{pattern.pattern_name}** - {', '.join(reason)}"
                )
        else:
            report_lines.append("- No patterns currently need attention")
        
        report_lines.extend([
            "",
            "## Visualizations",
            "- [Tier Distribution](tier_distribution.png)",
            "- [Health Score Distribution](health_histogram.png)",
            "- [Top Patterns](top_patterns.png)",
            "- [Trend Charts](trends/)",
            ""
        ])
        
        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Summary report saved to {output_path}")
    
    def export_quarterly_data(self, output_path: Path):
        """Export data for quarterly review"""
        health_data = self.get_all_pattern_health()
        
        # Prepare export data
        export_data = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_patterns': len(health_data),
                'average_health': np.mean([p.health_score for p in health_data]) if health_data else 0,
                'tier_distribution': {},
                'trend_distribution': {}
            },
            'patterns': []
        }
        
        # Calculate distributions
        for pattern in health_data:
            # Update tier distribution
            tier = pattern.tier
            export_data['summary']['tier_distribution'][tier] = \
                export_data['summary']['tier_distribution'].get(tier, 0) + 1
            
            # Update trend distribution
            trend = pattern.trend
            export_data['summary']['trend_distribution'][trend] = \
                export_data['summary']['trend_distribution'].get(trend, 0) + 1
            
            # Add pattern data
            export_data['patterns'].append({
                'name': pattern.pattern_name,
                'health_score': pattern.health_score,
                'tier': pattern.tier,
                'trend': pattern.trend,
                'github_stars': pattern.github_stars,
                'stack_overflow_questions': pattern.stack_overflow_questions,
                'conference_talks': pattern.conference_talks,
                'job_postings': pattern.job_postings,
                'last_updated': pattern.last_updated
            })
        
        # Write export file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Quarterly review data exported to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate pattern health dashboard')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--output-dir', type=Path, default=Path('health-dashboard'),
                       help='Output directory for dashboard')
    parser.add_argument('--data-dir', type=Path,
                       help='Directory for storing health data')
    parser.add_argument('--pattern', help='Generate trend chart for specific pattern')
    parser.add_argument('--export-quarterly', action='store_true',
                       help='Export data for quarterly review')
    
    args = parser.parse_args()
    
    # Ensure patterns directory exists
    if not args.patterns_dir.exists():
        logger.error(f"Patterns directory not found: {args.patterns_dir}")
        return 1
    
    # Initialize dashboard
    dashboard = PatternHealthDashboard(args.patterns_dir, args.data_dir)
    
    if args.pattern:
        # Generate trend chart for specific pattern
        output_path = args.output_dir / f'{args.pattern}_trend.png'
        args.output_dir.mkdir(parents=True, exist_ok=True)
        dashboard.generate_trend_chart(args.pattern, output_path)
        print(f"Trend chart saved to: {output_path}")
    elif args.export_quarterly:
        # Export quarterly data
        output_path = args.output_dir / f'quarterly_review_{datetime.now().strftime("%Y%m%d")}.json'
        args.output_dir.mkdir(parents=True, exist_ok=True)
        dashboard.export_quarterly_data(output_path)
        print(f"Quarterly data exported to: {output_path}")
    else:
        # Generate full dashboard
        dashboard.generate_dashboard(args.output_dir)
        print(f"\nDashboard generated in: {args.output_dir}")
        print(f"  - View summary: {args.output_dir}/health_summary.md")
        print(f"  - View charts: {args.output_dir}/*.png")
    
    return 0

if __name__ == '__main__':
    exit(main())