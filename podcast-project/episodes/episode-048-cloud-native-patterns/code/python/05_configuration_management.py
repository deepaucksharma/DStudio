#!/usr/bin/env python3
"""
Configuration Management System - IRCTC Style
Cloud Native Configuration Patterns for Microservices

IRCTC ke ticketing system ke liye configuration management
Environment-based configs, secrets management, dynamic updates
"""

import os
import json
import yaml
import base64
import hashlib
import time
import threading
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
from contextlib import contextmanager
import boto3
from botocore.exceptions import ClientError


class ConfigSourceType(Enum):
    """Configuration source types"""
    ENVIRONMENT = "environment"
    FILE = "file" 
    AWS_SECRETS = "aws_secrets"
    AWS_PARAMETER_STORE = "aws_parameter_store"
    KUBERNETES = "kubernetes"
    CONSUL = "consul"
    ETCD = "etcd"


@dataclass
class ConfigItem:
    """Individual configuration item"""
    key: str
    value: Any
    source: ConfigSourceType
    encrypted: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"
    metadata: Dict = field(default_factory=dict)
    
    def is_expired(self, ttl_seconds: int = None) -> bool:
        """Check if config item has expired"""
        if ttl_seconds is None:
            return False
        return (datetime.utcnow() - self.last_updated).total_seconds() > ttl_seconds


@dataclass
class ConfigSchema:
    """Configuration schema for validation"""
    required_keys: List[str]
    optional_keys: List[str] = field(default_factory=list)
    key_types: Dict[str, type] = field(default_factory=dict)
    key_validators: Dict[str, Callable] = field(default_factory=dict)


class IRCTCConfigManager:
    """
    IRCTC Configuration Management System
    Train booking system ke liye comprehensive config management
    """
    
    def __init__(self, 
                 service_name: str = "irctc-booking-service",
                 environment: str = "production",
                 config_sources: List[ConfigSourceType] = None):
        self.service_name = service_name
        self.environment = environment
        self.config_sources = config_sources or [
            ConfigSourceType.ENVIRONMENT,
            ConfigSourceType.FILE,
            ConfigSourceType.AWS_SECRETS
        ]
        
        # Configuration storage
        self.configs: Dict[str, ConfigItem] = {}
        self.schemas: Dict[str, ConfigSchema] = {}
        self.watchers: Dict[str, List[Callable]] = {}
        self.cache_ttl = 300  # 5 minutes default TTL
        
        # Thread safety
        self.lock = threading.RLock()
        
        # AWS clients (initialized lazily)
        self._secrets_client = None
        self._ssm_client = None
        
        # Setup logging
        self.setup_logging()
        
        # Load initial configurations
        self.load_default_config()
        
        self.logger.info(f"🚂 IRCTC Config Manager initialized for {service_name}")
        self.logger.info(f"🌍 Environment: {environment}")
        self.logger.info(f"📋 Sources: {[s.value for s in self.config_sources]}")
    
    def setup_logging(self):
        """Setup configuration logging"""
        self.logger = logging.getLogger(f"irctc-config-{self.service_name}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.service_name}] %(asctime)s %(levelname)s [%(name)s]: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    @property
    def secrets_client(self):
        """Lazy initialization of AWS Secrets Manager client"""
        if self._secrets_client is None:
            self._secrets_client = boto3.client('secretsmanager', region_name='ap-south-1')
        return self._secrets_client
    
    @property
    def ssm_client(self):
        """Lazy initialization of AWS Systems Manager client"""
        if self._ssm_client is None:
            self._ssm_client = boto3.client('ssm', region_name='ap-south-1')
        return self._ssm_client
    
    def load_default_config(self):
        """Load default IRCTC configurations"""
        default_configs = {
            # Database configurations
            'database.host': 'irctc-db-cluster.ap-south-1.rds.amazonaws.com',
            'database.port': 5432,
            'database.name': f'irctc_{self.environment}',
            'database.pool_size': 20,
            'database.connection_timeout': 30,
            
            # Redis configurations
            'redis.host': 'irctc-cache-cluster.ap-south-1.cache.amazonaws.com',
            'redis.port': 6379,
            'redis.ttl': 3600,
            'redis.max_connections': 100,
            
            # IRCTC specific configurations
            'irctc.booking_window_minutes': 120,
            'irctc.max_tickets_per_booking': 6,
            'irctc.tatkal_booking_time': '10:00',
            'irctc.premium_tatkal_booking_time': '10:00',
            'irctc.advance_reservation_period_days': 120,
            'irctc.cancellation_charges_percent': 5.0,
            
            # Railway zones configuration
            'irctc.railway_zones': [
                'Northern Railway', 'Southern Railway', 'Eastern Railway',
                'Western Railway', 'Central Railway', 'South Central Railway',
                'South Eastern Railway', 'North Eastern Railway',
                'Northeast Frontier Railway', 'East Central Railway',
                'East Coast Railway', 'North Central Railway',
                'North Western Railway', 'South East Central Railway',
                'South Western Railway', 'West Central Railway'
            ],
            
            # Payment configurations
            'payment.gateway_timeout': 30,
            'payment.retry_attempts': 3,
            'payment.supported_methods': ['upi', 'netbanking', 'card', 'wallet'],
            
            # Monitoring and observability
            'monitoring.metrics_endpoint': '/metrics',
            'monitoring.health_endpoint': '/health',
            'logging.level': 'INFO',
            'logging.format': 'json'
        }
        
        # Load from environment variables first
        for key, default_value in default_configs.items():
            env_key = key.replace('.', '_').upper()
            env_value = os.environ.get(env_key)
            
            if env_value is not None:
                # Try to parse the environment value
                try:
                    if isinstance(default_value, bool):
                        value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(default_value, int):
                        value = int(env_value)
                    elif isinstance(default_value, float):
                        value = float(env_value)
                    elif isinstance(default_value, list):
                        value = json.loads(env_value) if env_value.startswith('[') else env_value.split(',')
                    else:
                        value = env_value
                except (ValueError, json.JSONDecodeError):
                    value = env_value
                
                self.set_config(key, value, ConfigSourceType.ENVIRONMENT)
            else:
                self.set_config(key, default_value, ConfigSourceType.FILE)
    
    def set_config(self, 
                   key: str, 
                   value: Any, 
                   source: ConfigSourceType = ConfigSourceType.FILE,
                   encrypted: bool = False,
                   metadata: Dict = None) -> bool:
        """Set configuration value"""
        with self.lock:
            try:
                config_item = ConfigItem(
                    key=key,
                    value=value,
                    source=source,
                    encrypted=encrypted,
                    last_updated=datetime.utcnow(),
                    version=str(int(time.time())),
                    metadata=metadata or {}
                )
                
                old_value = self.configs.get(key)
                self.configs[key] = config_item
                
                # Notify watchers if value changed
                if old_value is None or old_value.value != value:
                    self._notify_watchers(key, value, old_value.value if old_value else None)
                
                self.logger.debug(f"🔧 Config set: {key} = {value} (source: {source.value})")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Failed to set config {key}: {e}")
                return False
    
    def get_config(self, 
                   key: str, 
                   default: Any = None,
                   required: bool = False) -> Any:
        """Get configuration value"""
        with self.lock:
            config_item = self.configs.get(key)
            
            if config_item is None:
                if required:
                    raise ValueError(f"Required configuration key '{key}' not found")
                return default
            
            # Check if config has expired
            if config_item.is_expired(self.cache_ttl):
                self.logger.warning(f"⏰ Config {key} has expired, attempting refresh...")
                self._refresh_config(key)
                config_item = self.configs.get(key)  # Get refreshed config
            
            return config_item.value if config_item else default
    
    def get_config_info(self, key: str) -> Optional[Dict]:
        """Get detailed configuration information"""
        with self.lock:
            config_item = self.configs.get(key)
            if config_item is None:
                return None
            
            return {
                'key': config_item.key,
                'value': '***' if config_item.encrypted else config_item.value,
                'source': config_item.source.value,
                'encrypted': config_item.encrypted,
                'last_updated': config_item.last_updated.isoformat(),
                'version': config_item.version,
                'metadata': config_item.metadata,
                'expired': config_item.is_expired(self.cache_ttl)
            }
    
    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load configurations from file (JSON/YAML)"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"❌ Config file not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ['.yml', '.yaml']:
                    configs = yaml.safe_load(f)
                else:
                    configs = json.load(f)
            
            # Flatten nested configurations
            flattened = self._flatten_dict(configs)
            
            count = 0
            for key, value in flattened.items():
                if self.set_config(key, value, ConfigSourceType.FILE):
                    count += 1
            
            self.logger.info(f"📄 Loaded {count} configurations from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load config from file {file_path}: {e}")
            return False
    
    def load_from_aws_secrets(self, secret_names: List[str]) -> bool:
        """Load configurations from AWS Secrets Manager"""
        if ConfigSourceType.AWS_SECRETS not in self.config_sources:
            return False
        
        try:
            count = 0
            for secret_name in secret_names:
                try:
                    response = self.secrets_client.get_secret_value(SecretId=secret_name)
                    secret_string = response['SecretString']
                    
                    # Parse secret (assume JSON format)
                    secrets = json.loads(secret_string)
                    
                    for key, value in secrets.items():
                        config_key = f"secrets.{secret_name}.{key}"
                        if self.set_config(config_key, value, ConfigSourceType.AWS_SECRETS, encrypted=True):
                            count += 1
                
                except ClientError as e:
                    self.logger.error(f"❌ Failed to load secret {secret_name}: {e}")
                    continue
            
            self.logger.info(f"🔐 Loaded {count} configurations from AWS Secrets Manager")
            return count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load from AWS Secrets: {e}")
            return False
    
    def load_from_parameter_store(self, parameter_prefix: str = None) -> bool:
        """Load configurations from AWS Parameter Store"""
        if ConfigSourceType.AWS_PARAMETER_STORE not in self.config_sources:
            return False
        
        try:
            prefix = parameter_prefix or f"/irctc/{self.environment}/"
            
            paginator = self.ssm_client.get_paginator('get_parameters_by_path')
            page_iterator = paginator.paginate(
                Path=prefix,
                Recursive=True,
                WithDecryption=True
            )
            
            count = 0
            for page in page_iterator:
                for parameter in page['Parameters']:
                    # Remove prefix from parameter name
                    key = parameter['Name'][len(prefix):].replace('/', '.')
                    value = parameter['Value']
                    
                    # Detect if parameter is encrypted
                    encrypted = parameter['Type'] == 'SecureString'
                    
                    if self.set_config(key, value, ConfigSourceType.AWS_PARAMETER_STORE, encrypted=encrypted):
                        count += 1
            
            self.logger.info(f"📊 Loaded {count} configurations from AWS Parameter Store")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load from Parameter Store: {e}")
            return False
    
    def register_schema(self, schema_name: str, schema: ConfigSchema):
        """Register configuration schema for validation"""
        self.schemas[schema_name] = schema
        self.logger.info(f"📋 Registered schema: {schema_name}")
    
    def validate_config(self, schema_name: str) -> Dict[str, List[str]]:
        """Validate configuration against schema"""
        schema = self.schemas.get(schema_name)
        if not schema:
            return {'errors': [f'Schema {schema_name} not found']}
        
        errors = []
        warnings = []
        
        # Check required keys
        for required_key in schema.required_keys:
            if required_key not in self.configs:
                errors.append(f'Required key missing: {required_key}')
        
        # Check key types and run validators
        for key, config_item in self.configs.items():
            # Type checking
            expected_type = schema.key_types.get(key)
            if expected_type and not isinstance(config_item.value, expected_type):
                errors.append(f'Type mismatch for {key}: expected {expected_type.__name__}, got {type(config_item.value).__name__}')
            
            # Custom validation
            validator = schema.key_validators.get(key)
            if validator:
                try:
                    if not validator(config_item.value):
                        errors.append(f'Validation failed for {key}')
                except Exception as e:
                    errors.append(f'Validator error for {key}: {str(e)}')
        
        return {'errors': errors, 'warnings': warnings}
    
    def watch_config(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Watch for configuration changes"""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
        self.logger.info(f"👁️  Watching config key: {key}")
    
    def _notify_watchers(self, key: str, new_value: Any, old_value: Any):
        """Notify all watchers of configuration changes"""
        watchers = self.watchers.get(key, [])
        for callback in watchers:
            try:
                callback(key, new_value, old_value)
            except Exception as e:
                self.logger.error(f"❌ Watcher callback error for {key}: {e}")
    
    def _refresh_config(self, key: str):
        """Refresh a specific configuration from its source"""
        config_item = self.configs.get(key)
        if not config_item:
            return
        
        # Attempt to refresh based on source type
        if config_item.source == ConfigSourceType.AWS_SECRETS:
            # Refresh from secrets manager
            # This is simplified - in real implementation, track which secret contains which key
            pass
        elif config_item.source == ConfigSourceType.AWS_PARAMETER_STORE:
            # Refresh from parameter store
            try:
                parameter_name = f"/irctc/{self.environment}/{key.replace('.', '/')}"
                response = self.ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
                new_value = response['Parameter']['Value']
                
                if new_value != config_item.value:
                    self.set_config(key, new_value, ConfigSourceType.AWS_PARAMETER_STORE, config_item.encrypted)
                    self.logger.info(f"🔄 Refreshed config: {key}")
            except ClientError:
                self.logger.warning(f"⚠️  Failed to refresh config: {key}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def get_all_configs(self, include_encrypted: bool = False) -> Dict[str, Any]:
        """Get all configurations"""
        with self.lock:
            result = {}
            for key, config_item in self.configs.items():
                if config_item.encrypted and not include_encrypted:
                    result[key] = '***'
                else:
                    result[key] = config_item.value
            return result
    
    def export_config(self, file_path: Union[str, Path], format: str = 'json') -> bool:
        """Export configurations to file"""
        try:
            configs = self.get_all_configs(include_encrypted=False)
            file_path = Path(file_path)
            
            with open(file_path, 'w') as f:
                if format.lower() == 'yaml':
                    yaml.dump(configs, f, default_flow_style=False)
                else:
                    json.dump(configs, f, indent=2)
            
            self.logger.info(f"📤 Exported configurations to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export config: {e}")
            return False
    
    @contextmanager
    def config_context(self, temporary_configs: Dict[str, Any]):
        """Context manager for temporary configuration overrides"""
        original_configs = {}
        
        # Save original values and apply temporary ones
        for key, temp_value in temporary_configs.items():
            original_configs[key] = self.get_config(key)
            self.set_config(key, temp_value, ConfigSourceType.ENVIRONMENT)
        
        try:
            yield self
        finally:
            # Restore original values
            for key, original_value in original_configs.items():
                if original_value is not None:
                    self.set_config(key, original_value, ConfigSourceType.ENVIRONMENT)
                else:
                    # Remove the key if it didn't exist originally
                    if key in self.configs:
                        del self.configs[key]
    
    def health_check(self) -> Dict:
        """Health check for configuration system"""
        try:
            total_configs = len(self.configs)
            expired_configs = sum(1 for config in self.configs.values() 
                                if config.is_expired(self.cache_ttl))
            
            source_distribution = {}
            for config in self.configs.values():
                source = config.source.value
                source_distribution[source] = source_distribution.get(source, 0) + 1
            
            health_status = 'healthy'
            if expired_configs > total_configs * 0.5:
                health_status = 'degraded'
            
            return {
                'status': health_status,
                'total_configs': total_configs,
                'expired_configs': expired_configs,
                'source_distribution': source_distribution,
                'schemas_registered': len(self.schemas),
                'watchers_active': sum(len(watchers) for watchers in self.watchers.values()),
                'service_name': self.service_name,
                'environment': self.environment,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# IRCTC Configuration Schemas
def create_irctc_schemas() -> Dict[str, ConfigSchema]:
    """Create configuration schemas for IRCTC services"""
    
    def positive_int(value):
        return isinstance(value, int) and value > 0
    
    def positive_float(value):
        return isinstance(value, (int, float)) and value > 0
    
    def valid_port(value):
        return isinstance(value, int) and 1 <= value <= 65535
    
    def valid_percentage(value):
        return isinstance(value, (int, float)) and 0 <= value <= 100
    
    return {
        'database': ConfigSchema(
            required_keys=['database.host', 'database.port', 'database.name'],
            optional_keys=['database.pool_size', 'database.connection_timeout'],
            key_types={
                'database.host': str,
                'database.port': int,
                'database.name': str,
                'database.pool_size': int,
                'database.connection_timeout': int
            },
            key_validators={
                'database.port': valid_port,
                'database.pool_size': positive_int,
                'database.connection_timeout': positive_int
            }
        ),
        
        'irctc_business': ConfigSchema(
            required_keys=[
                'irctc.booking_window_minutes',
                'irctc.max_tickets_per_booking',
                'irctc.advance_reservation_period_days'
            ],
            optional_keys=[
                'irctc.tatkal_booking_time',
                'irctc.cancellation_charges_percent'
            ],
            key_types={
                'irctc.booking_window_minutes': int,
                'irctc.max_tickets_per_booking': int,
                'irctc.advance_reservation_period_days': int,
                'irctc.cancellation_charges_percent': float
            },
            key_validators={
                'irctc.booking_window_minutes': positive_int,
                'irctc.max_tickets_per_booking': lambda x: isinstance(x, int) and 1 <= x <= 6,
                'irctc.advance_reservation_period_days': positive_int,
                'irctc.cancellation_charges_percent': valid_percentage
            }
        )
    }


# Configuration change handlers
def config_change_handler(key: str, new_value: Any, old_value: Any):
    """Handle configuration changes"""
    print(f"🔄 Config changed: {key}")
    print(f"   Old value: {old_value}")
    print(f"   New value: {new_value}")
    
    # Handle specific configuration changes
    if key.startswith('database.'):
        print("   🔄 Database configuration changed - consider connection pool restart")
    elif key.startswith('irctc.'):
        print("   🚂 IRCTC business rule changed - updating runtime parameters")


if __name__ == '__main__':
    # Demo IRCTC Configuration Management
    print("🚂 IRCTC Configuration Management Demo")
    print("=" * 50)
    
    # Initialize configuration manager
    config_manager = IRCTCConfigManager("irctc-booking-service", "development")
    
    # Register schemas
    schemas = create_irctc_schemas()
    for schema_name, schema in schemas.items():
        config_manager.register_schema(schema_name, schema)
    
    # Watch for configuration changes
    config_manager.watch_config('irctc.booking_window_minutes', config_change_handler)
    config_manager.watch_config('database.pool_size', config_change_handler)
    
    # Test configuration operations
    print("\n📋 Testing Configuration Operations:")
    
    # Get configurations
    print(f"Database host: {config_manager.get_config('database.host')}")
    print(f"Booking window: {config_manager.get_config('irctc.booking_window_minutes')} minutes")
    print(f"Max tickets per booking: {config_manager.get_config('irctc.max_tickets_per_booking')}")
    
    # Update configuration (should trigger watcher)
    print(f"\n🔄 Updating booking window from 120 to 90 minutes...")
    config_manager.set_config('irctc.booking_window_minutes', 90)
    
    # Validate configurations
    print(f"\n✅ Validating configurations:")
    for schema_name in schemas.keys():
        validation_result = config_manager.validate_config(schema_name)
        if validation_result['errors']:
            print(f"   ❌ {schema_name}: {validation_result['errors']}")
        else:
            print(f"   ✅ {schema_name}: Valid")
    
    # Test temporary configuration override
    print(f"\n🔀 Testing temporary configuration override:")
    print(f"Current max tickets: {config_manager.get_config('irctc.max_tickets_per_booking')}")
    
    with config_manager.config_context({'irctc.max_tickets_per_booking': 8}):
        print(f"Inside context: {config_manager.get_config('irctc.max_tickets_per_booking')}")
    
    print(f"After context: {config_manager.get_config('irctc.max_tickets_per_booking')}")
    
    # Health check
    print(f"\n🏥 Configuration Health Check:")
    health = config_manager.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Total configs: {health['total_configs']}")
    print(f"   Source distribution: {health['source_distribution']}")
    
    # Export configuration
    print(f"\n📤 Exporting configuration...")
    config_manager.export_config('/tmp/irctc_config_export.json')
    
    print("\n" + "=" * 50)
    print("🎯 IRCTC Configuration Management Demo Complete!")
    print("Key features demonstrated:")
    print("1. Multi-source configuration loading")
    print("2. Schema validation")
    print("3. Configuration watching and change handling")
    print("4. Temporary configuration overrides")
    print("5. Health monitoring and export capabilities")