---
title: Truth & Consensus Exercises
description: "Hands-on exercises to build understanding through practical application"
type: pillar
difficulty: advanced
reading_time: 25 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../../index.md) → [Part II: Pillars](../index.md) → [Truth](/part2-pillars/truth/) → **Truth & Consensus Exercises**

# Truth & Consensus Exercises

## Exercise 1: Implement a Lamport Clock System

**Challenge**: Build a system that maintains logical time across distributed nodes.

```python
class LamportClock:
    def __init__(self):
        self.time = 0

    def tick(self):
        """Increment logical time for local event"""
        # TODO: Implement local event handling
        pass

    def send_message(self, message):
        """Attach timestamp when sending message"""
        # TODO: Implement send logic with timestamp
        pass

    def receive_message(self, message, timestamp):
        """Update clock when receiving message"""
        # TODO: Implement receive logic with clock update
        pass

class DistributedSystem:
    def __init__(self, num_nodes):
        self.nodes = {}
        # TODO: Initialize nodes with Lamport clocks

    def simulate_events(self, events):
        """
        Simulate a series of events
        events = [
            ('node1', 'local'),
            ('node1', 'send', 'node2', 'msg1'),
            ('node2', 'receive', 'node1', 'msg1'),
            ('node2', 'local')
        ]
        """
        # TODO: Process events and track timestamps
        pass
```

<details>
<summary>Solution</summary>

```python
class LamportClock:
    def __init__(self):
        self.time = 0

    def tick(self):
        """Increment logical time for local event"""
        self.time += 1
        return self.time

    def send_message(self, message):
        """Attach timestamp when sending message"""
        self.tick()  # Increment before send
        return {
            'content': message,
            'timestamp': self.time
        }

    def receive_message(self, message, timestamp):
        """Update clock when receiving message"""
        # Update to max(local, received) + 1
        self.time = max(self.time, timestamp) + 1
        return self.time

    def get_time(self):
        return self.time

class DistributedSystem:
    def __init__(self, num_nodes):
        self.nodes = {}
        for i in range(num_nodes):
            node_id = f"node{i}"
            self.nodes[node_id] = {
                'clock': LamportClock(),
                'messages': [],
                'log': []
            }

    def simulate_events(self, events):
        """Simulate a series of events"""
        for event in events:
            if event[1] == 'local':
                # Local event
                node_id = event[0]
                time = self.nodes[node_id]['clock'].tick()
                self.nodes[node_id]['log'].append({
                    'type': 'local',
                    'time': time,
                    'event': f"Local event on {node_id}"
                })
                print(f"{node_id}: Local event at time {time}")

            elif event[1] == 'send':
                # Send message
                sender = event[0]
                receiver = event[2]
                msg_content = event[3]

                msg = self.nodes[sender]['clock'].send_message(msg_content)
                self.nodes[receiver]['messages'].append({
                    'from': sender,
                    'message': msg
                })

                self.nodes[sender]['log'].append({
                    'type': 'send',
                    'time': msg['timestamp'],
                    'to': receiver,
                    'message': msg_content
                })

                print(f"{sender}: Sent '{msg_content}' to {receiver} at time {msg['timestamp']}")

            elif event[1] == 'receive':
                # Receive message
                receiver = event[0]
                sender = event[2]

                # Find message from sender
                msg = None
                for i, m in enumerate(self.nodes[receiver]['messages']):
                    if m['from'] == sender:
                        msg = m['message']
                        del self.nodes[receiver]['messages'][i]
                        break

                if msg:
                    time = self.nodes[receiver]['clock'].receive_message(
                        msg['content'],
                        msg['timestamp']
                    )

                    self.nodes[receiver]['log'].append({
                        'type': 'receive',
                        'time': time,
                        'from': sender,
                        'message': msg['content'],
                        'sent_time': msg['timestamp']
                    })

                    print(f"{receiver}: Received '{msg['content']}' from {sender} at time {time}")

    def verify_causality(self):
        """Verify causality is preserved"""
        all_events = []

        # Collect all events
        for node_id, node in self.nodes.items():
            for event in node['log']:
                all_events.append({
                    'node': node_id,
                    'event': event
                })

        # Sort by Lamport time
        all_events.sort(key=lambda x: x['event']['time'])

        print("\nTotal ordering of events:")
        for e in all_events:
            print(f"Time {e['event']['time']}: {e['node']} - {e['event']['type']}")

        # Verify causality
        for i, event in enumerate(all_events):
            if event['event']['type'] == 'receive':
                sent_time = event['event']['sent_time']
                receive_time = event['event']['time']

                # Send must happen before receive
                assert sent_time < receive_time, "Causality violation!"

        print("\nCausality verified ✓")

# Test the implementation
if __name__ == "__main__":
    system = DistributedSystem(3)

    events = [
        ('node0', 'local'),
        ('node0', 'send', 'node1', 'Hello'),
        ('node1', 'local'),
        ('node1', 'receive', 'node0', 'Hello'),
        ('node1', 'send', 'node2', 'Hi there'),
        ('node2', 'receive', 'node1', 'Hi there'),
        ('node2', 'local'),
        ('node0', 'send', 'node2', 'Bye'),
        ('node2', 'receive', 'node0', 'Bye')
    ]

    system.simulate_events(events)
    system.verify_causality()
```

</details>

## Exercise 2: Build a Leader Election System

**Challenge**: Implement a leader election algorithm for a distributed system.

```python
class LeaderElection:
    def __init__(self, node_id, all_nodes):
        self.node_id = node_id
        self.all_nodes = all_nodes
        self.leader = None
        self.election_in_progress = False

    def start_election(self):
        """
        Initiate leader election
        TODO: Implement bully algorithm or ring algorithm
        """
        pass

    def handle_election_message(self, from_node, message_type):
        """
        Handle election-related messages
        TODO: Process ELECTION, OK, COORDINATOR messages
        """
        pass

    def detect_leader_failure(self):
        """
        Detect when current leader has failed
        TODO: Implement heartbeat/timeout mechanism
        """
        pass
```

<details>
<summary>Solution</summary>

```python
import threading
import time
import random

class LeaderElection:
    """Bully Algorithm Implementation"""
    def __init__(self, node_id, all_nodes, network):
        self.node_id = node_id
        self.all_nodes = sorted(all_nodes)  # Ensure consistent ordering
        self.network = network
        self.leader = None
        self.election_in_progress = False
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 1.0
        self.heartbeat_timeout = 3.0
        self.active = True

        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def start_election(self):
        """Initiate leader election using bully algorithm"""
        if self.election_in_progress:
            return

        print(f"Node {self.node_id}: Starting election")
        self.election_in_progress = True
        self.leader = None

        # Send ELECTION message to all nodes with higher ID
        higher_nodes = [n for n in self.all_nodes if n > self.node_id]

        if not higher_nodes:
            # We have the highest ID, become leader
            self._become_leader()
            return

        # Send election messages
        responses = []
        for node in higher_nodes:
            response = self.network.send_message(
                self.node_id,
                node,
                {'type': 'ELECTION', 'from': self.node_id}
            )
            if response and response.get('type') == 'OK':
                responses.append(response)

        if responses:
            # Someone with higher ID responded, wait for COORDINATOR
            self.election_in_progress = False

            # Set timeout to restart election if no COORDINATOR received
            threading.Timer(5.0, self._check_coordinator_received).start()
        else:
            # No one with higher ID responded, become leader
            self._become_leader()

    def handle_election_message(self, from_node, message):
        """Handle election-related messages"""
        msg_type = message.get('type')

        if msg_type == 'ELECTION':
            # Someone with lower ID started election
            if from_node < self.node_id:
                # Respond with OK
                self.network.send_message(
                    self.node_id,
                    from_node,
                    {'type': 'OK', 'from': self.node_id}
                )

                # Start our own election
                self.start_election()

        elif msg_type == 'OK':
            # Someone with higher ID is alive
            # Handled in start_election()
            pass

        elif msg_type == 'COORDINATOR':
            # New leader announcement
            self.leader = from_node
            self.election_in_progress = False
            print(f"Node {self.node_id}: Accepted {from_node} as leader")

        elif msg_type == 'HEARTBEAT':
            # Leader heartbeat
            if from_node == self.leader:
                self.last_heartbeat = time.time()

    def _become_leader(self):
        """Become the leader and announce to all"""
        self.leader = self.node_id
        self.election_in_progress = False
        print(f"Node {self.node_id}: Became leader")

        # Announce to all other nodes
        for node in self.all_nodes:
            if node != self.node_id:
                self.network.send_message(
                    self.node_id,
                    node,
                    {'type': 'COORDINATOR', 'from': self.node_id}
                )

    def _heartbeat_loop(self):
        """Send heartbeats if leader, check heartbeats if follower"""
        while self.active:
            if self.leader == self.node_id:
                # Send heartbeats to all
                for node in self.all_nodes:
                    if node != self.node_id:
                        self.network.send_message(
                            self.node_id,
                            node,
                            {'type': 'HEARTBEAT', 'from': self.node_id}
                        )
            else:
                # Check if leader is alive
                if self.leader and (time.time() - self.last_heartbeat > self.heartbeat_timeout):
                    print(f"Node {self.node_id}: Leader {self.leader} timeout")
                    self.start_election()

            time.sleep(self.heartbeat_interval)

    def _check_coordinator_received(self):
        """Check if COORDINATOR message was received"""
        if not self.leader and not self.election_in_progress:
            # No coordinator received, restart election
            print(f"Node {self.node_id}: No coordinator received, restarting election")
            self.start_election()

class Network:
    """Simulated network for message passing"""
    def __init__(self):
        self.nodes = {}
        self.message_loss_rate = 0.1  # 10% message loss

    def register_node(self, node_id, node):
        self.nodes[node_id] = node

    def send_message(self, from_node, to_node, message):
        # Simulate message loss
        if random.random() < self.message_loss_rate:
            return None

        if to_node in self.nodes:
            # Simulate network delay
            delay = random.uniform(0.01, 0.1)

            def deliver():
                self.nodes[to_node].handle_election_message(from_node, message)

            threading.Timer(delay, deliver).start()

            # Return OK for ELECTION messages
            if message.get('type') == 'ELECTION':
                return {'type': 'OK', 'from': to_node}

        return None

# Test the implementation
def test_leader_election():
    network = Network()
    nodes = []

    # Create 5 nodes
    for i in range(5):
        node = LeaderElection(i, list(range(5)), network)
        nodes.append(node)
        network.register_node(i, node)

    # Start election from node 0
    nodes[0].start_election()

    # Wait for election to complete
    time.sleep(2)

    # Verify all nodes agree on leader
    leaders = [node.leader for node in nodes]
    print(f"\nLeaders: {leaders}")
    assert all(l == 4 for l in leaders), "Not all nodes agree on leader!"

    # Simulate leader failure
    print("\nSimulating leader (node 4) failure...")
    nodes[4].active = False

    # Wait for failure detection and new election
    time.sleep(5)

    # Check new leader (should be node 3)
    active_nodes = nodes[:4]
    leaders = [node.leader for node in active_nodes]
    print(f"New leaders: {leaders}")
    assert all(l == 3 for l in leaders), "Failed to elect new leader!"

if __name__ == "__main__":
    test_leader_election()
```

</details>

## Exercise 3: Implement Two-Phase Commit

**Challenge**: Build a distributed transaction coordinator using 2PC protocol.

```python
class TransactionCoordinator:
    def __init__(self, participants):
        self.participants = participants
        self.tx_log = []

    def begin_transaction(self, tx_id):
        """Start a new distributed transaction"""
        # TODO: Initialize transaction state
        pass

    def execute_transaction(self, tx_id, operations):
        """
        Execute transaction across participants
        operations = {
            'participant1': ['op1', 'op2'],
            'participant2': ['op3', 'op4']
        }
        TODO: Implement 2PC protocol
        """
        pass

class Participant:
    def __init__(self, participant_id):
        self.participant_id = participant_id
        self.prepared_transactions = {}

    def prepare(self, tx_id, operations):
        """Prepare phase of 2PC"""
        # TODO: Validate and prepare operations
        pass

    def commit(self, tx_id):
        """Commit prepared transaction"""
        # TODO: Make changes permanent
        pass

    def abort(self, tx_id):
        """Abort prepared transaction"""
        # TODO: Rollback changes
        pass
```

<details>
<summary>Solution</summary>

```python
import enum
import time
import threading
from collections import defaultdict

class TxState(enum.Enum):
    INIT = "INIT"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"

class TransactionCoordinator:
    def __init__(self, participants):
        self.participants = participants
        self.tx_log = []
        self.transactions = {}
        self.lock = threading.Lock()

    def begin_transaction(self, tx_id):
        """Start a new distributed transaction"""
        with self.lock:
            if tx_id in self.transactions:
                raise Exception(f"Transaction {tx_id} already exists")

            self.transactions[tx_id] = {
                'state': TxState.INIT,
                'participants': set(),
                'prepare_votes': {},
                'start_time': time.time()
            }

            self._log(tx_id, 'BEGIN', {})
            return True

    def execute_transaction(self, tx_id, operations):
        """Execute transaction across participants using 2PC"""
        if tx_id not in self.transactions:
            raise Exception(f"Transaction {tx_id} not found")

        tx = self.transactions[tx_id]
        tx['participants'] = set(operations.keys())

        try:
            # Phase 1: Prepare
            if not self._prepare_phase(tx_id, operations):
                self._abort_transaction(tx_id)
                return False

            # Phase 2: Commit
            return self._commit_phase(tx_id)

        except Exception as e:
            print(f"Transaction {tx_id} failed: {e}")
            self._abort_transaction(tx_id)
            return False

    def _prepare_phase(self, tx_id, operations):
        """Phase 1: Ask all participants to prepare"""
        tx = self.transactions[tx_id]
        tx['state'] = TxState.PREPARING
        self._log(tx_id, 'PREPARE', {'participants': list(tx['participants'])})

        # Send prepare to all participants
        prepare_threads = []

        def prepare_participant(participant_id, ops):
            participant = self.participants[participant_id]
            vote = participant.prepare(tx_id, ops)

            with self.lock:
                tx['prepare_votes'][participant_id] = vote

        # Start prepare requests in parallel
        for participant_id, ops in operations.items():
            thread = threading.Thread(
                target=prepare_participant,
                args=(participant_id, ops)
            )
            thread.start()
            prepare_threads.append(thread)

        # Wait for all prepares with timeout
        timeout = 5.0
        start_time = time.time()

        for thread in prepare_threads:
            remaining = timeout - (time.time() - start_time)
            if remaining > 0:
                thread.join(timeout=remaining)

            if thread.is_alive():
                print(f"Prepare timeout for transaction {tx_id}")
                return False

        # Check votes
        all_votes = all(tx['prepare_votes'].values())

        if all_votes:
            tx['state'] = TxState.PREPARED
            self._log(tx_id, 'PREPARED', {'votes': tx['prepare_votes']})

        return all_votes

    def _commit_phase(self, tx_id):
        """Phase 2: Send commit to all participants"""
        tx = self.transactions[tx_id]
        tx['state'] = TxState.COMMITTING
        self._log(tx_id, 'COMMIT', {})

        # Send commit to all participants
        commit_threads = []
        commit_results = {}

        def commit_participant(participant_id):
            participant = self.participants[participant_id]
            try:
                participant.commit(tx_id)
                commit_results[participant_id] = True
            except Exception as e:
                print(f"Commit failed for {participant_id}: {e}")
                commit_results[participant_id] = False

        for participant_id in tx['participants']:
            thread = threading.Thread(
                target=commit_participant,
                args=(participant_id,)
            )
            thread.start()
            commit_threads.append(thread)

        # Wait for all commits
        for thread in commit_threads:
            thread.join()

        # Transaction is committed even if some participants fail
        # They must eventually commit based on the log
        tx['state'] = TxState.COMMITTED
        self._log(tx_id, 'COMMITTED', {'results': commit_results})

        return True

    def _abort_transaction(self, tx_id):
        """Abort transaction and notify participants"""
        tx = self.transactions[tx_id]
        tx['state'] = TxState.ABORTING
        self._log(tx_id, 'ABORT', {})

        # Send abort to all participants
        for participant_id in tx['participants']:
            if participant_id in self.participants:
                try:
                    self.participants[participant_id].abort(tx_id)
                except Exception as e:
                    print(f"Abort failed for {participant_id}: {e}")

        tx['state'] = TxState.ABORTED
        self._log(tx_id, 'ABORTED', {})

    def _log(self, tx_id, action, data):
        """Write to transaction log for recovery"""
        entry = {
            'timestamp': time.time(),
            'tx_id': tx_id,
            'action': action,
            'data': data
        }
        self.tx_log.append(entry)
        print(f"LOG: {action} for tx {tx_id}")

    def recover(self):
        """Recover from crash using transaction log"""
        # Replay log to determine transaction states
        tx_states = {}

        for entry in self.tx_log:
            tx_id = entry['tx_id']
            action = entry['action']

            if action == 'BEGIN':
                tx_states[tx_id] = TxState.INIT
            elif action == 'PREPARED':
                tx_states[tx_id] = TxState.PREPARED
            elif action == 'COMMITTED':
                tx_states[tx_id] = TxState.COMMITTED
            elif action == 'ABORTED':
                tx_states[tx_id] = TxState.ABORTED

        # Handle incomplete transactions
        for tx_id, state in tx_states.items():
            if state == TxState.PREPARED:
                # Transaction was prepared but not committed/aborted
                # Need to ask participants or make decision
                print(f"Recovery: Transaction {tx_id} in prepared state")
                # In real system, would query participants
                self._abort_transaction(tx_id)

class Participant:
    def __init__(self, participant_id):
        self.participant_id = participant_id
        self.prepared_transactions = {}
        self.committed_transactions = set()
        self.data = {}
        self.lock = threading.Lock()

    def prepare(self, tx_id, operations):
        """Prepare phase of 2PC"""
        with self.lock:
            if tx_id in self.prepared_transactions:
                # Already prepared
                return True

            try:
                # Validate operations
                temp_changes = {}
                for op in operations:
                    if op['type'] == 'set':
                        temp_changes[op['key']] = op['value']
                    elif op['type'] == 'increment':
                        current = self.data.get(op['key'], 0)
                        temp_changes[op['key']] = current + op['amount']
                    else:
                        raise Exception(f"Unknown operation type: {op['type']}")

                # Save prepared state
                self.prepared_transactions[tx_id] = {
                    'operations': operations,
                    'changes': temp_changes,
                    'timestamp': time.time()
                }

                print(f"Participant {self.participant_id}: Prepared tx {tx_id}")
                return True

            except Exception as e:
                print(f"Participant {self.participant_id}: Prepare failed - {e}")
                return False

    def commit(self, tx_id):
        """Commit prepared transaction"""
        with self.lock:
            if tx_id not in self.prepared_transactions:
                raise Exception(f"Transaction {tx_id} not prepared")

            if tx_id in self.committed_transactions:
                # Already committed
                return True

            # Apply changes
            changes = self.prepared_transactions[tx_id]['changes']
            self.data.update(changes)

            # Mark as committed
            self.committed_transactions.add(tx_id)
            del self.prepared_transactions[tx_id]

            print(f"Participant {self.participant_id}: Committed tx {tx_id}")
            return True

    def abort(self, tx_id):
        """Abort prepared transaction"""
        with self.lock:
            if tx_id in self.prepared_transactions:
                del self.prepared_transactions[tx_id]
                print(f"Participant {self.participant_id}: Aborted tx {tx_id}")

            return True

    def get_value(self, key):
        """Get current value"""
        with self.lock:
            return self.data.get(key)

# Test the implementation
def test_2pc():
    # Create participants
    participants = {
        'db1': Participant('db1'),
        'db2': Participant('db2'),
        'db3': Participant('db3')
    }

    # Create coordinator
    coordinator = TransactionCoordinator(participants)

    # Test successful transaction
    print("=== Test 1: Successful transaction ===")
    tx_id = 'tx001'
    coordinator.begin_transaction(tx_id)

    operations = {
        'db1': [
            {'type': 'set', 'key': 'user:1', 'value': 'Alice'},
            {'type': 'set', 'key': 'balance:1', 'value': 100}
        ],
        'db2': [
            {'type': 'set', 'key': 'user:2', 'value': 'Bob'},
            {'type': 'set', 'key': 'balance:2', 'value': 200}
        ],
        'db3': [
            {'type': 'increment', 'key': 'total_users', 'amount': 2}
        ]
    }

    result = coordinator.execute_transaction(tx_id, operations)
    print(f"Transaction result: {result}")

    # Verify data
    print(f"db1 user:1 = {participants['db1'].get_value('user:1')}")
    print(f"db2 user:2 = {participants['db2'].get_value('user:2')}")
    print(f"db3 total_users = {participants['db3'].get_value('total_users')}")

    # Test failed transaction
    print("\n=== Test 2: Failed transaction ===")
    tx_id = 'tx002'
    coordinator.begin_transaction(tx_id)

    operations = {
        'db1': [
            {'type': 'set', 'key': 'user:3', 'value': 'Charlie'}
        ],
        'db2': [
            {'type': 'invalid_op', 'key': 'test'}  # This will fail
        ]
    }

    result = coordinator.execute_transaction(tx_id, operations)
    print(f"Transaction result: {result}")

    # Verify rollback
    print(f"db1 user:3 = {participants['db1'].get_value('user:3')}")  # Should be None

if __name__ == "__main__":
    test_2pc()
```

</details>

## Exercise 4: Byzantine Generals Problem

**Challenge**: Implement a solution to the Byzantine Generals Problem where some nodes can be faulty.

```python
class ByzantineGeneral:
    def __init__(self, general_id, is_traitor=False):
        self.general_id = general_id
        self.is_traitor = is_traitor
        self.received_values = defaultdict(dict)

    def propose_action(self, action):
        """Commander proposes action to all lieutenants"""
        # TODO: Implement message sending (may lie if traitor)
        pass

    def receive_value(self, round, from_general, value):
        """Receive value from another general"""
        # TODO: Store received values for consensus
        pass

    def decide_action(self, f):
        """Decide on action with up to f traitors"""
        # TODO: Implement Byzantine fault tolerant consensus
        pass
```

## Exercise 5: Implement Raft Leader Election

**Challenge**: Build the leader election portion of the Raft consensus algorithm.

```python
class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for = None
        self.state = 'follower'
        self.leader = None

    def election_timeout(self):
        """Called when election timeout expires"""
        # TODO: Start new election
        pass

    def request_vote(self, term, candidate_id, last_log_index, last_log_term):
        """Handle RequestVote RPC"""
        # TODO: Decide whether to grant vote
        pass

    def become_leader(self):
        """Transition to leader state"""
        # TODO: Send heartbeats to maintain leadership
        pass
```

## Exercise 6: Distributed Snapshot

**Challenge**: Implement the Chandy-Lamport algorithm for taking consistent global snapshots.

```python
class DistributedProcess:
    def __init__(self, process_id, channels):
        self.process_id = process_id
        self.channels = channels  # incoming and outgoing
        self.local_state = {}
        self.recording = False

    def initiate_snapshot(self):
        """Start global snapshot algorithm"""
        # TODO: Record local state and send markers
        pass

    def receive_marker(self, channel_id):
        """Handle marker message"""
        # TODO: Implement Chandy-Lamport algorithm
        pass

    def get_snapshot(self):
        """Return collected snapshot"""
        # TODO: Combine local state and channel states
        pass
```

## Exercise 7: Consensus with Failures

**Task**: Implement a consensus algorithm that handles node failures during the protocol.

```python
class FaultTolerantConsensus:
    def __init__(self, nodes, f):
        self.nodes = nodes
        self.f = f  # Maximum failures to tolerate

    def propose(self, value):
        """Propose a value for consensus"""
        # TODO: Handle up to f crash failures
        pass

    def handle_timeout(self, phase):
        """Handle timeout in any phase"""
        # TODO: Recover from partial failures
        pass
```

## Thought Experiments

### 1. The CAP Trade-off
You're designing a global social media "like" counter.
- If you choose consistency, what happens during network partitions?
- If you choose availability, how wrong can the count get?
- Design a solution that gives "good enough" consistency.

### 2. The Time Problem
Without synchronized clocks, how do you order these events?
- User A posts at "2:00 PM" in New York
- User B comments at "2:01 PM" in Tokyo
- User C likes the post at "2:00:30 PM" in London
Design a system that preserves causality without global time.

### 3. The Trust Boundary
In a blockchain with 1000 nodes:
- How many Byzantine nodes can it tolerate?
- What if nodes collude?
- How does the consensus mechanism change with different trust assumptions?

## Research Questions

1. **Why is consensus impossible with asynchronous communication and one failure?** (FLP impossibility)

2. **How do real systems circumvent the FLP impossibility result?**

3. **What's the relationship between consensus and atomic broadcast?**

4. **When is eventual consistency sufficient for consensus?**

## Practical Scenarios

### Scenario 1: Payment Processing
Design a consensus mechanism for a payment system where:
- Multiple banks must agree on transaction order
- Some banks may be temporarily offline
- No transaction can be lost or duplicated

### Scenario 2: Distributed Lock Service
Build a lock service that:
- Survives node failures
- Prevents split-brain scenarios
- Provides fair ordering

### Scenario 3: Configuration Management
Create a configuration system where:
- All nodes eventually see the same config
- Config changes are atomic
- Rollback is possible

## Key Concepts to Master

1. **Safety vs Liveness**
   - Safety: Nothing bad happens
   - Liveness: Something good eventually happens

2. **Failure Detectors**
   - Perfect vs Eventually perfect
   - Strong vs Weak completeness

3. **Consensus Numbers**
   - What primitives can implement consensus?
   - Why are some problems harder than others?

## Reflection

After completing these exercises:

1. Why is distributed consensus considered one of the hardest problems in computer science?

2. What are the fundamental trade-offs between different consensus algorithms?

3. How do you choose the right consensus mechanism for your system?

4. What role does time play in achieving consensus?

Remember: Truth in distributed systems is not absolute—it's what the majority agrees on. Design your truth mechanisms to match your actual needs, not theoretical perfection.
