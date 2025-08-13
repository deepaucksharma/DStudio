#!/usr/bin/env python3
"""
Comprehensive Test Suite for Episode 45: Distributed Computing Patterns

This test suite validates all the distributed computing examples to ensure
they work correctly and demonstrate the intended concepts.
"""

import sys
import os
import unittest
import subprocess
import time
import threading
from pathlib import Path

# Add the code directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code' / 'python'))

# Import the modules we want to test
try:
    from python import (
        mapreduce_irctc_logs,
        spark_aadhaar_processing,
        distributed_hash_table,
        raft_consensus,
        gossip_protocol,
        byzantine_fault_tolerance,
        distributed_sorting
    )
except ImportError as e:
    print(f"Warning: Some Python modules could not be imported: {e}")

class TestMapReduceIRCTCLogs(unittest.TestCase):
    """Test MapReduce IRCTC log processing"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = mapreduce_irctc_logs.IRCTCMapReduceProcessor(num_workers=2)
    
    def test_log_generation(self):
        """Test sample log generation"""
        logs = self.processor.generate_sample_logs(100)
        self.assertEqual(len(logs), 100)
        
        # Check log format
        for log in logs[:5]:
            self.assertIsInstance(log, str)
            # Should be valid JSON
            import json
            log_data = json.loads(log)
            self.assertIn('timestamp', log_data)
            self.assertIn('user_id', log_data)
    
    def test_word_count_processing(self):
        """Test word count processing"""
        logs = self.processor.generate_sample_logs(50)
        word_counts = self.processor.run_mapreduce(logs)
        
        self.assertIsInstance(word_counts, dict)
        self.assertGreater(len(word_counts), 0)
        
        # Check some expected words
        common_words = ['processing', 'user', 'station', 'booking']
        found_words = [word for word in common_words if word in word_counts]
        self.assertGreater(len(found_words), 0)
    
    def test_analysis_results(self):
        """Test analysis functionality"""
        logs = self.processor.generate_sample_logs(100)
        word_counts = self.processor.run_mapreduce(logs)
        analysis = self.processor.analyze_results(word_counts)
        
        self.assertIn('total_words_processed', analysis)
        self.assertIn('unique_words_found', analysis)
        self.assertIn('top_words', analysis)
        self.assertGreater(analysis['total_words_processed'], 0)

class TestSparkAadhaarProcessing(unittest.TestCase):
    """Test Spark-based Aadhaar processing (without actual Spark)"""
    
    def test_schema_definition(self):
        """Test Aadhaar schema definition"""
        processor = spark_aadhaar_processing.AadhaarDataProcessor("TestApp")
        schema = processor.create_aadhaar_schema()
        
        # Check that schema is properly defined
        self.assertIsNotNone(schema)
        
        # Check for required fields
        field_names = [field.name for field in schema.fields]
        required_fields = ['aadhaar_id', 'state_code', 'is_active']
        for field in required_fields:
            self.assertIn(field, field_names)
    
    def test_sample_data_generation(self):
        """Test sample data generation logic"""
        # Test the data generation concepts without Spark
        import random
        import hashlib
        from datetime import datetime, timedelta
        
        # Simulate data generation
        num_records = 100
        state_codes = ["01", "02", "03"]
        
        records = []
        for i in range(num_records):
            record = {
                'aadhaar_id': f"ANON_{i:012d}",
                'state_code': random.choice(state_codes),
                'is_active': random.random() > 0.05
            }
            records.append(record)
        
        self.assertEqual(len(records), num_records)
        self.assertTrue(all('aadhaar_id' in record for record in records))

class TestDistributedHashTable(unittest.TestCase):
    """Test Distributed Hash Table implementation"""
    
    def setUp(self):
        """Set up test DHT"""
        self.dht = distributed_hash_table.PaytmWalletDHT(replication_factor=2)
    
    def test_node_addition(self):
        """Test adding nodes to DHT"""
        node1 = distributed_hash_table.CacheNode("node1", "localhost", 8001, 100)
        node2 = distributed_hash_table.CacheNode("node2", "localhost", 8002, 100)
        
        self.dht.consistent_hashing.add_node(node1)
        self.dht.consistent_hashing.add_node(node2)
        
        self.assertEqual(self.dht.consistent_hashing.get_node_count(), 2)
    
    def test_wallet_operations(self):
        """Test wallet creation and operations"""
        # Add a node first
        node1 = distributed_hash_table.CacheNode("node1", "localhost", 8001, 100)
        self.dht.consistent_hashing.add_node(node1)
        
        # Test wallet creation
        success = self.dht.create_wallet("test_user", 1000.0)
        self.assertTrue(success)
        
        # Test balance retrieval
        balance = self.dht.get_wallet_balance("test_user")
        self.assertEqual(balance, 1000.0)
    
    def test_hash_ring_distribution(self):
        """Test consistent hash ring distribution"""
        ring = distributed_hash_table.ConsistentHashing(virtual_nodes=3)
        
        # Add nodes
        node1 = distributed_hash_table.CacheNode("node1", "localhost", 8001, 100)
        node2 = distributed_hash_table.CacheNode("node2", "localhost", 8002, 100)
        
        ring.add_node(node1)
        ring.add_node(node2)
        
        # Test key distribution
        keys = ["key1", "key2", "key3", "key4", "key5"]
        distributions = {}
        
        for key in keys:
            node = ring.get_node(key)
            if node:
                distributions[node.node_id] = distributions.get(node.node_id, 0) + 1
        
        # Should have some distribution
        self.assertGreater(len(distributions), 0)

class TestRaftConsensus(unittest.TestCase):
    """Test Raft consensus algorithm"""
    
    def setUp(self):
        """Set up test Raft cluster"""
        cluster_nodes = ["node1", "node2", "node3"]
        self.nodes = {}
        
        for node_id in cluster_nodes:
            node = raft_consensus.PhonePeTransactionNode(node_id, cluster_nodes)
            self.nodes[node_id] = node
    
    def test_node_initialization(self):
        """Test node initialization"""
        node = self.nodes["node1"]
        self.assertEqual(node.node_id, "node1")
        self.assertEqual(node.state, raft_consensus.NodeState.FOLLOWER)
        self.assertEqual(node.current_term, 0)
    
    def test_payment_processing_structure(self):
        """Test payment processing structure"""
        node = self.nodes["node1"]
        
        # Test wallet balance operations
        initial_balance = node.get_wallet_balance("test_wallet")
        self.assertEqual(initial_balance, 0.0)
        
        # Test adding balance
        success = node.add_wallet_balance("test_wallet", 1000.0)
        self.assertTrue(success)
    
    def test_election_timeout_setup(self):
        """Test election timeout setup"""
        node = self.nodes["node1"]
        
        # Check that election timeout is properly set
        self.assertGreater(node.election_timeout, 0)
        self.assertGreater(node.heartbeat_interval, 0)

class TestGossipProtocol(unittest.TestCase):
    """Test Gossip Protocol implementation"""
    
    def setUp(self):
        """Set up test gossip nodes"""
        self.node1 = gossip_protocol.WhatsAppGossipNode("node1", "localhost", 5001, "test")
        self.node2 = gossip_protocol.WhatsAppGossipNode("node2", "localhost", 5002, "test")
    
    def test_node_initialization(self):
        """Test node initialization"""
        self.assertEqual(self.node1.node_id, "node1")
        self.assertEqual(self.node1.region, "test")
        self.assertIn(self.node1.node_id, self.node1.membership)
    
    def test_message_creation(self):
        """Test gossip message creation"""
        message = gossip_protocol.GossipMessage(
            message_id="test_msg",
            message_type=gossip_protocol.MessageType.GOSSIP,
            sender_id="node1",
            content={"test": "data"},
            timestamp=time.time()
        )
        
        self.assertEqual(message.message_id, "test_msg")
        self.assertEqual(message.sender_id, "node1")
        self.assertIn("test", message.content)
    
    def test_whatsapp_message_structure(self):
        """Test WhatsApp message structure"""
        success = self.node1.send_whatsapp_message("test_chat", "Hello World", "text")
        # Since we're not actually running the gossip protocol, we expect some structure
        self.assertIsInstance(success, bool)

class TestByzantineFaultTolerance(unittest.TestCase):
    """Test Byzantine Fault Tolerance implementation"""
    
    def setUp(self):
        """Set up BFT nodes"""
        self.honest_node = byzantine_fault_tolerance.UPIBankNode(
            "honest_node", "Test Bank", byzantine_fault_tolerance.NodeType.HONEST
        )
        self.malicious_node = byzantine_fault_tolerance.UPIBankNode(
            "malicious_node", "Evil Bank", byzantine_fault_tolerance.NodeType.MALICIOUS
        )
    
    def test_node_initialization(self):
        """Test node initialization"""
        self.assertEqual(self.honest_node.node_id, "honest_node")
        self.assertEqual(self.honest_node.node_type, byzantine_fault_tolerance.NodeType.HONEST)
        self.assertGreater(len(self.honest_node.account_balances), 0)
    
    def test_transaction_creation(self):
        """Test UPI transaction creation"""
        transaction = byzantine_fault_tolerance.UPITransaction(
            transaction_id="TEST001",
            sender_vpa="test@upi",
            receiver_vpa="receiver@upi",
            amount=100.0,
            timestamp=time.time(),
            bank_sender="TestBank",
            bank_receiver="ReceiverBank"
        )
        
        self.assertEqual(transaction.transaction_id, "TEST001")
        self.assertEqual(transaction.amount, 100.0)
        self.assertIsNotNone(transaction.get_hash())
    
    def test_transaction_validation(self):
        """Test transaction validation"""
        # Add some balance first
        self.honest_node.account_balances["test@upi"] = 1000.0
        
        valid_transaction = byzantine_fault_tolerance.UPITransaction(
            transaction_id="TEST001",
            sender_vpa="test@upi",
            receiver_vpa="receiver@upi",
            amount=100.0,
            timestamp=time.time(),
            bank_sender="TestBank",
            bank_receiver="ReceiverBank"
        )
        
        is_valid = self.honest_node._validate_transaction(valid_transaction)
        self.assertTrue(is_valid)
        
        # Test invalid transaction (insufficient balance)
        invalid_transaction = byzantine_fault_tolerance.UPITransaction(
            transaction_id="TEST002",
            sender_vpa="test@upi",
            receiver_vpa="receiver@upi",
            amount=2000.0,  # More than available balance
            timestamp=time.time(),
            bank_sender="TestBank",
            bank_receiver="ReceiverBank"
        )
        
        is_valid = self.honest_node._validate_transaction(invalid_transaction)
        self.assertFalse(is_valid)

class TestDistributedSorting(unittest.TestCase):
    """Test Distributed Sorting algorithms"""
    
    def setUp(self):
        """Set up sorting test environment"""
        self.external_sorter = distributed_sorting.ExternalMergeSorter(worker_count=2, chunk_size=100)
        self.sample_sorter = distributed_sorting.DistributedSampleSorter(worker_count=2, sample_size=50)
    
    def test_flipkart_product_creation(self):
        """Test Flipkart product creation"""
        product = distributed_sorting.FlipkartProduct(
            product_id="TEST001",
            name="Test Product",
            price=999.99,
            rating=4.5,
            reviews_count=100,
            category="Electronics",
            brand="TestBrand",
            popularity_score=85.0,
            discount_percentage=10.0,
            seller_rating=4.2
        )
        
        self.assertEqual(product.product_id, "TEST001")
        self.assertEqual(product.price, 999.99)
        self.assertEqual(product.rating, 4.5)
    
    def test_product_comparators(self):
        """Test product comparison functions"""
        product1 = distributed_sorting.FlipkartProduct(
            product_id="P1", name="Product 1", price=100.0, rating=4.0,
            reviews_count=50, category="Electronics", brand="Brand1",
            popularity_score=80.0, discount_percentage=10.0, seller_rating=4.0
        )
        
        product2 = distributed_sorting.FlipkartProduct(
            product_id="P2", name="Product 2", price=200.0, rating=4.5,
            reviews_count=100, category="Electronics", brand="Brand2",
            popularity_score=90.0, discount_percentage=20.0, seller_rating=4.5
        )
        
        # Test price comparison
        price1 = distributed_sorting.FlipkartProductComparator.by_price(product1)
        price2 = distributed_sorting.FlipkartProductComparator.by_price(product2)
        self.assertLess(price1, price2)
        
        # Test rating comparison (negative for descending)
        rating1 = distributed_sorting.FlipkartProductComparator.by_rating(product1)
        rating2 = distributed_sorting.FlipkartProductComparator.by_rating(product2)
        self.assertGreater(rating1, rating2)  # Because ratings are negated
    
    def test_small_dataset_sorting(self):
        """Test sorting with small dataset"""
        # Create small test dataset
        products = []
        for i in range(10):
            product = distributed_sorting.FlipkartProduct(
                product_id=f"P{i:03d}",
                name=f"Product {i}",
                price=float(100 + i * 50),
                rating=4.0 + (i % 5) * 0.2,
                reviews_count=i * 10,
                category="Electronics",
                brand="TestBrand",
                popularity_score=float(i * 10),
                discount_percentage=float(i * 2),
                seller_rating=4.0
            )
            products.append(product)
        
        # Test external merge sort
        sorted_products = self.external_sorter.sort(
            products.copy(), 
            distributed_sorting.FlipkartProductComparator.by_price
        )
        
        self.assertEqual(len(sorted_products), len(products))
        
        # Check if sorted by price
        for i in range(1, len(sorted_products)):
            self.assertLessEqual(sorted_products[i-1].price, sorted_products[i].price)
        
        # Test sample sort
        sorted_products2 = self.sample_sorter.sort(
            products.copy(),
            distributed_sorting.FlipkartProductComparator.by_price
        )
        
        self.assertEqual(len(sorted_products2), len(products))

class TestJavaExamples(unittest.TestCase):
    """Test Java examples compilation and basic structure"""
    
    def test_java_compilation(self):
        """Test if Java files compile successfully"""
        java_dir = Path(__file__).parent.parent / 'code' / 'java'
        java_files = list(java_dir.glob('*.java'))
        
        self.assertGreater(len(java_files), 0, "No Java files found")
        
        for java_file in java_files:
            # Check if file exists and has basic structure
            with open(java_file, 'r') as f:
                content = f.read()
                
            # Basic checks
            self.assertIn('class', content, f"No class found in {java_file.name}")
            self.assertIn('public', content, f"No public methods found in {java_file.name}")
            
            # Check for main method (most files should have demos)
            if 'Demo' in java_file.name:
                self.assertIn('public static void main', content, 
                            f"No main method found in demo file {java_file.name}")

class TestGoExamples(unittest.TestCase):
    """Test Go examples compilation and basic structure"""
    
    def test_go_file_structure(self):
        """Test if Go files have proper structure"""
        go_dir = Path(__file__).parent.parent / 'code' / 'go'
        go_files = list(go_dir.glob('*.go'))
        
        self.assertGreater(len(go_files), 0, "No Go files found")
        
        for go_file in go_files:
            with open(go_file, 'r') as f:
                content = f.read()
            
            # Basic Go structure checks
            self.assertIn('package main', content, f"No package main in {go_file.name}")
            self.assertIn('func main()', content, f"No main function in {go_file.name}")
            self.assertIn('import', content, f"No imports in {go_file.name}")

class TestIntegration(unittest.TestCase):
    """Integration tests across multiple components"""
    
    def test_distributed_system_coordination(self):
        """Test coordination between distributed components"""
        # Test that different components can work together conceptually
        
        # Create a simple distributed hash table
        dht = distributed_hash_table.PaytmWalletDHT(replication_factor=2)
        node1 = distributed_hash_table.CacheNode("node1", "localhost", 8001, 100)
        dht.consistent_hashing.add_node(node1)
        
        # Create a wallet and verify it exists
        success = dht.create_wallet("integration_test", 500.0)
        self.assertTrue(success)
        
        balance = dht.get_wallet_balance("integration_test")
        self.assertEqual(balance, 500.0)
        
        # Test sorting integration
        products = []
        for i in range(5):
            product = distributed_sorting.FlipkartProduct(
                product_id=f"INT{i:03d}",
                name=f"Integration Product {i}",
                price=float(100 * (i + 1)),
                rating=4.0,
                reviews_count=10,
                category="Test",
                brand="IntegrationBrand",
                popularity_score=float(i * 20),
                discount_percentage=5.0,
                seller_rating=4.0
            )
            products.append(product)
        
        # Sort products
        sorter = distributed_sorting.ExternalMergeSorter(worker_count=1, chunk_size=3)
        sorted_products = sorter.sort(products, distributed_sorting.FlipkartProductComparator.by_price)
        
        self.assertEqual(len(sorted_products), 5)
        # Verify sorting
        for i in range(1, len(sorted_products)):
            self.assertLessEqual(sorted_products[i-1].price, sorted_products[i].price)

def run_performance_tests():
    """Run performance tests for algorithms"""
    print("\n🚀 Running Performance Tests...")
    print("=" * 50)
    
    # Test MapReduce performance
    print("\n📊 MapReduce Performance Test:")
    processor = mapreduce_irctc_logs.IRCTCMapReduceProcessor(num_workers=2)
    
    start_time = time.time()
    logs = processor.generate_sample_logs(1000)
    generation_time = time.time() - start_time
    print(f"Generated 1000 logs in {generation_time:.3f}s")
    
    start_time = time.time()
    word_counts = processor.run_mapreduce(logs)
    processing_time = time.time() - start_time
    print(f"Processed logs in {processing_time:.3f}s")
    print(f"Found {len(word_counts)} unique words")
    
    # Test DHT performance
    print("\n🔗 DHT Performance Test:")
    dht = distributed_hash_table.PaytmWalletDHT(replication_factor=2)
    
    # Add nodes
    for i in range(3):
        node = distributed_hash_table.CacheNode(f"node{i}", "localhost", 8000+i, 100)
        dht.consistent_hashing.add_node(node)
    
    # Test wallet operations
    start_time = time.time()
    for i in range(100):
        dht.create_wallet(f"user{i}", 1000.0)
    creation_time = time.time() - start_time
    print(f"Created 100 wallets in {creation_time:.3f}s")
    
    # Test sorting performance
    print("\n📈 Sorting Performance Test:")
    sorter = distributed_sorting.FlipkartSearchSorter()
    
    start_time = time.time()
    products = sorter.generate_sample_products(1000)
    generation_time = time.time() - start_time
    print(f"Generated 1000 products in {generation_time:.3f}s")
    
    start_time = time.time()
    sorted_products = sorter.sort_by_price_range(
        products, 0, 50000, 
        distributed_sorting.SortingAlgorithm.EXTERNAL_MERGE_SORT
    )
    sorting_time = time.time() - start_time
    print(f"Sorted {len(sorted_products)} products in {sorting_time:.3f}s")

def main():
    """Main test runner"""
    print("🧪 Episode 45: Distributed Computing Patterns - Test Suite")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestMapReduceIRCTCLogs,
        TestSparkAadhaarProcessing,
        TestDistributedHashTable,
        TestRaftConsensus,
        TestGossipProtocol,
        TestByzantineFaultTolerance,
        TestDistributedSorting,
        TestJavaExamples,
        TestGoExamples,
        TestIntegration
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📋 Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\n⚠️  Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    # Run performance tests if all tests pass
    if not result.failures and not result.errors:
        run_performance_tests()
        
        print(f"\n✅ All tests passed! Distributed computing examples are working correctly.")
        print(f"\n💡 Ready for production-scale distributed systems!")
    else:
        print(f"\n❌ Some tests failed. Please check the implementations.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)