# Design YouTube

## Problem Statement

"Design a video sharing platform like YouTube that allows users to upload, view, and share videos. The system should handle billions of users and hours of video uploads every minute."

## Clarifying Questions

1. **Core Features**
   - Upload, view, search videos?
   - Comments and likes?
   - Subscriptions and notifications?
   - Live streaming?

2. **Scale Requirements**
   - Number of users? (2+ billion)
   - Videos watched per day? (1 billion hours)
   - Upload rate? (500 hours per minute)
   - Storage requirements?

3. **Video Specifications**
   - Maximum video length? (12 hours)
   - Supported formats? (MP4, AVI, MOV, etc.)
   - Resolution support? (144p to 8K)
   - Mobile vs desktop?

4. **Quality Requirements**
   - Video start latency? (<2 seconds)
   - Buffering tolerance? (Minimal)
   - Upload processing time? (Minutes to hours)

## Requirements Summary

### Functional Requirements
- Video upload and processing
- Video streaming (adaptive bitrate)
- Search and discovery
- User interactions (like, comment, subscribe)
- View analytics
- Content recommendation

### Non-Functional Requirements
- **Scale**: 2B users, 1B hours watched/day
- **Performance**: <2s video start time
- **Availability**: 99.9% for viewing, 99% for upload
- **Storage**: Efficient storage and CDN distribution
- **Global**: Low latency worldwide

### Out of Scope
- Monetization (ads, premium)
- Content moderation details
- Copyright detection
- Live streaming

## Scale Estimation

### Storage Requirements
```
Daily uploads: 500 hours/min × 60 min × 24 hours = 720,000 hours/day
Average video size: 
  - Raw: 1 GB/minute of HD video
  - After encoding (multiple resolutions): 5 GB/minute
  
Daily storage: 720,000 hours × 60 min × 5 GB = 216 PB/day
Annual storage: ~78 EB/year

With replication and CDN:
Total storage: 200+ EB
```

### Bandwidth Requirements
```
Concurrent viewers: 100 million
Average bitrate: 3 Mbps
Total bandwidth: 300 Tbps

CDN requirements:
- Edge locations: 100+
- Cache hit rate: 90%
- Origin bandwidth: 30 Tbps
```

### Compute Requirements
```
Video encoding: 100,000 CPU cores
Recommendation: 50,000 servers
API servers: 10,000 servers
Database: 5,000 servers
```

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│  (Web, Mobile, TV, API)                                     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                          CDN                                 │
│  (Global Edge Locations - Video Serving)                    │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                   (Geographic routing)                       │
└─────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  API Service  │     │Upload Service │     │Stream Service │
└───────────────┘     └───────────────┘     └───────────────┘
        │                      │                      │
        ├──────────────────────┴──────────────────────┘
        ▼
┌─────────────────────────────────────────────────────────────┐
│                     Microservices                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │Metadata │ │ Search  │ │Comments │ │Analytics│          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Bigtable │ │ Spanner │ │   GCS    │ │  Kafka  │      │
│  │(Metadata)│ │(User DB) │ │ (Videos) │ │(Events) │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Component Design

### 1. Video Upload Pipeline

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Client  │────▶│  Upload │────▶│  Queue  │────▶│ Process │
│         │     │  Server │     │         │     │ Worker  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                      │                                │
                      ▼                                ▼
                ┌─────────┐                      ┌─────────┐
                │Raw Video│                      │Processed│
                │Storage  │                      │ Videos  │
                │  (GCS)  │                      │  (GCS)  │
                └─────────┘                      └─────────┘
```

**Upload Process**
```python
class VideoUploadService:
    def upload_video(self, video_file, metadata):
        # 1. Generate unique video_id
        video_id = generate_uuid()
        
        # 2. Upload to temporary storage
        temp_location = upload_to_gcs(video_file, 'temp-bucket')
        
        # 3. Create metadata entry
        video_metadata = {
            'video_id': video_id,
            'user_id': metadata['user_id'],
            'title': metadata['title'],
            'status': 'processing',
            'upload_time': time.now(),
            'temp_location': temp_location
        }
        save_to_bigtable(video_metadata)
        
        # 4. Queue for processing
        publish_to_queue({
            'video_id': video_id,
            'location': temp_location,
            'metadata': video_metadata
        })
        
        return video_id
```

**Video Processing Pipeline**
```python
class VideoProcessor:
    def process_video(self, message):
        video_id = message['video_id']
        input_path = message['location']
        
        # 1. Download from temp storage
        local_file = download_from_gcs(input_path)
        
        # 2. Extract metadata
        video_info = extract_video_info(local_file)
        
        # 3. Generate multiple resolutions
        resolutions = ['144p', '240p', '360p', '480p', '720p', '1080p', '4K']
        encoded_files = []
        
        for resolution in resolutions:
            output_file = encode_video(local_file, resolution)
            # Segment for HLS/DASH
            segments = segment_video(output_file)
            # Upload to storage
            cdn_path = upload_segments_to_cdn(segments, video_id, resolution)
            encoded_files.append({
                'resolution': resolution,
                'path': cdn_path,
                'bitrate': calculate_bitrate(output_file)
            })
        
        # 4. Generate thumbnails
        thumbnails = generate_thumbnails(local_file)
        thumbnail_urls = upload_thumbnails(thumbnails)
        
        # 5. Update metadata
        update_video_metadata(video_id, {
            'status': 'ready',
            'resolutions': encoded_files,
            'thumbnails': thumbnail_urls,
            'duration': video_info['duration'],
            'processing_time': time.now()
        })
        
        # 6. Clean up temp files
        delete_temp_files(input_path, local_file)
```

### 2. Video Streaming Service

**Adaptive Bitrate Streaming**
```
Client                     CDN                      Origin
  │                         │                         │
  ├──GET /manifest.m3u8────▶│                         │
  │                         ├──(Cache Miss)──────────▶│
  │                         │◀─────manifest.m3u8──────┤
  │◀────manifest.m3u8───────┤                         │
  │                         │                         │
  ├──GET /segment1.ts──────▶│                         │
  │◀─────segment1.ts────────┤                         │
  │                         │                         │
  └──(Adapt bitrate)        │                         │
  ├──GET /segment2_720p.ts─▶│                         │
  │◀────segment2_720p.ts────┤                         │
```

**Video Manifest (HLS)**
```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
360p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=842x480
480p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/playlist.m3u8
```

**Streaming Service Implementation**
```python
class StreamingService:
    def get_video_manifest(self, video_id, client_info):
        # Get video metadata
        video = get_video_metadata(video_id)
        
        # Determine available resolutions based on client
        available_resolutions = self.filter_resolutions(
            video['resolutions'],
            client_info['device_type'],
            client_info['network_speed']
        )
        
        # Generate manifest
        manifest = self.generate_hls_manifest(
            video_id,
            available_resolutions
        )
        
        # Return with CDN URL
        cdn_url = self.get_nearest_cdn(client_info['location'])
        return f"{cdn_url}/{video_id}/manifest.m3u8"
    
    def get_video_segment(self, video_id, resolution, segment_num):
        # This is typically handled by CDN
        # Origin only serves on cache miss
        segment_path = f"{video_id}/{resolution}/segment{segment_num}.ts"
        return redirect_to_cdn(segment_path)
```

### 3. Metadata and Search

**Video Metadata Schema**
```protobuf
message Video {
  string video_id = 1;
  string user_id = 2;
  string title = 3;
  string description = 4;
  repeated string tags = 5;
  int64 upload_timestamp = 6;
  int64 duration_seconds = 7;
  int64 view_count = 8;
  int64 like_count = 9;
  int64 dislike_count = 10;
  string thumbnail_url = 11;
  repeated Resolution resolutions = 12;
  VideoStatus status = 13;
  map<string, string> metadata = 14;
}

message Resolution {
  string quality = 1;  // "720p", "1080p", etc.
  string manifest_url = 2;
  int32 bitrate_kbps = 3;
}
```

**Search Index Design**
```python
class VideoSearchIndex:
    def __init__(self):
        self.inverted_index = {}  # term -> [video_ids]
        self.video_features = {}  # video_id -> features
    
    def index_video(self, video):
        # Extract searchable terms
        terms = self.extract_terms(video.title, video.description, video.tags)
        
        # Update inverted index
        for term in terms:
            if term not in self.inverted_index:
                self.inverted_index[term] = []
            self.inverted_index[term].append(video.video_id)
        
        # Store features for ranking
        self.video_features[video.video_id] = {
            'upload_time': video.upload_timestamp,
            'view_count': video.view_count,
            'engagement_rate': video.like_count / (video.view_count + 1),
            'channel_authority': self.get_channel_score(video.user_id)
        }
    
    def search(self, query, limit=20):
        # Parse query
        terms = self.parse_query(query)
        
        # Find candidate videos
        candidates = set()
        for term in terms:
            if term in self.inverted_index:
                candidates.update(self.inverted_index[term])
        
        # Rank results
        ranked = self.rank_videos(candidates, query)
        
        return ranked[:limit]
```

### 4. Recommendation System

**Collaborative Filtering Pipeline**
```
User Interactions ─────▶ Feature Extraction ─────▶ Model Training
      │                         │                        │
      ▼                         ▼                        ▼
 View History              User Embeddings          TensorFlow
 Like/Dislike             Video Embeddings          Serving
 Watch Time               Context Features
      │                         │                        │
      └─────────────────────────┴────────────────────────┘
                                │
                                ▼
                        Recommendation API
```

**Real-time Recommendation Service**
```python
class RecommendationService:
    def get_recommendations(self, user_id, context):
        # Get user features
        user_features = self.get_user_features(user_id)
        
        # Get candidate videos
        candidates = self.get_candidates(user_features, context)
        
        # Score and rank
        scores = self.model.predict({
            'user_features': user_features,
            'video_features': [self.get_video_features(v) for v in candidates],
            'context': context
        })
        
        # Apply business rules
        filtered = self.apply_filters(candidates, scores, user_id)
        
        # Return top recommendations
        return filtered[:20]
    
    def get_candidates(self, user_features, context):
        candidates = []
        
        # Recent uploads from subscriptions
        candidates.extend(self.get_subscription_videos(user_features['user_id']))
        
        # Similar videos to watch history
        candidates.extend(self.get_similar_videos(user_features['watch_history']))
        
        # Trending videos
        candidates.extend(self.get_trending_videos(context['location']))
        
        # Collaborative filtering
        candidates.extend(self.get_cf_recommendations(user_features))
        
        return list(set(candidates))
```

### 5. CDN and Caching Strategy

**Multi-Tier Caching**
```
┌─────────────────────────────────────────┐
│            Browser Cache                 │ ← 1 hour
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          ISP Cache (Optional)           │ ← 1 day
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         CDN Edge Locations              │ ← 1 week
│   (Popular videos, thumbnails)          │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│      Regional CDN (All videos)          │ ← 1 month
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│    Origin Storage (GCS - Forever)       │
└─────────────────────────────────────────┘
```

**Cache Warming Strategy**
```python
class CacheWarmer:
    def warm_caches(self):
        # Predict popular videos
        trending = self.predict_trending_videos()
        
        # Pre-load to edge locations
        for video in trending:
            for location in self.edge_locations:
                self.preload_video(video, location)
        
        # Geographic optimization
        for region in self.regions:
            regional_popular = self.get_regional_popular(region)
            self.preload_to_region(regional_popular, region)
```

## Data Models

### User Data (Spanner)
```sql
CREATE TABLE users (
    user_id STRING(36) NOT NULL,
    email STRING(255),
    username STRING(50),
    created_at TIMESTAMP,
    channel_name STRING(100),
    subscriber_count INT64,
) PRIMARY KEY (user_id);

CREATE TABLE subscriptions (
    user_id STRING(36) NOT NULL,
    channel_id STRING(36) NOT NULL,
    subscribed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (channel_id) REFERENCES users(user_id),
) PRIMARY KEY (user_id, channel_id);
```

### Video Metadata (Bigtable)
```
Row Key: video_id
Column Families:
- metadata: title, description, tags, duration
- stats: views, likes, dislikes, comments
- storage: resolutions, cdn_urls, thumbnails
- processing: status, encoding_details
```

### Analytics Events (BigQuery)
```sql
CREATE TABLE video_events (
    event_id STRING,
    user_id STRING,
    video_id STRING,
    event_type STRING,  -- 'view', 'like', 'share', 'comment'
    timestamp TIMESTAMP,
    watch_time_seconds INT64,
    client_info STRUCT<
        device_type STRING,
        os STRING,
        browser STRING,
        ip_address STRING,
        country STRING
    >
) PARTITION BY DATE(timestamp);
```

## Performance Optimizations

### 1. Video Delivery Optimization
- **Adaptive Bitrate**: Adjust quality based on network
- **Segment Prefetching**: Load next segments proactively
- **P2P Assistance**: Share segments between nearby users
- **Connection Pooling**: Reuse HTTP connections

### 2. Encoding Optimization
- **Distributed Encoding**: Parallel processing of segments
- **Hardware Acceleration**: GPU/ASIC for encoding
- **Perceptual Encoding**: Optimize for human vision
- **Incremental Encoding**: Only encode requested resolutions

### 3. Storage Optimization
- **Deduplication**: Identify duplicate uploads
- **Compression**: Video-specific compression
- **Tiered Storage**: Hot videos on SSD, cold on HDD
- **Erasure Coding**: Efficient redundancy

## Challenges and Solutions

### 1. Copyright Protection
**Challenge**: Detecting copyrighted content
**Solution**:
- Content ID system with audio/video fingerprinting
- Machine learning for similarity detection
- Manual review process
- Rights holder tools

### 2. Global Distribution
**Challenge**: Low latency worldwide
**Solution**:
- 100+ edge locations
- Anycast routing
- Regional encoding
- Local CDN partnerships

### 3. Abuse Prevention
**Challenge**: Spam, inappropriate content
**Solution**:
- ML-based content moderation
- User reporting system
- Trust scores
- Rate limiting

### 4. Cost Management
**Challenge**: Massive storage and bandwidth costs
**Solution**:
- Efficient encoding (VP9, AV1)
- Intelligent caching
- P2P offloading
- Tiered storage

## Monitoring and Analytics

### Key Metrics
```
User Experience:
- Video Start Time: <2 seconds
- Rebuffering Rate: <0.5%
- Video Quality: >720p for 80% users

System Health:
- Upload Success Rate: >99%
- Processing Time: <30 minutes
- CDN Cache Hit Rate: >90%
- API Latency: <100ms p99

Business Metrics:
- Daily Active Users
- Watch Time per User
- Upload Rate
- Engagement Rate
```

### Real-time Dashboards
```python
class YouTubeMonitoring:
    def track_metrics(self):
        metrics = {
            'qps': self.get_current_qps(),
            'active_users': self.get_active_users(),
            'upload_rate': self.get_upload_rate(),
            'cdn_health': self.check_cdn_health(),
            'processing_queue': self.get_queue_depth()
        }
        
        # Alert on anomalies
        if metrics['qps'] > self.qps_threshold:
            self.alert('High QPS detected')
        
        return metrics
```

## Security Considerations

### Access Control
- OAuth 2.0 for authentication
- Channel-based permissions
- Private video sharing
- Age restrictions

### Content Security
- HTTPS everywhere
- Token-based video access
- DRM for premium content
- Watermarking

## Future Enhancements

### Near-term
1. **8K Video Support**: Higher resolution content
2. **360° Videos**: Immersive experiences
3. **Better Compression**: AV1 codec adoption
4. **5G Optimization**: Ultra-low latency streaming

### Long-term
1. **AI-Generated Summaries**: Automatic video highlights
2. **Real-time Translation**: Live subtitle generation
3. **Interactive Videos**: Choose-your-own-adventure
4. **VR/AR Integration**: Immersive viewing experiences

## Interview Tips

1. **Start with Upload and View**: Core functionality first
2. **Address Scale Early**: Billions of users, petabytes of data
3. **Consider CDN**: Critical for global video delivery
4. **Mention Encoding**: Multiple resolutions and formats
5. **Don't Forget Analytics**: View counts, recommendations

## Common Follow-up Questions

1. **"How would you handle live streaming?"**
   - RTMP ingest, real-time encoding
   - Minimal latency CDN distribution
   - Chat and interaction systems

2. **"How do you implement video search?"**
   - Text search on metadata
   - Thumbnail-based search
   - Audio transcription search

3. **"How would you optimize for mobile?"**
   - Lower bitrates, efficient codecs
   - Offline download capability
   - Background prefetching

4. **"How do you handle viral videos?"**
   - Auto-scaling CDN capacity
   - Dynamic cache warming
   - Geographic load distribution