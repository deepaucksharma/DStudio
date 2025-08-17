#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures for Episodes 92-100
हिंदी पॉडकास्ट टेस्टिंग कॉन्फ़िगरेशन

This module provides shared fixtures, test data, and configuration
for comprehensive testing of all code examples with Indian context.
"""

import asyncio
import json
import os
import random
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Generator
from unittest.mock import Mock

import pytest
import requests
from faker import Faker
from faker.providers import bank, internet, address, phone_number

# Initialize Faker with Indian locale
fake = Faker(['en_IN', 'hi_IN'])
fake.add_provider(bank)
fake.add_provider(internet)
fake.add_provider(address)
fake.add_provider(phone_number)

# Test configuration
TEST_CONFIG = {
    "environment": os.getenv("TEST_ENV", "test"),
    "region": os.getenv("INDIAN_REGION", "mumbai"),
    "upi_test_mode": os.getenv("UPI_TEST_MODE", "true").lower() == "true",
    "chaos_testing": os.getenv("CHAOS_TESTING", "false").lower() == "true",
    "max_test_duration": int(os.getenv("MAX_TEST_DURATION", "300")),
    "load_test_vus": int(os.getenv("LOAD_TEST_VUS", "100")),
}

# Indian cities and their characteristics
INDIAN_CITIES = {
    "mumbai": {
        "name": "Mumbai",
        "population": 20_000_000,
        "timezone": "Asia/Kolkata",
        "financial_hub": True,
        "avg_latency_ms": 25,
        "peak_traffic_multiplier": 3.0
    },
    "delhi": {
        "name": "Delhi",
        "population": 32_000_000,
        "timezone": "Asia/Kolkata", 
        "government_hub": True,
        "avg_latency_ms": 30,
        "peak_traffic_multiplier": 2.8
    },
    "bangalore": {
        "name": "Bangalore",
        "population": 13_000_000,
        "timezone": "Asia/Kolkata",
        "tech_hub": True,
        "avg_latency_ms": 20,
        "peak_traffic_multiplier": 2.5
    },
    "chennai": {
        "name": "Chennai",
        "population": 11_000_000,
        "timezone": "Asia/Kolkata",
        "automotive_hub": True,
        "avg_latency_ms": 35,
        "peak_traffic_multiplier": 2.2
    },
    "kolkata": {
        "name": "Kolkata",
        "population": 15_000_000,
        "timezone": "Asia/Kolkata",
        "cultural_hub": True,
        "avg_latency_ms": 40,
        "peak_traffic_multiplier": 2.0
    }
}

# Indian banks and their characteristics
INDIAN_BANKS = {
    "HDFC": {
        "name": "HDFC Bank",
        "type": "private",
        "upi_handle": "@hdfcbank",
        "market_share": 15.2,
        "avg_processing_time_ms": 150
    },
    "ICICI": {
        "name": "ICICI Bank", 
        "type": "private",
        "upi_handle": "@icici",
        "market_share": 12.8,
        "avg_processing_time_ms": 140
    },
    "SBI": {
        "name": "State Bank of India",
        "type": "public",
        "upi_handle": "@sbi",
        "market_share": 22.3,
        "avg_processing_time_ms": 200
    },
    "AXIS": {
        "name": "Axis Bank",
        "type": "private", 
        "upi_handle": "@axisbank",
        "market_share": 8.5,
        "avg_processing_time_ms": 160
    },
    "KOTAK": {
        "name": "Kotak Mahindra Bank",
        "type": "private",
        "upi_handle": "@kotak",
        "market_share": 5.2,
        "avg_processing_time_ms": 145
    }
}

# Festival and event calendar
INDIAN_FESTIVALS = {
    "diwali": {
        "name": "Diwali",
        "duration_days": 5,
        "traffic_multiplier": 15.0,
        "ecommerce_boost": 20.0,
        "peak_hours": ["19:00", "20:00", "21:00"]
    },
    "holi": {
        "name": "Holi",
        "duration_days": 2,
        "traffic_multiplier": 8.0,
        "ecommerce_boost": 5.0,
        "peak_hours": ["10:00", "11:00", "12:00"]
    },
    "dussehra": {
        "name": "Dussehra",
        "duration_days": 10,
        "traffic_multiplier": 6.0,
        "ecommerce_boost": 8.0,
        "peak_hours": ["18:00", "19:00", "20:00"]
    },
    "ipl_final": {
        "name": "IPL Final",
        "duration_hours": 4,
        "traffic_multiplier": 25.0,
        "streaming_boost": 50.0,
        "peak_hours": ["19:30", "20:30", "21:30"]
    }
}

# Performance benchmarks
PERFORMANCE_TARGETS = {
    "api_latency_p95_ms": 100,
    "api_latency_p99_ms": 200,
    "database_latency_p95_ms": 50,
    "database_latency_p99_ms": 100,
    "throughput_min_tps": 1000,
    "availability_percent": 99.9,
    "error_rate_max_percent": 0.1,
    "memory_usage_max_mb": 512,
    "cpu_usage_max_percent": 80
}

# Test Data Generators
class IndianTestDataGenerator:
    """Generate realistic Indian test data"""
    
    @staticmethod
    def indian_name():
        """Generate Indian name"""
        first_names = [
            "Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Kavya", 
            "Arjun", "Meera", "Rohit", "Anita", "Deepak", "Sujata",
            "Rahul", "Pooja", "Sunil", "Nisha", "Anil", "Rekha"
        ]
        last_names = [
            "Sharma", "Patel", "Singh", "Gupta", "Kumar", "Verma",
            "Shah", "Jain", "Agarwal", "Sinha", "Joshi", "Iyer"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    @staticmethod
    def indian_phone():
        """Generate Indian phone number"""
        return f"+91{random.randint(7000000000, 9999999999)}"
    
    @staticmethod
    def indian_email():
        """Generate Indian email"""
        name = IndianTestDataGenerator.indian_name().lower().replace(" ", ".")
        domains = ["gmail.com", "yahoo.co.in", "hotmail.com", "rediffmail.com"]
        return f"{name}@{random.choice(domains)}"
    
    @staticmethod
    def bank_account():
        """Generate Indian bank account"""
        bank = random.choice(list(INDIAN_BANKS.keys()))
        account_number = f"{bank}{random.randint(10000000, 99999999)}"
        return {
            "account_number": account_number,
            "bank": bank,
            "ifsc": f"{bank}0001234",
            "balance": random.randint(1000, 1000000)
        }
    
    @staticmethod
    def upi_id():
        """Generate UPI ID"""
        name = IndianTestDataGenerator.indian_name().lower().replace(" ", "")
        handles = ["@paytm", "@phonepe", "@googlepay", "@amazonpay", "@bhim"]
        return f"{name}{random.choice(handles)}"
    
    @staticmethod
    def indian_address():
        """Generate Indian address"""
        cities = list(INDIAN_CITIES.keys())
        city = random.choice(cities)
        areas = {
            "mumbai": ["Andheri", "Bandra", "Powai", "Malad", "Thane"],
            "delhi": ["CP", "Gurgaon", "Noida", "Dwarka", "Lajpat Nagar"],
            "bangalore": ["Koramangala", "Whitefield", "HSR Layout", "Indiranagar", "Jayanagar"],
            "chennai": ["T Nagar", "Anna Nagar", "Velachery", "Adyar", "Tambaram"],
            "kolkata": ["Salt Lake", "Park Street", "Ballygunge", "Howrah", "New Town"]
        }
        area = random.choice(areas.get(city, ["Central Area"]))
        
        return {
            "street": f"{random.randint(1, 999)} {area} Road",
            "area": area,
            "city": INDIAN_CITIES[city]["name"],
            "state": {
                "mumbai": "Maharashtra",
                "delhi": "Delhi",
                "bangalore": "Karnataka", 
                "chennai": "Tamil Nadu",
                "kolkata": "West Bengal"
            }[city],
            "pincode": random.randint(100001, 999999)
        }

# Pytest Fixtures
@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def indian_cities():
    """Indian cities data fixture"""
    return INDIAN_CITIES

@pytest.fixture(scope="session")
def indian_banks():
    """Indian banks data fixture"""
    return INDIAN_BANKS

@pytest.fixture(scope="session")
def indian_festivals():
    """Indian festivals data fixture"""
    return INDIAN_FESTIVALS

@pytest.fixture(scope="session")
def performance_targets():
    """Performance targets fixture"""
    return PERFORMANCE_TARGETS

@pytest.fixture
def indian_test_data():
    """Indian test data generator fixture"""
    return IndianTestDataGenerator()

@pytest.fixture
def temp_directory():
    """Temporary directory fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_database():
    """Mock database fixture"""
    db = Mock()
    db.data = {}
    
    def get(key):
        return db.data.get(key)
    
    def set(key, value):
        db.data[key] = value
        return True
    
    def delete(key):
        return db.data.pop(key, None)
    
    def exists(key):
        return key in db.data
    
    db.get = get
    db.set = set
    db.delete = delete
    db.exists = exists
    
    return db

@pytest.fixture
def mock_redis():
    """Mock Redis fixture"""
    redis = Mock()
    redis.data = {}
    redis.expiry = {}
    
    def set(key, value, ex=None):
        redis.data[key] = value
        if ex:
            redis.expiry[key] = time.time() + ex
        return True
    
    def get(key):
        if key in redis.expiry and time.time() > redis.expiry[key]:
            del redis.data[key]
            del redis.expiry[key]
            return None
        return redis.data.get(key)
    
    def delete(key):
        redis.data.pop(key, None)
        redis.expiry.pop(key, None)
        return True
    
    def exists(key):
        if key in redis.expiry and time.time() > redis.expiry[key]:
            del redis.data[key]
            del redis.expiry[key]
            return False
        return key in redis.data
    
    redis.set = set
    redis.get = get
    redis.delete = delete
    redis.exists = exists
    
    return redis

@pytest.fixture
def mock_http_client():
    """Mock HTTP client fixture"""
    client = Mock()
    client.responses = {}
    client.call_count = {}
    
    def get(url, **kwargs):
        client.call_count[url] = client.call_count.get(url, 0) + 1
        response = Mock()
        if url in client.responses:
            response.status_code = client.responses[url].get("status_code", 200)
            response.json.return_value = client.responses[url].get("json", {})
            response.text = client.responses[url].get("text", "")
        else:
            response.status_code = 200
            response.json.return_value = {"status": "ok"}
            response.text = "OK"
        return response
    
    def post(url, **kwargs):
        return get(url, **kwargs)
    
    def put(url, **kwargs):
        return get(url, **kwargs)
    
    def delete(url, **kwargs):
        return get(url, **kwargs)
    
    client.get = get
    client.post = post
    client.put = put
    client.delete = delete
    
    return client

@pytest.fixture
def indian_user_session():
    """Simulated Indian user session"""
    user = {
        "id": fake.uuid4(),
        "name": IndianTestDataGenerator.indian_name(),
        "email": IndianTestDataGenerator.indian_email(),
        "phone": IndianTestDataGenerator.indian_phone(),
        "address": IndianTestDataGenerator.indian_address(),
        "bank_account": IndianTestDataGenerator.bank_account(),
        "upi_id": IndianTestDataGenerator.upi_id(),
        "created_at": fake.date_time_this_year(),
        "last_login": fake.date_time_this_month(),
        "session_id": fake.uuid4(),
        "device_info": {
            "type": random.choice(["mobile", "desktop", "tablet"]),
            "os": random.choice(["Android", "iOS", "Windows", "macOS"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"])
        }
    }
    return user

@pytest.fixture
def festival_traffic_simulator():
    """Festival traffic simulation fixture"""
    class FestivalSimulator:
        def __init__(self):
            self.base_load = 1000
            self.current_multiplier = 1.0
            
        def simulate_festival(self, festival_name: str):
            if festival_name in INDIAN_FESTIVALS:
                festival = INDIAN_FESTIVALS[festival_name]
                self.current_multiplier = festival["traffic_multiplier"]
                return {
                    "festival": festival_name,
                    "multiplier": self.current_multiplier,
                    "expected_load": self.base_load * self.current_multiplier,
                    "duration": festival.get("duration_days", 1),
                    "peak_hours": festival.get("peak_hours", [])
                }
            return None
            
        def get_current_load(self):
            return int(self.base_load * self.current_multiplier)
            
        def reset(self):
            self.current_multiplier = 1.0
    
    return FestivalSimulator()

@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture"""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
            
        def start_timer(self, operation: str):
            self.start_times[operation] = time.time()
            
        def end_timer(self, operation: str):
            if operation in self.start_times:
                duration = time.time() - self.start_times[operation]
                if operation not in self.metrics:
                    self.metrics[operation] = []
                self.metrics[operation].append(duration * 1000)  # Convert to ms
                del self.start_times[operation]
                return duration * 1000
            return None
            
        def get_stats(self, operation: str):
            if operation in self.metrics:
                times = self.metrics[operation]
                return {
                    "count": len(times),
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                    "p95": sorted(times)[int(0.95 * len(times))],
                    "p99": sorted(times)[int(0.99 * len(times))]
                }
            return None
            
        def assert_performance(self, operation: str, max_p95_ms: float):
            stats = self.get_stats(operation)
            if stats:
                assert stats["p95"] <= max_p95_ms, f"P95 latency {stats['p95']:.2f}ms exceeds {max_p95_ms}ms"
            
        def reset(self):
            self.metrics.clear()
            self.start_times.clear()
    
    return PerformanceMonitor()

@pytest.fixture
def chaos_simulator():
    """Chaos engineering simulation fixture"""
    class ChaosSimulator:
        def __init__(self):
            self.active_chaos = []
            self.chaos_enabled = TEST_CONFIG["chaos_testing"]
            
        def network_delay(self, delay_ms: int):
            if self.chaos_enabled:
                chaos = {
                    "type": "network_delay",
                    "delay_ms": delay_ms,
                    "start_time": time.time()
                }
                self.active_chaos.append(chaos)
                return chaos
            return None
            
        def service_failure(self, service_name: str, failure_rate: float):
            if self.chaos_enabled:
                chaos = {
                    "type": "service_failure",
                    "service": service_name,
                    "failure_rate": failure_rate,
                    "start_time": time.time()
                }
                self.active_chaos.append(chaos)
                return chaos
            return None
            
        def memory_pressure(self, pressure_percent: int):
            if self.chaos_enabled:
                chaos = {
                    "type": "memory_pressure",
                    "pressure_percent": pressure_percent,
                    "start_time": time.time()
                }
                self.active_chaos.append(chaos)
                return chaos
            return None
            
        def stop_all_chaos(self):
            self.active_chaos.clear()
            
        def is_chaos_active(self, chaos_type: str):
            return any(c["type"] == chaos_type for c in self.active_chaos)
    
    return ChaosSimulator()

@pytest.fixture
def load_test_scenario():
    """Load testing scenario fixture"""
    class LoadTestScenario:
        def __init__(self):
            self.scenarios = {
                "normal": {"vus": 100, "duration": "30s", "ramp_up": "10s"},
                "peak": {"vus": 1000, "duration": "60s", "ramp_up": "20s"},
                "diwali": {"vus": 5000, "duration": "300s", "ramp_up": "60s"},
                "ipl_match": {"vus": 10000, "duration": "180s", "ramp_up": "30s"}
            }
            
        def get_scenario(self, scenario_name: str):
            return self.scenarios.get(scenario_name, self.scenarios["normal"])
            
        def custom_scenario(self, vus: int, duration: str, ramp_up: str = "10s"):
            return {"vus": vus, "duration": duration, "ramp_up": ramp_up}
    
    return LoadTestScenario()

# Event Loop Fixtures for Async Testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Async test utilities
@pytest.fixture
async def async_context_manager():
    """Async context manager for resource cleanup"""
    resources = []
    
    class AsyncResourceManager:
        async def add_resource(self, resource):
            resources.append(resource)
            return resource
            
        async def cleanup_all(self):
            for resource in reversed(resources):
                if hasattr(resource, 'cleanup'):
                    await resource.cleanup()
                elif hasattr(resource, 'close'):
                    await resource.close()
            resources.clear()
    
    manager = AsyncResourceManager()
    yield manager
    await manager.cleanup_all()

# Parametrized fixtures for testing multiple scenarios
@pytest.fixture(params=["mumbai", "delhi", "bangalore", "chennai", "kolkata"])
def indian_city(request):
    """Parametrized fixture for testing across Indian cities"""
    return request.param

@pytest.fixture(params=["HDFC", "ICICI", "SBI", "AXIS", "KOTAK"])
def indian_bank(request):
    """Parametrized fixture for testing across Indian banks"""
    return request.param

@pytest.fixture(params=["diwali", "holi", "dussehra", "ipl_final"])
def indian_festival(request):
    """Parametrized fixture for testing across Indian festivals"""
    return request.param

# Cleanup and teardown
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Auto-cleanup fixture for test data"""
    yield
    # Cleanup any temp files, reset mocks, etc.
    # This runs after every test automatically

# Custom markers and test categorization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "indian_context: mark test as using Indian context scenarios"
    )
    config.addinivalue_line(
        "markers", "banking: mark test as banking/fintech related"
    )
    config.addinivalue_line(
        "markers", "ecommerce: mark test as e-commerce related"
    )
    config.addinivalue_line(
        "markers", "gaming: mark test as gaming/entertainment related"
    )
    config.addinivalue_line(
        "markers", "load: mark test as load/performance test"
    )
    config.addinivalue_line(
        "markers", "chaos: mark test as chaos engineering test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )

# Test data files
@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory fixture"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session") 
def indian_cities_data(test_data_dir):
    """Load Indian cities test data"""
    cities_file = test_data_dir / "indian_cities.json"
    if not cities_file.exists():
        with open(cities_file, 'w') as f:
            json.dump(INDIAN_CITIES, f, indent=2)
    
    with open(cities_file) as f:
        return json.load(f)

@pytest.fixture(scope="session")
def performance_targets_data(test_data_dir):
    """Load performance targets test data"""
    targets_file = test_data_dir / "performance_targets.json"
    if not targets_file.exists():
        with open(targets_file, 'w') as f:
            json.dump(PERFORMANCE_TARGETS, f, indent=2)
    
    with open(targets_file) as f:
        return json.load(f)