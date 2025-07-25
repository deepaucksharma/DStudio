# Design Google Docs (Collaborative Editing)

## Problem Statement

"Design a real-time collaborative document editing system like Google Docs that allows multiple users to edit the same document simultaneously with conflict resolution and version history."

## Clarifying Questions

1. **Core Features**
   - Real-time collaborative editing?
   - Cursor positions and selections?
   - Comments and suggestions?
   - Version history?
   - Offline editing with sync?
   - Format support (text, images, tables)?

2. **Scale Requirements**
   - Number of concurrent editors per doc? (100+)
   - Document size limits? (100MB)
   - Total documents? (Billions)
   - Active users? (100M+)

3. **Performance Requirements**
   - Edit latency? (<100ms perceived)
   - Sync frequency? (Real-time)
   - Conflict resolution time? (Milliseconds)
   - Character input lag? (None)

4. **Consistency Requirements**
   - Strong consistency for edits?
   - Eventual consistency acceptable?
   - How to handle conflicts?

## Requirements Summary

### Functional Requirements
- Real-time collaborative editing
- Automatic conflict resolution
- Show other users' cursors and selections
- Version history and rollback
- Comments and suggestions
- Rich text formatting
- Offline support with sync

### Non-Functional Requirements
- **Latency**: <100ms for edit propagation
- **Scale**: Support 100+ concurrent editors
- **Consistency**: Eventual consistency with conflict-free resolution
- **Availability**: 99.9% uptime
- **Performance**: No perceptible lag while typing

### Out of Scope
- Video/audio embedding
- Complex formatting (LaTeX)
- Code execution
- Drawing tools

## Scale Estimation

### Data Size
```
Documents: 1 billion
Average document size: 50KB
Total document storage: 50TB

With versions and operations log:
Average operations per document: 10,000
Operation size: 100 bytes
Operations storage: 1PB

Total storage with redundancy: ~5PB
```

### Traffic Estimation
```
Active documents: 10 million/day
Average editors per document: 3
Edit operations per second per user: 2
Total operations: 10M × 3 × 2 = 60M ops/sec

Peak load (10x): 600M ops/sec
```

### Infrastructure
```
WebSocket servers: 10,000
Operation processors: 5,000
Storage servers: 1,000
Cache servers: 500
```

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│                (Web, Mobile, Desktop)                        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   WebSocket Gateway                          │
│              (Persistent connections)                        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Operation Transform                         │
│                     Service (OT)                            │
└─────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Document    │      │   Session    │      │   History    │
│   Service    │      │   Manager    │      │   Service    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Document │  │Operation │  │ Session  │  │ Version  │   │
│  │    DB    │  │   Log    │  │  Store   │  │  Store   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Algorithm: Operational Transformation (OT)

### Understanding OT

Operational Transformation is the key algorithm that enables real-time collaboration by transforming operations to maintain consistency.

```python
class Operation:
    """Base operation class"""
    pass

class Insert(Operation):
    def __init__(self, position, text, client_id):
        self.position = position
        self.text = text
        self.client_id = client_id
        self.length = len(text)

class Delete(Operation):
    def __init__(self, position, length, client_id):
        self.position = position
        self.length = length
        self.client_id = client_id

class OperationalTransform:
    @staticmethod
    def transform(op1, op2):
        """
        Transform op1 against op2 to handle concurrent edits
        Returns (op1_prime, op2_prime) where:
        - op1_prime is op1 transformed against op2
        - op2_prime is op2 transformed against op1
        """
        
        if isinstance(op1, Insert) and isinstance(op2, Insert):
            return OperationalTransform.transform_insert_insert(op1, op2)
        elif isinstance(op1, Insert) and isinstance(op2, Delete):
            return OperationalTransform.transform_insert_delete(op1, op2)
        elif isinstance(op1, Delete) and isinstance(op2, Insert):
            op2_prime, op1_prime = OperationalTransform.transform_insert_delete(op2, op1)
            return op1_prime, op2_prime
        elif isinstance(op1, Delete) and isinstance(op2, Delete):
            return OperationalTransform.transform_delete_delete(op1, op2)
    
    @staticmethod
    def transform_insert_insert(ins1, ins2):
        if ins1.position < ins2.position:
# ins1 happens before ins2
            return ins1, Insert(ins2.position + ins1.length, ins2.text, ins2.client_id)
        elif ins1.position > ins2.position:
# ins2 happens before ins1
            return Insert(ins1.position + ins2.length, ins1.text, ins1.client_id), ins2
        else:
# Same position - use client_id for deterministic ordering
            if ins1.client_id < ins2.client_id:
                return ins1, Insert(ins2.position + ins1.length, ins2.text, ins2.client_id)
            else:
                return Insert(ins1.position + ins2.length, ins1.text, ins1.client_id), ins2
    
    @staticmethod
    def transform_insert_delete(ins, delete):
        if ins.position <= delete.position:
# Insert happens before delete
            return ins, Delete(delete.position + ins.length, delete.length, delete.client_id)
        elif ins.position >= delete.position + delete.length:
# Insert happens after delete
            return Insert(ins.position - delete.length, ins.text, ins.client_id), delete
        else:
# Insert happens in middle of delete
            return Insert(delete.position, ins.text, ins.client_id), \
                   Delete(delete.position + ins.length, delete.length, delete.client_id)
    
    @staticmethod
    def transform_delete_delete(del1, del2):
        if del1.position + del1.length <= del2.position:
# del1 happens before del2
            return del1, Delete(del2.position - del1.length, del2.length, del2.client_id)
        elif del2.position + del2.length <= del1.position:
# del2 happens before del1
            return Delete(del1.position - del2.length, del1.length, del1.client_id), del2
        else:
# Overlapping deletes
            if del1.position <= del2.position:
                if del1.position + del1.length >= del2.position + del2.length:
# del1 contains del2
                    return Delete(del1.position, del1.length - del2.length, del1.client_id), \
                           Delete(del1.position, 0, del2.client_id)
                else:
# Partial overlap
                    overlap = del1.position + del1.length - del2.position
                    return Delete(del1.position, del1.length - overlap, del1.client_id), \
                           Delete(del1.position + del1.length - overlap, del2.length - overlap, del2.client_id)
            else:
# Mirror case
                del2_prime, del1_prime = OperationalTransform.transform_delete_delete(del2, del1)
                return del1_prime, del2_prime
```

## Detailed Component Design

### 1. Client-Side Editor

**Local Operation Handling**
```javascript
class CollaborativeEditor {
    constructor(documentId, userId) {
        this.documentId = documentId;
        this.userId = userId;
        this.document = new Document();
        this.pendingOperations = [];
        this.acknowledgedOperations = [];
        this.websocket = null;
        this.version = 0;
    }
    
    // Handle local text insertion
    handleLocalInsert(position, text) {
        // Apply immediately for responsive feel
        this.document.insert(position, text);
        
        // Create operation
        const operation = new Insert(position, text, this.userId);
        
        // Transform against pending operations
        let transformedOp = operation;
        for (let pendingOp of this.pendingOperations) {
            [transformedOp, pendingOp] = transform(transformedOp, pendingOp);
        }
        
        // Send to server
        this.sendOperation(transformedOp);
        
        // Add to pending
        this.pendingOperations.push(transformedOp);
    }
    
    // Handle remote operation
    handleRemoteOperation(operation) {
        // Transform against pending operations
        let transformedOp = operation;
        const newPending = [];
        
        for (let pendingOp of this.pendingOperations) {
            [pendingOp, transformedOp] = transform(pendingOp, transformedOp);
            newPending.push(pendingOp);
        }
        
        this.pendingOperations = newPending;
        
        // Apply transformed operation
        this.applyOperation(transformedOp);
        
        // Update version
        this.version++;
    }
    
    // Handle acknowledgment from server
    handleAcknowledgment(operationId) {
        // Move from pending to acknowledged
        const index = this.pendingOperations.findIndex(op => op.id === operationId);
        if (index !== -1) {
            const [acknowledged] = this.pendingOperations.splice(index, 1);
            this.acknowledgedOperations.push(acknowledged);
        }
    }
}
```

**Cursor and Selection Tracking**
```javascript
class CursorManager {
    constructor(editor) {
        this.editor = editor;
        this.remoteCursors = new Map();
        this.localSelection = null;
    }
    
    updateLocalSelection(start, end) {
        this.localSelection = { start, end };
        this.broadcastSelection();
    }
    
    handleRemoteSelection(userId, selection) {
        // Transform selection based on pending operations
        let transformedSelection = this.transformSelection(selection);
        
        // Update or create remote cursor
        if (!this.remoteCursors.has(userId)) {
            this.remoteCursors.set(userId, new RemoteCursor(userId));
        }
        
        const cursor = this.remoteCursors.get(userId);
        cursor.updatePosition(transformedSelection);
        cursor.render();
    }
    
    transformSelection(selection) {
        let { start, end } = selection;
        
        for (let op of this.editor.pendingOperations) {
            if (op instanceof Insert) {
                if (op.position <= start) {
                    start += op.length;
                    end += op.length;
                } else if (op.position < end) {
                    end += op.length;
                }
            } else if (op instanceof Delete) {
                if (op.position + op.length <= start) {
                    start -= op.length;
                    end -= op.length;
                } else if (op.position < start) {
                    const deletedBeforeStart = start - op.position;
                    start = op.position;
                    end -= deletedBeforeStart;
                }
            }
        }
        
        return { start, end };
    }
}
```

### 2. Server-Side Operation Processing

**Document Session Manager**
```python
class DocumentSession:
    def __init__(self, document_id):
        self.document_id = document_id
        self.clients = {}  # client_id -> ClientState
        self.document = self.load_document(document_id)
        self.operation_history = []
        self.version = 0
        self.lock = threading.Lock()
    
    def add_client(self, client_id, websocket):
        with self.lock:
            self.clients[client_id] = ClientState(
                client_id=client_id,
                websocket=websocket,
                version=self.version
            )
            
# Send current document state
            self.send_document_state(client_id)
    
    def handle_operation(self, client_id, operation):
        with self.lock:
            client = self.clients[client_id]
            
# Transform operation against operations the client hasn't seen
            transformed_op = operation
            for i in range(client.version, self.version):
                history_op = self.operation_history[i]
                transformed_op, _ = transform(transformed_op, history_op)
            
# Apply operation
            self.document.apply_operation(transformed_op)
            
# Add to history
            self.operation_history.append(transformed_op)
            self.version += 1
            
# Broadcast to other clients
            self.broadcast_operation(transformed_op, exclude_client=client_id)
            
# Acknowledge to sender
            self.acknowledge_operation(client_id, operation.id)
            
# Update client version
            client.version = self.version
            
# Persist operation
            self.persist_operation(transformed_op)
    
    def broadcast_operation(self, operation, exclude_client=None):
        for client_id, client in self.clients.items():
            if client_id != exclude_client:
                try:
                    client.websocket.send_json({
                        'type': 'operation',
                        'operation': operation.to_dict(),
                        'version': self.version
                    })
                except:
# Handle disconnected client
                    self.remove_client(client_id)
```

**Conflict Resolution Service**
```python
class ConflictResolver:
    def __init__(self):
        self.operation_buffer = {}  # document_id -> operation_queue
        
    def resolve_conflicts(self, document_id, operations):
        """
        Resolve conflicts among concurrent operations
        """
        if len(operations) <= 1:
            return operations
        
# Sort by timestamp and client_id for deterministic ordering
        sorted_ops = sorted(operations, key=lambda op: (op.timestamp, op.client_id))
        
# Apply operational transformation
        resolved = []
        for i, op in enumerate(sorted_ops):
            transformed_op = op
# Transform against all previously resolved operations
            for prev_op in resolved:
                transformed_op, _ = transform(transformed_op, prev_op)
            resolved.append(transformed_op)
        
        return resolved
```

### 3. Document Storage

**Document Model**
```python
class DocumentModel:
    def __init__(self):
        self.storage = SpannerClient()
        
    def save_document(self, document):
        """Save document with ACID guarantees"""
        with self.storage.transaction() as txn:
# Save document metadata
            txn.insert('documents', {
                'document_id': document.id,
                'title': document.title,
                'owner_id': document.owner_id,
                'created_at': document.created_at,
                'modified_at': timestamp(),
                'version': document.version
            })
            
# Save document content
            txn.insert('document_content', {
                'document_id': document.id,
                'content': document.get_content(),
                'content_hash': document.calculate_hash()
            })
            
# Save access control
            for user_id, permission in document.permissions.items():
                txn.insert('document_permissions', {
                    'document_id': document.id,
                    'user_id': user_id,
                    'permission': permission,
                    'granted_at': timestamp()
                })
    
    def save_operation(self, document_id, operation):
        """Save operation to operation log"""
        self.storage.insert('operations', {
            'operation_id': generate_uuid(),
            'document_id': document_id,
            'operation_type': operation.__class__.__name__,
            'operation_data': json.dumps(operation.to_dict()),
            'client_id': operation.client_id,
            'timestamp': operation.timestamp,
            'version': operation.version
        })
```

### 4. Version History

**Version Management**
```python
class VersionManager:
    def __init__(self):
        self.storage = StorageService()
        self.compression = CompressionService()
        
    def create_version(self, document_id, trigger='auto'):
        """Create a new version snapshot"""
# Get current document state
        document = self.get_document(document_id)
        
# Get operations since last version
        last_version = self.get_latest_version(document_id)
        operations = self.get_operations_since(document_id, last_version.version)
        
# Create version snapshot
        version = {
            'version_id': generate_uuid(),
            'document_id': document_id,
            'version_number': last_version.version_number + 1,
            'content': self.compression.compress(document.content),
            'operation_count': len(operations),
            'created_at': timestamp(),
            'created_by': document.last_modified_by,
            'trigger': trigger,  # 'auto', 'manual', 'before_major_change'
            'size_bytes': len(document.content)
        }
        
# Store version
        self.storage.save_version(version)
        
# Clean up old operations if needed
        if len(operations) > 10000:
            self.compact_operations(document_id, version)
        
        return version
    
    def restore_version(self, document_id, version_id):
        """Restore document to a specific version"""
# Get target version
        version = self.get_version(version_id)
        
# Get all operations from target version to current
        current_ops = self.get_operations_since(document_id, version.version_number)
        
# Create reverse operations
        reverse_ops = []
        for op in reversed(current_ops):
            if isinstance(op, Insert):
                reverse_ops.append(Delete(op.position, op.length, 'system'))
            elif isinstance(op, Delete):
# Need to get deleted text from document history
                deleted_text = self.get_deleted_text(op)
                reverse_ops.append(Insert(op.position, deleted_text, 'system'))
        
# Apply reverse operations
        return reverse_ops
```

### 5. Offline Support

**Offline Queue Manager**
```javascript
class OfflineManager {
    constructor(editor) {
        this.editor = editor;
        this.offlineQueue = [];
        this.isOnline = navigator.onLine;
        this.localStorage = window.localStorage;
        
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
    }
    
    queueOperation(operation) {
        // Add to offline queue
        this.offlineQueue.push(operation);
        
        // Persist to localStorage
        this.saveOfflineQueue();
        
        // Apply locally
        this.editor.applyOperationLocally(operation);
    }
    
    handleOnline() {
        this.isOnline = true;
        
        // Sync offline changes
        this.syncOfflineChanges();
    }
    
    async syncOfflineChanges() {
        // Get latest document state from server
        const serverState = await this.fetchDocumentState();
        
        // Get operations that happened while offline
        const serverOps = this.getServerOperationsSince(this.lastSyncVersion);
        
        // Transform offline operations against server operations
        let transformedOfflineOps = [];
        for (let offlineOp of this.offlineQueue) {
            let transformed = offlineOp;
            for (let serverOp of serverOps) {
                [transformed, ] = transform(transformed, serverOp);
            }
            transformedOfflineOps.push(transformed);
        }
        
        // Send transformed operations to server
        for (let op of transformedOfflineOps) {
            await this.editor.sendOperation(op);
        }
        
        // Clear offline queue
        this.offlineQueue = [];
        this.saveOfflineQueue();
    }
}
```

### 6. Comments and Suggestions

**Comment System**
```python
class CommentSystem:
    def __init__(self):
        self.comment_store = CommentStore()
        
    def add_comment(self, document_id, comment_data):
        """Add a comment to a document"""
        comment = {
            'comment_id': generate_uuid(),
            'document_id': document_id,
            'thread_id': comment_data.get('thread_id') or generate_uuid(),
            'author_id': comment_data['author_id'],
            'content': comment_data['content'],
            'range_start': comment_data['range_start'],
            'range_end': comment_data['range_end'],
            'created_at': timestamp(),
            'resolved': False
        }
        
# Save comment
        self.comment_store.save(comment)
        
# Notify participants
        self.notify_comment_participants(comment)
        
        return comment
    
    def transform_comment_range(self, comment, operations):
        """Transform comment range based on document operations"""
        start = comment['range_start']
        end = comment['range_end']
        
        for op in operations:
            if isinstance(op, Insert):
                if op.position <= start:
                    start += op.length
                    end += op.length
                elif op.position < end:
                    end += op.length
            elif isinstance(op, Delete):
                if op.position + op.length <= start:
                    start -= op.length
                    end -= op.length
                elif op.position < end:
# Comment partially or fully deleted
                    if op.position <= start and op.position + op.length >= end:
# Comment fully deleted
                        return None
# Adjust for partial deletion
                    if op.position <= start:
                        deleted_before_start = start - op.position
                        start = op.position
                        end -= deleted_before_start
                    else:
                        end = min(end, op.position)
        
        return {'range_start': start, 'range_end': end}
```

## Performance Optimizations

### 1. Operation Batching
```python
class OperationBatcher:
    def __init__(self, flush_interval=50):  # 50ms
        self.operation_buffer = []
        self.flush_interval = flush_interval
        self.timer = None
        
    def add_operation(self, operation):
        self.operation_buffer.append(operation)
        
# Reset timer
        if self.timer:
            self.timer.cancel()
        
# Set new timer
        self.timer = threading.Timer(
            self.flush_interval / 1000.0,
            self.flush_operations
        )
        self.timer.start()
    
    def flush_operations(self):
        if not self.operation_buffer:
            return
        
# Merge consecutive operations where possible
        merged = self.merge_operations(self.operation_buffer)
        
# Send batch
        self.send_batch(merged)
        
# Clear buffer
        self.operation_buffer = []
```

### 2. Lazy Loading
```javascript
class DocumentLoader {
    constructor() {
        this.loadedChunks = new Map();
        this.chunkSize = 1000; // 1000 characters per chunk
    }
    
    async loadVisibleContent(viewport) {
        const startChunk = Math.floor(viewport.start / this.chunkSize);
        const endChunk = Math.ceil(viewport.end / this.chunkSize);
        
        const chunks = [];
        for (let i = startChunk; i <= endChunk; i++) {
            if (!this.loadedChunks.has(i)) {
                const chunk = await this.fetchChunk(i);
                this.loadedChunks.set(i, chunk);
            }
            chunks.push(this.loadedChunks.get(i));
        }
        
        return chunks.join('');
    }
}
```

### 3. Delta Compression
```python
class DeltaCompression:
    def compress_operations(self, operations):
        """Compress a sequence of operations"""
        compressed = []
        current_insert = None
        
        for op in operations:
            if isinstance(op, Insert):
                if current_insert and current_insert.position + current_insert.length == op.position:
# Merge consecutive inserts
                    current_insert.text += op.text
                    current_insert.length += op.length
                else:
                    if current_insert:
                        compressed.append(current_insert)
                    current_insert = op
            else:
                if current_insert:
                    compressed.append(current_insert)
                    current_insert = None
                compressed.append(op)
        
        if current_insert:
            compressed.append(current_insert)
        
        return compressed
```

## Challenges and Solutions

### 1. Network Latency
**Challenge**: Users experience lag when typing
**Solution**:
- Optimistic UI updates
- Local operation application
- Operation prediction
- Regional servers

### 2. Large Documents
**Challenge**: Performance degrades with document size
**Solution**:
- Document chunking
- Lazy loading
- Virtual scrolling
- Progressive rendering

### 3. Complex Formatting
**Challenge**: Rich text formatting conflicts
**Solution**:
- Attribute-based operations
- Format inheritance rules
- Style conflict resolution
- Nested structure handling

### 4. Presence Awareness
**Challenge**: Showing who's editing what
**Solution**:
- Efficient cursor broadcasting
- Viewport-based updates
- Presence timeout handling
- Color assignment algorithm

## Monitoring and Analytics

### Key Metrics
```python
class DocsMetrics:
    def collect_metrics(self):
        return {
            'performance': {
                'operation_latency_p50': self.get_percentile('op_latency', 50),
                'operation_latency_p99': self.get_percentile('op_latency', 99),
                'sync_time_p50': self.get_percentile('sync_time', 50),
                'conflict_rate': self.calculate_conflict_rate()
            },
            'scale': {
                'active_documents': self.count_active_documents(),
                'concurrent_editors': self.count_concurrent_editors(),
                'operations_per_second': self.get_ops_rate(),
                'websocket_connections': self.count_connections()
            },
            'quality': {
                'sync_success_rate': self.calculate_sync_success(),
                'data_loss_incidents': self.count_data_loss(),
                'version_restore_success': self.calculate_restore_success()
            }
        }
```

## Security Considerations

### Access Control
```python
class AccessControl:
    def check_permission(self, user_id, document_id, action):
# Get user's permission level
        permission = self.get_user_permission(user_id, document_id)
        
# Check action allowed
        if action == 'read':
            return permission in ['viewer', 'commenter', 'editor', 'owner']
        elif action == 'comment':
            return permission in ['commenter', 'editor', 'owner']
        elif action == 'edit':
            return permission in ['editor', 'owner']
        elif action == 'admin':
            return permission == 'owner'
        
        return False
```

### Operation Validation
- Validate all operations server-side
- Check operation bounds
- Verify user permissions
- Rate limiting per user

## Future Enhancements

### Near-term
1. **Voice Typing**: Real-time transcription
2. **Smart Compose**: AI-powered suggestions
3. **Template System**: Document templates
4. **Plugin API**: Third-party extensions

### Long-term
1. **CRDT Alternative**: Explore CRDTs for P2P editing
2. **Blockchain Verification**: Tamper-proof documents
3. **AR Collaboration**: Spatial document editing
4. **AI Co-author**: Intelligent writing assistant

## Interview Tips

1. **Start with OT**: Core algorithm understanding crucial
2. **Handle Conflicts**: Show deep understanding of edge cases
3. **Consider Scale**: Millions of concurrent edits
4. **Network Issues**: Address latency and offline scenarios
5. **Data Model**: Efficient storage and retrieval

## Common Follow-up Questions

1. **"How would you handle image/video in documents?"**
   - Separate asset pipeline
   - CDN for media delivery
   - Placeholder while loading
   - Collaborative annotations

2. **"How do you implement access control?"**
   - Document-level permissions
   - Real-time permission updates
   - Share link generation
   - Audit logging

3. **"How would you handle very large documents?"**
   - Document sharding
   - Pagination/chunking
   - Lazy loading
   - Section-based editing

4. **"How do you ensure no data loss?"**
   - Multiple operation logs
   - Frequent auto-save
   - Client-side persistence
   - Multi-region replication