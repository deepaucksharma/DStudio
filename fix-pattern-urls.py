#!/usr/bin/env python3
"""Fix pattern URLs and categories in pattern-filtering.js"""

import re
import os

# Read the current JavaScript file
js_file = '/home/deepak/DStudio/docs/javascripts/pattern-filtering.js'
with open(js_file, 'r') as f:
    content = f.read()

# Pattern remapping based on actual file locations
pattern_fixes = [
    # Scaling patterns that were miscategorized
    ('"/DStudio/patterns/id-generation-scale/"', '"/DStudio/pattern-library/scaling/id-generation-scale/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/analytics-scale/"', '"/DStudio/pattern-library/scaling/analytics-scale/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/url-normalization/"', '"/DStudio/pattern-library/scaling/url-normalization/"', 'specialized', 'scaling'),
    
    # Architecture patterns
    ('"/DStudio/patterns/valet-key/"', '"/DStudio/pattern-library/architecture/valet-key/"', 'specialized', 'architecture'),
    ('"/DStudio/patterns/event-streaming/"', '"/DStudio/pattern-library/architecture/event-streaming/"', 'specialized', 'architecture'),
    ('"/DStudio/patterns/lambda-architecture/"', '"/DStudio/pattern-library/architecture/lambda-architecture/"', 'specialized', 'architecture'),
    ('"/DStudio/patterns/kappa-architecture/"', '"/DStudio/pattern-library/architecture/kappa-architecture/"', 'specialized', 'architecture'),
    ('"/DStudio/patterns/graphql-federation/"', '"/DStudio/pattern-library/architecture/graphql-federation/"', 'specialized', 'architecture'),
    
    # Data management patterns
    ('"/DStudio/patterns/bloom-filter/"', '"/DStudio/pattern-library/data-management/bloom-filter/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/merkle-trees/"', '"/DStudio/pattern-library/data-management/merkle-trees/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/crdt/"', '"/DStudio/pattern-library/data-management/crdt/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/lsm-tree/"', '"/DStudio/pattern-library/data-management/lsm-tree/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/polyglot-persistence/"', '"/DStudio/pattern-library/data-management/polyglot-persistence/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/distributed-storage/"', '"/DStudio/pattern-library/data-management/distributed-storage/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/data-lake/"', '"/DStudio/pattern-library/data-management/data-lake/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/tunable-consistency/"', '"/DStudio/pattern-library/data-management/tunable-consistency/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/deduplication/"', '"/DStudio/pattern-library/data-management/deduplication/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/shared-database/"', '"/DStudio/pattern-library/data-management/shared-database/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/read-repair/"', '"/DStudio/pattern-library/data-management/read-repair/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/segmented-log/"', '"/DStudio/pattern-library/data-management/segmented-log/"', 'specialized', 'data-management'),
    ('"/DStudio/patterns/delta-sync/"', '"/DStudio/pattern-library/data-management/delta-sync/"', 'specialized', 'data-management'),
    
    # Coordination patterns
    ('"/DStudio/patterns/actor-model/"', '"/DStudio/pattern-library/coordination/actor-model/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/distributed-queue/"', '"/DStudio/pattern-library/coordination/distributed-queue/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/cas/"', '"/DStudio/pattern-library/coordination/cas/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/emergent-leader/"', '"/DStudio/pattern-library/coordination/emergent-leader/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/leader-follower/"', '"/DStudio/pattern-library/coordination/leader-follower/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/low-high-water-marks/"', '"/DStudio/pattern-library/coordination/low-high-water-marks/"', 'specialized', 'coordination'),
    ('"/DStudio/patterns/state-watch/"', '"/DStudio/pattern-library/coordination/state-watch/"', 'specialized', 'coordination'),
    
    # Scaling patterns
    ('"/DStudio/patterns/chunking/"', '"/DStudio/pattern-library/scaling/chunking/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/geo-distribution/"', '"/DStudio/pattern-library/scaling/geo-distribution/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/geo-replication/"', '"/DStudio/pattern-library/scaling/geo-replication/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/queues-streaming/"', '"/DStudio/pattern-library/scaling/queues-streaming/"', 'specialized', 'scaling'),
    ('"/DStudio/patterns/tile-caching/"', '"/DStudio/pattern-library/scaling/tile-caching/"', 'specialized', 'scaling'),
    
    # Patterns that don't exist - will be removed
    ('"/DStudio/patterns/geohashing/"', '', 'specialized', ''),
    ('"/DStudio/patterns/request-routing/"', '', 'specialized', ''),
    ('"/DStudio/patterns/time-series-ids/"', '', 'specialized', ''),
    ('"/DStudio/patterns/spatial-indexing/"', '', 'specialized', ''),
    ('"/DStudio/patterns/data-mesh/"', '', 'specialized', ''),
    ('"/DStudio/patterns/adaptive-scheduling/"', '', 'specialized', ''),
    ('"/DStudio/patterns/blue-green-deployment/"', '', 'specialized', ''),
    ('"/DStudio/patterns/idempotent-receiver/"', '', 'specialized', ''),
    ('"/DStudio/patterns/observability/"', '', 'specialized', ''),
    ('"/DStudio/patterns/single-socket-channel/"', '', 'specialized', ''),
    ('"/DStudio/patterns/singleton-database/"', '', 'specialized', ''),
    ('"/DStudio/patterns/stored-procedures/"', '', 'specialized', ''),
    ('"/DStudio/patterns/thick-client/"', '', 'specialized', ''),
    ('"/DStudio/patterns/database-per-service/"', '', 'scaling', ''),
    ('"/DStudio/patterns/database-sharding/"', '', 'scaling', ''),
    ('"/DStudio/patterns/geographic-load-balancing/"', '', 'scaling', ''),
    ('"/DStudio/patterns/horizontal-pod-autoscaler/"', '', 'scaling', ''),
    ('"/DStudio/patterns/content-delivery-network/"', '', 'scaling', ''),
    ('"/DStudio/patterns/event-driven/"', '', 'architectural', ''),
    ('"/DStudio/patterns/multi-region/"', '', 'resilience', ''),
    ('"/DStudio/patterns/fault-tolerance/"', '', 'specialized', ''),
]

# Apply fixes
for old_url, new_url, old_cat, new_cat in pattern_fixes:
    if old_url and new_url:  # Update URL and category
        # Find patterns with this URL and update both URL and category
        pattern = rf'({{[^}}]*url: {re.escape(old_url)}[^}}]*category: "{old_cat}"[^}}]*}})'
        
        def replacer(match):
            entry = match.group(1)
            entry = entry.replace(old_url, new_url)
            entry = entry.replace(f'category: "{old_cat}"', f'category: "{new_cat}"')
            return entry
        
        content = re.sub(pattern, replacer, content)
    elif old_url and not new_url:  # Remove pattern
        # Find and remove the entire pattern entry
        pattern = rf'    {{[^}}]*url: {re.escape(old_url)}[^}}]*}},?\n'
        content = re.sub(pattern, '', content)

# Clean up any double commas or trailing commas before closing brackets
content = re.sub(r',\s*,', ',', content)
content = re.sub(r',\s*\]', ']', content)

# Write the fixed content back
with open(js_file, 'w') as f:
    f.write(content)

print("Pattern URLs and categories have been fixed!")