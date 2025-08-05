#!/usr/bin/env python3
"""
Add Missing Descriptions to Pattern Files

This script adds thoughtful descriptions to patterns that are missing them,
based on their content and established patterns.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any

class DescriptionAdder:
    def __init__(self, base_path: str = "docs/pattern-library"):
        self.base_path = Path(base_path)
        
        # Enhanced descriptions based on pattern analysis
        self.enhanced_descriptions = {
            "cap-theorem": "Fundamental theorem defining trade-offs between Consistency, Availability, and Partition tolerance in distributed systems",
            "event-driven": "Architectural pattern where components communicate through events, enabling loose coupling and scalability",
            "cell-based": "Architecture pattern that isolates failures by partitioning systems into independent cells with shared-nothing design",
            "distributed-lock": "Coordination pattern that ensures mutual exclusion across distributed systems using consensus algorithms",
            "event-sourcing": "Data management pattern that stores all changes as immutable events, enabling audit trails and time travel",
            "cdc": "Data synchronization pattern that captures and propagates database changes in real-time",
            "cqrs": "Architectural pattern separating read and write operations to optimize performance and scalability",
            "consistent-hashing": "Load distribution algorithm that minimizes reorganization when nodes are added or removed",
            "geo-distribution": "Scaling pattern that distributes data and compute across geographic regions for performance and compliance",
            "multi-region": "Deployment pattern that spans multiple geographic regions for disaster recovery and latency optimization",
            "sharding": "Data partitioning technique that horizontally distributes data across multiple database instances",
            "backpressure": "Flow control mechanism that prevents system overload by limiting upstream request rates",
            "auto-scaling": "Dynamic resource management pattern that adjusts capacity based on demand metrics",
            "load-balancing": "Traffic distribution pattern that spreads requests across multiple backend instances",
            "service-mesh": "Infrastructure layer providing service-to-service communication, security, and observability",
            "publish-subscribe": "Messaging pattern that decouples producers and consumers through event-based communication",
            "request-reply": "Synchronous communication pattern where clients wait for responses from services",
            "service-discovery": "Pattern that allows services to find and connect to each other dynamically in distributed systems",
            "service-registry": "Centralized directory that maintains locations and metadata of available services",
            "websocket": "Full-duplex communication protocol enabling real-time bidirectional data exchange",
            "api-gateway": "Single entry point that routes requests to appropriate backend services with cross-cutting concerns",
            "grpc": "High-performance RPC framework using Protocol Buffers for efficient service communication",
            "bulkhead": "Isolation pattern that prevents failures in one component from cascading to others",
            "health-check": "Monitoring pattern that regularly verifies service availability and operational status",
            "graceful-degradation": "Resilience pattern that maintains partial functionality when components fail",
            "failover": "Disaster recovery pattern that automatically switches to backup systems during failures",
            "split-brain": "Problem and solution pattern for handling network partitions in distributed systems",
            "timeout": "Time-bound execution pattern that prevents indefinite waits in distributed operations",
            "retry-backoff": "Error handling pattern that implements intelligent retry logic with exponential backoff",
            "fault-tolerance": "System design approach that continues operating despite component failures",
            "load-shedding": "Overload protection pattern that selectively drops requests to maintain system stability",
            "heartbeat": "Liveness detection pattern using periodic signals between distributed components",
            "actor-model": "Concurrency pattern using isolated actors that communicate through message passing",
            "cas": "Atomic operation pattern for lock-free data structure updates in concurrent systems",
            "clock-sync": "Time coordination pattern ensuring consistent ordering across distributed nodes",
            "consensus": "Agreement protocol enabling distributed nodes to reach consistent decisions",
            "leader-election": "Coordination pattern for selecting a single coordinator among distributed nodes",
            "leader-follower": "Replication pattern with a primary node handling writes and replicas serving reads",
            "lease": "Time-bound exclusive access pattern for distributed resource management",
            "logical-clocks": "Ordering mechanism for events in distributed systems without global time",
            "distributed-lock": "Mutual exclusion primitive for coordinating access to shared resources",
            "distributed-queue": "Message queuing pattern that provides ordering and delivery guarantees",
            "emergent-leader": "Dynamic leadership pattern where coordinators emerge based on system conditions",
            "generation-clock": "Versioning mechanism for detecting stale data and coordinating updates",
            "hlc": "Hybrid logical clock combining physical and logical time for event ordering",
            "low-high-water-marks": "Progress tracking pattern using boundaries to manage data consistency",
            "state-watch": "Notification pattern for monitoring and reacting to state changes",
            "bloom-filter": "Probabilistic data structure for space-efficient set membership testing",
            "crdt": "Conflict-free replicated data type enabling concurrent updates without coordination",
            "data-lake": "Storage architecture for raw data in native format with schema-on-read",
            "deduplication": "Data cleaning pattern that removes duplicate records from datasets",
            "delta-sync": "Incremental synchronization pattern transferring only changed data",
            "distributed-storage": "Storage architecture that spreads data across multiple nodes for scalability",
            "eventual-consistency": "Consistency model where replicas converge to the same state over time",
            "lsm-tree": "Write-optimized data structure using multiple levels of sorted files",
            "materialized-view": "Pre-computed query results stored for fast read access",
            "merkle-trees": "Tree structure using cryptographic hashes for efficient data verification",
            "outbox": "Transactional messaging pattern ensuring reliable event publishing",
            "polyglot-persistence": "Architecture using different databases optimized for specific data needs",
            "read-repair": "Consistency maintenance pattern that fixes stale data during read operations",
            "saga": "Long-running transaction pattern using compensating actions for failure recovery",
            "segmented-log": "Append-only storage pattern dividing logs into manageable segments",
            "shared-database": "Anti-pattern where multiple services share the same database",
            "tunable-consistency": "Flexible consistency model allowing applications to choose guarantees",
            "write-ahead-log": "Durability pattern that logs changes before applying them to storage",
            "analytics-scale": "Architecture patterns for processing large-scale analytical workloads",
            "chunking": "Data processing pattern that divides large datasets into manageable pieces",
            "edge-computing": "Computing paradigm that processes data closer to its source",
            "geo-replication": "Data replication across geographic regions for locality and disaster recovery",
            "id-generation-scale": "Scalable identifier generation patterns for distributed systems",
            "priority-queue": "Data structure that serves elements based on priority rather than insertion order",
            "queues-streaming": "Data processing patterns using queues and streams for scalable pipelines",
            "rate-limiting": "Traffic control pattern that restricts the number of requests per time window",
            "request-batching": "Optimization pattern that groups multiple requests for efficient processing",
            "scatter-gather": "Parallel processing pattern that distributes work and collects results",
            "tile-caching": "Caching strategy for geographic and hierarchical data using tile-based storage",
            "url-normalization": "URL processing pattern that standardizes URLs for consistent handling",
            "caching-strategies": "Systematic approaches to storing frequently accessed data for performance"
        }

    def extract_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter and body from markdown content."""
        if not content.startswith('---'):
            return {}, content
        
        try:
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                end_marker = content.find('\n---', 3)
                if end_marker == -1:
                    return {}, content
            
            frontmatter = content[3:end_marker].strip()
            body = content[end_marker + 4:]
            
            metadata = yaml.safe_load(frontmatter) or {}
            return metadata, body
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return {}, content

    def write_frontmatter(self, metadata: Dict[str, Any], body: str) -> str:
        """Write metadata and body back to markdown format."""
        if not metadata:
            return body
        
        frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        return f"---\n{frontmatter}---\n{body}"

    def add_description(self, file_path: Path) -> bool:
        """Add description to a pattern file if missing."""
        pattern_name = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Could not read {file_path.name}: {e}")
            return False
        
        metadata, body = self.extract_frontmatter(content)
        
        if not metadata:
            print(f"⚠️  No frontmatter in {file_path.name}")
            return False
        
        # Check if description already exists and is meaningful
        current_desc = metadata.get("description", "")
        if current_desc and not current_desc.startswith("Distributed systems pattern:"):
            print(f"ℹ️  {file_path.name} already has a meaningful description")
            return False
        
        # Add enhanced description
        if pattern_name in self.enhanced_descriptions:
            metadata["description"] = self.enhanced_descriptions[pattern_name]
            print(f"✓ Added enhanced description to {file_path.name}")
        else:
            # Fallback to generic description
            readable_name = pattern_name.replace('-', ' ').title()
            metadata["description"] = f"Distributed systems pattern: {readable_name}"
            print(f"✓ Added generic description to {file_path.name}")
        
        # Write back to file
        try:
            new_content = self.write_frontmatter(metadata, body)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"❌ Could not write {file_path.name}: {e}")
            return False

    def process_all_patterns(self) -> Dict[str, int]:
        """Process all pattern files to add missing descriptions."""
        pattern_files = [f for f in self.base_path.rglob("*.md") 
                        if f.name != "index.md" and "pattern-" not in f.name]
        
        stats = {
            "total_files": len(pattern_files),
            "files_modified": 0,
            "files_with_errors": 0,
            "files_skipped": 0
        }
        
        print(f"🔍 Processing {stats['total_files']} pattern files...")
        
        for file_path in pattern_files:
            try:
                if self.add_description(file_path):
                    stats["files_modified"] += 1
                else:
                    stats["files_skipped"] += 1
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                stats["files_with_errors"] += 1
        
        return stats

def main():
    """Main function."""
    print("📝 Adding Missing Pattern Descriptions")
    print("=" * 50)
    
    adder = DescriptionAdder()
    stats = adder.process_all_patterns()
    
    print(f"\n📊 SUMMARY")
    print(f"{'='*30}")
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Files skipped (already have descriptions): {stats['files_skipped']}")
    print(f"Files with errors: {stats['files_with_errors']}")
    
    if stats["files_modified"] > 0:
        print(f"\n✅ Added descriptions to {stats['files_modified']} pattern files!")
        print("Run the validation script to verify all fixes.")
    else:
        print(f"\nℹ️  All files already have descriptions or were skipped.")

if __name__ == "__main__":
    main()