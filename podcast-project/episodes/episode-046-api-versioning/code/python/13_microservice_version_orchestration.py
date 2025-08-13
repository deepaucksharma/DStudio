"""
Microservice Version Orchestration System
माइक्रोसर्विस वर्जन ऑर्केस्ट्रेशन सिस्टम

Real-world example: Flipkart's microservice version management
Handles rolling deployments and version compatibility across services
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import random

class ServiceStatus(Enum):
    """Service status types - सर्विस स्टेटस के प्रकार"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DEPLOYING = "deploying"
    ROLLING_BACK = "rolling_back"

class DeploymentStrategy(Enum):
    """Deployment strategy types - डिप्लॉयमेंट स्ट्रैटेजी के प्रकार"""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    A_B_TESTING = "a_b_testing"

@dataclass
class ServiceVersion:
    """Service version metadata - सर्विस वर्जन मेटाडेटा"""
    service_name: str
    version: str
    image_url: str
    config_hash: str
    dependencies: Dict[str, str]  # service_name -> min_version
    health_check_endpoint: str
    created_at: datetime

@dataclass
class ServiceInstance:
    """Service instance information - सर्विस इंस्टेंस जानकारी"""
    instance_id: str
    service_name: str
    version: str
    host: str
    port: int
    status: ServiceStatus
    last_health_check: datetime
    cpu_usage: float
    memory_usage: float

class FlipkartServiceOrchestrator:
    """
    Flipkart-style Microservice Version Orchestrator
    फ्लिपकार्ट-स्टाइल माइक्रोसर्विस वर्जन ऑर्केस्ट्रेटर
    
    Manages version deployments across microservices with dependency checking
    """
    
    def __init__(self):
        self.services: Dict[str, List[ServiceVersion]] = {}
        self.active_versions: Dict[str, str] = {}  # service -> current version
        self.instances: Dict[str, List[ServiceInstance]] = {}
        self.deployment_configs: Dict[str, Dict] = {}
        
    def register_service_version(self, version: ServiceVersion):
        """
        Register new service version
        नया सर्विस वर्जन रजिस्टर करें
        """
        if version.service_name not in self.services:
            self.services[version.service_name] = []
            
        self.services[version.service_name].append(version)
        print(f"📦 Registered {version.service_name} v{version.version}")
    
    def validate_dependencies(self, service_name: str, 
                            target_version: str) -> Dict[str, bool]:
        """
        Validate service dependencies
        सर्विस डिपेंडेंसीज की जांच करें
        """
        validation_results = {}
        
        # Find target version
        target_service_version = None
        for version in self.services.get(service_name, []):
            if version.version == target_version:
                target_service_version = version
                break
                
        if not target_service_version:
            return {"error": False, "message": "Version not found"}
        
        # Check each dependency
        for dep_service, min_version in target_service_version.dependencies.items():
            current_dep_version = self.active_versions.get(dep_service)
            
            if not current_dep_version:
                validation_results[dep_service] = False
                print(f"❌ Dependency {dep_service} not deployed")
            else:
                # Simple version comparison (in real world, use semantic versioning)
                is_compatible = self._compare_versions(current_dep_version, min_version) >= 0
                validation_results[dep_service] = is_compatible
                
                if not is_compatible:
                    print(f"❌ {dep_service} v{current_dep_version} < required v{min_version}")
                else:
                    print(f"✅ {dep_service} v{current_dep_version} compatible")
                    
        return validation_results
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare version strings - वर्जन स्ट्रिंग्स की तुलना करें"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        return 0
    
    async def rolling_deployment(self, service_name: str, 
                               target_version: str,
                               batch_size: int = 2) -> bool:
        """
        Perform rolling deployment
        रोलिंग डिप्लॉयमेंट करें
        """
        print(f"🚀 Starting rolling deployment: {service_name} v{target_version}")
        
        # Validate dependencies first
        dep_validation = self.validate_dependencies(service_name, target_version)
        if not all(dep_validation.values()):
            print("❌ Dependency validation failed")
            return False
        
        # Get current instances
        current_instances = self.instances.get(service_name, [])
        if not current_instances:
            print("❌ No current instances found")
            return False
        
        total_instances = len(current_instances)
        updated_instances = 0
        
        # Update in batches
        for i in range(0, total_instances, batch_size):
            batch_instances = current_instances[i:i + batch_size]
            
            print(f"📦 Updating batch {i//batch_size + 1}: {len(batch_instances)} instances")
            
            # Deploy new version to batch
            for instance in batch_instances:
                instance.status = ServiceStatus.DEPLOYING
                instance.version = target_version
                
                # Simulate deployment time
                await asyncio.sleep(2)
                
                # Health check
                if await self._health_check(instance):
                    instance.status = ServiceStatus.HEALTHY
                    updated_instances += 1
                    print(f"✅ {instance.instance_id} updated successfully")
                else:
                    instance.status = ServiceStatus.UNHEALTHY
                    print(f"❌ {instance.instance_id} health check failed")
                    # Rollback logic would go here
                    return False
            
            # Wait between batches
            await asyncio.sleep(1)
            
            # Check overall service health
            if not await self._check_service_health(service_name):
                print("❌ Service health degraded, stopping deployment")
                return False
        
        # Update active version
        self.active_versions[service_name] = target_version
        print(f"✅ Rolling deployment completed: {updated_instances}/{total_instances} instances")
        return True
    
    async def canary_deployment(self, service_name: str, 
                              target_version: str,
                              canary_percentage: float = 10.0) -> bool:
        """
        Perform canary deployment
        कैनरी डिप्लॉयमेंट करें
        """
        print(f"🐦 Starting canary deployment: {service_name} v{target_version} ({canary_percentage}%)")
        
        current_instances = self.instances.get(service_name, [])
        canary_count = max(1, int(len(current_instances) * canary_percentage / 100))
        
        print(f"📊 Deploying to {canary_count} canary instances")
        
        # Select canary instances
        canary_instances = current_instances[:canary_count]
        
        # Deploy to canary instances
        for instance in canary_instances:
            instance.status = ServiceStatus.DEPLOYING
            instance.version = target_version
            await asyncio.sleep(1)
            
            if await self._health_check(instance):
                instance.status = ServiceStatus.HEALTHY
                print(f"✅ Canary {instance.instance_id} healthy")
            else:
                instance.status = ServiceStatus.UNHEALTHY
                print(f"❌ Canary {instance.instance_id} failed")
                return False
        
        # Monitor canary for some time
        print("📈 Monitoring canary metrics...")
        await asyncio.sleep(5)
        
        # Simulate metrics analysis
        canary_success_rate = random.uniform(0.85, 0.99)
        print(f"📊 Canary success rate: {canary_success_rate:.2%}")
        
        if canary_success_rate > 0.95:
            print("✅ Canary metrics healthy, ready for full rollout")
            return True
        else:
            print("❌ Canary metrics degraded, rolling back")
            await self._rollback_canary(canary_instances)
            return False
    
    async def _health_check(self, instance: ServiceInstance) -> bool:
        """Perform health check - हेल्थ चेक करें"""
        # Simulate health check
        await asyncio.sleep(0.5)
        instance.last_health_check = datetime.now()
        
        # Simulate random failures
        return random.random() > 0.1
    
    async def _check_service_health(self, service_name: str) -> bool:
        """Check overall service health - सर्विस की समग्र हेल्थ चेक करें"""
        instances = self.instances.get(service_name, [])
        healthy_instances = sum(1 for i in instances if i.status == ServiceStatus.HEALTHY)
        
        health_percentage = healthy_instances / len(instances) if instances else 0
        return health_percentage >= 0.8  # 80% healthy threshold
    
    async def _rollback_canary(self, canary_instances: List[ServiceInstance]):
        """Rollback canary instances - कैनरी इंस्टेंसेज को रोलबैक करें"""
        print("🔄 Rolling back canary instances...")
        
        for instance in canary_instances:
            # Restore previous version (simplified)
            instance.status = ServiceStatus.ROLLING_BACK
            await asyncio.sleep(1)
            instance.status = ServiceStatus.HEALTHY
            print(f"🔄 {instance.instance_id} rolled back")
    
    def get_service_topology(self) -> Dict[str, List[str]]:
        """
        Get service dependency topology
        सर्विस डिपेंडेंसी टोपोलॉजी प्राप्त करें
        """
        topology = {}
        
        for service_name, versions in self.services.items():
            if versions:
                latest_version = versions[-1]  # Assume last is latest
                topology[service_name] = list(latest_version.dependencies.keys())
                
        return topology

async def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🏢 Flipkart Microservice Orchestration Demo")
    print("=" * 50)
    
    orchestrator = FlipkartServiceOrchestrator()
    
    # Register services with versions
    services_config = [
        {
            "name": "user-service",
            "version": "1.2.0",
            "dependencies": {}
        },
        {
            "name": "product-catalog",
            "version": "2.1.0",
            "dependencies": {"user-service": "1.0.0"}
        },
        {
            "name": "cart-service",
            "version": "1.5.0",
            "dependencies": {
                "user-service": "1.1.0",
                "product-catalog": "2.0.0"
            }
        },
        {
            "name": "payment-service",
            "version": "3.0.0",
            "dependencies": {
                "user-service": "1.2.0",
                "cart-service": "1.4.0"
            }
        }
    ]
    
    for service_config in services_config:
        version = ServiceVersion(
            service_name=service_config["name"],
            version=service_config["version"],
            image_url=f"flipkart/{service_config['name']}:{service_config['version']}",
            config_hash="abc123",
            dependencies=service_config["dependencies"],
            health_check_endpoint="/health",
            created_at=datetime.now()
        )
        orchestrator.register_service_version(version)
        orchestrator.active_versions[service_config["name"]] = service_config["version"]
        
        # Create mock instances
        instances = []
        for i in range(4):  # 4 instances per service
            instance = ServiceInstance(
                instance_id=f"{service_config['name']}-{i+1}",
                service_name=service_config["name"],
                version=service_config["version"],
                host=f"10.0.0.{i+1}",
                port=8080,
                status=ServiceStatus.HEALTHY,
                last_health_check=datetime.now(),
                cpu_usage=random.uniform(20, 80),
                memory_usage=random.uniform(30, 70)
            )
            instances.append(instance)
        orchestrator.instances[service_config["name"]] = instances
    
    print("\n📊 Service Topology:")
    topology = orchestrator.get_service_topology()
    for service, deps in topology.items():
        print(f"  {service} -> {deps if deps else ['No dependencies']}")
    
    # Demo rolling deployment
    print("\n🚀 Rolling Deployment Demo:")
    success = await orchestrator.rolling_deployment("cart-service", "1.6.0")
    print(f"Rolling deployment result: {'✅ Success' if success else '❌ Failed'}")
    
    # Demo canary deployment
    print("\n🐦 Canary Deployment Demo:")
    success = await orchestrator.canary_deployment("payment-service", "3.1.0", 20.0)
    print(f"Canary deployment result: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(main())