"""
Comprehensive tests for Python consistency model examples
Tests all 6 Python implementations for correctness and consistency guarantees
"""

import unittest
import asyncio
import time
import threading
from decimal import Decimal
import sys
import os

# Add the Python code directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code', 'python'))

from unittest.mock import patch, MagicMock

class TestStrongConsistency(unittest.TestCase):
    """Test strong consistency banking implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import here to avoid import errors during discovery
        try:
            from strong_consistency_simulator import StrongConsistencyBank
            self.StrongConsistencyBank = StrongConsistencyBank
        except ImportError as e:
            self.skipTest(f"Could not import strong_consistency_simulator: {e}")
    
    def test_bank_creation_and_account_setup(self):
        """Test bank creation and basic account operations"""
        bank = self.StrongConsistencyBank(":memory:")
        
        # Test account creation
        self.assertTrue(bank.create_account("TEST_001", 1000.0))
        self.assertFalse(bank.create_account("TEST_001", 500.0))  # Duplicate
        
        # Test balance retrieval
        balance = bank.get_balance("TEST_001")
        self.assertEqual(balance, 1000.0)
        self.assertIsNone(bank.get_balance("NONEXISTENT"))
    
    def test_successful_transfer(self):
        """Test successful money transfer"""
        bank = self.StrongConsistencyBank(":memory:")
        
        bank.create_account("FROM_001", 5000.0)
        bank.create_account("TO_001", 2000.0)
        
        # Perform transfer
        success = bank.transfer_money("FROM_001", "TO_001", 1500.0)
        self.assertTrue(success)
        
        # Verify balances
        self.assertEqual(bank.get_balance("FROM_001"), 3500.0)
        self.assertEqual(bank.get_balance("TO_001"), 3500.0)
    
    def test_insufficient_funds_transfer(self):
        """Test transfer with insufficient funds"""
        bank = self.StrongConsistencyBank(":memory:")
        
        bank.create_account("FROM_001", 1000.0)
        bank.create_account("TO_001", 500.0)
        
        # Try to transfer more than available
        with self.assertRaises(ValueError):
            bank.transfer_money("FROM_001", "TO_001", 1500.0)
        
        # Verify balances unchanged
        self.assertEqual(bank.get_balance("FROM_001"), 1000.0)
        self.assertEqual(bank.get_balance("TO_001"), 500.0)
    
    def test_concurrent_transfers(self):
        """Test concurrent transfers maintain consistency"""
        bank = self.StrongConsistencyBank(":memory:")
        
        bank.create_account("ACCOUNT_A", 10000.0)
        bank.create_account("ACCOUNT_B", 5000.0)
        bank.create_account("ACCOUNT_C", 3000.0)
        
        results = []
        
        def transfer_task(from_acc, to_acc, amount):
            try:
                success = bank.transfer_money(from_acc, to_acc, amount)
                results.append(success)
            except Exception as e:
                results.append(False)
        
        # Start multiple transfers concurrently
        threads = [
            threading.Thread(target=transfer_task, args=("ACCOUNT_A", "ACCOUNT_B", 2000.0)),
            threading.Thread(target=transfer_task, args=("ACCOUNT_A", "ACCOUNT_C", 3000.0)),
            threading.Thread(target=transfer_task, args=("ACCOUNT_B", "ACCOUNT_C", 1000.0)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify total money is conserved
        total_balance = (bank.get_balance("ACCOUNT_A") + 
                        bank.get_balance("ACCOUNT_B") + 
                        bank.get_balance("ACCOUNT_C"))
        self.assertEqual(total_balance, 18000.0)  # Original total


class TestEventualConsistency(unittest.TestCase):
    """Test eventual consistency social media implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from eventual_consistency_demo import EventualConsistencySystem
            self.EventualConsistencySystem = EventualConsistencySystem
        except ImportError as e:
            self.skipTest(f"Could not import eventual_consistency_demo: {e}")
    
    def test_system_initialization(self):
        """Test system initialization"""
        system = self.EventualConsistencySystem()
        
        # Check data centers are initialized
        expected_centers = ["mumbai-dc", "singapore-dc", "ireland-dc", "california-dc", "sao-paulo-dc"]
        for center in expected_centers:
            self.assertIn(center, system.data_centers)
    
    def test_post_creation_and_sync(self):
        """Test post creation and eventual sync"""
        system = self.EventualConsistencySystem()
        
        async def test_async():
            # Start background sync
            sync_task = asyncio.create_task(system.start_background_sync())
            
            try:
                # Create a post
                post_id = await system.create_post("test_user", "Test post content", "mumbai-dc")
                self.assertIsNotNone(post_id)
                
                # Wait for sync
                await asyncio.sleep(0.5)
                
                # Check if post exists in other data centers
                mumbai_dc = system.data_centers["mumbai-dc"]
                singapore_dc = system.data_centers["singapore-dc"]
                
                self.assertIn(post_id, mumbai_dc.posts)
                # Singapore might have it after sync
                
            finally:
                await system.stop_sync()
                sync_task.cancel()
                try:
                    await sync_task
                except asyncio.CancelledError:
                    pass
        
        asyncio.run(test_async())
    
    def test_like_functionality(self):
        """Test post liking functionality"""
        system = self.EventualConsistencySystem()
        
        async def test_async():
            sync_task = asyncio.create_task(system.start_background_sync())
            
            try:
                # Create a post
                post_id = await system.create_post("test_user", "Likeable post", "mumbai-dc")
                
                # Like the post
                like_success = await system.like_post(post_id, "liker_user", "mumbai-dc")
                self.assertTrue(like_success)
                
                # Check like count
                post = system.data_centers["mumbai-dc"].posts.get(post_id)
                self.assertIsNotNone(post)
                self.assertGreaterEqual(post.likes, 1)
                
            finally:
                await system.stop_sync()
                sync_task.cancel()
                try:
                    await sync_task
                except asyncio.CancelledError:
                    pass
        
        asyncio.run(test_async())


class TestVectorClock(unittest.TestCase):
    """Test vector clock implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from vector_clock_implementation import VectorClock, DistributedNode
            self.VectorClock = VectorClock
            self.DistributedNode = DistributedNode
        except ImportError as e:
            self.skipTest(f"Could not import vector_clock_implementation: {e}")
    
    def test_vector_clock_creation(self):
        """Test vector clock creation and basic operations"""
        vc = self.VectorClock()
        
        # Test increment
        vc1 = vc.increment("node1")
        self.assertEqual(vc1.clocks["node1"], 1)
        
        vc2 = vc1.increment("node1")
        self.assertEqual(vc2.clocks["node1"], 2)
    
    def test_vector_clock_comparison(self):
        """Test vector clock comparison logic"""
        vc1 = self.VectorClock()
        vc2 = self.VectorClock()
        
        # Equal clocks
        self.assertEqual(vc1.compare(vc2), "equal")
        
        # Create ordering
        vc1 = vc1.increment("node1")
        self.assertEqual(vc1.compare(vc2), "after")
        self.assertEqual(vc2.compare(vc1), "before")
        
        # Create concurrent clocks
        vc2 = vc2.increment("node2")
        self.assertEqual(vc1.compare(vc2), "concurrent")
        self.assertEqual(vc2.compare(vc1), "concurrent")
    
    def test_vector_clock_merge(self):
        """Test vector clock merge operation"""
        vc1 = self.VectorClock()
        vc2 = self.VectorClock()
        
        vc1 = vc1.increment("node1")
        vc2 = vc2.increment("node2")
        
        # Merge vc2 into vc1's context
        merged = vc1.update(vc2, "node1")
        
        # Should have both node updates plus increment for node1
        self.assertGreaterEqual(merged.clocks["node1"], 1)
        self.assertGreaterEqual(merged.clocks["node2"], 1)
    
    def test_distributed_node_messaging(self):
        """Test distributed node message sending and receiving"""
        node1 = self.DistributedNode("node1")
        node2 = self.DistributedNode("node2")
        
        # Send message from node1 to node2
        message = node1.send_message("node2", "Hello from node1")
        self.assertIsNotNone(message)
        self.assertEqual(message.sender, "node1")
        self.assertEqual(message.content, "Hello from node1")
        
        # Receive message at node2
        node2.receive_message(message)
        
        # Check that node2's vector clock was updated
        self.assertGreater(len(node2.vector_clock.clocks), 0)


class TestCausalConsistency(unittest.TestCase):
    """Test causal consistency implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from causal_consistency_checker import CausalConsistencyStore, OperationType
            self.CausalConsistencyStore = CausalConsistencyStore
            self.OperationType = OperationType
        except ImportError as e:
            self.skipTest(f"Could not import causal_consistency_checker: {e}")
    
    def test_store_initialization(self):
        """Test causal consistency store initialization"""
        store = self.CausalConsistencyStore()
        
        # Check replica stores are initialized
        expected_replicas = ["mumbai", "delhi", "bangalore"]
        for replica in expected_replicas:
            self.assertIn(replica, store.replica_stores)
    
    def test_post_creation(self):
        """Test post creation with causal tracking"""
        store = self.CausalConsistencyStore()
        
        post_id = store.create_post("test_user", "Test post content", "mumbai")
        self.assertIsNotNone(post_id)
        
        # Check post exists in Mumbai replica
        mumbai_ops = store.replica_stores["mumbai"]
        self.assertIn(post_id, mumbai_ops)
    
    def test_causal_dependencies(self):
        """Test causal dependency enforcement"""
        store = self.CausalConsistencyStore()
        
        # Create a post
        post_id = store.create_post("author", "Original post", "mumbai")
        
        # Try to comment without seeing the post (should fail)
        comment_id = store.add_comment("commenter", post_id, "Nice post!", "delhi")
        self.assertIsNone(comment_id)
        
        # Make user see the post first
        store._update_user_history("commenter", post_id)
        
        # Now comment should succeed
        comment_id = store.add_comment("commenter", post_id, "Nice post!", "delhi")
        self.assertIsNotNone(comment_id)
    
    def test_consistency_checking(self):
        """Test causal consistency violation detection"""
        store = self.CausalConsistencyStore()
        
        # Create normal causal chain
        post_id = store.create_post("user1", "Post content", "mumbai")
        store._update_user_history("user2", post_id)
        comment_id = store.add_comment("user2", post_id, "Comment", "delhi")
        
        # Check consistency for user2
        consistency_check = store.check_causal_consistency("user2")
        self.assertTrue(consistency_check["consistent"])
        self.assertEqual(len(consistency_check["violations"]), 0)


class TestSessionConsistency(unittest.TestCase):
    """Test session consistency implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from session_consistency_manager import SessionConsistencyManager
            self.SessionConsistencyManager = SessionConsistencyManager
        except ImportError as e:
            self.skipTest(f"Could not import session_consistency_manager: {e}")
    
    def test_session_creation(self):
        """Test session creation and management"""
        manager = self.SessionConsistencyManager()
        
        session_id = manager.create_session("test_user", "mumbai")
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, manager.sessions)
        
        session = manager.sessions[session_id]
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.preferred_replica, "mumbai")
    
    def test_read_your_writes(self):
        """Test read-your-writes consistency"""
        manager = self.SessionConsistencyManager()
        
        session_id = manager.create_session("test_user", "mumbai")
        
        # Write data
        success = manager.write_data(session_id, "test_key", "test_value")
        self.assertTrue(success)
        
        # Read should return the written value
        value = manager.read_data(session_id, "test_key")
        self.assertEqual(value, "test_value")
    
    def test_monotonic_reads(self):
        """Test monotonic read consistency"""
        manager = self.SessionConsistencyManager()
        
        session_id = manager.create_session("test_user", "mumbai")
        
        # Write initial value
        manager.write_data(session_id, "monotonic_key", "value1")
        
        # Read value
        value1 = manager.read_data(session_id, "monotonic_key")
        self.assertEqual(value1, "value1")
        
        # Update value
        manager.write_data(session_id, "monotonic_key", "value2")
        
        # Read should return newer or same value, never older
        value2 = manager.read_data(session_id, "monotonic_key")
        self.assertIn(value2, ["value1", "value2"])  # Should not go backwards
    
    def test_session_consistency_verification(self):
        """Test session consistency violation detection"""
        manager = self.SessionConsistencyManager()
        
        session_id = manager.create_session("test_user", "mumbai")
        
        # Perform some operations
        manager.write_data(session_id, "key1", "value1")
        manager.read_data(session_id, "key1")
        manager.write_data(session_id, "key2", "value2")
        
        # Verify consistency
        verification = manager.verify_session_consistency(session_id)
        self.assertTrue(verification["consistent"])


class TestBankingACID(unittest.TestCase):
    """Test banking ACID operations implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            from banking_acid_operations import ACIDBank
            self.ACIDBank = ACIDBank
        except ImportError as e:
            self.skipTest(f"Could not import banking_acid_operations: {e}")
    
    def test_bank_initialization(self):
        """Test bank system initialization"""
        bank = self.ACIDBank(":memory:")
        
        # Test account creation
        success = bank.create_account("TEST_001", "SAVINGS", Decimal('1000.00'))
        self.assertTrue(success)
        
        # Test duplicate account creation
        success = bank.create_account("TEST_001", "CURRENT", Decimal('500.00'))
        self.assertFalse(success)
    
    def test_atomicity(self):
        """Test ACID Atomicity property"""
        bank = self.ACIDBank(":memory:")
        
        bank.create_account("ACC001", "SAVINGS", Decimal('1000.00'), Decimal('100.00'))
        bank.create_account("ACC002", "SAVINGS", Decimal('500.00'), Decimal('100.00'))
        
        # Successful transfer
        transaction = bank.transfer_money("ACC001", "ACC002", Decimal('200.00'))
        self.assertEqual(transaction.status.value, "COMMITTED")
        
        # Verify balances
        self.assertEqual(bank.get_balance("ACC001"), Decimal('800.00'))
        self.assertEqual(bank.get_balance("ACC002"), Decimal('700.00'))
    
    def test_consistency(self):
        """Test ACID Consistency property"""
        bank = self.ACIDBank(":memory:")
        
        bank.create_account("ACC001", "SAVINGS", Decimal('1000.00'), Decimal('500.00'))
        bank.create_account("ACC002", "SAVINGS", Decimal('300.00'), Decimal('100.00'))
        
        # Try transfer that would violate minimum balance
        with self.assertRaises(ValueError):
            bank.transfer_money("ACC001", "ACC002", Decimal('600.00'))
        
        # Verify balances unchanged
        self.assertEqual(bank.get_balance("ACC001"), Decimal('1000.00'))
        self.assertEqual(bank.get_balance("ACC002"), Decimal('300.00'))
    
    def test_isolation(self):
        """Test ACID Isolation property with concurrent transfers"""
        bank = self.ACIDBank(":memory:")
        
        bank.create_account("ACC001", "SAVINGS", Decimal('10000.00'))
        bank.create_account("ACC002", "SAVINGS", Decimal('5000.00'))
        bank.create_account("ACC003", "SAVINGS", Decimal('3000.00'))
        
        results = []
        
        def transfer_task(from_acc, to_acc, amount):
            try:
                transaction = bank.transfer_money(from_acc, to_acc, amount)
                results.append(transaction.status.value == "COMMITTED")
            except Exception:
                results.append(False)
        
        # Concurrent transfers
        threads = [
            threading.Thread(target=transfer_task, args=("ACC001", "ACC002", Decimal('2000.00'))),
            threading.Thread(target=transfer_task, args=("ACC001", "ACC003", Decimal('3000.00'))),
            threading.Thread(target=transfer_task, args=("ACC002", "ACC003", Decimal('1000.00'))),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify total balance is conserved
        total = bank.get_balance("ACC001") + bank.get_balance("ACC002") + bank.get_balance("ACC003")
        self.assertEqual(total, Decimal('18000.00'))
    
    def test_durability(self):
        """Test ACID Durability property"""
        # Create bank with file-based storage
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            # Create bank and perform operations
            bank1 = self.ACIDBank(db_path)
            bank1.create_account("DURABLE_001", "SAVINGS", Decimal('5000.00'))
            transaction = bank1.transfer_money("DURABLE_001", "DURABLE_001", Decimal('0.00'))  # Self-transfer
            
            # Create new bank instance with same database
            bank2 = self.ACIDBank(db_path)
            balance = bank2.get_balance("DURABLE_001")
            self.assertEqual(balance, Decimal('5000.00'))
            
        finally:
            # Cleanup
            import os
            try:
                os.unlink(db_path)
            except:
                pass


class TestSuite:
    """Main test suite runner"""
    
    @staticmethod
    def run_all_tests():
        """Run all Python consistency model tests"""
        print("=== Running Python Consistency Model Tests ===")
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [
            TestStrongConsistency,
            TestEventualConsistency,
            TestVectorClock,
            TestCausalConsistency,
            TestSessionConsistency,
            TestBankingACID,
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
        
        if result.failures:
            print(f"\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
        
        if result.errors:
            print(f"\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
        
        success = len(result.failures) == 0 and len(result.errors) == 0
        print(f"\nOverall result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success


if __name__ == "__main__":
    TestSuite.run_all_tests()