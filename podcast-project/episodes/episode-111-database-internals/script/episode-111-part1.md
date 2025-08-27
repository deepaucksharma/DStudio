# Episode 111: Database Internals - The Storage Engine
## Part 1: The Foundation of Data (Minutes 1-60)

*Total Word Count Target: 20,000 words*
*Part 1 Target: 7,000 words*

---

## Opening Hook - The Aadhaar Mystery

*[Sound effect: Hard drive spinning, keyboard clicks]*

**Narrator (mysteriously):** "Dosto, ek sawal - Aadhaar database mein 140 crore Indians ka data hai. Har record mein photo, fingerprints, iris scan - matlab terabytes of data! Phir bhi, aapka Aadhaar verification 2 second mein kaise ho jata hai? IRCTC pe Tatkal booking time pe 10 lakh log ek saath ticket book karte hain - database crash kyun nahi hota?"

*[Pause for effect]*

"Aaj hum dekhenge database ke andar kya magic hota hai. B-trees, LSM trees, Write-Ahead Logging - ye sab technical terms sunne mein complex lagte hain, lekin main aapko Mumbai ke examples se samjhaunga. Imagine karo, database ek bahut bada library hai, aur hume 1 second mein koi bhi book dhundni hai!"

## Chapter 1: The B-Tree - The Library Catalog System

### Understanding B-Trees Through Mumbai's Telephone Directory

"B-Tree ko samjhne ke liye, think of Mumbai's old telephone directory - lakhs of phone numbers, alphabetically arranged, aur aap 10 seconds mein kisi ka bhi number dhund sakte the!"

```python
import bisect
from typing import List, Optional, Any, Tuple
import json

class BTreeNode:
    """
    B-Tree node implementation
    Like a page in telephone directory
    """
    
    def __init__(self, order: int = 4, is_leaf: bool = True):
        self.order = order  # Maximum children per node
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.children: List['BTreeNode'] = []
        self.is_leaf = is_leaf
        self.parent: Optional['BTreeNode'] = None
        
        # Metadata like in Aadhaar database
        self.metadata = {
            'created_at': None,
            'modified_at': None,
            'access_count': 0,
            'page_id': None
        }
    
    def is_full(self) -> bool:
        """Check if node is full"""
        return len(self.keys) >= 2 * self.order - 1
    
    def is_empty(self) -> bool:
        """Check if node is empty"""
        return len(self.keys) == 0

class AadhaarBTree:
    """
    B-Tree implementation inspired by Aadhaar database
    Handling 1.4 billion records efficiently
    """
    
    def __init__(self, order: int = 128):
        """
        Initialize B-Tree
        Order 128 means each node can have 256 keys
        Like Aadhaar's actual implementation
        """
        self.root = BTreeNode(order=order, is_leaf=True)
        self.order = order
        self.height = 1
        self.total_keys = 0
        
        # Performance metrics
        self.stats = {
            'searches': 0,
            'inserts': 0,
            'disk_reads': 0,
            'disk_writes': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        print(f"🌳 Aadhaar B-Tree Initialized")
        print(f"   Order: {order} (max {2*order-1} keys per node)")
        print(f"   Like: Mumbai telephone directory pages")
        print(f"   Capacity: Can handle 1.4 billion records efficiently")
    
    def insert(self, aadhaar_number: str, citizen_data: dict):
        """
        Insert citizen data into B-Tree
        Like adding new phone number to directory
        """
        print(f"\n📝 Inserting Aadhaar: {aadhaar_number}")
        
        # Check if root is full
        if self.root.is_full():
            print("   ⚠️ Root full - splitting like adding new directory volume")
            old_root = self.root
            self.root = BTreeNode(order=self.order, is_leaf=False)
            self.root.children.append(old_root)
            old_root.parent = self.root
            self._split_child(self.root, 0)
            self.height += 1
        
        self._insert_non_full(self.root, aadhaar_number, citizen_data)
        self.total_keys += 1
        self.stats['inserts'] += 1
        
        print(f"   ✅ Inserted successfully")
        print(f"   Total records: {self.total_keys:,}")
    
    def search(self, aadhaar_number: str) -> Optional[dict]:
        """
        Search for citizen data
        Like looking up phone number in directory
        """
        print(f"\n🔍 Searching Aadhaar: {aadhaar_number}")
        self.stats['searches'] += 1
        
        result, disk_reads = self._search_recursive(self.root, aadhaar_number, 0)
        
        self.stats['disk_reads'] += disk_reads
        
        if result:
            print(f"   ✅ Found in {disk_reads} disk reads")
            print(f"   Time complexity: O(log n) where n = {self.total_keys:,}")
        else:
            print(f"   ❌ Not found after {disk_reads} disk reads")
        
        return result
    
    def _search_recursive(self, node: BTreeNode, key: str, depth: int) -> Tuple[Optional[dict], int]:
        """
        Recursive search implementation
        """
        disk_reads = 1  # Reading current node
        node.metadata['access_count'] += 1
        
        # Find position where key should be
        pos = bisect.bisect_left(node.keys, key)
        
        # Check if key found
        if pos < len(node.keys) and node.keys[pos] == key:
            if node.is_leaf:
                return node.values[pos], disk_reads
            else:
                # In non-leaf, continue to child
                child_result, child_reads = self._search_recursive(
                    node.children[pos + 1], key, depth + 1
                )
                return child_result, disk_reads + child_reads
        
        # If leaf node, key not found
        if node.is_leaf:
            return None, disk_reads
        
        # Search in appropriate child
        child_result, child_reads = self._search_recursive(
            node.children[pos], key, depth + 1
        )
        return child_result, disk_reads + child_reads
    
    def _insert_non_full(self, node: BTreeNode, key: str, value: dict):
        """
        Insert into non-full node
        """
        pos = bisect.bisect_left(node.keys, key)
        
        if node.is_leaf:
            # Insert directly into leaf
            node.keys.insert(pos, key)
            node.values.insert(pos, value)
            self.stats['disk_writes'] += 1
        else:
            # Insert into appropriate child
            child = node.children[pos]
            
            if child.is_full():
                self._split_child(node, pos)
                # After split, key might go to next child
                if key > node.keys[pos]:
                    child = node.children[pos + 1]
            
            self._insert_non_full(child, key, value)
    
    def _split_child(self, parent: BTreeNode, index: int):
        """
        Split full child node
        Like splitting phone directory into two volumes
        """
        order = self.order
        child = parent.children[index]
        new_child = BTreeNode(order=order, is_leaf=child.is_leaf)
        
        # Move half of keys to new node
        mid_index = order - 1
        new_child.keys = child.keys[mid_index + 1:]
        child.keys = child.keys[:mid_index]
        
        if child.is_leaf:
            new_child.values = child.values[mid_index + 1:]
            child.values = child.values[:mid_index]
        else:
            new_child.children = child.children[mid_index + 1:]
            child.children = child.children[:mid_index + 1]
            
            # Update parent pointers
            for grandchild in new_child.children:
                grandchild.parent = new_child
        
        # Insert middle key into parent
        parent.keys.insert(index, child.keys[mid_index])
        parent.children.insert(index + 1, new_child)
        new_child.parent = parent
        
        self.stats['disk_writes'] += 3  # Parent, child, new_child
        
    def analyze_performance(self):
        """
        Analyze B-Tree performance
        Like analyzing library efficiency
        """
        print("\n📊 B-Tree Performance Analysis:")
        print(f"   Tree Height: {self.height}")
        print(f"   Total Keys: {self.total_keys:,}")
        print(f"   Max Keys per Node: {2 * self.order - 1}")
        
        # Calculate capacity at each level
        print("\n   🏗️ Level-wise Capacity:")
        total_capacity = 0
        for level in range(self.height):
            if level == 0:
                capacity = 2 * self.order - 1
            else:
                capacity = (2 * self.order) ** level * (2 * self.order - 1)
            total_capacity += capacity
            print(f"   Level {level}: {capacity:,} keys")
        
        print(f"   Total Capacity: {total_capacity:,} keys")
        
        # Performance metrics
        print("\n   ⚡ Operation Statistics:")
        print(f"   Searches: {self.stats['searches']:,}")
        print(f"   Inserts: {self.stats['inserts']:,}")
        print(f"   Disk Reads: {self.stats['disk_reads']:,}")
        print(f"   Disk Writes: {self.stats['disk_writes']:,}")
        
        if self.stats['searches'] > 0:
            avg_reads = self.stats['disk_reads'] / self.stats['searches']
            print(f"   Avg Reads per Search: {avg_reads:.2f}")
            print(f"   Theoretical Maximum: {self.height}")
```

### B+ Tree - The Optimized Version

"B+ Tree is like improved telephone directory - index pages upar, actual data pages neeche. Aadhaar database actually B+ Tree use karta hai!"

```python
class BPlusTreeNode:
    """
    B+ Tree node - optimized for range queries
    Used in actual database systems
    """
    
    def __init__(self, order: int = 128, is_leaf: bool = True):
        self.order = order
        self.keys: List[str] = []
        self.is_leaf = is_leaf
        
        if is_leaf:
            # Leaf nodes store actual data
            self.values: List[dict] = []
            self.next_leaf: Optional['BPlusTreeNode'] = None  # Linked list of leaves
            self.prev_leaf: Optional['BPlusTreeNode'] = None
        else:
            # Internal nodes store child pointers
            self.children: List['BPlusTreeNode'] = []
        
        self.parent: Optional['BPlusTreeNode'] = None

class IRCTCBPlusTree:
    """
    B+ Tree optimized for IRCTC Tatkal booking
    Handles millions of concurrent searches
    """
    
    def __init__(self, order: int = 256):
        """
        Higher order for better cache performance
        Like IRCTC's actual database configuration
        """
        self.root = BPlusTreeNode(order=order, is_leaf=True)
        self.order = order
        self.first_leaf = self.root  # For range queries
        
        print(f"🚂 IRCTC B+ Tree Initialized")
        print(f"   Order: {order}")
        print(f"   Optimized for: Tatkal booking surge")
        print(f"   Special: Linked leaves for range queries")
    
    def insert_train_seat(self, pnr: str, booking_data: dict):
        """
        Insert train seat booking
        Optimized for Tatkal time rush
        """
        # If root is full, split it
        if len(self.root.keys) >= 2 * self.order - 1:
            new_root = BPlusTreeNode(order=self.order, is_leaf=False)
            new_root.children.append(self.root)
            self.root.parent = new_root
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, pnr, booking_data)
    
    def range_query(self, start_pnr: str, end_pnr: str) -> List[dict]:
        """
        Range query - get all bookings in PNR range
        Very efficient in B+ Tree due to linked leaves
        """
        print(f"\n📋 Range Query: {start_pnr} to {end_pnr}")
        
        results = []
        
        # Find starting leaf
        current_leaf = self._find_leaf(start_pnr)
        
        # Traverse linked list of leaves
        while current_leaf:
            for i, key in enumerate(current_leaf.keys):
                if key >= start_pnr and key <= end_pnr:
                    results.append({
                        'pnr': key,
                        'data': current_leaf.values[i]
                    })
                elif key > end_pnr:
                    print(f"   ✅ Found {len(results)} bookings")
                    return results
            
            current_leaf = current_leaf.next_leaf
        
        print(f"   ✅ Found {len(results)} bookings")
        return results
    
    def _find_leaf(self, key: str) -> BPlusTreeNode:
        """
        Find leaf node for given key
        """
        current = self.root
        
        while not current.is_leaf:
            # Binary search in internal node
            pos = bisect.bisect_right(current.keys, key)
            current = current.children[pos]
        
        return current
    
    def _split_child(self, parent: BPlusTreeNode, index: int):
        """
        Split child node when full
        """
        child = parent.children[index]
        new_node = BPlusTreeNode(order=self.order, is_leaf=child.is_leaf)
        
        mid_index = self.order - 1
        
        if child.is_leaf:
            # Split leaf node
            new_node.keys = child.keys[mid_index:]
            new_node.values = child.values[mid_index:]
            child.keys = child.keys[:mid_index]
            child.values = child.values[:mid_index]
            
            # Update linked list pointers
            new_node.next_leaf = child.next_leaf
            new_node.prev_leaf = child
            child.next_leaf = new_node
            
            if new_node.next_leaf:
                new_node.next_leaf.prev_leaf = new_node
            
            # In B+ tree, copy first key of new node to parent
            parent.keys.insert(index, new_node.keys[0])
        else:
            # Split internal node
            new_node.keys = child.keys[mid_index + 1:]
            new_node.children = child.children[mid_index + 1:]
            
            # Move middle key up to parent
            parent.keys.insert(index, child.keys[mid_index])
            
            child.keys = child.keys[:mid_index]
            child.children = child.children[:mid_index + 1]
            
            # Update parent pointers
            for grandchild in new_node.children:
                grandchild.parent = new_node
        
        parent.children.insert(index + 1, new_node)
        new_node.parent = parent
```

## Chapter 2: LSM Trees - The Write-Optimized Architecture

### Understanding LSM Through Mumbai Dabbawalas

"LSM Tree is like Mumbai ke dabbawalas - collect karo, sort karo, merge karo, deliver karo! Write fast, read with some delay but very efficient!"

```python
import heapq
import os
import pickle
from typing import List, Dict, Any, Optional
import time

class MemTable:
    """
    In-memory component of LSM tree
    Like dabbawala's morning collection point
    """
    
    def __init__(self, max_size: int = 1000000):  # 1MB
        self.data: Dict[str, Any] = {}
        self.size = 0
        self.max_size = max_size
        self.write_count = 0
        
        print(f"📝 MemTable Initialized")
        print(f"   Max Size: {max_size / 1000000:.1f} MB")
        print(f"   Like: Dabbawala collection point")
    
    def put(self, key: str, value: Any) -> bool:
        """
        Write to MemTable
        """
        value_size = len(str(value).encode())
        
        if self.size + value_size > self.max_size:
            return False  # Need to flush
        
        self.data[key] = value
        self.size += value_size
        self.write_count += 1
        
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """
        Read from MemTable
        """
        return self.data.get(key)
    
    def is_full(self) -> bool:
        """Check if MemTable needs flushing"""
        return self.size >= self.max_size

class SSTable:
    """
    Sorted String Table - Immutable disk component
    Like sorted dabba arrangement at station
    """
    
    def __init__(self, level: int, filename: str):
        self.level = level
        self.filename = filename
        self.index: Dict[str, int] = {}  # Key -> file offset
        self.bloom_filter = set()  # Simplified bloom filter
        self.size = 0
        self.key_range = (None, None)  # Min and max keys
        
    def write_from_memtable(self, memtable: MemTable):
        """
        Flush MemTable to SSTable
        Like dabbawalas sorting at station
        """
        print(f"\n💾 Flushing MemTable to SSTable")
        print(f"   Level: {self.level}")
        print(f"   Keys: {len(memtable.data)}")
        
        # Sort keys
        sorted_keys = sorted(memtable.data.keys())
        
        if sorted_keys:
            self.key_range = (sorted_keys[0], sorted_keys[-1])
        
        # Write to disk (simulated)
        with open(self.filename, 'wb') as f:
            offset = 0
            for key in sorted_keys:
                self.index[key] = offset
                self.bloom_filter.add(key)
                
                # Serialize and write
                data = pickle.dumps({key: memtable.data[key]})
                f.write(data)
                offset += len(data)
                self.size += len(data)
        
        print(f"   ✅ Written {self.size / 1000:.1f} KB")
        print(f"   Key Range: {self.key_range}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Read from SSTable
        """
        # Check bloom filter first
        if key not in self.bloom_filter:
            return None
        
        # Binary search in index
        if key not in self.index:
            return None
        
        # Read from disk
        with open(self.filename, 'rb') as f:
            f.seek(self.index[key])
            # Read approximate size (simplified)
            data = f.read(1000)
            record = pickle.loads(data)
            return record.get(key)

class LSMTree:
    """
    Complete LSM Tree implementation
    Like Cassandra/RocksDB storage engine
    Used by WhatsApp, Instagram
    """
    
    def __init__(self, memtable_size: int = 1000000, level_multiplier: int = 10):
        self.memtable = MemTable(max_size=memtable_size)
        self.immutable_memtable: Optional[MemTable] = None
        self.levels: List[List[SSTable]] = [[] for _ in range(7)]  # 7 levels like RocksDB
        self.level_multiplier = level_multiplier
        
        # Statistics
        self.stats = {
            'writes': 0,
            'reads': 0,
            'flushes': 0,
            'compactions': 0
        }
        
        print(f"🌲 LSM Tree Initialized")
        print(f"   Levels: 7 (L0 to L6)")
        print(f"   Level Multiplier: {level_multiplier}x")
        print(f"   Like: WhatsApp message storage")
    
    def put(self, key: str, value: Any):
        """
        Write to LSM Tree
        Always writes to MemTable first
        """
        self.stats['writes'] += 1
        
        # Try to write to MemTable
        if not self.memtable.put(key, value):
            # MemTable full, need to flush
            print(f"\n⚠️ MemTable full - triggering flush")
            self._flush_memtable()
            
            # Retry write
            self.memtable.put(key, value)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Read from LSM Tree
        Check MemTable -> Immutable MemTable -> SSTables (newest to oldest)
        """
        self.stats['reads'] += 1
        
        # Check MemTable
        result = self.memtable.get(key)
        if result is not None:
            return result
        
        # Check Immutable MemTable if exists
        if self.immutable_memtable:
            result = self.immutable_memtable.get(key)
            if result is not None:
                return result
        
        # Check SSTables level by level
        for level in range(len(self.levels)):
            # Search from newest to oldest in each level
            for sstable in reversed(self.levels[level]):
                # Check key range first
                if sstable.key_range[0] and sstable.key_range[1]:
                    if key < sstable.key_range[0] or key > sstable.key_range[1]:
                        continue
                
                result = sstable.get(key)
                if result is not None:
                    return result
        
        return None
    
    def _flush_memtable(self):
        """
        Flush MemTable to disk as SSTable
        """
        self.stats['flushes'] += 1
        
        # Create new SSTable at Level 0
        sstable_filename = f"sstable_L0_{int(time.time())}.db"
        sstable = SSTable(level=0, filename=sstable_filename)
        sstable.write_from_memtable(self.memtable)
        
        # Add to Level 0
        self.levels[0].append(sstable)
        
        # Create new MemTable
        self.memtable = MemTable(max_size=self.memtable.max_size)
        
        # Trigger compaction if needed
        self._maybe_compact()
    
    def _maybe_compact(self):
        """
        Check if compaction needed
        Like reorganizing dabbas for efficient delivery
        """
        for level in range(len(self.levels) - 1):
            max_files = 4 if level == 0 else (self.level_multiplier ** level)
            
            if len(self.levels[level]) > max_files:
                print(f"\n🔄 Compaction needed at Level {level}")
                self._compact_level(level)
                self.stats['compactions'] += 1
    
    def _compact_level(self, level: int):
        """
        Compact SSTables from level to level+1
        Merge and deduplicate data
        """
        print(f"   Compacting Level {level} -> Level {level + 1}")
        
        # Select SSTables to compact
        files_to_compact = self.levels[level][:4]  # Compact 4 files
        
        # Merge sort all entries
        merged_data = {}
        for sstable in files_to_compact:
            # Read all data from SSTable (simplified)
            for key in sstable.index.keys():
                value = sstable.get(key)
                merged_data[key] = value  # Latest value wins
        
        # Create new SSTable at next level
        new_sstable_filename = f"sstable_L{level+1}_{int(time.time())}.db"
        new_sstable = SSTable(level=level+1, filename=new_sstable_filename)
        
        # Create temporary MemTable for writing
        temp_memtable = MemTable()
        for key, value in merged_data.items():
            temp_memtable.put(key, value)
        
        new_sstable.write_from_memtable(temp_memtable)
        
        # Update levels
        self.levels[level + 1].append(new_sstable)
        
        # Remove compacted files from current level
        for sstable in files_to_compact:
            self.levels[level].remove(sstable)
            # Delete file (simplified)
            if os.path.exists(sstable.filename):
                os.remove(sstable.filename)
        
        print(f"   ✅ Compacted {len(files_to_compact)} files into 1")
    
    def analyze_structure(self):
        """
        Analyze LSM Tree structure
        """
        print("\n📊 LSM Tree Structure Analysis:")
        
        total_sstables = 0
        total_size = 0
        
        for level in range(len(self.levels)):
            sstables = self.levels[level]
            level_size = sum(s.size for s in sstables)
            total_sstables += len(sstables)
            total_size += level_size
            
            if sstables:
                print(f"   Level {level}: {len(sstables)} SSTables, {level_size/1000:.1f} KB")
        
        print(f"\n   Total SSTables: {total_sstables}")
        print(f"   Total Size: {total_size/1000:.1f} KB")
        print(f"   Write Amplification: ~{total_sstables/max(1, self.stats['writes']/1000):.1f}x")
        
        print(f"\n   Statistics:")
        print(f"   Writes: {self.stats['writes']:,}")
        print(f"   Reads: {self.stats['reads']:,}")
        print(f"   Flushes: {self.stats['flushes']}")
        print(f"   Compactions: {self.stats['compactions']}")
```

## Chapter 3: Write-Ahead Logging (WAL) - The Safety Net

### WAL as Cashier's Daily Register

"WAL is like cashier ka daily register - pehle likho, phir kaam karo. Power cut ho jaye, data safe!"

```python
import struct
import hashlib
from enum import Enum
from dataclasses import dataclass
import threading

class WALRecordType(Enum):
    """Types of WAL records"""
    BEGIN_TXN = 1
    COMMIT_TXN = 2
    ABORT_TXN = 3
    INSERT = 4
    UPDATE = 5
    DELETE = 6
    CHECKPOINT = 7

@dataclass
class WALRecord:
    """Single WAL record entry"""
    lsn: int  # Log Sequence Number
    txn_id: int  # Transaction ID
    record_type: WALRecordType
    table_name: str
    data: dict
    timestamp: float
    checksum: str = ""
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for integrity"""
        data_str = f"{self.lsn}{self.txn_id}{self.record_type}{self.data}"
        return hashlib.md5(data_str.encode()).hexdigest()[:8]

class BankingWAL:
    """
    Write-Ahead Logging for banking transactions
    Like SBI Core Banking System
    """
    
    def __init__(self, wal_file: str = "sbi_transactions.wal"):
        self.wal_file = wal_file
        self.current_lsn = 0
        self.active_transactions = {}
        self.lock = threading.Lock()
        self.buffer = []
        self.buffer_size = 8192  # 8KB buffer
        
        # Recovery information
        self.last_checkpoint_lsn = 0
        
        print(f"💾 WAL System Initialized")
        print(f"   File: {wal_file}")
        print(f"   Like: SBI daily transaction log")
        print(f"   Buffer: {self.buffer_size} bytes")
    
    def begin_transaction(self, txn_id: int) -> int:
        """
        Start new transaction
        Like opening new page in cashier's register
        """
        with self.lock:
            self.current_lsn += 1
            record = WALRecord(
                lsn=self.current_lsn,
                txn_id=txn_id,
                record_type=WALRecordType.BEGIN_TXN,
                table_name="",
                data={},
                timestamp=time.time()
            )
            
            self._write_record(record)
            self.active_transactions[txn_id] = self.current_lsn
            
            print(f"\n📝 Transaction {txn_id} started")
            print(f"   LSN: {self.current_lsn}")
            
            return self.current_lsn
    
    def log_operation(self, txn_id: int, operation: str, 
                      table: str, data: dict) -> int:
        """
        Log database operation
        Like writing each transaction in register
        """
        with self.lock:
            if txn_id not in self.active_transactions:
                raise ValueError(f"Transaction {txn_id} not active")
            
            self.current_lsn += 1
            
            # Map operation to record type
            op_map = {
                'INSERT': WALRecordType.INSERT,
                'UPDATE': WALRecordType.UPDATE,
                'DELETE': WALRecordType.DELETE
            }
            
            record = WALRecord(
                lsn=self.current_lsn,
                txn_id=txn_id,
                record_type=op_map[operation],
                table_name=table,
                data=data,
                timestamp=time.time()
            )
            record.checksum = record.calculate_checksum()
            
            self._write_record(record)
            
            print(f"   ➡️ {operation} on {table}")
            print(f"      LSN: {self.current_lsn}")
            
            return self.current_lsn
    
    def commit_transaction(self, txn_id: int):
        """
        Commit transaction
        Like stamping 'verified' on register entry
        """
        with self.lock:
            if txn_id not in self.active_transactions:
                raise ValueError(f"Transaction {txn_id} not active")
            
            self.current_lsn += 1
            record = WALRecord(
                lsn=self.current_lsn,
                txn_id=txn_id,
                record_type=WALRecordType.COMMIT_TXN,
                table_name="",
                data={},
                timestamp=time.time()
            )
            
            self._write_record(record)
            self._flush_buffer()  # Force flush on commit
            
            del self.active_transactions[txn_id]
            
            print(f"   ✅ Transaction {txn_id} committed")
            print(f"      LSN: {self.current_lsn}")
    
    def _write_record(self, record: WALRecord):
        """
        Write record to WAL buffer
        """
        # Serialize record (simplified)
        serialized = f"{record.lsn}|{record.txn_id}|{record.record_type.value}|"
        serialized += f"{record.table_name}|{record.data}|{record.timestamp}|{record.checksum}\n"
        
        self.buffer.append(serialized)
        
        # Flush if buffer full
        if len("".join(self.buffer).encode()) > self.buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """
        Flush buffer to disk
        Like closing cash register at day end
        """
        if not self.buffer:
            return
        
        with open(self.wal_file, 'a') as f:
            for record in self.buffer:
                f.write(record)
        
        self.buffer.clear()
        print(f"   💾 Buffer flushed to disk")
    
    def recover(self) -> List[WALRecord]:
        """
        Recover from WAL after crash
        Like reconstructing day's transactions from register
        """
        print("\n🔄 Starting Recovery from WAL")
        
        recovered_records = []
        committed_txns = set()
        aborted_txns = set()
        
        try:
            with open(self.wal_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) < 7:
                        continue
                    
                    record = WALRecord(
                        lsn=int(parts[0]),
                        txn_id=int(parts[1]),
                        record_type=WALRecordType(int(parts[2])),
                        table_name=parts[3],
                        data=eval(parts[4]) if parts[4] != '{}' else {},
                        timestamp=float(parts[5]),
                        checksum=parts[6] if len(parts) > 6 else ""
                    )
                    
                    # Track transaction status
                    if record.record_type == WALRecordType.COMMIT_TXN:
                        committed_txns.add(record.txn_id)
                    elif record.record_type == WALRecordType.ABORT_TXN:
                        aborted_txns.add(record.txn_id)
                    
                    recovered_records.append(record)
        
        except FileNotFoundError:
            print("   ⚠️ No WAL file found")
            return []
        
        # Filter records - only replay committed transactions
        valid_records = []
        for record in recovered_records:
            if record.txn_id in committed_txns:
                valid_records.append(record)
                print(f"   ✅ Replaying TXN {record.txn_id}, LSN {record.lsn}")
            elif record.txn_id in aborted_txns:
                print(f"   ❌ Skipping aborted TXN {record.txn_id}")
            elif record.record_type not in [WALRecordType.BEGIN_TXN, 
                                           WALRecordType.CHECKPOINT]:
                print(f"   ⚠️ Incomplete TXN {record.txn_id} - rolling back")
        
        print(f"\n   Recovery Summary:")
        print(f"   Total Records: {len(recovered_records)}")
        print(f"   Valid Records: {len(valid_records)}")
        print(f"   Committed Transactions: {len(committed_txns)}")
        
        return valid_records
```

---

*[Part 1 continues to reach 7,000 words with more examples and explanations...]*

**[TO BE CONTINUED IN PART 2...]**