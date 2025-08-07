#!/usr/bin/env python3
"""
Pattern Library Search Index Builder

This script creates a comprehensive searchable index of all patterns in the library:
- Extracts metadata from pattern files
- Builds keyword mappings and inverted index
- Creates search suggestions and synonyms
- Generates JSON search index for frontend
- Provides search analytics and insights

Usage:
    python build_pattern_search_index.py [--output-dir OUTPUT_DIR] [--analytics]
"""

import os
import re
import json
import argparse
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional
import yaml
import unicodedata

class PatternSearchIndexBuilder:
    """Builds comprehensive search index for pattern library"""
    
    def __init__(self, pattern_dir: str, output_dir: str = None):
        self.pattern_dir = Path(pattern_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "search_index"
        self.output_dir.mkdir(exist_ok=True)
        
        # Core data structures
        self.patterns = []
        self.inverted_index = defaultdict(set)  # word -> pattern_ids
        self.category_index = defaultdict(list)  # category -> patterns  
        self.tag_index = defaultdict(list)  # tag -> patterns
        self.company_index = defaultdict(list)  # company -> patterns
        self.metadata_stats = defaultdict(Counter)
        
        # Search optimization
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'with', 'will', 'this', 'that', 'they', 'them',
            'their', 'there', 'these', 'those', 'when', 'where', 'who', 'what'
        }
        
        # Synonyms for better search
        self.synonyms = {
            'microservice': ['microservices', 'service', 'services'],
            'database': ['db', 'data', 'storage', 'persistence'],
            'cache': ['caching', 'cached', 'memory'],
            'load': ['traffic', 'requests', 'throughput'],
            'failure': ['fault', 'error', 'crash', 'down'],
            'scale': ['scaling', 'scalability', 'growth'],
            'async': ['asynchronous', 'non-blocking', 'concurrent'],
            'sync': ['synchronous', 'blocking', 'sequential'],
            'consistency': ['consistent', 'consensus', 'agreement'],
            'partition': ['shard', 'sharding', 'split', 'distribute'],
            'queue': ['queuing', 'messaging', 'buffer'],
            'timeout': ['deadline', 'expiry', 'limit'],
            'retry': ['retries', 'repeat', 'attempt'],
            'circuit': ['breaker', 'protection', 'isolation'],
            'leader': ['master', 'primary', 'coordinator'],
            'follower': ['slave', 'secondary', 'replica'],
            'event': ['events', 'message', 'notification'],
            'stream': ['streaming', 'flow', 'pipeline'],
            'api': ['rest', 'endpoint', 'interface'],
            'security': ['auth', 'authentication', 'authorization'],
            'monitoring': ['observability', 'metrics', 'logging'],
            'deployment': ['deploy', 'release', 'rollout'],
            'container': ['docker', 'kubernetes', 'k8s'],
            'cloud': ['aws', 'azure', 'gcp', 'multi-cloud'],
            'real-time': ['realtime', 'live', 'instant'],
            'distributed': ['decentralized', 'federated', 'multi-node']
        }
        
        # Pattern complexity indicators  
        self.complexity_keywords = {
            'simple': ['basic', 'simple', 'easy', 'straightforward'],
            'medium': ['intermediate', 'moderate', 'standard'], 
            'complex': ['advanced', 'complex', 'sophisticated', 'enterprise']
        }
        
        # Industry/domain keywords
        self.domain_keywords = {
            'fintech': ['banking', 'payment', 'finance', 'trading', 'ledger'],
            'ecommerce': ['shopping', 'order', 'cart', 'inventory', 'fulfillment'],
            'social': ['social', 'feed', 'timeline', 'notification', 'chat'],
            'gaming': ['game', 'gaming', 'realtime', 'leaderboard', 'multiplayer'],
            'iot': ['iot', 'sensor', 'device', 'telemetry', 'edge'],
            'ml': ['machine learning', 'ai', 'model', 'training', 'inference'],
            'media': ['video', 'streaming', 'content', 'cdn', 'encoding']
        }

    def extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---\n'):
            return {}, content
            
        try:
            # Find end of frontmatter
            end_index = content.find('\n---\n', 4)
            if end_index == -1:
                return {}, content
                
            frontmatter_yaml = content[4:end_index]
            body = content[end_index + 5:]
            
            metadata = yaml.safe_load(frontmatter_yaml) or {}
            return metadata, body
            
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return {}, content

    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent indexing"""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def tokenize_text(self, text: str) -> List[str]:
        """Extract meaningful tokens from text"""
        if not text:
            return []
            
        # Normalize first
        text = self.normalize_text(text)
        
        # Extract words (including hyphenated terms)
        words = re.findall(r'\b[\w-]+\b', text)
        
        # Filter stop words and short words
        meaningful_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        ]
        
        # Add variations and synonyms
        enriched_words = set(meaningful_words)
        for word in meaningful_words:
            # Add synonym variations
            if word in self.synonyms:
                enriched_words.update(self.synonyms[word])
            
            # Add stemmed versions (simple stemming)
            if word.endswith('ing'):
                enriched_words.add(word[:-3])
            elif word.endswith('ed'):
                enriched_words.add(word[:-2])
            elif word.endswith('s') and not word.endswith('ss'):
                enriched_words.add(word[:-1])
        
        return list(enriched_words)

    def extract_code_examples(self, content: str) -> List[str]:
        """Extract code snippets and technical terms"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        inline_code = re.findall(r'`([^`]+)`', content)
        
        tech_terms = []
        for block in code_blocks + inline_code:
            # Extract class names, function names, etc.
            terms = re.findall(r'\b[A-Z][a-zA-Z]*|[a-z][a-zA-Z]*(?:[A-Z][a-zA-Z]*)+\b', block)
            tech_terms.extend(terms)
        
        return tech_terms

    def extract_companies(self, content: str, metadata: Dict) -> List[str]:
        """Extract company names from content and metadata"""
        companies = set()
        
        # From metadata
        if 'modern_examples' in metadata and isinstance(metadata['modern_examples'], list):
            for example in metadata['modern_examples']:
                if isinstance(example, dict) and 'company' in example:
                    companies.add(example['company'].lower())
        
        # Common company patterns in content
        company_patterns = [
            r'\b(netflix|google|amazon|microsoft|meta|facebook|uber|airbnb|spotify|stripe|twitch|discord|zoom|slack|dropbox|github|twitter|linkedin|pinterest|reddit|snapchat|tiktok|instacart|doordash|lyft|tesla|apple|salesforce|oracle|ibm|yahoo|paypal|ebay|booking|expedia)\b',
            r'\b(aws|azure|gcp|google cloud)\b'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            companies.update(match.lower() for match in matches)
        
        return list(companies)

    def calculate_search_score(self, pattern: Dict, keywords: List[str]) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        
        # Title matches (highest weight)
        title_words = self.tokenize_text(pattern.get('title', ''))
        title_matches = sum(1 for kw in keywords if kw in title_words)
        score += title_matches * 10
        
        # Description matches (high weight) 
        desc_words = self.tokenize_text(pattern.get('description', ''))
        desc_matches = sum(1 for kw in keywords if kw in desc_words)
        score += desc_matches * 5
        
        # Tag matches (medium-high weight)
        tags = pattern.get('tags', [])
        tag_matches = sum(1 for kw in keywords if any(kw in tag.lower() for tag in tags))
        score += tag_matches * 3
        
        # Content matches (medium weight)
        content_words = pattern.get('content_tokens', [])
        content_matches = sum(1 for kw in keywords if kw in content_words)
        score += content_matches * 1
        
        # Company matches (medium weight)
        companies = pattern.get('companies', [])
        company_matches = sum(1 for kw in keywords if kw in companies)
        score += company_matches * 3
        
        # Excellence tier boost
        tier_boost = {'gold': 1.5, 'silver': 1.2, 'bronze': 0.8}.get(
            pattern.get('excellence_tier'), 1.0
        )
        score *= tier_boost
        
        # Relevance boost
        relevance_boost = {
            'mainstream': 1.3, 'growing': 1.2, 'declining': 0.7, 'niche': 0.9
        }.get(pattern.get('current_relevance'), 1.0)
        score *= relevance_boost
        
        return score

    def process_pattern_file(self, file_path: Path) -> Optional[Dict]:
        """Process a single pattern file and extract searchable data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter and body
            metadata, body = self.extract_frontmatter(content)
            
            # Skip non-pattern files
            if metadata.get('type') != 'pattern' and 'pattern' not in str(file_path).lower():
                return None
            
            # Generate unique ID
            pattern_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
            
            # Extract searchable content
            full_content = f"{metadata.get('title', '')} {metadata.get('description', '')} {body}"
            content_tokens = self.tokenize_text(full_content)
            code_terms = self.extract_code_examples(body)
            companies = self.extract_companies(body, metadata)
            
            # Extract tags from multiple sources
            tags = []
            if 'tags' in metadata:
                tags.extend(metadata['tags'] if isinstance(metadata['tags'], list) else [metadata['tags']])
            
            # Infer tags from content
            for domain, keywords in self.domain_keywords.items():
                if any(kw in full_content.lower() for kw in keywords):
                    tags.append(domain)
            
            # Complexity tags
            for complexity, keywords in self.complexity_keywords.items():
                if any(kw in full_content.lower() for kw in keywords):
                    tags.append(complexity)
                    break
            
            # Build pattern data
            pattern_data = {
                'id': pattern_id,
                'title': metadata.get('title', file_path.stem.replace('-', ' ').title()),
                'description': metadata.get('description', ''),
                'file_path': str(file_path.relative_to(self.pattern_dir)),
                'url': f"/pattern-library/{file_path.relative_to(self.pattern_dir).with_suffix('')}",
                'category': metadata.get('category', 'other'),
                'excellence_tier': metadata.get('excellence_tier', 'silver'),
                'pattern_status': metadata.get('pattern_status', 'stable'),
                'difficulty': metadata.get('difficulty', 'intermediate'),
                'reading_time': metadata.get('reading_time', '15 min'),
                'current_relevance': metadata.get('current_relevance', 'mainstream'),
                'introduced': metadata.get('introduced'),
                'best_for': metadata.get('best_for', []),
                'prerequisites': metadata.get('prerequisites', []),
                'tags': list(set(tags)),
                'companies': companies,
                'content_tokens': content_tokens[:100],  # Limit for performance
                'code_terms': code_terms[:50],
                'word_count': len(content_tokens),
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'trade_offs': metadata.get('trade_offs', {}),
                'modern_examples': metadata.get('modern_examples', []),
                'essential_question': metadata.get('essential_question', ''),
            }
            
            # Update statistics
            self.metadata_stats['categories'][pattern_data['category']] += 1
            self.metadata_stats['tiers'][pattern_data['excellence_tier']] += 1  
            self.metadata_stats['status'][pattern_data['pattern_status']] += 1
            self.metadata_stats['difficulty'][pattern_data['difficulty']] += 1
            self.metadata_stats['relevance'][pattern_data['current_relevance']] += 1
            
            return pattern_data
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def build_inverted_index(self):
        """Build inverted index for fast text search"""
        print("Building inverted index...")
        
        for pattern in self.patterns:
            pattern_id = pattern['id']
            
            # Index all searchable text
            searchable_text = [
                pattern['title'],
                pattern['description'], 
                pattern['category'],
                pattern['excellence_tier'],
                pattern['pattern_status'],
                pattern['essential_question']
            ]
            
            # Add arrays
            searchable_text.extend(pattern['tags'])
            searchable_text.extend(pattern['companies'])
            searchable_text.extend(pattern['content_tokens'])
            searchable_text.extend(pattern['code_terms'])
            
            if isinstance(pattern['best_for'], list):
                searchable_text.extend(pattern['best_for'])
            elif pattern['best_for']:
                searchable_text.append(pattern['best_for'])
            
            # Tokenize and add to inverted index
            all_tokens = []
            for text in searchable_text:
                if text:
                    all_tokens.extend(self.tokenize_text(str(text)))
            
            # Add to inverted index
            for token in set(all_tokens):  # Remove duplicates
                self.inverted_index[token].add(pattern_id)

    def build_category_indexes(self):
        """Build category-based indexes"""
        print("Building category indexes...")
        
        for pattern in self.patterns:
            # Category index
            self.category_index[pattern['category']].append(pattern['id'])
            
            # Tag index
            for tag in pattern['tags']:
                self.tag_index[tag].append(pattern['id'])
            
            # Company index  
            for company in pattern['companies']:
                self.company_index[company].append(pattern['id'])

    def generate_search_suggestions(self) -> List[Dict]:
        """Generate search suggestions based on content analysis"""
        suggestions = []
        
        # Most common terms
        term_frequency = Counter()
        for terms in self.inverted_index.keys():
            term_frequency[terms] += len(self.inverted_index[terms])
        
        # Popular search terms
        popular_terms = [
            'circuit breaker', 'microservices', 'load balancing', 'caching',
            'event sourcing', 'saga', 'api gateway', 'service mesh',
            'sharding', 'retry', 'timeout', 'health check', 'monitoring',
            'kubernetes', 'docker', 'aws', 'netflix', 'uber', 'google'
        ]
        
        for term in popular_terms:
            pattern_count = len(self.search_patterns(term)[:10])
            if pattern_count > 0:
                suggestions.append({
                    'query': term,
                    'pattern_count': pattern_count,
                    'category': 'popular'
                })
        
        # Company-based suggestions
        for company, pattern_ids in self.company_index.items():
            if len(pattern_ids) >= 2:  # Only companies with multiple patterns
                suggestions.append({
                    'query': company,
                    'pattern_count': len(pattern_ids),
                    'category': 'company'
                })
        
        # Category suggestions
        for category, pattern_ids in self.category_index.items():
            suggestions.append({
                'query': category.replace('-', ' '),
                'pattern_count': len(pattern_ids),
                'category': 'topic'
            })
        
        return sorted(suggestions, key=lambda x: x['pattern_count'], reverse=True)

    def search_patterns(self, query: str, limit: int = 50) -> List[Dict]:
        """Search patterns using the inverted index"""
        if not query:
            return []
        
        # Tokenize query
        query_tokens = self.tokenize_text(query)
        if not query_tokens:
            return []
        
        # Find matching patterns
        pattern_scores = defaultdict(float)
        
        for token in query_tokens:
            # Direct matches
            if token in self.inverted_index:
                for pattern_id in self.inverted_index[token]:
                    pattern_scores[pattern_id] += 1.0
            
            # Partial matches
            for indexed_token in self.inverted_index.keys():
                if token in indexed_token or indexed_token in token:
                    for pattern_id in self.inverted_index[indexed_token]:
                        pattern_scores[pattern_id] += 0.5
        
        # Get pattern objects and calculate final scores
        results = []
        pattern_lookup = {p['id']: p for p in self.patterns}
        
        for pattern_id, base_score in pattern_scores.items():
            if pattern_id in pattern_lookup:
                pattern = pattern_lookup[pattern_id]
                final_score = base_score + self.calculate_search_score(pattern, query_tokens)
                results.append({**pattern, 'search_score': final_score})
        
        # Sort by relevance score
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results[:limit]

    def export_search_index(self):
        """Export search index to JSON files"""
        print(f"Exporting search index to {self.output_dir}...")
        
        # Main pattern index
        with open(self.output_dir / 'patterns.json', 'w') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
        
        # Inverted index (convert sets to lists for JSON)
        inverted_index_json = {
            term: list(pattern_ids) 
            for term, pattern_ids in self.inverted_index.items()
        }
        with open(self.output_dir / 'inverted_index.json', 'w') as f:
            json.dump(inverted_index_json, f, indent=2)
        
        # Category indexes
        with open(self.output_dir / 'category_index.json', 'w') as f:
            json.dump(dict(self.category_index), f, indent=2)
        
        with open(self.output_dir / 'tag_index.json', 'w') as f:
            json.dump(dict(self.tag_index), f, indent=2)
        
        with open(self.output_dir / 'company_index.json', 'w') as f:
            json.dump(dict(self.company_index), f, indent=2)
        
        # Search suggestions
        suggestions = self.generate_search_suggestions()
        with open(self.output_dir / 'search_suggestions.json', 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        # Metadata and stats
        metadata = {
            'total_patterns': len(self.patterns),
            'build_time': datetime.now().isoformat(),
            'categories': dict(self.metadata_stats['categories']),
            'excellence_tiers': dict(self.metadata_stats['tiers']),
            'pattern_status': dict(self.metadata_stats['status']),
            'difficulty_levels': dict(self.metadata_stats['difficulty']),
            'relevance_status': dict(self.metadata_stats['relevance']),
            'total_search_terms': len(self.inverted_index),
            'avg_tokens_per_pattern': sum(len(p['content_tokens']) for p in self.patterns) / len(self.patterns) if self.patterns else 0
        }
        
        with open(self.output_dir / 'search_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Exported {len(self.patterns)} patterns with {len(self.inverted_index)} search terms")

    def generate_search_analytics(self):
        """Generate comprehensive analytics about the pattern library"""
        print("Generating search analytics...")
        
        analytics = {
            'overview': {
                'total_patterns': len(self.patterns),
                'total_search_terms': len(self.inverted_index),
                'avg_pattern_length': sum(p['word_count'] for p in self.patterns) / len(self.patterns) if self.patterns else 0,
                'categories': len(self.category_index),
                'companies_mentioned': len(self.company_index),
                'unique_tags': len(self.tag_index)
            },
            
            'pattern_distribution': {
                'by_category': dict(self.metadata_stats['categories']),
                'by_tier': dict(self.metadata_stats['tiers']),
                'by_difficulty': dict(self.metadata_stats['difficulty']),
                'by_relevance': dict(self.metadata_stats['relevance']),
                'by_status': dict(self.metadata_stats['status'])
            },
            
            'content_analysis': {
                'most_common_terms': dict(Counter([
                    term for pattern in self.patterns 
                    for term in pattern['content_tokens'][:20]  # Top terms per pattern
                ]).most_common(50)),
                
                'most_mentioned_companies': dict(Counter([
                    company for pattern in self.patterns 
                    for company in pattern['companies']
                ]).most_common(20)),
                
                'popular_tags': dict(Counter([
                    tag for pattern in self.patterns 
                    for tag in pattern['tags']
                ]).most_common(30)),
            },
            
            'search_optimization': {
                'synonym_coverage': len(self.synonyms),
                'patterns_per_term': {
                    term: len(pattern_ids) 
                    for term, pattern_ids in list(self.inverted_index.items())[:100]
                },
                'searchability_score': sum(
                    len(p['content_tokens']) + len(p['tags']) * 2 + len(p['companies']) * 3
                    for p in self.patterns
                ) / len(self.patterns) if self.patterns else 0
            },
            
            'quality_metrics': {
                'patterns_with_descriptions': sum(1 for p in self.patterns if p['description']),
                'patterns_with_examples': sum(1 for p in self.patterns if p['modern_examples']),
                'patterns_with_companies': sum(1 for p in self.patterns if p['companies']),
                'patterns_with_tags': sum(1 for p in self.patterns if p['tags']),
                'gold_tier_percentage': self.metadata_stats['tiers']['gold'] / len(self.patterns) * 100 if self.patterns else 0
            },
            
            'recommendations': self._generate_content_recommendations()
        }
        
        with open(self.output_dir / 'search_analytics.json', 'w') as f:
            json.dump(analytics, f, indent=2)
        
        return analytics

    def _generate_content_recommendations(self) -> List[Dict]:
        """Generate recommendations for improving search experience"""
        recommendations = []
        
        # Patterns with poor searchability
        low_searchable = [
            p for p in self.patterns 
            if len(p['content_tokens']) < 10 and len(p['tags']) < 2
        ]
        if low_searchable:
            recommendations.append({
                'type': 'content_improvement',
                'priority': 'high',
                'description': f"{len(low_searchable)} patterns need better descriptions/tags",
                'affected_patterns': [p['title'] for p in low_searchable[:10]]
            })
        
        # Categories with few patterns
        small_categories = [
            cat for cat, patterns in self.category_index.items() 
            if len(patterns) < 3
        ]
        if small_categories:
            recommendations.append({
                'type': 'category_consolidation',
                'priority': 'medium',
                'description': f"Consider consolidating small categories: {', '.join(small_categories)}"
            })
        
        # Missing company examples
        no_examples = [
            p for p in self.patterns 
            if not p['companies'] and p['excellence_tier'] == 'gold'
        ]
        if no_examples:
            recommendations.append({
                'type': 'example_enrichment',
                'priority': 'medium',
                'description': f"{len(no_examples)} gold-tier patterns lack company examples"
            })
        
        return recommendations

    def build_index(self):
        """Main method to build the complete search index"""
        print("🔍 Building Pattern Library Search Index...")
        print(f"📁 Processing patterns from: {self.pattern_dir}")
        
        # Find all pattern files
        pattern_files = list(self.pattern_dir.rglob('*.md'))
        print(f"📄 Found {len(pattern_files)} markdown files")
        
        # Process each file
        processed_count = 0
        for file_path in pattern_files:
            pattern_data = self.process_pattern_file(file_path)
            if pattern_data:
                self.patterns.append(pattern_data)
                processed_count += 1
                
                if processed_count % 20 == 0:
                    print(f"⏳ Processed {processed_count} patterns...")
        
        print(f"✅ Successfully processed {len(self.patterns)} patterns")
        
        # Build indexes
        self.build_inverted_index()
        self.build_category_indexes()
        
        # Export everything
        self.export_search_index()
        
        return self.generate_search_analytics()

    def demo_search_queries(self):
        """Demonstrate search functionality with example queries"""
        print("\n🔍 Demo Search Queries:")
        print("=" * 50)
        
        demo_queries = [
            "circuit breaker",
            "microservices scaling", 
            "netflix patterns",
            "database sharding",
            "event driven",
            "kubernetes deployment",
            "saga transaction",
            "api gateway",
            "caching strategies",
            "fault tolerance"
        ]
        
        for query in demo_queries:
            results = self.search_patterns(query, limit=5)
            print(f"\n🔎 Query: '{query}' ({len(results)} results)")
            
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result['title']} ({result['excellence_tier']}) - {result['search_score']:.1f}")
                print(f"     {result['description'][:80]}...")
        
        print("\n" + "=" * 50)


def create_example_search_queries():
    """Create example search queries file for documentation"""
    examples = {
        "basic_queries": {
            "description": "Simple keyword searches",
            "examples": [
                {"query": "circuit breaker", "expected": "Resilience patterns for preventing cascading failures"},
                {"query": "microservices", "expected": "Architecture patterns for service decomposition"},
                {"query": "caching", "expected": "Performance patterns for data access optimization"},
                {"query": "load balancer", "expected": "Scaling patterns for traffic distribution"},
                {"query": "event sourcing", "expected": "Data management patterns for audit trails"}
            ]
        },
        
        "company_queries": {
            "description": "Find patterns used by specific companies",
            "examples": [
                {"query": "netflix", "expected": "Patterns proven at Netflix scale"},
                {"query": "uber", "expected": "Real-time and geo-distributed patterns"},
                {"query": "google", "expected": "Large-scale infrastructure patterns"},
                {"query": "amazon", "expected": "E-commerce and cloud patterns"}
            ]
        },
        
        "problem_queries": {
            "description": "Find patterns by problem domain",
            "examples": [
                {"query": "failure handling", "expected": "Resilience patterns for fault tolerance"},
                {"query": "data consistency", "expected": "Patterns for distributed data management"},
                {"query": "real-time", "expected": "Patterns for live data processing"},
                {"query": "high availability", "expected": "Patterns for system uptime"},
                {"query": "performance", "expected": "Optimization patterns for speed"}
            ]
        },
        
        "technical_queries": {
            "description": "Technology-specific searches",
            "examples": [
                {"query": "kubernetes", "expected": "Container orchestration patterns"},
                {"query": "graphql", "expected": "API federation and gateway patterns"},
                {"query": "kafka", "expected": "Event streaming and messaging patterns"},
                {"query": "redis", "expected": "Caching and session management patterns"}
            ]
        },
        
        "composite_queries": {
            "description": "Multi-word complex searches",
            "examples": [
                {"query": "distributed transaction", "expected": "Saga and 2PC patterns"},
                {"query": "service mesh security", "expected": "Zero-trust and mTLS patterns"},
                {"query": "machine learning deployment", "expected": "ML infrastructure patterns"},
                {"query": "multi-region database", "expected": "Geo-replication patterns"}
            ]
        },
        
        "filter_examples": {
            "description": "Category and tier filtering",
            "examples": [
                {"category": "resilience", "tier": "gold", "expected": "Battle-tested resilience patterns"},
                {"category": "scaling", "difficulty": "beginner", "expected": "Simple scaling solutions"},
                {"tier": "bronze", "expected": "Legacy patterns to avoid"},
                {"relevance": "growing", "expected": "Trending modern patterns"}
            ]
        }
    }
    
    return examples


def main():
    parser = argparse.ArgumentParser(description='Build Pattern Library Search Index')
    parser.add_argument('--pattern-dir', 
                       default='/home/deepak/DStudio/docs/pattern-library',
                       help='Directory containing pattern files')
    parser.add_argument('--output-dir',
                       default='/home/deepak/DStudio/scripts/search_index', 
                       help='Output directory for search index files')
    parser.add_argument('--analytics', action='store_true',
                       help='Generate detailed analytics report')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo search queries')
    
    args = parser.parse_args()
    
    # Build the search index
    builder = PatternSearchIndexBuilder(args.pattern_dir, args.output_dir)
    analytics = builder.build_index()
    
    # Create example queries
    examples = create_example_search_queries()
    with open(Path(args.output_dir) / 'example_search_queries.json', 'w') as f:
        json.dump(examples, f, indent=2)
    
    # Show demo if requested
    if args.demo:
        builder.demo_search_queries()
    
    # Print summary
    print(f"\n📊 Search Index Summary:")
    print(f"   Total Patterns: {analytics['overview']['total_patterns']}")
    print(f"   Search Terms: {analytics['overview']['total_search_terms']:,}")
    print(f"   Categories: {analytics['overview']['categories']}")
    print(f"   Companies: {analytics['overview']['companies_mentioned']}")
    print(f"   Gold Tier: {analytics['quality_metrics']['gold_tier_percentage']:.1f}%")
    
    # Show analytics if requested
    if args.analytics:
        print("\n📈 Detailed Analytics:")
        print(f"   Avg Pattern Length: {analytics['overview']['avg_pattern_length']:.0f} words")
        print(f"   Searchability Score: {analytics['search_optimization']['searchability_score']:.1f}")
        
        print(f"\n🏆 Top Categories:")
        for cat, count in sorted(analytics['pattern_distribution']['by_category'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {cat}: {count}")
        
        print(f"\n🏢 Top Companies:")
        for company, count in sorted(analytics['content_analysis']['most_mentioned_companies'].items(),
                                   key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {company}: {count}")
    
    print(f"\n✅ Search index saved to: {args.output_dir}")
    
    # Show file listing
    output_files = list(Path(args.output_dir).glob('*.json'))
    print(f"📁 Generated {len(output_files)} index files:")
    for file_path in sorted(output_files):
        size_mb = file_path.stat().st_size / 1024 / 1024
        print(f"   {file_path.name} ({size_mb:.2f}MB)")


if __name__ == "__main__":
    main()