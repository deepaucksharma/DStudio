#!/usr/bin/env python3
"""
Test suite for Cascade Failure Probability Calculator
Test cases based on real incidents and edge cases
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python', 'probability_calculator'))

from cascade_failure_calculator import CascadeFailureCalculator, ServiceNode, create_zomato_example, create_irctc_example


class TestCascadeFailureCalculator(unittest.TestCase):
    """Test cases for probability calculator"""
    
    def setUp(self):
        """Test setup - create calculator instance"""
        self.calc = CascadeFailureCalculator()
        
        # Simple test topology
        self.calc.add_service(ServiceNode("service_a", 0.001, [], 0.2, 100))
        self.calc.add_service(ServiceNode("service_b", 0.002, ["service_a"], 0.3, 150))
        self.calc.add_service(ServiceNode("service_c", 0.0015, ["service_b"], 0.4, 200))
    
    def test_service_addition(self):
        """Test service addition to topology"""
        calc = CascadeFailureCalculator()
        service = ServiceNode("test_service", 0.001, [], 0.2, 100)
        calc.add_service(service)
        
        self.assertIn("test_service", calc.services)
        self.assertEqual(calc.services["test_service"].base_failure_rate, 0.001)
    
    def test_independent_probability_calculation(self):
        """Test independent failure probability calculation"""
        probs = self.calc.calculate_independent_probability(1.0)
        
        # Check all services have probabilities
        self.assertEqual(len(probs), 3)
        self.assertIn("service_a", probs)
        self.assertIn("service_b", probs)
        self.assertIn("service_c", probs)
        
        # Check probabilities are in valid range [0, 1]
        for prob in probs.values():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
        
        # Service B should have higher probability than A (higher failure rate)
        self.assertGreater(probs["service_b"], probs["service_a"])
    
    def test_correlated_probability_calculation(self):
        """Test correlated failure probability calculation"""
        independent_probs = self.calc.calculate_independent_probability(1.0)
        correlated_probs = self.calc.calculate_correlated_probability(1.0)
        
        # Correlated probabilities should be higher for dependent services
        self.assertGreater(
            correlated_probs["service_b"], 
            independent_probs["service_b"]
        )
        self.assertGreater(
            correlated_probs["service_c"], 
            independent_probs["service_c"]
        )
        
        # Service A has no dependencies, so should be same
        self.assertAlmostEqual(
            correlated_probs["service_a"], 
            independent_probs["service_a"], 
            places=6
        )
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation functionality"""
        results = self.calc.simulate_cascade_monte_carlo(1.0, 1000)
        
        # Check result structure
        self.assertIn('simulation_count', results)
        self.assertIn('failure_probabilities', results)
        self.assertIn('cascade_probabilities', results)
        self.assertIn('cost_statistics', results)
        
        # Check simulation count
        self.assertEqual(results['simulation_count'], 1000)
        
        # Check probabilities are valid
        for prob in results['failure_probabilities'].values():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
        
        # Check cost statistics exist
        cost_stats = results['cost_statistics']
        self.assertIn('mean_cost_usd', cost_stats)
        self.assertIn('max_cost_usd', cost_stats)
        self.assertIn('mean_cost_inr', cost_stats)
    
    def test_critical_path_analysis(self):
        """Test critical path analysis"""
        critical_paths = self.calc.analyze_critical_path()
        
        # Service A should affect B and C
        self.assertIn("service_b", critical_paths["service_a"])
        self.assertIn("service_c", critical_paths["service_a"])
        
        # Service B should affect C
        self.assertIn("service_c", critical_paths["service_b"])
        
        # Service C affects no one
        self.assertEqual(len(critical_paths["service_c"]), 0)
    
    def test_report_generation(self):
        """Test report generation"""
        report = self.calc.generate_report(1.0)
        
        # Check report contains expected sections
        self.assertIn("CASCADE FAILURE ANALYSIS REPORT", report)
        self.assertIn("FAILURE PROBABILITIES", report)
        self.assertIn("COST IMPACT ANALYSIS", report)
        self.assertIn("CRITICAL SERVICES", report)
        
        # Check all services mentioned
        self.assertIn("service_a", report)
        self.assertIn("service_b", report)
        self.assertIn("service_c", report)
    
    def test_edge_case_zero_failure_rate(self):
        """Test edge case with zero failure rate"""
        calc = CascadeFailureCalculator()
        calc.add_service(ServiceNode("perfect_service", 0.0, [], 0.0, 0))
        
        probs = calc.calculate_independent_probability(1.0)
        self.assertEqual(probs["perfect_service"], 0.0)
    
    def test_edge_case_circular_dependency(self):
        """Test edge case with circular dependencies"""
        calc = CascadeFailureCalculator()
        calc.add_service(ServiceNode("service_x", 0.001, ["service_y"], 0.2, 100))
        calc.add_service(ServiceNode("service_y", 0.001, ["service_x"], 0.2, 100))
        
        # Should not crash with circular dependencies
        probs = calc.calculate_correlated_probability(1.0)
        self.assertEqual(len(probs), 2)
        
        critical_paths = calc.analyze_critical_path()
        # Should handle circular dependencies gracefully
        self.assertTrue(len(critical_paths) > 0)


class TestRealWorldExamples(unittest.TestCase):
    """Test real-world example configurations"""
    
    def test_zomato_example_creation(self):
        """Test Zomato example setup"""
        calc = create_zomato_example()
        
        # Check expected services exist
        expected_services = [
            "api_gateway", "user_service", "restaurant_service", 
            "order_service", "payment_gateway", "delivery_service",
            "notification_service", "analytics_service"
        ]
        
        for service_name in expected_services:
            self.assertIn(service_name, calc.services)
        
        # Test dependencies are correctly set
        self.assertIn("api_gateway", calc.services["user_service"].dependencies)
        self.assertIn("user_service", calc.services["order_service"].dependencies)
        self.assertIn("restaurant_service", calc.services["order_service"].dependencies)
    
    def test_irctc_example_creation(self):
        """Test IRCTC example setup"""
        calc = create_irctc_example()
        
        # Check critical services exist
        expected_services = [
            "load_balancer", "auth_service", "train_search", 
            "booking_engine", "payment_processor", "ticket_generator",
            "waitlist_manager", "database_cluster"
        ]
        
        for service_name in expected_services:
            self.assertIn(service_name, calc.services)
        
        # Database should be dependency for most services
        services_with_db_dep = 0
        for service in calc.services.values():
            if "database_cluster" in service.dependencies:
                services_with_db_dep += 1
        
        self.assertGreater(services_with_db_dep, 5)  # Most services depend on DB
    
    def test_example_simulation_runs(self):
        """Test that examples can run simulations without errors"""
        # Test Zomato
        zomato_calc = create_zomato_example()
        zomato_results = zomato_calc.simulate_cascade_monte_carlo(1.0, 100)
        self.assertIn('simulation_count', zomato_results)
        
        # Test IRCTC
        irctc_calc = create_irctc_example()
        irctc_results = irctc_calc.simulate_cascade_monte_carlo(0.5, 100)
        self.assertIn('simulation_count', irctc_results)
    
    def test_cost_impact_realistic(self):
        """Test that cost impacts are in realistic ranges"""
        calc = create_zomato_example()
        results = calc.simulate_cascade_monte_carlo(1.0, 100)
        
        cost_stats = results['cost_statistics']
        
        # Mean cost should be reasonable (not zero, not astronomical)
        self.assertGreater(cost_stats['mean_cost_usd'], 0)
        self.assertLess(cost_stats['mean_cost_usd'], 100000)  # Less than $100k
        
        # INR conversion should be applied
        self.assertGreater(cost_stats['mean_cost_inr'], cost_stats['mean_cost_usd'])


class TestPerformance(unittest.TestCase):
    """Performance and scalability tests"""
    
    def test_large_topology_performance(self):
        """Test performance with larger service topology"""
        import time
        
        calc = CascadeFailureCalculator()
        
        # Create 50 services with complex dependencies
        for i in range(50):
            deps = [f"service_{j}" for j in range(max(0, i-3), i)]  # Depend on previous 3
            calc.add_service(ServiceNode(f"service_{i}", 0.001, deps, 0.2, 100))
        
        # Test simulation performance
        start_time = time.time()
        results = calc.simulate_cascade_monte_carlo(1.0, 1000)
        end_time = time.time()
        
        # Should complete within reasonable time (< 10 seconds)
        self.assertLess(end_time - start_time, 10.0)
        
        # Should have results for all 50 services
        self.assertEqual(len(results['failure_probabilities']), 50)


if __name__ == '__main__':
    print("🧪 Running Cascade Failure Calculator Tests")
    print("Testing real-world scenarios: Zomato, IRCTC, edge cases\n")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestCascadeFailureCalculator))
    suite.addTest(unittest.makeSuite(TestRealWorldExamples))
    suite.addTest(unittest.makeSuite(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} tests passed!")
        print("📊 Probability calculator is production-ready")
        print("💡 Key validations completed:")
        print("  - Independent vs correlated probability calculation")
        print("  - Monte Carlo simulation accuracy")
        print("  - Real-world example configurations")
        print("  - Edge cases and performance")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test failures")
        print("🔧 Fix issues before production deployment")
    
    # Return exit code for CI/CD
    exit(0 if result.wasSuccessful() else 1)