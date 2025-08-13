"""
Causal Consistency Checker
Ensures causally related operations are seen in same order
Example: Social media comments, Email reply chains
"""

import time
import uuid
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

class OperationType(Enum):
    POST_CREATE = "POST_CREATE"
    COMMENT_ADD = "COMMENT_ADD"
    LIKE_ADD = "LIKE_ADD"
    SHARE = "SHARE"

@dataclass
class Operation:
    """
    Single operation in the system
    Facebook post/comment jaisa operation
    """
    op_id: str
    op_type: OperationType
    user_id: str
    target_id: str  # Post ID or Comment ID
    content: str
    timestamp: float
    depends_on: Set[str] = field(default_factory=set)  # Causal dependencies
    
@dataclass
class CausalHistory:
    """
    User ka causal history - kya dekha hai usne
    """
    user_id: str
    seen_operations: Set[str] = field(default_factory=set)
    operation_order: List[str] = field(default_factory=list)

class CausalConsistencyStore:
    """
    Causal consistency maintain karne wala store
    Facebook/Instagram jaisa social media backend
    """
    
    def __init__(self):
        self.operations: Dict[str, Operation] = {}
        self.user_histories: Dict[str, CausalHistory] = {}
        self.replica_stores: Dict[str, Dict[str, Operation]] = {}
        self.lock = threading.RLock()
        
        # Initialize replicas - Mumbai, Delhi, Bangalore servers
        self.replica_stores = {
            "mumbai": {},
            "delhi": {},
            "bangalore": {}
        }
        
    def create_post(self, user_id: str, content: str, replica: str = "mumbai") -> str:
        """
        Naya post banao - Instagram/Facebook jaisa
        """
        with self.lock:
            op_id = f"post_{str(uuid.uuid4())[:8]}"
            
            operation = Operation(
                op_id=op_id,
                op_type=OperationType.POST_CREATE,
                user_id=user_id,
                target_id=op_id,  # Post ka own ID
                content=content,
                timestamp=time.time()
            )
            
            # Store in specified replica
            self.operations[op_id] = operation
            self.replica_stores[replica][op_id] = operation
            
            # Update user's causal history
            self._update_user_history(user_id, op_id)
            
            logging.info(f"Post created: {op_id} by {user_id} in {replica}")
            return op_id
            
    def add_comment(self, user_id: str, post_id: str, content: str, 
                   replica: str = "mumbai") -> Optional[str]:
        """
        Comment add karo - post pe depend karta hai
        """
        with self.lock:
            # Check if user has seen the post (causal dependency)
            if not self._has_user_seen_operation(user_id, post_id):
                logging.warning(f"User {user_id} hasn't seen post {post_id} yet")
                return None
                
            op_id = f"comment_{str(uuid.uuid4())[:8]}"
            
            operation = Operation(
                op_id=op_id,
                op_type=OperationType.COMMENT_ADD,
                user_id=user_id,
                target_id=post_id,
                content=content,
                timestamp=time.time(),
                depends_on={post_id}  # Causal dependency on post
            )
            
            self.operations[op_id] = operation
            self.replica_stores[replica][op_id] = operation
            
            # Update user's causal history
            self._update_user_history(user_id, op_id)
            
            logging.info(f"Comment added: {op_id} by {user_id} on post {post_id}")
            return op_id
            
    def like_post(self, user_id: str, post_id: str, replica: str = "mumbai") -> Optional[str]:
        """
        Post ko like karo - post exist karna chahiye
        """
        with self.lock:
            if not self._has_user_seen_operation(user_id, post_id):
                logging.warning(f"User {user_id} hasn't seen post {post_id} yet")
                return None
                
            op_id = f"like_{str(uuid.uuid4())[:8]}"
            
            operation = Operation(
                op_id=op_id,
                op_type=OperationType.LIKE_ADD,
                user_id=user_id,
                target_id=post_id,
                content=f"liked",
                timestamp=time.time(),
                depends_on={post_id}
            )
            
            self.operations[op_id] = operation
            self.replica_stores[replica][op_id] = operation
            
            self._update_user_history(user_id, op_id)
            
            logging.info(f"Like added: {op_id} by {user_id} on post {post_id}")
            return op_id
            
    def share_post(self, user_id: str, post_id: str, replica: str = "mumbai") -> Optional[str]:
        """
        Post share karo - causally dependent on seeing the post
        """
        with self.lock:
            if not self._has_user_seen_operation(user_id, post_id):
                logging.warning(f"User {user_id} hasn't seen post {post_id} yet")
                return None
                
            op_id = f"share_{str(uuid.uuid4())[:8]}"
            
            operation = Operation(
                op_id=op_id,
                op_type=OperationType.SHARE,
                user_id=user_id,
                target_id=post_id,
                content=f"shared",
                timestamp=time.time(),
                depends_on={post_id}
            )
            
            self.operations[op_id] = operation
            self.replica_stores[replica][op_id] = operation
            
            self._update_user_history(user_id, op_id)
            
            logging.info(f"Post shared: {op_id} by {user_id}")
            return op_id
            
    def sync_to_replica(self, source_replica: str, target_replica: str, 
                       delay: float = 0.1) -> List[str]:
        """
        Replicas ke beech sync karo - network delay ke saath
        """
        time.sleep(delay)  # Network latency simulation
        
        source_ops = self.replica_stores[source_replica]
        target_ops = self.replica_stores[target_replica]
        
        synced_ops = []
        
        for op_id, operation in source_ops.items():
            if op_id not in target_ops:
                # Check causal dependencies before sync
                if self._can_apply_operation(operation, target_replica):
                    target_ops[op_id] = operation
                    synced_ops.append(op_id)
                    logging.info(f"Synced {op_id} from {source_replica} to {target_replica}")
                else:
                    logging.warning(f"Cannot sync {op_id} - missing dependencies")
                    
        return synced_ops
        
    def get_user_feed(self, user_id: str, replica: str = "mumbai") -> List[Operation]:
        """
        User ka feed generate karo - causal order mein
        """
        replica_ops = self.replica_stores[replica]
        user_history = self.user_histories.get(user_id, CausalHistory(user_id))
        
        # Get all operations user can see
        visible_ops = []
        for op_id in user_history.operation_order:
            if op_id in replica_ops:
                visible_ops.append(replica_ops[op_id])
                
        return visible_ops
        
    def _update_user_history(self, user_id: str, op_id: str):
        """
        User ka causal history update karo
        """
        if user_id not in self.user_histories:
            self.user_histories[user_id] = CausalHistory(user_id)
            
        history = self.user_histories[user_id]
        if op_id not in history.seen_operations:
            history.seen_operations.add(op_id)
            history.operation_order.append(op_id)
            
    def _has_user_seen_operation(self, user_id: str, op_id: str) -> bool:
        """
        Check karo ki user ne operation dekha hai ya nahi
        """
        history = self.user_histories.get(user_id)
        return history and op_id in history.seen_operations
        
    def _can_apply_operation(self, operation: Operation, replica: str) -> bool:
        """
        Check karo ki operation apply kar sakte hain ya nahi
        Causal dependencies satisfy honi chahiye
        """
        replica_ops = self.replica_stores[replica]
        
        for dep_id in operation.depends_on:
            if dep_id not in replica_ops:
                return False
                
        return True
        
    def check_causal_consistency(self, user_id: str) -> Dict:
        """
        User ke liye causal consistency check karo
        """
        history = self.user_histories.get(user_id)
        if not history:
            return {"consistent": True, "violations": []}
            
        violations = []
        
        # Check if all dependencies are satisfied
        for op_id in history.operation_order:
            operation = self.operations.get(op_id)
            if not operation:
                continue
                
            for dep_id in operation.depends_on:
                dep_index = -1
                op_index = history.operation_order.index(op_id)
                
                try:
                    dep_index = history.operation_order.index(dep_id)
                except ValueError:
                    violations.append({
                        "type": "missing_dependency",
                        "operation": op_id,
                        "missing_dependency": dep_id
                    })
                    continue
                    
                if dep_index > op_index:
                    violations.append({
                        "type": "causal_violation",
                        "operation": op_id,
                        "dependency": dep_id,
                        "issue": "dependency seen after operation"
                    })
                    
        return {
            "consistent": len(violations) == 0,
            "violations": violations
        }
        
    def simulate_user_activity(self, user_id: str, replica: str):
        """
        User activity simulate karo - realistic behavior
        """
        # User joins and sees existing content
        existing_posts = [op_id for op_id, op in self.replica_stores[replica].items() 
                         if op.op_type == OperationType.POST_CREATE]
        
        # Randomly see some existing posts
        posts_to_see = random.sample(existing_posts, min(3, len(existing_posts)))
        for post_id in posts_to_see:
            self._update_user_history(user_id, post_id)
            
        # Create a new post
        post_id = self.create_post(user_id, f"Hello from {user_id}!", replica)
        
        # Interact with seen posts
        for seen_post in posts_to_see:
            if random.random() < 0.7:  # 70% chance to like
                self.like_post(user_id, seen_post, replica)
                
            if random.random() < 0.3:  # 30% chance to comment
                self.add_comment(user_id, seen_post, f"Nice post!", replica)

def demonstrate_causal_consistency():
    """
    Real-world demo: Social media feed with causal consistency
    Instagram/Facebook jaisa behavior
    """
    print("=== Causal Consistency Demo: Social Media System ===")
    
    store = CausalConsistencyStore()
    
    # Create initial posts in Mumbai server
    print("\n=== Initial Posts Creation ===")
    rahul_post = store.create_post("rahul", "Mumbai mein baarish! 🌧️", "mumbai")
    priya_post = store.create_post("priya", "Coffee time ☕", "mumbai")
    vikram_post = store.create_post("vikram", "Working from home today", "mumbai")
    
    print(f"Created posts: {rahul_post}, {priya_post}, {vikram_post}")
    
    # Sync to other replicas
    print("\n=== Syncing to Other Cities ===")
    store.sync_to_replica("mumbai", "delhi", 0.05)
    store.sync_to_replica("mumbai", "bangalore", 0.08)
    
    # User interactions - causal dependencies
    print("\n=== User Interactions (Causal Dependencies) ===")
    
    # Anita sees Rahul's post and comments
    store._update_user_history("anita", rahul_post)  # Anita sees the post
    comment1 = store.add_comment("anita", rahul_post, "Stay safe in the rain!", "delhi")
    
    # Rohan sees both post and comment, then likes
    store._update_user_history("rohan", rahul_post)
    if comment1:
        store._update_user_history("rohan", comment1)
    like1 = store.like_post("rohan", rahul_post, "bangalore")
    
    # Sangeeta tries to comment without seeing the post (should fail)
    print("\n=== Causal Violation Test ===")
    result = store.add_comment("sangeeta", rahul_post, "Nice post!", "mumbai")
    print(f"Comment without seeing post: {'Failed' if result is None else 'Success'}")
    
    # Now Sangeeta sees the post and comments
    store._update_user_history("sangeeta", rahul_post)
    comment2 = store.add_comment("sangeeta", rahul_post, "Now I can comment!", "mumbai")
    
    # Chain of dependencies - Reply to comment
    if comment1:
        store._update_user_history("rahul", comment1)  # Rahul sees Anita's comment
        reply = store.add_comment("rahul", rahul_post, "@anita Thanks for caring!", "mumbai")
    
    # Simulate realistic user activity
    print("\n=== Simulating Realistic User Activity ===")
    users = ["amit", "deepika", "arjun", "kavya"]
    replicas = ["mumbai", "delhi", "bangalore"]
    
    for user in users:
        replica = random.choice(replicas)
        store.simulate_user_activity(user, replica)
        
    # Sync everything
    print("\n=== Final Sync Between All Replicas ===")
    for source in replicas:
        for target in replicas:
            if source != target:
                store.sync_to_replica(source, target, 0.02)
                
    # Check causal consistency for each user
    print("\n=== Causal Consistency Analysis ===")
    all_users = ["rahul", "priya", "vikram", "anita", "rohan", "sangeeta"] + users
    
    for user in all_users:
        consistency_check = store.check_causal_consistency(user)
        status = "✅ CONSISTENT" if consistency_check["consistent"] else "❌ VIOLATIONS"
        print(f"{user}: {status}")
        
        if not consistency_check["consistent"]:
            for violation in consistency_check["violations"]:
                print(f"  - {violation['type']}: {violation}")
                
    # Show feed for a specific user
    print("\n=== User Feed (Causal Order) ===")
    rahul_feed = store.get_user_feed("rahul", "mumbai")
    print(f"Rahul's feed ({len(rahul_feed)} items):")
    
    for operation in rahul_feed[-5:]:  # Show last 5 items
        op_type = operation.op_type.value
        content = operation.content[:30] + "..." if len(operation.content) > 30 else operation.content
        print(f"  {op_type}: {content} by {operation.user_id}")
        
    # Performance metrics
    print("\n=== System Metrics ===")
    total_ops = len(store.operations)
    
    for replica, ops in store.replica_stores.items():
        sync_percentage = (len(ops) / total_ops) * 100 if total_ops > 0 else 0
        print(f"{replica.capitalize()} replica: {len(ops)}/{total_ops} operations ({sync_percentage:.1f}% synced)")
        
    # Demonstrate causal ordering importance
    print("\n=== Why Causal Consistency Matters ===")
    print("Scenario: Comment reply chain")
    print("1. Rahul posts: 'Mumbai mein baarish!'")
    print("2. Anita comments: 'Stay safe!'") 
    print("3. Rahul replies: '@anita Thanks!'")
    print("\nWithout causal consistency:")
    print("- User might see reply before original comment")
    print("- Confusing conversation flow")
    print("\nWith causal consistency:")
    print("- Reply always appears after original comment")
    print("- Natural conversation flow maintained")

if __name__ == "__main__":
    demonstrate_causal_consistency()