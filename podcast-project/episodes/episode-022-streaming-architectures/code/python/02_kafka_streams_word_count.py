#!/usr/bin/env python3
"""
Episode 22: Streaming Architectures - Kafka Streams Word Count for Indian Social Media
Author: Code Developer Agent
Description: Real-time word count processing for Indian social media content analysis

Kafka Streams है stateful stream processing का powerful tool
यह Twitter/Instagram comments का real-time analysis करता है
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Mock Kafka Streams (replace with confluent-kafka in production)
class MockKafkaStreams:
    """Mock Kafka Streams for demonstration"""
    
    def __init__(self, application_id: str, bootstrap_servers: str):
        self.application_id = application_id
        self.bootstrap_servers = bootstrap_servers
        self.topology = StreamsTopology()
        self.state_stores = {}
        self.running = False
        print(f"🌊 Kafka Streams initialized: {application_id}")
    
    def stream(self, topic: str) -> 'StreamBuilder':
        """Create a stream from topic"""
        return StreamBuilder(topic, self)
    
    def table(self, topic: str, store_name: str) -> 'TableBuilder':
        """Create a table from topic"""
        return TableBuilder(topic, store_name, self)
    
    def start(self):
        """Start the streams application"""
        self.running = True
        print(f"🚀 Kafka Streams started: {self.application_id}")
    
    def close(self):
        """Close the streams application"""
        self.running = False
        print(f"🔚 Kafka Streams closed: {self.application_id}")

class StreamsTopology:
    """Kafka Streams topology builder"""
    
    def __init__(self):
        self.processors = []
    
    def add_processor(self, processor):
        self.processors.append(processor)

# Social Media Models
@dataclass
class SocialMediaPost:
    """Social media post model"""
    post_id: str
    user_id: str
    username: str
    content: str
    platform: str  # twitter, instagram, facebook
    language: str
    timestamp: datetime
    location: Optional[str]
    hashtags: List[str]
    mentions: List[str]
    likes_count: int
    shares_count: int
    comments_count: int

@dataclass
class WordCount:
    """Word count result"""
    word: str
    count: int
    window_start: datetime
    window_end: datetime
    platform: str
    language: str

@dataclass
class TrendingTopic:
    """Trending topic result"""
    topic: str
    count: int
    growth_rate: float
    platforms: List[str]
    sample_posts: List[str]
    timestamp: datetime

# Stream Processing Classes
class StreamBuilder:
    """Stream builder for processing social media posts"""
    
    def __init__(self, source_topic: str, streams_app: MockKafkaStreams):
        self.source_topic = source_topic
        self.streams_app = streams_app
        self.processors = []
    
    def filter(self, predicate_func):
        """Filter stream based on predicate"""
        self.processors.append(('filter', predicate_func))
        return self
    
    def map(self, mapper_func):
        """Transform each record"""
        self.processors.append(('map', mapper_func))
        return self
    
    def flat_map(self, mapper_func):
        """Flat map transformation"""
        self.processors.append(('flat_map', mapper_func))
        return self
    
    def group_by_key(self):
        """Group by key"""
        self.processors.append(('group_by_key', None))
        return GroupedStream(self)
    
    def to(self, topic: str):
        """Send to output topic"""
        self.processors.append(('to', topic))
        return self

class GroupedStream:
    """Grouped stream for aggregations"""
    
    def __init__(self, parent_stream: StreamBuilder):
        self.parent_stream = parent_stream
        self.processors = parent_stream.processors.copy()
    
    def window(self, time_window_ms: int):
        """Time-based windowing"""
        self.processors.append(('window', time_window_ms))
        return WindowedStream(self, time_window_ms)
    
    def count(self, store_name: str):
        """Count aggregation"""
        self.processors.append(('count', store_name))
        return self
    
    def aggregate(self, initializer, aggregator, store_name: str):
        """Custom aggregation"""
        self.processors.append(('aggregate', (initializer, aggregator, store_name)))
        return self

class WindowedStream:
    """Windowed stream for time-based aggregations"""
    
    def __init__(self, parent_stream: GroupedStream, window_size_ms: int):
        self.parent_stream = parent_stream
        self.window_size_ms = window_size_ms
        self.processors = parent_stream.processors.copy()
    
    def count(self, store_name: str):
        """Windowed count"""
        self.processors.append(('windowed_count', store_name))
        return self

class TableBuilder:
    """Table builder for stateful operations"""
    
    def __init__(self, source_topic: str, store_name: str, streams_app: MockKafkaStreams):
        self.source_topic = source_topic
        self.store_name = store_name
        self.streams_app = streams_app

# Social Media Stream Processor
class SocialMediaWordCountProcessor:
    """Real-time word count processor for Indian social media"""
    
    def __init__(self, bootstrap_servers: str):
        self.streams_app = MockKafkaStreams(
            application_id="social-media-word-count",
            bootstrap_servers=bootstrap_servers
        )
        
        # State stores for aggregations
        self.word_counts = defaultdict(int)
        self.windowed_word_counts = defaultdict(lambda: defaultdict(int))
        self.trending_topics = defaultdict(int)
        self.language_stats = defaultdict(int)
        
        # Hindi stop words (common words to ignore)
        self.hindi_stop_words = {
            'का', 'के', 'की', 'को', 'में', 'से', 'पर', 'और', 'है', 'हैं', 'था', 'थे',
            'यह', 'वह', 'ये', 'वे', 'कि', 'जो', 'तो', 'या', 'भी', 'नहीं', 'कोई',
            'सब', 'कुछ', 'लिए', 'साथ', 'बाद', 'पहले', 'अब', 'यहाँ', 'वहाँ'
        }
        
        # English stop words
        self.english_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        self.setup_topology()
    
    def setup_topology(self):
        """Setup Kafka Streams topology"""
        print("📊 Setting up social media word count topology...")
        
        # Main stream processing pipeline
        posts_stream = self.streams_app.stream("social-media-posts")
        
        # Process posts for word counting
        word_counts_stream = (posts_stream
            .filter(self.is_valid_post)
            .map(self.parse_post)
            .flat_map(self.extract_words)
            .filter(self.is_meaningful_word)
            .map(self.normalize_word)
            .group_by_key()
            .window(300000)  # 5-minute windows
            .count("word-count-store")
        )
        
        # Extract trending hashtags
        hashtag_stream = (posts_stream
            .filter(self.has_hashtags)
            .flat_map(self.extract_hashtags)
            .group_by_key()
            .window(900000)  # 15-minute windows
            .count("hashtag-count-store")
        )
        
        # Language analysis
        language_stream = (posts_stream
            .map(self.extract_language_stats)
            .group_by_key()
            .count("language-stats-store")
        )
        
        print("✅ Topology setup completed")
    
    def is_valid_post(self, key: str, post_data: Dict) -> bool:
        """Filter valid posts"""
        try:
            post = self.deserialize_post(post_data)
            return (
                post.content and 
                len(post.content.strip()) > 10 and
                post.language in ['hindi', 'english', 'hinglish']
            )
        except:
            return False
    
    def parse_post(self, key: str, post_data: Dict) -> tuple:
        """Parse post data"""
        post = self.deserialize_post(post_data)
        return key, post
    
    def extract_words(self, key: str, post: SocialMediaPost) -> List[tuple]:
        """Extract words from post content"""
        words = []
        
        # Clean content
        content = post.content.lower()
        
        # Remove URLs, mentions, hashtags for word counting
        content = re.sub(r'http[s]?://\S+', '', content)
        content = re.sub(r'@\w+', '', content)
        content = re.sub(r'#\w+', '', content)
        
        # Extract words (support Hindi and English)
        word_pattern = r'[\w\u0900-\u097F]+'
        extracted_words = re.findall(word_pattern, content)
        
        for word in extracted_words:
            if len(word) >= 2:  # Minimum word length
                # Create composite key: word|platform|language
                composite_key = f"{word}|{post.platform}|{post.language}"
                words.append((composite_key, {
                    'word': word,
                    'platform': post.platform,
                    'language': post.language,
                    'timestamp': post.timestamp.isoformat(),
                    'post_id': post.post_id
                }))
        
        return words
    
    def is_meaningful_word(self, key: str, word_data: Dict) -> bool:
        """Filter meaningful words (remove stop words)"""
        word = word_data['word']
        language = word_data['language']
        
        if language == 'hindi' and word in self.hindi_stop_words:
            return False
        
        if language == 'english' and word in self.english_stop_words:
            return False
        
        # Filter very common words that are not meaningful
        common_words = {'hai', 'kar', 'kya', 'koi', 'kal', 'aaj', 'ab', 'bas'}
        if word in common_words:
            return False
        
        return len(word) >= 3  # Minimum meaningful word length
    
    def normalize_word(self, key: str, word_data: Dict) -> tuple:
        """Normalize word for counting"""
        word = word_data['word'].lower().strip()
        
        # Basic stemming for Hindi words (simplified)
        hindi_suffixes = ['ों', 'ें', 'ी', 'े', 'ा', 'ान', 'ता', 'ना']
        for suffix in hindi_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                word = word[:-len(suffix)]
                break
        
        # English stemming (basic)
        english_suffixes = ['ing', 'ed', 'er', 'est', 'ly', 's']
        for suffix in english_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                word = word[:-len(suffix)]
                break
        
        word_data['normalized_word'] = word
        return f"{word}|{word_data['platform']}|{word_data['language']}", word_data
    
    def has_hashtags(self, key: str, post_data: Dict) -> bool:
        """Check if post has hashtags"""
        try:
            post = self.deserialize_post(post_data)
            return len(post.hashtags) > 0
        except:
            return False
    
    def extract_hashtags(self, key: str, post_data: Dict) -> List[tuple]:
        """Extract hashtags from post"""
        post = self.deserialize_post(post_data)
        hashtags = []
        
        for hashtag in post.hashtags:
            hashtag_key = f"hashtag:{hashtag.lower()}|{post.platform}"
            hashtags.append((hashtag_key, {
                'hashtag': hashtag.lower(),
                'platform': post.platform,
                'timestamp': post.timestamp.isoformat(),
                'post_id': post.post_id
            }))
        
        return hashtags
    
    def extract_language_stats(self, key: str, post_data: Dict) -> tuple:
        """Extract language statistics"""
        post = self.deserialize_post(post_data)
        stats_key = f"language:{post.language}|{post.platform}"
        
        return stats_key, {
            'language': post.language,
            'platform': post.platform,
            'word_count': len(post.content.split()),
            'timestamp': post.timestamp.isoformat()
        }
    
    def deserialize_post(self, post_data: Dict) -> SocialMediaPost:
        """Deserialize post from JSON"""
        return SocialMediaPost(
            post_id=post_data['post_id'],
            user_id=post_data['user_id'],
            username=post_data['username'],
            content=post_data['content'],
            platform=post_data['platform'],
            language=post_data['language'],
            timestamp=datetime.fromisoformat(post_data['timestamp']),
            location=post_data.get('location'),
            hashtags=post_data.get('hashtags', []),
            mentions=post_data.get('mentions', []),
            likes_count=post_data.get('likes_count', 0),
            shares_count=post_data.get('shares_count', 0),
            comments_count=post_data.get('comments_count', 0)
        )
    
    async def start_processing(self):
        """Start stream processing"""
        print("🌊 Starting social media word count processing...")
        self.streams_app.start()
        
        # Simulate processing (in real implementation, this would be handled by Kafka Streams)
        await self.simulate_processing()
    
    async def simulate_processing(self):
        """Simulate stream processing for demo"""
        # Generate sample social media posts
        sample_posts = self.generate_sample_posts()
        
        print(f"📱 Processing {len(sample_posts)} social media posts...")
        
        # Process each post through the pipeline
        for post_data in sample_posts:
            try:
                # Process through filters
                if self.is_valid_post("", post_data):
                    key, post = self.parse_post("", post_data)
                    
                    # Extract and count words
                    words = self.extract_words(key, post)
                    for word_key, word_data in words:
                        if self.is_meaningful_word(word_key, word_data):
                            normalized_key, normalized_data = self.normalize_word(word_key, word_data)
                            self.word_counts[normalized_key] += 1
                    
                    # Extract hashtags
                    if self.has_hashtags("", post_data):
                        hashtags = self.extract_hashtags("", post_data)
                        for hashtag_key, hashtag_data in hashtags:
                            self.trending_topics[hashtag_key] += 1
                    
                    # Language stats
                    lang_key, lang_data = self.extract_language_stats("", post_data)
                    self.language_stats[lang_key] += 1
                
                await asyncio.sleep(0.01)  # Simulate processing time
                
            except Exception as e:
                print(f"❌ Error processing post: {e}")
        
        # Display results
        self.display_results()
    
    def generate_sample_posts(self) -> List[Dict]:
        """Generate sample Indian social media posts"""
        sample_posts = []
        
        # Hindi posts
        hindi_posts = [
            {
                'post_id': 'H001',
                'user_id': 'user001',
                'username': 'rajesh_mumbai',
                'content': 'आज मुंबई में बारिश बहुत तेज है। ट्रेन की सेवा प्रभावित हो रही है। #MumbaiRains #LocalTrain',
                'platform': 'twitter',
                'language': 'hindi',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['MumbaiRains', 'LocalTrain'],
                'mentions': [],
                'likes_count': 45,
                'shares_count': 12,
                'comments_count': 8
            },
            {
                'post_id': 'H002',
                'user_id': 'user002',
                'username': 'priya_delhi',
                'content': 'दिल्ली की गर्मी से परेशान हूं। एयर कंडीशनर के बिना जीना मुश्किल है। #DelhiHeat #Summer',
                'platform': 'instagram',
                'language': 'hindi',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['DelhiHeat', 'Summer'],
                'mentions': [],
                'likes_count': 78,
                'shares_count': 23,
                'comments_count': 15
            }
        ]
        
        # English posts
        english_posts = [
            {
                'post_id': 'E001',
                'user_id': 'user003',
                'username': 'techie_bangalore',
                'content': 'Bangalore traffic is getting worse every day. Need better public transport system. #BangaloreTraffic #TechCity',
                'platform': 'twitter',
                'language': 'english',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['BangaloreTraffic', 'TechCity'],
                'mentions': [],
                'likes_count': 92,
                'shares_count': 31,
                'comments_count': 22
            },
            {
                'post_id': 'E002',
                'user_id': 'user004',
                'username': 'foodie_pune',
                'content': 'Amazing street food in Pune today! Tried the best vada pav and misal pav. #PuneFood #StreetFood',
                'platform': 'instagram',
                'language': 'english',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['PuneFood', 'StreetFood'],
                'mentions': [],
                'likes_count': 156,
                'shares_count': 67,
                'comments_count': 43
            }
        ]
        
        # Hinglish posts
        hinglish_posts = [
            {
                'post_id': 'HE001',
                'user_id': 'user005',
                'username': 'college_student',
                'content': 'Exam stress is real yaar! Padhai kar kar ke dimag ka दही हो गया है। #ExamStress #StudentLife',
                'platform': 'twitter',
                'language': 'hinglish',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['ExamStress', 'StudentLife'],
                'mentions': [],
                'likes_count': 234,
                'shares_count': 89,
                'comments_count': 67
            },
            {
                'post_id': 'HE002',
                'user_id': 'user006',
                'username': 'working_professional',
                'content': 'Office se ghar जाने में 2 घंटे लग रहे हैं। Bangalore traffic is insane! #OfficeLife #Traffic',
                'platform': 'facebook',
                'language': 'hinglish',
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['OfficeLife', 'Traffic'],
                'mentions': [],
                'likes_count': 123,
                'shares_count': 45,
                'comments_count': 32
            }
        ]
        
        sample_posts.extend(hindi_posts)
        sample_posts.extend(english_posts)
        sample_posts.extend(hinglish_posts)
        
        # Generate more variations
        for i in range(10):
            sample_posts.append({
                'post_id': f'G{i:03d}',
                'user_id': f'user{i+7:03d}',
                'username': f'user_{i+7}',
                'content': f'Sample post {i} about Indian social media trends and technology. #India #Social #Tech',
                'platform': ['twitter', 'instagram', 'facebook'][i % 3],
                'language': ['hindi', 'english', 'hinglish'][i % 3],
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['India', 'Social', 'Tech'],
                'mentions': [],
                'likes_count': 50 + i * 10,
                'shares_count': 10 + i * 2,
                'comments_count': 5 + i
            })
        
        return sample_posts
    
    def display_results(self):
        """Display processing results"""
        print("\n📊 Word Count Results:")
        print("=" * 50)
        
        # Top words by count
        top_words = sorted(self.word_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        print("\n🔤 Top Words:")
        for i, (composite_key, count) in enumerate(top_words, 1):
            word, platform, language = composite_key.split('|')
            print(f"  {i:2d}. {word} ({language}, {platform}): {count} times")
        
        # Top hashtags
        top_hashtags = sorted(self.trending_topics.items(), key=lambda x: x[1], reverse=True)[:10]
        print("\n#️⃣ Trending Hashtags:")
        for i, (hashtag_key, count) in enumerate(top_hashtags, 1):
            hashtag_parts = hashtag_key.replace('hashtag:', '').split('|')
            hashtag, platform = hashtag_parts[0], hashtag_parts[1]
            print(f"  {i:2d}. #{hashtag} ({platform}): {count} times")
        
        # Language distribution
        print("\n🌐 Language Distribution:")
        total_posts = sum(self.language_stats.values())
        for lang_key, count in self.language_stats.items():
            parts = lang_key.split('|')
            language, platform = parts[0].replace('language:', ''), parts[1]
            percentage = (count / total_posts) * 100 if total_posts > 0 else 0
            print(f"  {language} ({platform}): {count} posts ({percentage:.1f}%)")
    
    def stop_processing(self):
        """Stop stream processing"""
        self.streams_app.close()

# Demo Function
async def demonstrate_social_media_word_count():
    """Demonstrate social media word count with Kafka Streams"""
    print("📱 Social Media Word Count Streaming Demo")
    print("=" * 50)
    
    bootstrap_servers = "localhost:9092"
    
    # Create processor
    processor = SocialMediaWordCountProcessor(bootstrap_servers)
    
    try:
        # Start processing
        await processor.start_processing()
        
        print("\n✅ Social Media Word Count Demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        processor.stop_processing()

if __name__ == "__main__":
    """
    Key Kafka Streams Benefits for Social Media Analysis:
    1. Real-time Processing: Immediate trend detection
    2. Stateful Operations: Word counting और aggregations
    3. Time Windows: Trending analysis over time periods
    4. Fault Tolerance: Stream processing durability
    5. Scalability: Parallel processing across partitions
    6. Complex Transformations: Join, filter, aggregate operations
    7. Exactly-once Semantics: Accurate counting
    """
    asyncio.run(demonstrate_social_media_word_count())