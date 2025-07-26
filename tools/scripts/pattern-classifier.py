#!/usr/bin/env python3
"""
Pattern Classifier Script

Automatically classifies patterns based on excellence criteria:
- GitHub stars and activity
- Conference talks and presentations
- Job posting frequency
- Production adoption metrics

Generates health scores and tier recommendations.
"""

import os
import re
import json
import requests
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PatternMetrics:
    """Metrics for pattern classification"""
    github_stars: int = 0
    github_repos: int = 0
    conference_talks: int = 0
    job_postings: int = 0
    stack_overflow_questions: int = 0
    years_in_production: float = 0.0
    major_adopters: List[str] = None
    health_score: float = 0.0
    recommended_tier: str = "bronze"
    
    def __post_init__(self):
        if self.major_adopters is None:
            self.major_adopters = []

class PatternClassifier:
    """Classifies patterns based on various metrics"""
    
    def __init__(self, patterns_dir: Path, github_token: Optional[str] = None):
        self.patterns_dir = patterns_dir
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        self.github_headers = {}
        if self.github_token:
            self.github_headers['Authorization'] = f'token {self.github_token}'
        
        # Load pattern metadata if exists
        self.metadata_file = patterns_dir / 'pattern_metadata.json'
        self.metadata = self._load_metadata()
        
        # Tier thresholds
        self.tier_thresholds = {
            'gold': {
                'health_score': 80,
                'github_stars': 10000,
                'conference_talks': 20,
                'major_adopters': 5
            },
            'silver': {
                'health_score': 60,
                'github_stars': 1000,
                'conference_talks': 5,
                'major_adopters': 2
            },
            'bronze': {
                'health_score': 0,
                'github_stars': 0,
                'conference_talks': 0,
                'major_adopters': 0
            }
        }
    
    def _load_metadata(self) -> Dict:
        """Load existing pattern metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save pattern metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def search_github_repos(self, pattern_name: str) -> Tuple[int, int]:
        """Search GitHub for repositories mentioning the pattern"""
        try:
            # Clean pattern name for search
            search_term = pattern_name.replace('-', ' ')
            
            # Search for repositories
            url = f"https://api.github.com/search/repositories"
            params = {
                'q': f'"{search_term}" in:readme in:description',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100
            }
            
            response = requests.get(url, params=params, headers=self.github_headers)
            if response.status_code == 200:
                data = response.json()
                total_repos = data.get('total_count', 0)
                
                # Sum stars from top repositories
                total_stars = sum(repo.get('stargazers_count', 0) 
                                for repo in data.get('items', [])[:20])
                
                return total_stars, total_repos
            else:
                logger.warning(f"GitHub API error for {pattern_name}: {response.status_code}")
                return 0, 0
        except Exception as e:
            logger.error(f"Error searching GitHub for {pattern_name}: {e}")
            return 0, 0
    
    def search_conference_talks(self, pattern_name: str) -> int:
        """Estimate conference talks about the pattern"""
        # This would ideally use conference APIs or scraping
        # For now, use a simple estimation based on pattern popularity
        known_talks = {
            'event-sourcing': 50,
            'cqrs': 45,
            'circuit-breaker': 40,
            'saga-pattern': 35,
            'service-mesh': 60,
            'api-gateway': 55,
            'leader-election': 30,
            'consensus': 40,
            'distributed-lock': 25,
            'sharding': 45,
            'consistent-hashing': 30,
            'gossip-protocol': 20,
            'heartbeat': 15,
            'bulkhead': 20,
            'retry': 25,
            'timeout': 20,
            'rate-limiting': 30,
            'load-balancing': 40,
            'service-discovery': 35,
            'health-check': 25,
            'distributed-tracing': 30,
            'blue-green-deployment': 35,
            'canary-deployment': 40,
            'feature-toggle': 30,
            'strangler-fig': 25,
            'ambassador': 20,
            'sidecar': 35,
            'adapter': 15,
            'anti-corruption-layer': 20,
            'bff': 25,
            'choreography': 20,
            'orchestration': 30,
            'distributed-queue': 25,
            'write-behind-cache': 20,
            'read-through-cache': 15,
            'cache-aside': 20,
            'geo-replication': 25,
            'leader-follower': 20,
            'peer-to-peer': 15,
            'master-slave': 10,
            'publish-subscribe': 30,
            'request-reply': 15,
            'competing-consumers': 20,
            'priority-queue': 15,
            'claim-check': 10,
            'pipes-and-filters': 15,
            'routing-slip': 10,
            'scatter-gather': 15,
            'splitter': 10,
            'aggregator': 15,
            'resequencer': 10,
            'content-based-router': 15,
            'message-translator': 10,
            'envelope-wrapper': 10,
            'data-mapper': 15,
            'shared-database': 20,
            'database-per-service': 35,
            'polyglot-persistence': 25,
            'transactional-outbox': 20,
            'change-data-capture': 30,
            'event-carried-state': 15,
            'correlation-id': 20
        }
        
        return known_talks.get(pattern_name, 5)
    
    def search_job_postings(self, pattern_name: str) -> int:
        """Estimate job postings mentioning the pattern"""
        # This would ideally use job board APIs
        # For now, use estimation based on industry adoption
        job_frequency = {
            'microservices': 1000,
            'event-sourcing': 150,
            'cqrs': 120,
            'circuit-breaker': 200,
            'api-gateway': 500,
            'service-mesh': 300,
            'distributed-tracing': 250,
            'load-balancing': 600,
            'service-discovery': 400,
            'rate-limiting': 350,
            'sharding': 400,
            'consistent-hashing': 150,
            'leader-election': 100,
            'consensus': 80,
            'saga-pattern': 100,
            'blue-green-deployment': 300,
            'canary-deployment': 350,
            'feature-toggle': 400
        }
        
        # Default to 50 for unknown patterns
        return job_frequency.get(pattern_name, 50)
    
    def search_stack_overflow(self, pattern_name: str) -> int:
        """Search Stack Overflow for questions about the pattern"""
        try:
            # Stack Overflow API
            url = "https://api.stackexchange.com/2.3/search"
            params = {
                'intitle': pattern_name.replace('-', ' '),
                'site': 'stackoverflow',
                'pagesize': 1
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('total', 0)
            else:
                logger.warning(f"Stack Overflow API error for {pattern_name}")
                return 0
        except Exception as e:
            logger.error(f"Error searching Stack Overflow for {pattern_name}: {e}")
            return 0
    
    def extract_pattern_info(self, pattern_file: Path) -> Dict:
        """Extract pattern information from markdown file"""
        with open(pattern_file, 'r') as f:
            content = f.read()
        
        # Extract front matter
        front_matter = {}
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                yaml_content = content[3:end_idx]
                try:
                    front_matter = yaml.safe_load(yaml_content) or {}
                except:
                    pass
        
        # Extract major adopters from modern_examples
        major_adopters = []
        if 'modern_examples' in front_matter:
            for example in front_matter.get('modern_examples', []):
                if isinstance(example, dict) and 'company' in example:
                    major_adopters.append(example['company'])
        
        # Calculate years in production
        years_in_production = 0
        if 'introduced' in front_matter:
            try:
                introduced_str = front_matter['introduced']
                # Handle YYYY-MM format
                if '-' in introduced_str:
                    year = int(introduced_str.split('-')[0])
                else:
                    year = int(introduced_str)
                years_in_production = datetime.now().year - year
            except:
                pass
        
        return {
            'front_matter': front_matter,
            'major_adopters': major_adopters,
            'years_in_production': years_in_production
        }
    
    def calculate_health_score(self, metrics: PatternMetrics) -> float:
        """Calculate overall health score (0-100)"""
        score = 0.0
        
        # GitHub popularity (25 points)
        if metrics.github_stars >= 50000:
            score += 25
        elif metrics.github_stars >= 10000:
            score += 20
        elif metrics.github_stars >= 5000:
            score += 15
        elif metrics.github_stars >= 1000:
            score += 10
        elif metrics.github_stars >= 500:
            score += 5
        
        # Conference talks (20 points)
        if metrics.conference_talks >= 50:
            score += 20
        elif metrics.conference_talks >= 20:
            score += 15
        elif metrics.conference_talks >= 10:
            score += 10
        elif metrics.conference_talks >= 5:
            score += 5
        
        # Job market demand (20 points)
        if metrics.job_postings >= 500:
            score += 20
        elif metrics.job_postings >= 200:
            score += 15
        elif metrics.job_postings >= 100:
            score += 10
        elif metrics.job_postings >= 50:
            score += 5
        
        # Production maturity (15 points)
        if metrics.years_in_production >= 20:
            score += 15
        elif metrics.years_in_production >= 10:
            score += 12
        elif metrics.years_in_production >= 5:
            score += 8
        elif metrics.years_in_production >= 2:
            score += 5
        
        # Major adopters (10 points)
        if len(metrics.major_adopters) >= 5:
            score += 10
        elif len(metrics.major_adopters) >= 3:
            score += 7
        elif len(metrics.major_adopters) >= 1:
            score += 5
        
        # Stack Overflow activity (10 points)
        if metrics.stack_overflow_questions >= 10000:
            score += 10
        elif metrics.stack_overflow_questions >= 5000:
            score += 7
        elif metrics.stack_overflow_questions >= 1000:
            score += 5
        elif metrics.stack_overflow_questions >= 500:
            score += 3
        
        return min(score, 100.0)
    
    def determine_tier(self, metrics: PatternMetrics) -> str:
        """Determine pattern tier based on metrics"""
        # Check gold criteria
        if (metrics.health_score >= self.tier_thresholds['gold']['health_score'] and
            metrics.github_stars >= self.tier_thresholds['gold']['github_stars'] and
            metrics.conference_talks >= self.tier_thresholds['gold']['conference_talks'] and
            len(metrics.major_adopters) >= self.tier_thresholds['gold']['major_adopters']):
            return 'gold'
        
        # Check silver criteria
        if (metrics.health_score >= self.tier_thresholds['silver']['health_score'] and
            metrics.github_stars >= self.tier_thresholds['silver']['github_stars'] and
            metrics.conference_talks >= self.tier_thresholds['silver']['conference_talks'] and
            len(metrics.major_adopters) >= self.tier_thresholds['silver']['major_adopters']):
            return 'silver'
        
        # Default to bronze
        return 'bronze'
    
    def classify_pattern(self, pattern_file: Path) -> PatternMetrics:
        """Classify a single pattern"""
        pattern_name = pattern_file.stem
        logger.info(f"Classifying pattern: {pattern_name}")
        
        # Check cache first
        cache_key = f"{pattern_name}_metrics"
        if cache_key in self.metadata:
            cache_data = self.metadata[cache_key]
            # Check if cache is fresh (less than 7 days old)
            if 'timestamp' in cache_data:
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time < timedelta(days=7):
                    logger.info(f"Using cached metrics for {pattern_name}")
                    metrics = PatternMetrics(**cache_data['metrics'])
                    return metrics
        
        # Extract pattern info from file
        pattern_info = self.extract_pattern_info(pattern_file)
        
        # Gather metrics
        metrics = PatternMetrics()
        
        # GitHub metrics
        github_stars, github_repos = self.search_github_repos(pattern_name)
        metrics.github_stars = github_stars
        metrics.github_repos = github_repos
        
        # Conference talks
        metrics.conference_talks = self.search_conference_talks(pattern_name)
        
        # Job postings
        metrics.job_postings = self.search_job_postings(pattern_name)
        
        # Stack Overflow
        metrics.stack_overflow_questions = self.search_stack_overflow(pattern_name)
        
        # Pattern-specific info
        metrics.major_adopters = pattern_info['major_adopters']
        metrics.years_in_production = pattern_info['years_in_production']
        
        # Calculate health score
        metrics.health_score = self.calculate_health_score(metrics)
        
        # Determine tier
        metrics.recommended_tier = self.determine_tier(metrics)
        
        # Cache the results
        self.metadata[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(metrics)
        }
        self._save_metadata()
        
        return metrics
    
    def classify_all_patterns(self) -> Dict[str, PatternMetrics]:
        """Classify all patterns in the directory"""
        results = {}
        
        # Find all pattern markdown files
        pattern_files = list(self.patterns_dir.glob('*.md'))
        pattern_files = [f for f in pattern_files if f.stem not in ['index', 'README']]
        
        logger.info(f"Found {len(pattern_files)} patterns to classify")
        
        for pattern_file in pattern_files:
            try:
                metrics = self.classify_pattern(pattern_file)
                results[pattern_file.stem] = metrics
            except Exception as e:
                logger.error(f"Error classifying {pattern_file.stem}: {e}")
        
        return results
    
    def generate_report(self, results: Dict[str, PatternMetrics], output_file: Path):
        """Generate classification report"""
        report_lines = [
            "# Pattern Classification Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total Patterns: {len(results)}",
            f"- Gold Tier: {sum(1 for m in results.values() if m.recommended_tier == 'gold')}",
            f"- Silver Tier: {sum(1 for m in results.values() if m.recommended_tier == 'silver')}",
            f"- Bronze Tier: {sum(1 for m in results.values() if m.recommended_tier == 'bronze')}",
            "",
            "## Pattern Details",
            ""
        ]
        
        # Sort patterns by health score
        sorted_patterns = sorted(results.items(), 
                               key=lambda x: x[1].health_score, 
                               reverse=True)
        
        for pattern_name, metrics in sorted_patterns:
            tier_emoji = {
                'gold': '🏆',
                'silver': '🥈',
                'bronze': '🥉'
            }.get(metrics.recommended_tier, '')
            
            report_lines.extend([
                f"### {pattern_name} {tier_emoji}",
                f"- **Health Score**: {metrics.health_score:.1f}/100",
                f"- **Recommended Tier**: {metrics.recommended_tier}",
                f"- **GitHub Stars**: {metrics.github_stars:,} (from {metrics.github_repos:,} repos)",
                f"- **Conference Talks**: {metrics.conference_talks}",
                f"- **Job Postings**: {metrics.job_postings:,}",
                f"- **Stack Overflow Questions**: {metrics.stack_overflow_questions:,}",
                f"- **Years in Production**: {metrics.years_in_production:.1f}",
                f"- **Major Adopters**: {', '.join(metrics.major_adopters) if metrics.major_adopters else 'None listed'}",
                ""
            ])
        
        # Write report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Report generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Classify patterns based on excellence criteria')
    parser.add_argument('--patterns-dir', type=Path, default=Path('docs/patterns'),
                       help='Directory containing pattern markdown files')
    parser.add_argument('--output', type=Path, default=Path('pattern_classification_report.md'),
                       help='Output report file')
    parser.add_argument('--github-token', help='GitHub API token for higher rate limits')
    parser.add_argument('--pattern', help='Classify a specific pattern only')
    
    args = parser.parse_args()
    
    # Ensure patterns directory exists
    if not args.patterns_dir.exists():
        logger.error(f"Patterns directory not found: {args.patterns_dir}")
        return 1
    
    # Initialize classifier
    classifier = PatternClassifier(args.patterns_dir, args.github_token)
    
    # Classify patterns
    if args.pattern:
        # Single pattern
        pattern_file = args.patterns_dir / f"{args.pattern}.md"
        if not pattern_file.exists():
            logger.error(f"Pattern file not found: {pattern_file}")
            return 1
        
        metrics = classifier.classify_pattern(pattern_file)
        print(f"\nPattern: {args.pattern}")
        print(f"Health Score: {metrics.health_score:.1f}/100")
        print(f"Recommended Tier: {metrics.recommended_tier}")
        print(f"GitHub Stars: {metrics.github_stars:,}")
        print(f"Conference Talks: {metrics.conference_talks}")
        print(f"Major Adopters: {', '.join(metrics.major_adopters) if metrics.major_adopters else 'None'}")
    else:
        # All patterns
        results = classifier.classify_all_patterns()
        classifier.generate_report(results, args.output)
        print(f"\nClassification complete. Report saved to: {args.output}")
    
    return 0

if __name__ == '__main__':
    exit(main())