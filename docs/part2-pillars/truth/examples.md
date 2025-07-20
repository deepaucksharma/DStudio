---
title: Truth & Consensus Examples
description: "class SpannerTransaction:
    def __init__(self, truetime):
        self.truetime = truetime
        self.commit_timestamp = None

    def ..."
type: pillar
difficulty: advanced
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Truth](/part2-pillars/truth/) → **Truth & Consensus Examples**

# Truth & Consensus Examples

## Real-World Case Studies

### 1. Google Spanner: Global Consistency with TrueTime

**Problem**: Achieve external consistency across globally distributed data centers

**Innovation**: TrueTime API - exposing clock uncertainty explicitly

```python
class TrueTimeAPI:
    def now(self):
        """Returns an interval [earliest, latest] within which current time lies"""
        # GPS and atomic clocks provide bounds on uncertainty
        uncertainty = self.get_clock_uncertainty()  # ~7ms average
        current = self.get_current_time()

        return TrueTimeInterval(
            earliest=current - uncertainty,
            latest=current + uncertainty
        )

    def after(self, timestamp):
        """True if timestamp is definitely in the past"""
        return self.now().earliest > timestamp

    def before(self, timestamp):
        """True if timestamp is definitely in the future"""
        return self.now().latest < timestamp

class SpannerTransaction:
    def __init__(self, truetime):
        self.truetime = truetime
        self.commit_timestamp = None

    def commit(self):
        # Assign commit timestamp
        self.commit_timestamp = self.truetime.now().latest

        # Wait out the uncertainty
        while not self.truetime.after(self.commit_timestamp):
            time.sleep(0.001)  # Wait 1ms

        # Now safe to release locks - guarantees external consistency
        self.release_locks()
        return self.commit_timestamp
```

**Key Insights**:
- By waiting out clock uncertainty, Spanner guarantees external consistency
- Commit wait averages 7ms - acceptable for many workloads
- Enables globally consistent snapshots without coordination

### 2. Bitcoin: Probabilistic Consensus Through Proof-of-Work

**Problem**: Achieve consensus without trusted parties in adversarial environment

**Solution**: Longest chain rule with economic incentives

```python
class BlockchainConsensus:
    def __init__(self):
        self.chain = []
        self.difficulty = 4  # Number of leading zeros required

    def mine_block(self, transactions, previous_hash):
        """Find nonce that produces valid hash"""
        block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': transactions,
            'previous_hash': previous_hash,
            'nonce': 0
        }

        # Proof of work
        while True:
            block_hash = self.calculate_hash(block)
            if block_hash.startswith('0' * self.difficulty):
                block['hash'] = block_hash
                return block
            block['nonce'] += 1

    def validate_chain(self, chain):
        """Validate entire blockchain"""
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]

            # Check hash link
            if current['previous_hash'] != previous['hash']:
                return False

            # Check proof of work
            if not self.valid_proof(current):
                return False

        return True

    def consensus(self, other_chains):
        """Adopt longest valid chain"""
        longest_chain = self.chain
        max_length = len(self.chain)

        for chain in other_chains:
            if len(chain) > max_length and self.validate_chain(chain):
                longest_chain = chain
                max_length = len(chain)

        if longest_chain != self.chain:
            self.chain = longest_chain
            return True  # Chain replaced

        return False
```

**Probabilistic Finality**:
- After 1 block: ~70% chance of permanence
- After 6 blocks: >99.9% chance
- After 100 blocks: Practically irreversible

### 3. Apache ZooKeeper: Hierarchical Consensus

**Problem**: Provide coordination primitives for distributed systems

**Architecture**: ZAB (ZooKeeper Atomic Broadcast)

```python
class ZooKeeperNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.state = 'follower'
        self.zxid = 0  # ZooKeeper transaction ID
        self.history = []  # Committed transactions

    class Transaction:
        def __init__(self, type, path, data, zxid):
            self.type = type  # create, set, delete
            self.path = path
            self.data = data
            self.zxid = zxid

    def propose_change(self, path, data):
        """Leader proposes change to followers"""
        if self.state != 'leader':
            raise Exception("Only leader can propose")

        # Assign transaction ID (epoch, counter)
        self.zxid += 1
        txn = self.Transaction('set', path, data, self.zxid)

        # Phase 1: Proposal
        acks = 0
        for follower in self.followers:
            if follower.log_proposal(txn):
                acks += 1

        # Phase 2: Commit (if quorum)
        if acks >= len(self.followers) // 2:
            for follower in self.followers:
                follower.commit(txn.zxid)
            self.history.append(txn)
            return True

        return False

    def create_ephemeral_node(self, path, data, session_id):
        """Create node tied to client session"""
        node = {
            'path': path,
            'data': data,
            'ephemeral': True,
            'session_id': session_id,
            'version': 0,
            'ctime': time.time(),
            'mtime': time.time()
        }

        # Use for distributed locks, leader election
        return self.create_node(node)

    def watch_node(self, path, watcher):
        """Get notified of changes"""
        # One-time trigger on change
        self.watchers[path].append(watcher)

        # Return current data
        return self.get_data(path)
```

**Use Cases**:
- Configuration management
- Service discovery
- Distributed locks
- Leader election
- Barrier synchronization

### 4. Ethereum: Smart Contract Consensus

**Problem**: Agree not just on data, but on computation results

**Solution**: Ethereum Virtual Machine with deterministic execution

```python
class EthereumConsensus:
    def __init__(self):
        self.state = {}  # Global state tree
        self.receipts = []  # Transaction receipts

    def execute_transaction(self, tx, block_context):
        """Execute transaction deterministically"""
        # Create execution context
        context = EVMContext(
            caller=tx.from_address,
            origin=tx.from_address,
            gas_price=tx.gas_price,
            value=tx.value,
            data=tx.data,
            block_number=block_context.number,
            timestamp=block_context.timestamp,
            difficulty=block_context.difficulty
        )

        # Execute with gas metering
        result = self.evm.execute(
            code=self.get_code(tx.to_address),
            context=context,
            gas_limit=tx.gas_limit
        )

        # Update state
        if result.success:
            self.apply_state_changes(result.state_changes)

        # Create receipt
        receipt = TransactionReceipt(
            transaction_hash=tx.hash,
            success=result.success,
            gas_used=result.gas_used,
            logs=result.logs,
            return_data=result.return_data
        )

        return receipt

    def validate_block(self, block):
        """Validate all transactions in block"""
        temp_state = self.state.copy()

        for tx in block.transactions:
            try:
                receipt = self.execute_transaction(tx, block)
                if not receipt.success:
                    return False
            except Exception:
                return False

        # Verify state root
        computed_root = self.compute_state_root()
        return computed_root == block.state_root
```

### 5. CockroachDB: Consensus for SQL

**Problem**: Distributed SQL with ACID guarantees

**Solution**: Raft consensus with MVCC

```python
class CockroachConsensus:
    def __init__(self):
        self.ranges = {}  # key_range -> RaftGroup

    class RaftGroup:
        def __init__(self, range_id, replicas):
            self.range_id = range_id
            self.replicas = replicas
            self.leader = None
            self.log = []
            self.commit_index = 0

        def propose_write(self, key, value, timestamp):
            """Propose write through Raft"""
            if not self.is_leader():
                return self.forward_to_leader(key, value, timestamp)

            # Create log entry
            entry = LogEntry(
                index=len(self.log),
                term=self.current_term,
                command=WriteCommand(key, value, timestamp),
                timestamp=timestamp
            )

            # Replicate to followers
            success_count = 1  # Leader counts

            for replica in self.replicas:
                if replica != self.node_id:
                    if self.replicate_entry(replica, entry):
                        success_count += 1

            # Commit if majority
            if success_count > len(self.replicas) // 2:
                self.commit_index = entry.index
                self.apply_entry(entry)
                return True

            return False

        def handle_split_brain(self):
            """Handle network partition"""
            # Only partition with majority can progress
            active_replicas = self.get_active_replicas()

            if len(active_replicas) <= len(self.replicas) // 2:
                # Step down - we're in minority
                self.state = 'follower'
                raise UnavailableException("In minority partition")
```

## Consensus Algorithm Implementations

### 1. Paxos Implementation

```python
class PaxosNode:
    def __init__(self, node_id, acceptors):
        self.node_id = node_id
        self.acceptors = acceptors

        # Proposer state
        self.proposal_number = 0

        # Acceptor state
        self.promised_proposal = None
        self.accepted_proposal = None
        self.accepted_value = None

    def propose(self, value):
        """Run Paxos to propose a value"""
        # Phase 1a: Prepare
        self.proposal_number += 1
        proposal_id = (self.proposal_number, self.node_id)

        # Send prepare to all acceptors
        promises = []
        for acceptor in self.acceptors:
            promise = acceptor.prepare(proposal_id)
            if promise:
                promises.append(promise)

        # Need majority
        if len(promises) <= len(self.acceptors) // 2:
            return False

        # Phase 2a: Accept
        # Choose value (highest numbered accepted value or our value)
        chosen_value = value
        for promise in promises:
            if promise.accepted_proposal:
                if not self.accepted_proposal or promise.accepted_proposal > self.accepted_proposal:
                    chosen_value = promise.accepted_value

        # Send accept to all acceptors
        accepted_count = 0
        for acceptor in self.acceptors:
            if acceptor.accept(proposal_id, chosen_value):
                accepted_count += 1

        # Success if majority accepted
        return accepted_count > len(self.acceptors) // 2

    def prepare(self, proposal_id):
        """Acceptor: Handle prepare request"""
        if self.promised_proposal and proposal_id < self.promised_proposal:
            return None  # Already promised higher proposal

        self.promised_proposal = proposal_id

        return {
            'promised': proposal_id,
            'accepted_proposal': self.accepted_proposal,
            'accepted_value': self.accepted_value
        }

    def accept(self, proposal_id, value):
        """Acceptor: Handle accept request"""
        if self.promised_proposal and proposal_id < self.promised_proposal:
            return False

        self.promised_proposal = proposal_id
        self.accepted_proposal = proposal_id
        self.accepted_value = value

        return True
```

### 2. Byzantine Fault Tolerant Consensus

```python
class PBFTNode:
    """Practical Byzantine Fault Tolerance"""
    def __init__(self, node_id, nodes, f):
        self.node_id = node_id
        self.nodes = nodes
        self.f = f  # Maximum Byzantine nodes
        self.view = 0
        self.sequence_number = 0

    def is_primary(self):
        return self.nodes[self.view % len(self.nodes)] == self.node_id

    def client_request(self, operation):
        """Handle client request (primary only)"""
        if not self.is_primary():
            return self.forward_to_primary(operation)

        # Assign sequence number
        seq = self.sequence_number
        self.sequence_number += 1

        # Phase 1: Pre-prepare
        message = PrePrepareMessage(self.view, seq, operation)
        self.broadcast_to_replicas(message)

        return seq

    def handle_preprepare(self, message):
        """Handle pre-prepare from primary"""
        if not self.verify_message(message):
            return

        # Phase 2: Prepare
        prepare = PrepareMessage(
            self.view,
            message.sequence,
            message.operation_digest,
            self.node_id
        )
        self.broadcast_to_replicas(prepare)

        self.log_prepare(prepare)

    def handle_prepare(self, message):
        """Collect prepare messages"""
        self.log_prepare(message)

        # Check if we have 2f prepares
        prepare_count = self.count_prepares(message.sequence)

        if prepare_count >= 2 * self.f:
            # Phase 3: Commit
            commit = CommitMessage(
                self.view,
                message.sequence,
                message.operation_digest,
                self.node_id
            )
            self.broadcast_to_replicas(commit)
            self.log_commit(commit)

    def handle_commit(self, message):
        """Collect commit messages"""
        self.log_commit(message)

        # Check if we have 2f+1 commits
        commit_count = self.count_commits(message.sequence)

        if commit_count >= 2 * self.f + 1:
            # Execute operation
            result = self.execute_operation(message.operation)
            self.send_reply_to_client(result)
```

### 3. Blockchain Consensus Variants

```python
class ProofOfStake:
    """Ethereum 2.0 style PoS consensus"""
    def __init__(self):
        self.validators = {}
        self.total_stake = 0

    def add_validator(self, address, stake):
        """Register validator with stake"""
        self.validators[address] = {
            'stake': stake,
            'active': True,
            'last_block': 0
        }
        self.total_stake += stake

    def select_block_proposer(self, slot, randomness):
        """Select proposer weighted by stake"""
        # Use RANDAO for randomness
        seed = hash(str(slot) + randomness)
        rand = seed % self.total_stake

        cumulative = 0
        for address, validator in self.validators.items():
            if validator['active']:
                cumulative += validator['stake']
                if rand < cumulative:
                    return address

        raise Exception("No active validators")

    def slash_validator(self, address, reason):
        """Penalize misbehaving validator"""
        if address not in self.validators:
            return

        validator = self.validators[address]

        # Different penalties for different violations
        if reason == 'double_vote':
            penalty = validator['stake'] * 0.05  # 5% slash
        elif reason == 'surround_vote':
            penalty = validator['stake'] * 0.01  # 1% slash
        else:
            penalty = 0

        validator['stake'] -= penalty
        validator['active'] = False  # Deactivate

        # Burn slashed stake
        self.total_stake -= penalty
```

## Truth Maintenance Systems

### 1. Distributed Version Vectors

```python
class VersionVector:
    """Track concurrent updates across nodes"""
    def __init__(self):
        self.versions = {}  # node_id -> version

    def increment(self, node_id):
        """Increment version for node"""
        if node_id not in self.versions:
            self.versions[node_id] = 0
        self.versions[node_id] += 1

    def merge(self, other):
        """Merge two version vectors"""
        merged = VersionVector()

        all_nodes = set(self.versions.keys()) | set(other.versions.keys())

        for node in all_nodes:
            merged.versions[node] = max(
                self.versions.get(node, 0),
                other.versions.get(node, 0)
            )

        return merged

    def descends_from(self, other):
        """Check if this descends from other"""
        for node, version in other.versions.items():
            if self.versions.get(node, 0) < version:
                return False
        return True

    def concurrent_with(self, other):
        """Check if versions are concurrent"""
        return (not self.descends_from(other) and
                not other.descends_from(self))

class DVVSet:
    """Distributed Version Vector Set - track all concurrent values"""
    def __init__(self):
        self.entries = []  # List of (value, version_vector, timestamp)

    def put(self, value, context, timestamp):
        """Add new value with context"""
        new_vv = context.version_vector.copy()
        new_vv.increment(context.node_id)

        # Remove entries obsoleted by this update
        self.entries = [
            e for e in self.entries
            if not e[1].descends_from(context.version_vector)
        ]

        # Add new entry
        self.entries.append((value, new_vv, timestamp))

    def get(self):
        """Get all concurrent values"""
        # Remove obsolete entries
        self.prune_obsolete()

        # Return all concurrent values
        return [(e[0], e[1]) for e in self.entries]

    def prune_obsolete(self):
        """Remove entries obsoleted by others"""
        pruned = []

        for i, entry in enumerate(self.entries):
            obsolete = False
            for j, other in enumerate(self.entries):
                if i != j and entry[1].descends_from(other[1]):
                    obsolete = True
                    break

            if not obsolete:
                pruned.append(entry)

        self.entries = pruned
```

## Key Takeaways

1. **Truth is expensive** - Consensus requires multiple round trips

2. **Different truths for different needs** - Strong, eventual, causal consistency

3. **Time is fundamental** - Can't order events without time

4. **Byzantine failures change everything** - 3f+1 nodes needed for f failures

5. **Probabilistic consensus can be enough** - Bitcoin proves it

Remember: Perfect truth is impossible in distributed systems. Choose the level of truth your application actually needs.
