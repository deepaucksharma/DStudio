#!/usr/bin/env python3
"""
Wrapper script to use existing pattern-health-metrics.json with dashboard
"""

import json
import sys
from pathlib import Path
import importlib.util
import argparse
import logging

# Load the pattern-health-dashboard module dynamically
dashboard_path = Path(__file__).parent / 'pattern-health-dashboard.py'
spec = importlib.util.spec_from_file_location("pattern_health_dashboard", dashboard_path)
pattern_health_dashboard = importlib.util.module_from_spec(spec)
sys.modules["pattern_health_dashboard"] = pattern_health_dashboard
spec.loader.exec_module(pattern_health_dashboard)

PatternHealthDashboard = pattern_health_dashboard.PatternHealthDashboard
PatternHealth = pattern_health_dashboard.PatternHealth
HealthTrend = pattern_health_dashboard.HealthTrend

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthDashboardWrapper(PatternHealthDashboard):
    """Wrapper that uses the existing pattern-health-metrics.json"""
    
    def __init__(self, patterns_dir: Path, data_dir: Path = None):
        # Initialize parent but don't load the default files
        self.patterns_dir = patterns_dir
        self.data_dir = data_dir or patterns_dir.parent.parent / 'health-data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the existing health metrics
        health_metrics_file = self.data_dir / 'pattern-health-metrics.json'
        if health_metrics_file.exists():
            with open(health_metrics_file, 'r') as f:
                self.health_data = json.load(f)
        else:
            logger.error(f"Health metrics file not found: {health_metrics_file}")
            self.health_data = {'patterns': []}
        
        # Convert to expected format
        self.history = {}
        self.current_metrics = {}
    
    def _normalize_trend(self, trend: str) -> str:
        """Normalize trend values from up/down/stable to rising/declining/stable"""
        trend_map = {
            'up': 'rising',
            'down': 'declining',
            'stable': 'stable'
        }
        return trend_map.get(trend, 'stable')
        
    def get_all_pattern_health(self):
        """Override to use the existing health data"""
        health_list = []
        
        for pattern in self.health_data.get('patterns', []):
            health = PatternHealth(
                pattern_name=pattern['name'],
                health_score=pattern.get('healthScore', 0),
                tier=pattern.get('tier', 'bronze'),
                github_stars=pattern.get('metrics', {}).get('githubStars', 0),
                stack_overflow_questions=0,  # Not in current data
                conference_talks=pattern.get('metrics', {}).get('conferenceTalks', 0),
                job_postings=pattern.get('metrics', {}).get('jobMentions', 0),
                trend=self._normalize_trend(pattern.get('trend', 'stable')),
                last_updated=self.health_data.get('lastUpdated', '')
            )
            health_list.append(health)
            
            # Store trend data for history
            if 'trendData' in pattern and pattern['trendData']:
                self.history[pattern['name']] = []
                # Create synthetic historical data from trend data
                trend_dates = self.health_data.get('trendDates', [])
                for i, score in enumerate(pattern['trendData']):
                    if i < len(trend_dates):
                        trend = HealthTrend(
                            date=f"{trend_dates[i]}-01T00:00:00",
                            health_score=score,
                            github_stars=pattern.get('metrics', {}).get('githubStars', 0),
                            stack_overflow_questions=0
                        )
                        self.history[pattern['name']].append(trend)
        
        return sorted(health_list, key=lambda x: x.health_score, reverse=True)
    
    def get_pattern_health(self, pattern_name: str):
        """Override to use the existing health data"""
        for pattern in self.health_data.get('patterns', []):
            if pattern['name'] == pattern_name:
                return PatternHealth(
                    pattern_name=pattern['name'],
                    health_score=pattern.get('healthScore', 0),
                    tier=pattern.get('tier', 'bronze'),
                    github_stars=pattern.get('metrics', {}).get('githubStars', 0),
                    stack_overflow_questions=0,
                    conference_talks=pattern.get('metrics', {}).get('conferenceTalks', 0),
                    job_postings=pattern.get('metrics', {}).get('jobMentions', 0),
                    trend=self._normalize_trend(pattern.get('trend', 'stable')),
                    last_updated=self.health_data.get('lastUpdated', '')
                )
        return None

def main():
    parser = argparse.ArgumentParser(description='Generate pattern health dashboard using existing metrics')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--output-dir', type=Path, default=Path('health-dashboard'),
                       help='Output directory for dashboard')
    parser.add_argument('--data-dir', type=Path,
                       help='Directory containing health data')
    
    args = parser.parse_args()
    
    # Use the wrapper dashboard
    dashboard = HealthDashboardWrapper(args.patterns_dir, args.data_dir)
    
    # Generate full dashboard
    dashboard.generate_dashboard(args.output_dir)
    print(f"\nDashboard generated in: {args.output_dir}")
    print(f"  - View summary: {args.output_dir}/health_summary.md")
    print(f"  - View charts: {args.output_dir}/*.png")
    
    return 0

if __name__ == '__main__':
    exit(main())
