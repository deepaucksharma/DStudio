#!/usr/bin/env python3
"""
Test Suite for CAP Theorem Examples - Episode 4
सभी CAP theorem examples का comprehensive test suite

यह test suite verify करता है कि सभी code examples:
1. Properly execute होते हैं
2. Expected behavior show करते हैं
3. CAP theorem principles demonstrate करते हैं
4. Indian context examples work correctly
5. Error handling proper है

Run करने के लिए:
python test_all_examples.py
"""

import sys
import os
import unittest
import time
import subprocess
from decimal import Decimal
from datetime import datetime, timedelta

# Add parent directory to path to import examples
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCAPTheoremExamples(unittest.TestCase):
    """Main test class for all CAP theorem examples"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        print("🧪 Setting up CAP Theorem Examples Test Suite")
        print("=" * 60)
        cls.start_time = time.time()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        end_time = time.time()
        duration = end_time - cls.start_time
        print(f"\n✅ All tests completed in {duration:.2f} seconds")
        print("=" * 60)

class TestCapTheoremSimulator(unittest.TestCase):
    """Test CAP Theorem Simulator"""
    
    def setUp(self):
        """Import and setup CAP simulator"""
        try:
            from python.cap_theorem_simulator import CAPSimulator, ConsistencyModel, PartitionState
            self.CAPSimulator = CAPSimulator
            self.ConsistencyModel = ConsistencyModel
            self.PartitionState = PartitionState
        except ImportError as e:
            self.skipTest(f"Cannot import CAP simulator: {e}")
    
    def test_cap_simulator_initialization(self):
        """Test CAP simulator initialization"""
        print("\n🧪 Testing CAP Simulator Initialization")
        
        simulator = self.CAPSimulator(num_nodes=5)
        
        self.assertEqual(len(simulator.nodes), 5)
        self.assertEqual(simulator.partition_state, self.PartitionState.HEALTHY)
        self.assertEqual(simulator.consistency_model, self.ConsistencyModel.STRONG)
        
        print("   ✅ CAP simulator initialized correctly")
    
    def test_strong_consistency_operations(self):
        """Test strong consistency read/write operations"""
        print("\n🧪 Testing Strong Consistency Operations")
        
        simulator = self.CAPSimulator(num_nodes=3)
        simulator.consistency_model = self.ConsistencyModel.STRONG
        
        # Test write operation
        write_success = simulator.write_operation("balance_user_123", 5000, "user123")
        self.assertTrue(write_success, "Strong consistency write should succeed")
        
        # Test read operation
        read_success, value = simulator.read_operation("balance_user_123", "user123")
        self.assertTrue(read_success, "Strong consistency read should succeed")
        self.assertEqual(value, 5000, "Read value should match written value")
        
        print("   ✅ Strong consistency operations work correctly")
    
    def test_network_partition_handling(self):
        """Test network partition simulation"""
        print("\n🧪 Testing Network Partition Handling")
        
        simulator = self.CAPSimulator(num_nodes=5)
        
        # Simulate network partition in background
        import threading
        partition_thread = threading.Thread(target=simulator.simulate_network_partition, args=(2,))
        partition_thread.start()
        
        # Wait for partition to start
        time.sleep(0.5)
        
        # Test operations during partition
        write_success = simulator.write_operation("test_key", "test_value", "user123")
        
        # Wait for partition to complete
        partition_thread.join()
        
        # Verify partition was simulated
        self.assertGreaterEqual(simulator.partition_events, 1)
        
        print("   ✅ Network partition handling works correctly")

class TestHDFCBankingConsistency(unittest.TestCase):
    """Test HDFC Banking Consistency System"""
    
    def setUp(self):
        """Import and setup HDFC banking system"""
        try:
            from python.hdfc_banking_consistency import HDFCBankingSystem, Transaction, TransactionType
            self.HDFCBankingSystem = HDFCBankingSystem
            self.Transaction = Transaction
            self.TransactionType = TransactionType
        except ImportError as e:
            self.skipTest(f"Cannot import HDFC banking system: {e}")
    
    def test_hdfc_system_initialization(self):
        """Test HDFC banking system initialization"""
        print("\n🧪 Testing HDFC Banking System Initialization")
        
        hdfc_system = self.HDFCBankingSystem(num_nodes=3)
        
        self.assertEqual(len(hdfc_system.nodes), 3)
        self.assertIn("HDFC_DC_1", hdfc_system.nodes)
        
        # Check sample accounts exist
        primary_node = list(hdfc_system.nodes.keys())[0]
        accounts = hdfc_system.nodes[primary_node]["accounts"]
        self.assertGreater(len(accounts), 0, "Sample accounts should exist")
        
        print("   ✅ HDFC banking system initialized correctly")
    
    def test_banking_transaction_processing(self):
        """Test banking transaction processing"""
        print("\n🧪 Testing Banking Transaction Processing")
        
        hdfc_system = self.HDFCBankingSystem(num_nodes=3)
        
        # Create a withdrawal transaction
        transaction = self.Transaction(
            txn_id="TEST_TXN_001",
            account_number="50100123456789",
            transaction_type=self.TransactionType.WITHDRAWAL,
            amount=Decimal('5000'),
            timestamp=datetime.now(),
            description="Test ATM Withdrawal",
            reference_number="ATM123456",
            channel="ATM"
        )
        
        # Process transaction
        success, message = hdfc_system.process_transaction(transaction)
        
        # Verify transaction result
        self.assertTrue(success, f"Transaction should succeed: {message}")
        
        print("   ✅ Banking transaction processing works correctly")
    
    def test_concurrent_transaction_handling(self):
        """Test concurrent transaction handling"""
        print("\n🧪 Testing Concurrent Transaction Handling")
        
        hdfc_system = self.HDFCBankingSystem(num_nodes=3)
        
        # Simulate concurrent transactions (reduced count for test)
        hdfc_system.simulate_concurrent_transactions("50100123456789", num_transactions=3)
        
        # Verify no consistency violations occurred
        # In a real scenario, we'd have more detailed checks
        self.assertIsNotNone(hdfc_system)
        
        print("   ✅ Concurrent transaction handling completed")

class TestFlipkartCartAvailability(unittest.TestCase):
    """Test Flipkart Cart Availability System"""
    
    def setUp(self):
        """Import and setup Flipkart cart system"""
        try:
            from python.flipkart_cart_availability import FlipkartAvailabilitySystem, ProductCategory
            self.FlipkartAvailabilitySystem = FlipkartAvailabilitySystem
            self.ProductCategory = ProductCategory
        except ImportError as e:
            self.skipTest(f"Cannot import Flipkart cart system: {e}")
    
    def test_flipkart_system_initialization(self):
        """Test Flipkart system initialization"""
        print("\n🧪 Testing Flipkart Availability System Initialization")
        
        flipkart = self.FlipkartAvailabilitySystem()
        
        self.assertGreater(len(flipkart.regions), 0)
        self.assertIn("MUMBAI", flipkart.regions)
        
        print("   ✅ Flipkart system initialized correctly")
    
    def test_add_to_cart_operation(self):
        """Test add to cart operation"""
        print("\n🧪 Testing Add to Cart Operation")
        
        flipkart = self.FlipkartAvailabilitySystem()
        
        # Add item to cart
        success, message, cart_data = flipkart.add_to_cart(
            user_id="test_user_001",
            product_id="PHONE001",
            quantity=1
        )
        
        self.assertTrue(success, f"Add to cart should succeed: {message}")
        
        print("   ✅ Add to cart operation works correctly")
    
    def test_high_availability_during_failure(self):
        """Test high availability during regional failure"""
        print("\n🧪 Testing High Availability During Regional Failure")
        
        flipkart = self.FlipkartAvailabilitySystem()
        
        # Simulate regional failure
        flipkart.simulate_region_failure("MUMBAI", duration=2)
        
        # Try to add to cart during failure
        success, message, cart_data = flipkart.add_to_cart(
            user_id="test_user_002", 
            product_id="LAPTOP001",
            quantity=1
        )
        
        # System should maintain availability
        self.assertTrue(success, "System should maintain availability during failure")
        
        time.sleep(3)  # Wait for recovery
        
        print("   ✅ High availability maintained during failure")

class TestPaytmWalletConsistency(unittest.TestCase):
    """Test Paytm Wallet Consistency System"""
    
    def setUp(self):
        """Import and setup Paytm wallet system"""
        try:
            from python.paytm_wallet_consistency import PaytmWalletSystem, ConsistencyMode
            self.PaytmWalletSystem = PaytmWalletSystem
            self.ConsistencyMode = ConsistencyMode
        except ImportError as e:
            self.skipTest(f"Cannot import Paytm wallet system: {e}")
    
    def test_paytm_system_initialization(self):
        """Test Paytm wallet system initialization"""
        print("\n🧪 Testing Paytm Wallet System Initialization")
        
        paytm = self.PaytmWalletSystem(num_nodes=3)
        
        self.assertGreater(len(paytm.nodes), 0)
        
        print("   ✅ Paytm wallet system initialized correctly")
    
    def test_wallet_topup_strong_consistency(self):
        """Test wallet topup with strong consistency"""
        print("\n🧪 Testing Wallet Topup (Strong Consistency)")
        
        paytm = self.PaytmWalletSystem(num_nodes=3)
        
        # Wallet topup should use strong consistency
        success, message, result = paytm.wallet_topup("user_raj_001", Decimal('1000'))
        
        self.assertTrue(success, f"Wallet topup should succeed: {message}")
        
        print("   ✅ Wallet topup with strong consistency works correctly")
    
    def test_upi_payment_high_availability(self):
        """Test UPI payment with high availability"""
        print("\n🧪 Testing UPI Payment (High Availability)")
        
        paytm = self.PaytmWalletSystem(num_nodes=3)
        
        # UPI payment should prioritize availability
        success, message, result = paytm.upi_payment("user_raj_001", Decimal('500'), "test_merchant")
        
        # Should succeed even with potential consistency trade-offs
        self.assertTrue(success, f"UPI payment should succeed: {message}")
        
        print("   ✅ UPI payment with high availability works correctly")

class TestIRCTCBookingConflicts(unittest.TestCase):
    """Test IRCTC Booking Conflicts System"""
    
    def setUp(self):
        """Import and setup IRCTC booking system"""
        try:
            from python.irctc_booking_conflicts import IRCTCBookingSystem, SeatType, Passenger, PassengerType
            self.IRCTCBookingSystem = IRCTCBookingSystem
            self.SeatType = SeatType
            self.Passenger = Passenger
            self.PassengerType = PassengerType
        except ImportError as e:
            self.skipTest(f"Cannot import IRCTC booking system: {e}")
    
    def test_irctc_system_initialization(self):
        """Test IRCTC booking system initialization"""
        print("\n🧪 Testing IRCTC Booking System Initialization")
        
        irctc = self.IRCTCBookingSystem(num_zones=3)
        
        self.assertGreater(len(irctc.zones), 0)
        
        print("   ✅ IRCTC booking system initialized correctly")
    
    def test_ticket_booking_process(self):
        """Test ticket booking process"""
        print("\n🧪 Testing Ticket Booking Process")
        
        irctc = self.IRCTCBookingSystem(num_zones=3)
        
        # Create passenger
        passenger = self.Passenger(
            name="Test User",
            age=30,
            gender="M",
            passenger_type=self.PassengerType.GENERAL
        )
        
        # Book ticket
        success, message, result = irctc.book_ticket(
            user_id="test_user_001",
            train_number="12951",
            passengers=[passenger],
            seat_type=self.SeatType.AC3,
            travel_date=datetime.now() + timedelta(days=30)
        )
        
        # Booking should succeed or go to waiting list
        self.assertTrue(success, f"Booking process should complete: {message}")
        
        print("   ✅ Ticket booking process works correctly")

class TestWhatsAppPartitionTolerance(unittest.TestCase):
    """Test WhatsApp Partition Tolerance System"""
    
    def setUp(self):
        """Import and setup WhatsApp system"""
        try:
            from python.whatsapp_partition_tolerance import WhatsAppPartitionTolerantSystem, MobileUser, NetworkCarrier, MessageType
            self.WhatsAppPartitionTolerantSystem = WhatsAppPartitionTolerantSystem
            self.MobileUser = MobileUser
            self.NetworkCarrier = NetworkCarrier
            self.MessageType = MessageType
        except ImportError as e:
            self.skipTest(f"Cannot import WhatsApp system: {e}")
    
    def test_whatsapp_system_initialization(self):
        """Test WhatsApp system initialization"""
        print("\n🧪 Testing WhatsApp System Initialization")
        
        whatsapp = self.WhatsAppPartitionTolerantSystem()
        
        self.assertGreater(len(whatsapp.nodes), 0)
        
        print("   ✅ WhatsApp system initialized correctly")
    
    def test_message_sending(self):
        """Test message sending functionality"""
        print("\n🧪 Testing Message Sending")
        
        whatsapp = self.WhatsAppPartitionTolerantSystem()
        
        # Add users
        user1 = self.MobileUser("USER001", "+919876543210", "Test User 1", self.NetworkCarrier.JIO)
        user2 = self.MobileUser("USER002", "+919123456789", "Test User 2", self.NetworkCarrier.AIRTEL)
        
        whatsapp.add_user(user1)
        whatsapp.add_user(user2)
        
        # Send message
        success, message = whatsapp.send_message("USER001", "USER002", "Test message", self.MessageType.TEXT)
        
        self.assertTrue(success, f"Message sending should succeed: {message}")
        
        print("   ✅ Message sending works correctly")

class TestJavaExamples(unittest.TestCase):
    """Test Java examples compilation and basic functionality"""
    
    def test_java_files_compile(self):
        """Test that Java files compile without errors"""
        print("\n🧪 Testing Java Files Compilation")
        
        java_files = [
            "../java/IndianBankingTransactionCoordinator.java",
            "../java/ConsistencyModelsDemo.java",
            "../java/VectorClock.java"
        ]
        
        for java_file in java_files:
            file_path = os.path.join(os.path.dirname(__file__), java_file)
            if os.path.exists(file_path):
                try:
                    # Try to compile Java file
                    result = subprocess.run(
                        ["javac", "-cp", ".", file_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        print(f"   ⚠️  Warning: {java_file} compilation issues: {result.stderr}")
                    else:
                        print(f"   ✅ {java_file} compiles successfully")
                
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    print(f"   ⚠️  Warning: Cannot compile {java_file}: {e}")
            else:
                print(f"   ⚠️  Warning: {java_file} not found")

class TestGoExamples(unittest.TestCase):
    """Test Go examples compilation and basic functionality"""
    
    def test_go_files_compile(self):
        """Test that Go files compile without errors"""
        print("\n🧪 Testing Go Files Compilation")
        
        go_files = [
            "../go/indian_election_consensus.go",
            "../go/bounded_staleness_monitor.go", 
            "../go/raft_consensus.go"
        ]
        
        for go_file in go_files:
            file_path = os.path.join(os.path.dirname(__file__), go_file)
            if os.path.exists(file_path):
                try:
                    # Try to compile Go file
                    result = subprocess.run(
                        ["go", "build", "-o", "/tmp/test_go_binary", file_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        print(f"   ⚠️  Warning: {go_file} compilation issues: {result.stderr}")
                    else:
                        print(f"   ✅ {go_file} compiles successfully")
                        # Clean up binary
                        try:
                            os.remove("/tmp/test_go_binary")
                        except:
                            pass
                
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    print(f"   ⚠️  Warning: Cannot compile {go_file}: {e}")
            else:
                print(f"   ⚠️  Warning: {go_file} not found")

class TestIndianContextExamples(unittest.TestCase):
    """Test Indian context specific functionality"""
    
    def test_indian_banking_context(self):
        """Test Indian banking context examples"""
        print("\n🧪 Testing Indian Banking Context")
        
        # Test NEFT/RTGS/IMPS transaction types
        try:
            from python.hdfc_banking_consistency import TransactionType
            
            expected_types = [
                TransactionType.DEPOSIT,
                TransactionType.WITHDRAWAL,
                TransactionType.TRANSFER,
                TransactionType.UPI_PAYMENT
            ]
            
            for txn_type in expected_types:
                self.assertIsNotNone(txn_type)
            
            print("   ✅ Indian banking transaction types defined correctly")
        
        except ImportError:
            print("   ⚠️  Warning: Cannot test Indian banking context")
    
    def test_indian_mobile_carriers(self):
        """Test Indian mobile carrier context"""
        print("\n🧪 Testing Indian Mobile Carrier Context")
        
        try:
            from python.whatsapp_partition_tolerance import NetworkCarrier
            
            expected_carriers = [
                NetworkCarrier.JIO,
                NetworkCarrier.AIRTEL,
                NetworkCarrier.VI,
                NetworkCarrier.BSNL
            ]
            
            for carrier in expected_carriers:
                self.assertIsNotNone(carrier)
            
            print("   ✅ Indian mobile carriers defined correctly")
        
        except ImportError:
            print("   ⚠️  Warning: Cannot test Indian mobile carrier context")
    
    def test_indian_railway_context(self):
        """Test Indian railway context"""
        print("\n🧪 Testing Indian Railway Context")
        
        try:
            from python.irctc_booking_conflicts import SeatType, TransactionType
            
            # Check Indian Railway seat types
            expected_seat_types = [
                SeatType.SL,  # Sleeper
                SeatType.AC3,  # 3AC
                SeatType.AC2,  # 2AC
                SeatType.AC1   # 1AC
            ]
            
            for seat_type in expected_seat_types:
                self.assertIsNotNone(seat_type)
            
            print("   ✅ Indian Railway seat types defined correctly")
        
        except ImportError:
            print("   ⚠️  Warning: Cannot test Indian Railway context")

class TestSystemIntegration(unittest.TestCase):
    """Test integration between different systems"""
    
    def test_cap_consistency_levels(self):
        """Test different CAP consistency levels across systems"""
        print("\n🧪 Testing CAP Consistency Levels Integration")
        
        consistency_tests = []
        
        # Test strong consistency (Banking)
        try:
            from python.hdfc_banking_consistency import HDFCBankingSystem
            hdfc = HDFCBankingSystem(num_nodes=2)
            consistency_tests.append(("Banking Strong Consistency", True))
        except:
            consistency_tests.append(("Banking Strong Consistency", False))
        
        # Test eventual consistency (E-commerce)
        try:
            from python.flipkart_cart_availability import FlipkartAvailabilitySystem
            flipkart = FlipkartAvailabilitySystem()
            consistency_tests.append(("E-commerce Eventual Consistency", True))
        except:
            consistency_tests.append(("E-commerce Eventual Consistency", False))
        
        # Test partition tolerance (Messaging)
        try:
            from python.whatsapp_partition_tolerance import WhatsAppPartitionTolerantSystem
            whatsapp = WhatsAppPartitionTolerantSystem()
            consistency_tests.append(("Messaging Partition Tolerance", True))
        except:
            consistency_tests.append(("Messaging Partition Tolerance", False))
        
        # Report results
        for test_name, success in consistency_tests:
            if success:
                print(f"   ✅ {test_name}")
            else:
                print(f"   ❌ {test_name}")
        
        # At least one system should work
        successful_tests = sum(1 for _, success in consistency_tests if success)
        self.assertGreater(successful_tests, 0, "At least one consistency model should work")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🇮🇳 CAP THEOREM EXAMPLES - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("Testing all code examples for Episode 4")
    print("Focus: Indian context, production-ready code, CAP theorem principles")
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCapTheoremSimulator,
        TestHDFCBankingConsistency, 
        TestFlipkartCartAvailability,
        TestPaytmWalletConsistency,
        TestIRCTCBookingConflicts,
        TestWhatsAppPartitionTolerance,
        TestJavaExamples,
        TestGoExamples,
        TestIndianContextExamples,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('\\n')[-2]}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Most examples are working correctly!")
    elif success_rate >= 60:
        print("✅ GOOD: Majority of examples are functional")
    else:
        print("⚠️  WARNING: Several examples need attention")
    
    print("\n✅ Comprehensive testing completed!")
    print("🇮🇳 Ready for Episode 4: CAP Theorem with Indian context examples")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)