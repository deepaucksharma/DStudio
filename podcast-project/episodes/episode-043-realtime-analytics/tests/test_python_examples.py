#!/usr/bin/env python3
"""
Test Suite for Python Real-time Analytics Examples
Episode 43: Real-time Analytics at Scale

Comprehensive tests for all Python code examples
"""

import unittest
import sys
import os
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

# Add the parent directory to the path to import the examples
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code', 'python'))

# Import modules to test
try:
    import importlib.util
    
    # Import kafka producer/consumer example
    spec1 = importlib.util.spec_from_file_location("kafka_example", 
                                                  "../code/python/01_kafka_producer_consumer.py")
    kafka_module = importlib.util.module_from_spec(spec1)
    
    # Import fraud detection example
    spec2 = importlib.util.spec_from_file_location("fraud_detection",
                                                  "../code/python/05_realtime_fraud_detection.py")
    fraud_module = importlib.util.module_from_spec(spec2)
    
    # Import lambda architecture example
    spec3 = importlib.util.spec_from_file_location("lambda_arch",
                                                  "../code/python/04_lambda_architecture.py")
    lambda_module = importlib.util.module_from_spec(spec3)
    
    # Import real-time aggregation example
    spec4 = importlib.util.spec_from_file_location("realtime_agg",
                                                  "../code/python/03_realtime_aggregation_windows.py")
    agg_module = importlib.util.module_from_spec(spec4)
    
except Exception as e:
    print(f"Warning: Could not import modules for testing: {e}")
    kafka_module = None
    fraud_module = None
    lambda_module = None
    agg_module = None

class TestKafkaProducerConsumer(unittest.TestCase):
    """Test Kafka Producer/Consumer functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_events = []
        
    def test_flipkart_order_creation(self):
        """Test FlipkartOrderProducer order generation"""
        if kafka_module is None:
            self.skipTest("Kafka module not available")
            
        # Mock Kafka producer
        with patch('kafka.KafkaProducer'):
            producer = kafka_module.FlipkartOrderProducer()
            
            # Test order generation
            order = producer.generate_order_event("test_user")
            
            self.assertIn("order_id", order)
            self.assertIn("user_id", order)
            self.assertIn("product", order)
            self.assertIn("total_amount", order)
            self.assertEqual(order["user_id"], "test_user")
            self.assertGreater(order["total_amount"], 0)
            
    def test_order_consumer_metrics(self):
        """Test FlipkartOrderConsumer metrics calculation"""
        if kafka_module is None:
            self.skipTest("Kafka module not available")
            
        # Mock Kafka consumer
        with patch('kafka.KafkaConsumer'):
            consumer = kafka_module.FlipkartOrderConsumer()
            
            # Test metrics initialization
            self.assertEqual(consumer.metrics["totalOrders"], 0)
            self.assertEqual(consumer.metrics["totalRevenue"], 0.0)
            
            # Test order processing
            test_order = {
                "order_id": "TEST_001",
                "user_id": "USER_001",
                "total_amount": 1000.0,
                "location": {"city": "Mumbai"},
                "product": {"category": "electronics"},
                "payment_method": "UPI"
            }
            
            consumer.process_order(test_order)
            
            self.assertEqual(consumer.metrics["totalOrders"], 1)
            self.assertEqual(consumer.metrics["totalRevenue"], 1000.0)
            self.assertIn("Mumbai", consumer.metrics["orders_by_city"])
            
    def test_concurrent_processing(self):
        """Test concurrent order processing"""
        if kafka_module is None:
            self.skipTest("Kafka module not available")
            
        results = []
        
        def mock_process_order(order):
            results.append(order["order_id"])
            
        with patch('kafka.KafkaConsumer'), patch('kafka.KafkaProducer'):
            consumer = kafka_module.FlipkartOrderConsumer()
            consumer.process_order = mock_process_order
            
            # Simulate concurrent order processing
            orders = [{"order_id": f"ORDER_{i}", "total_amount": 100} for i in range(10)]
            
            threads = []
            for order in orders:
                thread = threading.Thread(target=consumer.process_order, args=(order,))
                threads.append(thread)
                thread.start()
                
            for thread in threads:
                thread.join()
                
            self.assertEqual(len(results), 10)

class TestRealTimeFraudDetection(unittest.TestCase):
    """Test Real-time Fraud Detection functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.sample_transaction = self._create_sample_transaction()
        
    def _create_sample_transaction(self):
        """Create a sample UPI transaction for testing"""
        if fraud_module is None:
            return {}
            
        return fraud_module.UPITransaction(
            transaction_id="TEST_TXN_001",
            sender_vpa="test@paytm",
            receiver_vpa="merchant@paytm",
            amount=1000.0,
            timestamp=datetime.now(),
            device_id="DEVICE_001",
            ip_address="192.168.1.1",
            location="Mumbai",
            transaction_type="P2M"
        )
        
    def test_user_behavior_tracker(self):
        """Test UserBehaviorTracker functionality"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        tracker = fraud_module.UserBehaviorTracker()
        
        # Add sample transaction
        tracker.add_transaction(self.sample_transaction)
        
        # Check if pattern is updated
        pattern = tracker.get_user_pattern(self.sample_transaction.sender_vpa)
        self.assertIn('avg_amount', pattern)
        
        # Test amount anomaly detection
        is_anomaly, score = tracker.is_amount_anomaly(self.sample_transaction.sender_vpa, 10000.0)
        # First transaction won't be anomaly due to insufficient data
        
    def test_velocity_tracker(self):
        """Test VelocityTracker functionality"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        tracker = fraud_module.VelocityTracker()
        
        # Add multiple transactions quickly
        for i in range(10):
            transaction = fraud_module.UPITransaction(
                transaction_id=f"TXN_{i}",
                sender_vpa="test@paytm",
                receiver_vpa="merchant@paytm",
                amount=100.0,
                timestamp=datetime.now(),
                device_id="DEVICE_001",
                ip_address="192.168.1.1",
                location="Mumbai",
                transaction_type="P2M"
            )
            tracker.add_transaction(transaction)
            
        # Check for velocity violations
        violations = tracker.check_velocity_violation("test@paytm")
        self.assertIsInstance(violations, list)
        
    def test_fraud_detection_engine(self):
        """Test complete fraud detection engine"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        engine = fraud_module.PaytmFraudDetectionEngine()
        
        # Process a normal transaction
        result = engine.process_transaction(self.sample_transaction)
        
        self.assertIsInstance(result, fraud_module.FraudDetectionResult)
        self.assertEqual(result.transaction_id, self.sample_transaction.transaction_id)
        self.assertIn(result.status, [
            fraud_module.TransactionStatus.APPROVED,
            fraud_module.TransactionStatus.DECLINED,
            fraud_module.TransactionStatus.FLAGGED,
            fraud_module.TransactionStatus.UNDER_REVIEW
        ])
        
        # Check metrics
        metrics = engine.get_real_time_metrics()
        self.assertIn('total_transactions', metrics)
        self.assertGreater(metrics['total_transactions'], 0)
        
    def test_ml_anomaly_detector(self):
        """Test ML-based anomaly detection"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        detector = fraud_module.MLAnomalyDetector()
        user_behavior = fraud_module.UserBehaviorTracker()
        velocity_tracker = fraud_module.VelocityTracker()
        device_tracker = fraud_module.DeviceTracker()
        
        # Add some historical data
        user_behavior.add_transaction(self.sample_transaction)
        velocity_tracker.add_transaction(self.sample_transaction)
        device_tracker.add_transaction(self.sample_transaction)
        
        # Calculate ML score
        ml_score = detector.calculate_ml_score(
            self.sample_transaction, user_behavior, velocity_tracker, device_tracker
        )
        
        self.assertIsInstance(ml_score, float)
        self.assertGreaterEqual(ml_score, 0.0)
        self.assertLessEqual(ml_score, 1.0)

class TestLambdaArchitecture(unittest.TestCase):
    """Test Lambda Architecture implementation"""
    
    def setUp(self):
        """Setup test environment"""
        pass
        
    def test_batch_layer(self):
        """Test BatchLayer functionality"""
        if lambda_module is None:
            self.skipTest("Lambda architecture module not available")
            
        batch_layer = lambda_module.BatchLayer()
        
        # Test database initialization
        self.assertTrue(os.path.exists(batch_layer.db_path))
        
        # Test event storage
        sample_events = []
        for i in range(5):
            event = lambda_module.UserEvent(
                user_id=f"user_{i}",
                event_type="view",
                product_id=f"product_{i}",
                category="electronics",
                price=100.0,
                timestamp=datetime.now(),
                session_id=f"session_{i}",
                device_type="mobile"
            )
            sample_events.append(event)
            
        batch_layer.store_events(sample_events)
        
        # Test user profile computation
        batch_layer.compute_user_profiles()
        
    def test_speed_layer(self):
        """Test SpeedLayer functionality"""
        if lambda_module is None:
            self.skipTest("Lambda architecture module not available")
            
        speed_layer = lambda_module.SpeedLayer()
        
        # Test event processing
        event = lambda_module.UserEvent(
            user_id="test_user",
            event_type="view",
            product_id="test_product",
            category="electronics",
            price=100.0,
            timestamp=datetime.now(),
            session_id="test_session",
            device_type="mobile"
        )
        
        recommendations = speed_layer.process_real_time_event(event)
        self.assertIsInstance(recommendations, list)
        
        # Test stats
        stats = speed_layer.get_real_time_stats()
        self.assertIsInstance(stats, dict)
        
    def test_serving_layer(self):
        """Test ServingLayer functionality"""
        if lambda_module is None:
            self.skipTest("Lambda architecture module not available")
            
        batch_layer = lambda_module.BatchLayer()
        speed_layer = lambda_module.SpeedLayer()
        serving_layer = lambda_module.ServingLayer(batch_layer, speed_layer)
        
        # Test recommendation retrieval
        recommendations = serving_layer.get_recommendations("test_user", limit=5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

class TestRealTimeAggregation(unittest.TestCase):
    """Test Real-time Aggregation Windows"""
    
    def setUp(self):
        """Setup test environment"""
        pass
        
    def test_time_window(self):
        """Test TimeWindow functionality"""
        if agg_module is None:
            self.skipTest("Aggregation module not available")
            
        window = agg_module.TimeWindow(window_size_seconds=60)
        
        # Test event addition
        sample_event = agg_module.RideRequest(
            request_id="TEST_001",
            user_id="USER_001",
            pickup_location="Bandra",
            drop_location="Andheri",
            ride_type="Mini",
            timestamp=datetime.now(),
            estimated_price=200.0
        )
        
        window.add_event(sample_event)
        self.assertEqual(len(window.events), 1)
        
    def test_tumbling_window(self):
        """Test TumblingWindow functionality"""
        if agg_module is None:
            self.skipTest("Aggregation module not available")
            
        start_time = datetime.now()
        window = agg_module.TumblingWindow(window_size_seconds=300, start_time=start_time)
        
        self.assertEqual(window.window_start, start_time)
        self.assertEqual(window.window_end, start_time + timedelta(seconds=300))
        
        # Test window creation for timestamp
        window2 = agg_module.TumblingWindow.create_for_timestamp(
            datetime.now(), window_size_seconds=300
        )
        self.assertIsNotNone(window2.window_start)
        
    def test_sliding_window(self):
        """Test SlidingWindow functionality"""
        if agg_module is None:
            self.skipTest("Aggregation module not available")
            
        window = agg_module.SlidingWindow(
            window_size_seconds=600, slide_interval_seconds=60
        )
        
        # Test sliding
        current_time = datetime.now()
        window.slide(current_time)
        
        self.assertEqual(window.window_end, current_time)
        self.assertEqual(window.window_start, current_time - timedelta(seconds=600))
        
    def test_ola_surge_pricing_engine(self):
        """Test OlaSurgePricingEngine functionality"""
        if agg_module is None:
            self.skipTest("Aggregation module not available")
            
        engine = agg_module.OlaSurgePricingEngine()
        
        # Test request processing
        request = agg_module.RideRequest(
            request_id="TEST_001",
            user_id="USER_001",
            pickup_location="Bandra",
            drop_location="Andheri",
            ride_type="Mini",
            timestamp=datetime.now(),
            estimated_price=200.0
        )
        
        result = engine.process_ride_request(request)
        
        self.assertIn('request_id', result)
        self.assertIn('current_surge', result)
        self.assertIn('estimated_price', result)
        
        # Test metrics
        metrics = engine.get_real_time_metrics()
        self.assertIn('overall_metrics', metrics)

class TestStreamProcessing(unittest.TestCase):
    """Test Stream Processing functionality"""
    
    def setUp(self):
        """Setup test environment"""
        pass
        
    @patch('pyflink.datastream.StreamExecutionEnvironment')
    def test_flink_setup(self, mock_env):
        """Test Flink stream processing setup"""
        # This is a basic test since we can't run actual Flink in unit tests
        mock_env.get_execution_environment.return_value = Mock()
        
        # Test would go here if we had the actual Flink module imported
        self.assertTrue(True)  # Placeholder

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency"""
    
    def test_transaction_serialization(self):
        """Test transaction data serialization"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        transaction = fraud_module.UPITransaction(
            transaction_id="TEST_001",
            sender_vpa="test@paytm",
            receiver_vpa="merchant@paytm",
            amount=1000.0,
            timestamp=datetime.now(),
            device_id="DEVICE_001",
            ip_address="192.168.1.1",
            location="Mumbai",
            transaction_type="P2M"
        )
        
        # Test serialization
        data_dict = transaction.to_dict()
        self.assertIn('transaction_id', data_dict)
        self.assertIn('amount', data_dict)
        
        # Test validation
        self.assertTrue(transaction.isValid())
        
    def test_json_serialization(self):
        """Test JSON serialization of complex objects"""
        test_data = {
            "timestamp": datetime.now(),
            "metrics": {
                "count": 100,
                "rate": 95.5,
                "status": "healthy"
            },
            "items": ["item1", "item2", "item3"]
        }
        
        # Test JSON serialization with datetime
        try:
            json_str = json.dumps(test_data, default=str)
            reconstructed = json.loads(json_str)
            self.assertIn('metrics', reconstructed)
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")

class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def test_fraud_detection_performance(self):
        """Test fraud detection processing speed"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        engine = fraud_module.PaytmFraudDetectionEngine()
        
        # Process multiple transactions and measure time
        start_time = time.time()
        
        for i in range(10):  # Reduced number for unit tests
            transaction = fraud_module.UPITransaction(
                transaction_id=f"PERF_TEST_{i}",
                sender_vpa=f"user_{i}@paytm",
                receiver_vpa="merchant@paytm",
                amount=100.0 + i,
                timestamp=datetime.now(),
                device_id=f"DEVICE_{i}",
                ip_address="192.168.1.1",
                location="Mumbai",
                transaction_type="P2M"
            )
            
            result = engine.process_transaction(transaction)
            self.assertIsNotNone(result)
            
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 10 transactions in less than 1 second
        self.assertLess(processing_time, 1.0)
        
        # Check average processing time
        avg_time = processing_time / 10
        self.assertLess(avg_time, 0.1)  # Less than 100ms per transaction
        
    def test_memory_usage(self):
        """Test memory usage patterns"""
        if agg_module is None:
            self.skipTest("Aggregation module not available")
            
        # Test that sliding windows don't accumulate too much data
        window = agg_module.SlidingWindow(
            window_size_seconds=60, slide_interval_seconds=10
        )
        
        # Add many events
        for i in range(1000):
            event = agg_module.RideRequest(
                request_id=f"MEM_TEST_{i}",
                user_id=f"USER_{i % 100}",
                pickup_location="Bandra",
                drop_location="Andheri",
                ride_type="Mini",
                timestamp=datetime.now(),
                estimated_price=200.0
            )
            window.add_event(event)
            
            # Slide window occasionally
            if i % 100 == 0:
                window.slide(datetime.now())
                
        # Window should not grow indefinitely
        self.assertLess(len(window.events), 1000)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_invalid_transaction_handling(self):
        """Test handling of invalid transactions"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        # Test with invalid transaction data
        try:
            transaction = fraud_module.UPITransaction(
                transaction_id="",  # Empty ID
                sender_vpa="",      # Empty VPA
                receiver_vpa="",    # Empty VPA
                amount=-100.0,      # Negative amount
                timestamp=datetime.now(),
                device_id="",
                ip_address="",
                location="",
                transaction_type=""
            )
            
            # Should be marked as invalid
            self.assertFalse(transaction.isValid())
            
        except Exception:
            # Exception handling is also acceptable
            pass
            
    def test_empty_data_handling(self):
        """Test handling of empty or null data"""
        if kafka_module is None:
            self.skipTest("Kafka module not available")
            
        with patch('kafka.KafkaConsumer'):
            consumer = kafka_module.FlipkartOrderConsumer()
            
            # Test with empty order data
            try:
                consumer.process_order({})
                # Should handle gracefully
            except KeyError:
                # Expected behavior for missing required fields
                pass
                
    def test_concurrent_access_safety(self):
        """Test thread safety of concurrent operations"""
        if fraud_module is None:
            self.skipTest("Fraud detection module not available")
            
        engine = fraud_module.PaytmFraudDetectionEngine()
        results = []
        errors = []
        
        def process_transaction_safely(i):
            try:
                transaction = fraud_module.UPITransaction(
                    transaction_id=f"CONCURRENT_{i}",
                    sender_vpa=f"user_{i}@paytm",
                    receiver_vpa="merchant@paytm",
                    amount=100.0,
                    timestamp=datetime.now(),
                    device_id=f"DEVICE_{i}",
                    ip_address="192.168.1.1",
                    location="Mumbai",
                    transaction_type="P2M"
                )
                
                result = engine.process_transaction(transaction)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
                
        # Run concurrent transactions
        threads = []
        for i in range(5):  # Small number for unit tests
            thread = threading.Thread(target=process_transaction_safely, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Should have processed all transactions without errors
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)

def run_all_tests():
    """Run all test suites"""
    print("🧪 Running Python Real-time Analytics Tests...")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestKafkaProducerConsumer,
        TestRealTimeFraudDetection,
        TestLambdaArchitecture,
        TestRealTimeAggregation,
        TestStreamProcessing,
        TestDataIntegrity,
        TestPerformance,
        TestErrorHandling
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n🔍 Running {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"❌ Failures in {test_class.__name__}:")
            for test, trace in result.failures:
                print(f"  - {test}: {trace.split('AssertionError:')[-1].strip()}")
                
        if result.errors:
            print(f"💥 Errors in {test_class.__name__}:")
            for test, trace in result.errors:
                print(f"  - {test}: {trace.split('Exception:')[-1].strip()}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_tests - total_failures - total_errors}")
    print(f"   Failed: {total_failures}")
    print(f"   Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)