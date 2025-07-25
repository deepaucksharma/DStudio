# Design Gmail

## Problem Statement

"Design an email service like Gmail that can handle billions of users, with features like send/receive, search, spam filtering, and attachment support."

## Clarifying Questions

1. **Core Features**
   - Send/receive emails?
   - Folders and labels?
   - Search functionality?
   - Spam filtering?
   - Attachments?
   - Threading/conversations?

2. **Scale Requirements**
   - Number of users? (1.8 billion)
   - Emails per day? (500 billion)
   - Average email size? (75KB with attachments)
   - Storage per user? (15GB free)

3. **Performance Requirements**
   - Email delivery time? (seconds)
   - Search latency? (<500ms)
   - Availability? (99.9%)

4. **Additional Features**
   - End-to-end encryption?
   - Offline support?
   - Third-party integrations?

## Requirements Summary

### Functional Requirements
- Send and receive emails
- Organize with labels and folders
- Full-text search
- Spam and virus detection
- Attachment support (up to 25MB)
- Threading/conversation view

### Non-Functional Requirements
- **Scale**: 1.8B users, 500B emails/day
- **Latency**: <1s for send, <500ms for search
- **Storage**: 15GB+ per user
- **Availability**: 99.9% uptime
- **Security**: Spam filtering, virus scanning, encryption

### Out of Scope
- Calendar integration
- Chat/Meet integration
- Payment processing
- Advanced AI features

## Scale Estimation

### Storage Requirements
```
Active users: 1.8 billion
Average emails per user: 10,000
Average email size: 75KB
Storage per user: 10,000 × 75KB = 750MB
Total email storage: 1.8B × 750MB = 1.35 EB

With attachments and redundancy:
Total storage needed: ~5 EB
```

### Traffic Estimation
```
Emails per day: 500 billion
Peak hours factor: 3x
Peak emails/second: 500B / (24×3600) × 3 = 17.4M/s

Read:Write ratio: 10:1
Email reads/sec: 174M/s
Email writes/sec: 17.4M/s
```

### Infrastructure
```
Mail servers: 100,000
Storage servers: 50,000
Search clusters: 10,000
Spam filters: 5,000
```

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Clients                             │
│         (Web, Mobile, Desktop, IMAP/POP3)                   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                    (Geographic routing)                      │
└─────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   SMTP       │      │   API        │      │   IMAP/POP   │
│   Servers    │      │   Servers    │      │   Servers    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │  Spam   │  │  Virus  │  │  Index  │  │ Deliver │      │
│  │ Filter  │  │  Scan   │  │  Email  │  │  Queue  │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                       Storage Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Metadata │  │  Email   │  │Attachment│  │  Search  │   │
│  │    DB    │  │  Store   │  │  Store   │  │  Index   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Component Design

### 1. Email Receiving Pipeline

**SMTP Server**
```python
class SMTPServer:
    def handle_connection(self, client_socket):
        self.send_response(client_socket, "220 smtp.gmail.com ESMTP")
        
        while True:
            command = self.read_command(client_socket)
            
            if command.startswith("HELO"):
                self.handle_helo(client_socket, command)
            elif command.startswith("MAIL FROM"):
                self.handle_mail_from(client_socket, command)
            elif command.startswith("RCPT TO"):
                self.handle_rcpt_to(client_socket, command)
            elif command == "DATA":
                self.handle_data(client_socket)
            elif command == "QUIT":
                break
    
    def handle_data(self, client_socket):
        self.send_response(client_socket, "354 End data with <CR><LF>.<CR><LF>")
        
# Receive email content
        email_data = self.read_until_terminator(client_socket)
        
# Parse email
        email = self.parse_email(email_data)
        
# Queue for processing
        message_id = generate_message_id()
        self.queue_service.enqueue({
            'message_id': message_id,
            'from': email.sender,
            'to': email.recipients,
            'data': email_data,
            'received_time': timestamp()
        })
        
        self.send_response(client_socket, f"250 OK {message_id}")
```

**Email Processing Pipeline**
```python
class EmailProcessor:
    def process_email(self, email_message):
# 1. Spam Check
        spam_score = self.spam_filter.check(email_message)
        if spam_score > SPAM_THRESHOLD:
            email_message.labels.append('SPAM')
            email_message.folder = 'Spam'
        
# 2. Virus Scan
        if self.has_attachments(email_message):
            scan_result = self.virus_scanner.scan(email_message.attachments)
            if scan_result.is_infected:
                self.quarantine_email(email_message)
                return
        
# 3. Process Attachments
        if email_message.attachments:
            attachment_urls = []
            for attachment in email_message.attachments:
                url = self.store_attachment(attachment)
                attachment_urls.append(url)
            email_message.attachment_urls = attachment_urls
        
# 4. Store Email
        self.store_email(email_message)
        
# 5. Update Indexes
        self.index_email(email_message)
        
# 6. Send Notifications
        self.notify_recipients(email_message)
```

### 2. Email Storage System

**Distributed Email Storage**
```python
class EmailStorage:
    def __init__(self):
        self.shard_manager = ShardManager()
        self.replica_manager = ReplicaManager()
    
    def store_email(self, email):
# Determine shard based on user_id
        user_id = email.recipient_id
        shard_id = self.shard_manager.get_shard(user_id)
        
# Serialize email
        email_data = self.serialize_email(email)
        
# Store with replication
        primary_node = self.get_primary_node(shard_id)
        email_id = primary_node.store(email_data)
        
# Async replication
        replicas = self.replica_manager.get_replicas(shard_id)
        for replica in replicas:
            self.async_replicate(replica, email_id, email_data)
        
# Update metadata
        self.update_metadata(user_id, email_id, email.metadata)
        
        return email_id
    
    def retrieve_email(self, user_id, email_id):
        shard_id = self.shard_manager.get_shard(user_id)
        
# Try primary first
        try:
            primary_node = self.get_primary_node(shard_id)
            return primary_node.retrieve(email_id)
        except NodeUnavailable:
# Fallback to replicas
            replicas = self.replica_manager.get_replicas(shard_id)
            for replica in replicas:
                try:
                    return replica.retrieve(email_id)
                except:
                    continue
            raise EmailNotFound()
```

**Email Data Model**
```protobuf
message Email {
    string message_id = 1;
    string thread_id = 2;
    
    message Address {
        string email = 1;
        string name = 2;
    }
    
    Address from = 3;
    repeated Address to = 4;
    repeated Address cc = 5;
    repeated Address bcc = 6;
    
    string subject = 7;
    string body_text = 8;
    string body_html = 9;
    
    repeated Attachment attachments = 10;
    repeated string labels = 11;
    
    int64 timestamp = 12;
    map<string, string> headers = 13;
}

message Attachment {
    string filename = 1;
    string content_type = 2;
    int64 size = 3;
    string storage_url = 4;
}
```

### 3. Search System

**Full-Text Search Index**
```python
class EmailSearchIndex:
    def __init__(self):
        self.inverted_index = InvertedIndex()
        self.user_index_shards = {}
    
    def index_email(self, email):
# Extract searchable content
        tokens = self.tokenize(
            email.subject,
            email.body_text,
            email.from_address,
            email.to_addresses
        )
        
# Update user-specific index
        user_shard = self.get_user_shard(email.user_id)
        
        for token in tokens:
            user_shard.add_posting(
                token,
                email.message_id,
                email.timestamp,
                self.calculate_relevance(token, email)
            )
        
# Update global index for admin/compliance
        self.global_index.add(email.message_id, tokens)
    
    def search(self, user_id, query, filters=None):
# Parse query
        parsed_query = self.parse_query(query)
        
# Get user's index shard
        user_shard = self.get_user_shard(user_id)
        
# Search with filters
        results = user_shard.search(
            parsed_query.terms,
            date_range=filters.get('date_range'),
            has_attachment=filters.get('has_attachment'),
            labels=filters.get('labels')
        )
        
# Rank results
        ranked = self.rank_results(results, parsed_query)
        
        return ranked[:50]  # Return top 50
```

**Search Query Optimization**
```python
class QueryOptimizer:
    def optimize_query(self, query):
# Handle special operators
        if "from:" in query:
            from_addr = self.extract_operator(query, "from:")
            query = query.replace(f"from:{from_addr}", "")
            filters['from'] = from_addr
        
        if "has:attachment" in query:
            filters['has_attachment'] = True
            query = query.replace("has:attachment", "")
        
# Spell correction
        corrected = self.spell_correct(query)
        
# Synonym expansion
        expanded = self.expand_synonyms(corrected)
        
        return expanded, filters
```

### 4. Spam Filtering

**ML-Based Spam Filter**
```python
class SpamFilter:
    def __init__(self):
        self.model = self.load_model()
        self.feature_extractor = FeatureExtractor()
        self.reputation_db = ReputationDB()
    
    def check_spam(self, email):
# Extract features
        features = self.feature_extractor.extract({
            'subject': email.subject,
            'body': email.body,
            'sender': email.from_address,
            'headers': email.headers
        })
        
# Check sender reputation
        sender_reputation = self.reputation_db.get_score(
            email.from_address,
            email.sender_ip
        )
        features['sender_reputation'] = sender_reputation
        
# Check for known spam patterns
        pattern_score = self.check_patterns(email)
        features['pattern_score'] = pattern_score
        
# ML prediction
        spam_probability = self.model.predict(features)
        
# Update reputation based on user feedback
        self.update_reputation(email.from_address, spam_probability)
        
        return spam_probability
    
    def check_patterns(self, email):
        patterns = [
            r'viagra|cialis',
            r'win.*prize|lottery',
            r'click.*here.*now',
            r'limited.*time.*offer'
        ]
        
        score = 0
        for pattern in patterns:
            if re.search(pattern, email.body, re.IGNORECASE):
                score += 0.2
        
        return min(score, 1.0)
```

### 5. Email Sending

**Outbound Email Processing**
```python
class EmailSender:
    def send_email(self, email_request):
# Validate recipients
        valid_recipients = self.validate_recipients(email_request.to)
        
# Check sending limits
        if not self.check_rate_limit(email_request.from_user):
            raise RateLimitExceeded()
        
# Process attachments
        if email_request.attachments:
            self.process_attachments(email_request)
        
# Build MIME message
        mime_message = self.build_mime_message(email_request)
        
# Queue for delivery
        for recipient in valid_recipients:
            self.delivery_queue.enqueue({
                'recipient': recipient,
                'message': mime_message,
                'priority': self.calculate_priority(email_request),
                'retry_count': 0
            })
        
# Store in sent folder
        self.store_sent_email(email_request.from_user, mime_message)
        
        return {'status': 'queued', 'message_id': mime_message.id}
```

**Delivery Queue Worker**
```python
class DeliveryWorker:
    def process_delivery(self, delivery_task):
        recipient = delivery_task['recipient']
        message = delivery_task['message']
        
        try:
# Get MX records
            mx_records = self.get_mx_records(recipient.domain)
            
# Try each MX server
            for mx_server in mx_records:
                try:
                    self.deliver_to_server(mx_server, recipient, message)
                    self.mark_delivered(delivery_task)
                    return
                except TemporaryFailure:
                    continue
            
# All MX servers failed
            self.handle_delivery_failure(delivery_task)
            
        except PermanentFailure as e:
            self.bounce_email(delivery_task, str(e))
```

### 6. Threading and Conversation View

**Thread Management**
```python
class ThreadManager:
    def assign_thread(self, email):
# Check In-Reply-To header
        if email.in_reply_to:
            parent_thread = self.get_thread_by_message_id(email.in_reply_to)
            if parent_thread:
                return parent_thread.thread_id
        
# Check References header
        if email.references:
            for ref_id in email.references:
                thread = self.get_thread_by_message_id(ref_id)
                if thread:
                    return thread.thread_id
        
# Check subject similarity
        similar_thread = self.find_similar_thread(
            email.subject,
            email.participants,
            time_window=timedelta(days=7)
        )
        if similar_thread:
            return similar_thread.thread_id
        
# Create new thread
        return self.create_new_thread(email)
    
    def get_thread_view(self, thread_id, user_id):
# Get all messages in thread
        messages = self.get_thread_messages(thread_id)
        
# Filter by user access
        accessible = [m for m in messages if self.can_access(user_id, m)]
        
# Sort by timestamp
        sorted_messages = sorted(accessible, key=lambda m: m.timestamp)
        
# Build conversation tree
        return self.build_conversation_tree(sorted_messages)
```

## Data Models

### User Mailbox Schema (Bigtable)
```
Row Key: {user_id}#{reverse_timestamp}#{message_id}
Column Families:
- metadata: folder, labels, read_status, starred
- headers: from, to, subject, date
- body: text_preview, has_attachments
- thread: thread_id, position_in_thread
```

### Search Index Schema
```
Row Key: {user_id}#{term}
Column Family: postings
Columns: {message_id} -> {score, timestamp, snippet}
```

### Attachment Storage (GCS)
```
Bucket: gmail-attachments-{region}
Path: {user_id_hash}/{message_id}/{attachment_id}/{filename}
Metadata:
- content-type
- size
- virus-scan-status
- upload-timestamp
```

## Performance Optimizations

### 1. Caching Strategy
```python
class EmailCache:
    def __init__(self):
        self.memory_cache = LRUCache(size_gb=100)
        self.redis_cache = RedisCluster()
        
    def get_email(self, user_id, email_id):
# L1: Memory cache
        cached = self.memory_cache.get(f"{user_id}:{email_id}")
        if cached:
            return cached
        
# L2: Redis cache
        cached = self.redis_cache.get(f"{user_id}:{email_id}")
        if cached:
            self.memory_cache.put(f"{user_id}:{email_id}", cached)
            return cached
        
# L3: Storage
        email = self.storage.get_email(user_id, email_id)
        
# Update caches
        self.redis_cache.setex(f"{user_id}:{email_id}", email, ttl=3600)
        self.memory_cache.put(f"{user_id}:{email_id}", email)
        
        return email
```

### 2. Batch Operations
```python
class BatchProcessor:
    def mark_as_read(self, user_id, email_ids):
# Batch update in storage
        updates = []
        for email_id in email_ids:
            updates.append({
                'row_key': f"{user_id}#{email_id}",
                'mutations': {'metadata:read_status': 'true'}
            })
        
        self.storage.batch_mutate(updates)
        
# Update cache
        for email_id in email_ids:
            self.cache.invalidate(f"{user_id}:{email_id}")
```

### 3. Predictive Prefetching
```python
class PrefetchService:
    def prefetch_emails(self, user_id, current_email_id):
# Predict next emails user might read
        predictions = self.ml_model.predict_next_emails(
            user_id,
            current_email_id
        )
        
# Prefetch top predictions
        for email_id, probability in predictions[:5]:
            if probability > 0.7:
                self.cache.warm(user_id, email_id)
```

## Challenges and Solutions

### 1. Handling Large Attachments
**Challenge**: 25MB attachment limit, efficient storage
**Solution**:
- Chunked upload for reliability
- Deduplication across users
- Progressive download
- Link sharing for larger files

### 2. Real-time Push
**Challenge**: Instant email notifications
**Solution**:
- WebSocket connections for web
- Push notifications for mobile
- Long polling fallback
- Presence detection

### 3. Search Performance
**Challenge**: Sub-second search across years of email
**Solution**:
- User-specific index shards
- Tiered indexes (recent vs. archive)
- Query result caching
- Progressive search results

### 4. Spam Evolution
**Challenge**: Adapting to new spam techniques
**Solution**:
- Online learning models
- User feedback loops
- Collaborative filtering
- Regular model updates

## Monitoring and Operations

### Key Metrics
```
Reliability:
- Email delivery rate: >99.9%
- Search success rate: >99.5%
- Spam detection accuracy: >99%
- False positive rate: <0.1%

Performance:
- Email send latency: p99 < 2s
- Email receive latency: p99 < 5s
- Search latency: p99 < 500ms
- UI load time: p99 < 1s

Scale:
- Emails processed/sec
- Active connections
- Storage growth rate
- Bandwidth usage
```

### Operational Tools
```python
class GmailMonitoring:
    def monitor_health(self):
        metrics = {
            'delivery_queue_depth': self.get_queue_depth('delivery'),
            'spam_processing_rate': self.get_processing_rate('spam'),
            'search_latency_p99': self.get_latency_percentile('search', 99),
            'storage_usage_percent': self.get_storage_usage(),
            'active_smtp_connections': self.get_connection_count('smtp')
        }
        
# Alert on anomalies
        if metrics['delivery_queue_depth'] > 1000000:
            self.alert('High delivery queue depth')
        
        return metrics
```

## Security and Privacy

### Email Security
- TLS for transport encryption
- Optional S/MIME and PGP support
- Sender authentication (SPF, DKIM, DMARC)
- Phishing detection

### Privacy Features
- Confidential mode (expiring emails)
- Two-factor authentication
- Suspicious login detection
- Data encryption at rest

## Future Enhancements

### Near-term
1. **Smart Compose**: AI-powered writing suggestions
2. **Smart Reply**: One-click responses
3. **Advanced Filters**: ML-based email organization
4. **Snooze**: Temporarily hide emails

### Long-term
1. **End-to-End Encryption**: Default encryption
2. **AI Assistant**: Email summarization and actions
3. **Voice Interface**: Voice-controlled email
4. **Blockchain**: Decentralized email verification

## Interview Tips

1. **Start Simple**: Basic send/receive functionality
2. **Scale Gradually**: Add complexity as you go
3. **Consider Storage**: Email accumulates over years
4. **Security Focus**: Spam and privacy are critical
5. **Search is Key**: Users expect instant search

## Common Follow-up Questions

1. **"How would you implement email recall?"**
   - Delay sending by 30 seconds
   - Revoke access if not yet read
   - Cannot recall from external domains

2. **"How do you handle email encryption?"**
   - TLS for transport
   - Optional E2E encryption
   - Key management service

3. **"How would you implement priority inbox?"**
   - ML model for importance
   - User feedback training
   - Multiple inbox sections

4. **"How do you handle bounce messages?"**
   - Parse bounce notifications
   - Classify bounce types
   - Update sender reputation