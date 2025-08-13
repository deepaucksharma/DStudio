#!/usr/bin/env python3
"""
Docker Compose Stack Management with Python
Episode 18: Infrastructure as Code

Python script to manage complex Docker Compose stacks.
Zomato-style food delivery application with microservices.

Cost Estimate: ₹2,000-5,000 per month for cloud hosting
"""

import os
import yaml
import subprocess
import time
import requests
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerComposeManager:
    """Docker Compose stack management for Zomato-style application"""
    
    def __init__(self, project_name: str = "zomato-app", environment: str = "dev"):
        self.project_name = project_name
        self.environment = environment
        self.compose_dir = Path(f"./docker-compose-{environment}")
        self.compose_file = self.compose_dir / "docker-compose.yml"
        self.env_file = self.compose_dir / ".env"
        
        # Create directory if not exists
        self.compose_dir.mkdir(exist_ok=True)
        
        logger.info(f"Docker Compose Manager initialized for {project_name}-{environment}")
    
    def generate_compose_file(self) -> Dict:
        """Generate comprehensive Docker Compose configuration"""
        
        compose_config = {
            'version': '3.8',
            'services': {
                # Database Services
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'container_name': f'{self.project_name}-postgres-{self.environment}',
                    'environment': {
                        'POSTGRES_DB': 'zomato_db',
                        'POSTGRES_USER': 'zomato_user',
                        'POSTGRES_PASSWORD': '${POSTGRES_PASSWORD}',
                        'POSTGRES_INITDB_ARGS': '--encoding=UTF-8 --lc-collate=C --lc-ctype=C'
                    },
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './init-db:/docker-entrypoint-initdb.d'
                    ],
                    'ports': ['5432:5432'] if self.environment == 'dev' else [],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'pg_isready -U zomato_user -d zomato_db'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 5
                    }
                },
                
                'redis': {
                    'image': 'redis:7-alpine',
                    'container_name': f'{self.project_name}-redis-{self.environment}',
                    'command': 'redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}',
                    'volumes': ['redis_data:/data'],
                    'ports': ['6379:6379'] if self.environment == 'dev' else [],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD', 'redis-cli', '--raw', 'incr', 'ping'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 3
                    }
                },
                
                'mongodb': {
                    'image': 'mongo:6.0',
                    'container_name': f'{self.project_name}-mongo-{self.environment}',
                    'environment': {
                        'MONGO_INITDB_ROOT_USERNAME': 'mongo_admin',
                        'MONGO_INITDB_ROOT_PASSWORD': '${MONGO_PASSWORD}',
                        'MONGO_INITDB_DATABASE': 'zomato_orders'
                    },
                    'volumes': [
                        'mongo_data:/data/db',
                        './mongo-init:/docker-entrypoint-initdb.d'
                    ],
                    'ports': ['27017:27017'] if self.environment == 'dev' else [],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                # Message Queue
                'rabbitmq': {
                    'image': 'rabbitmq:3.12-management-alpine',
                    'container_name': f'{self.project_name}-rabbitmq-{self.environment}',
                    'environment': {
                        'RABBITMQ_DEFAULT_USER': 'zomato_mq',
                        'RABBITMQ_DEFAULT_PASS': '${RABBITMQ_PASSWORD}',
                        'RABBITMQ_DEFAULT_VHOST': 'zomato'
                    },
                    'volumes': ['rabbitmq_data:/var/lib/rabbitmq'],
                    'ports': [
                        '5672:5672',  # AMQP port
                        '15672:15672' if self.environment == 'dev' else '15672'  # Management UI
                    ],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD', 'rabbitmq-diagnostics', '-q', 'ping'],
                        'interval': '30s',
                        'timeout': '30s',
                        'retries': 3
                    }
                },
                
                # Microservices
                'user-service': {
                    'build': {
                        'context': './services/user-service',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f'{self.project_name}-user-service-{self.environment}',
                    'environment': {
                        'NODE_ENV': self.environment,
                        'DB_HOST': 'postgres',
                        'DB_PORT': '5432',
                        'DB_NAME': 'zomato_db',
                        'DB_USER': 'zomato_user',
                        'DB_PASSWORD': '${POSTGRES_PASSWORD}',
                        'REDIS_HOST': 'redis',
                        'REDIS_PORT': '6379',
                        'REDIS_PASSWORD': '${REDIS_PASSWORD}',
                        'JWT_SECRET': '${JWT_SECRET}',
                        'PORT': '3001'
                    },
                    'ports': ['3001:3001'] if self.environment == 'dev' else [],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped',
                    'deploy': {
                        'replicas': 2 if self.environment == 'prod' else 1,
                        'resources': {
                            'limits': {
                                'cpus': '0.50',
                                'memory': '512M'
                            },
                            'reservations': {
                                'cpus': '0.25',
                                'memory': '256M'
                            }
                        }
                    }
                },
                
                'restaurant-service': {
                    'build': {
                        'context': './services/restaurant-service',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f'{self.project_name}-restaurant-service-{self.environment}',
                    'environment': {
                        'NODE_ENV': self.environment,
                        'DB_HOST': 'postgres',
                        'DB_PORT': '5432',
                        'DB_NAME': 'zomato_db',
                        'DB_USER': 'zomato_user',
                        'DB_PASSWORD': '${POSTGRES_PASSWORD}',
                        'REDIS_HOST': 'redis',
                        'REDIS_PASSWORD': '${REDIS_PASSWORD}',
                        'ELASTICSEARCH_URL': 'http://elasticsearch:9200',
                        'PORT': '3002'
                    },
                    'ports': ['3002:3002'] if self.environment == 'dev' else [],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'},
                        'elasticsearch': {'condition': 'service_healthy'}
                    },
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                'order-service': {
                    'build': {
                        'context': './services/order-service',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f'{self.project_name}-order-service-{self.environment}',
                    'environment': {
                        'NODE_ENV': self.environment,
                        'MONGO_URL': 'mongodb://mongo_admin:${MONGO_PASSWORD}@mongodb:27017/zomato_orders?authSource=admin',
                        'RABBITMQ_URL': 'amqp://zomato_mq:${RABBITMQ_PASSWORD}@rabbitmq:5672/zomato',
                        'REDIS_HOST': 'redis',
                        'REDIS_PASSWORD': '${REDIS_PASSWORD}',
                        'PAYMENT_SERVICE_URL': 'http://payment-service:3004',
                        'PORT': '3003'
                    },
                    'ports': ['3003:3003'] if self.environment == 'dev' else [],
                    'depends_on': {
                        'mongodb': {'condition': 'service_started'},
                        'rabbitmq': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                'payment-service': {
                    'build': {
                        'context': './services/payment-service',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f'{self.project_name}-payment-service-{self.environment}',
                    'environment': {
                        'NODE_ENV': self.environment,
                        'DB_HOST': 'postgres',
                        'DB_NAME': 'zomato_db',
                        'DB_USER': 'zomato_user',
                        'DB_PASSWORD': '${POSTGRES_PASSWORD}',
                        'RAZORPAY_KEY_ID': '${RAZORPAY_KEY_ID}',
                        'RAZORPAY_KEY_SECRET': '${RAZORPAY_KEY_SECRET}',
                        'UPI_GATEWAY_URL': '${UPI_GATEWAY_URL}',
                        'PORT': '3004'
                    },
                    'ports': ['3004:3004'] if self.environment == 'dev' else [],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'}
                    },
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                'delivery-service': {
                    'build': {
                        'context': './services/delivery-service',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f'{self.project_name}-delivery-service-{self.environment}',
                    'environment': {
                        'NODE_ENV': self.environment,
                        'MONGO_URL': 'mongodb://mongo_admin:${MONGO_PASSWORD}@mongodb:27017/zomato_delivery?authSource=admin',
                        'RABBITMQ_URL': 'amqp://zomato_mq:${RABBITMQ_PASSWORD}@rabbitmq:5672/zomato',
                        'GOOGLE_MAPS_API_KEY': '${GOOGLE_MAPS_API_KEY}',
                        'TWILIO_ACCOUNT_SID': '${TWILIO_ACCOUNT_SID}',
                        'TWILIO_AUTH_TOKEN': '${TWILIO_AUTH_TOKEN}',
                        'PORT': '3005'
                    },
                    'ports': ['3005:3005'] if self.environment == 'dev' else [],
                    'depends_on': {
                        'mongodb': {'condition': 'service_started'},
                        'rabbitmq': {'condition': 'service_healthy'}
                    },
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                # Search Engine
                'elasticsearch': {
                    'image': 'docker.elastic.co/elasticsearch/elasticsearch:8.10.0',
                    'container_name': f'{self.project_name}-elasticsearch-{self.environment}',
                    'environment': {
                        'discovery.type': 'single-node',
                        'ES_JAVA_OPTS': '-Xms512m -Xmx512m',
                        'xpack.security.enabled': 'false',
                        'xpack.security.enrollment.enabled': 'false'
                    },
                    'volumes': ['elasticsearch_data:/usr/share/elasticsearch/data'],
                    'ports': ['9200:9200'] if self.environment == 'dev' else [],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'curl -f http://localhost:9200/_cluster/health || exit 1'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 5
                    }
                },
                
                # API Gateway
                'nginx-gateway': {
                    'image': 'nginx:alpine',
                    'container_name': f'{self.project_name}-gateway-{self.environment}',
                    'volumes': [
                        './nginx/nginx.conf:/etc/nginx/nginx.conf',
                        './nginx/conf.d:/etc/nginx/conf.d',
                        './ssl:/etc/nginx/ssl'
                    ],
                    'ports': [
                        '80:80',
                        '443:443'
                    ],
                    'depends_on': [
                        'user-service',
                        'restaurant-service', 
                        'order-service',
                        'payment-service',
                        'delivery-service'
                    ],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                # Monitoring
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': f'{self.project_name}-prometheus-{self.environment}',
                    'volumes': [
                        './monitoring/prometheus.yml:/etc/prometheus/prometheus.yml',
                        'prometheus_data:/prometheus'
                    ],
                    'ports': ['9090:9090'] if self.environment == 'dev' else [],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                },
                
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': f'{self.project_name}-grafana-{self.environment}',
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': '${GRAFANA_PASSWORD}'
                    },
                    'volumes': [
                        'grafana_data:/var/lib/grafana',
                        './monitoring/grafana/dashboards:/var/lib/grafana/dashboards',
                        './monitoring/grafana/provisioning:/etc/grafana/provisioning'
                    ],
                    'ports': ['3000:3000'] if self.environment == 'dev' else [],
                    'depends_on': ['prometheus'],
                    'networks': ['zomato-network'],
                    'restart': 'unless-stopped'
                }
            },
            
            'volumes': {
                'postgres_data': {'driver': 'local'},
                'redis_data': {'driver': 'local'},
                'mongo_data': {'driver': 'local'},
                'rabbitmq_data': {'driver': 'local'},
                'elasticsearch_data': {'driver': 'local'},
                'prometheus_data': {'driver': 'local'},
                'grafana_data': {'driver': 'local'}
            },
            
            'networks': {
                'zomato-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [
                            {'subnet': '172.20.0.0/16'}
                        ]
                    }
                }
            }
        }
        
        return compose_config
    
    def generate_env_file(self) -> Dict[str, str]:
        """Generate environment variables file"""
        
        env_vars = {
            # Database passwords
            'POSTGRES_PASSWORD': 'zomato_db_password_2024',
            'REDIS_PASSWORD': 'zomato_redis_password_2024',
            'MONGO_PASSWORD': 'zomato_mongo_password_2024',
            'RABBITMQ_PASSWORD': 'zomato_mq_password_2024',
            
            # JWT Secret
            'JWT_SECRET': 'zomato_jwt_super_secret_key_2024_mumbai',
            
            # Third-party API keys (examples - replace with real keys)
            'RAZORPAY_KEY_ID': 'rzp_test_xxxxxxxxxx',
            'RAZORPAY_KEY_SECRET': 'your_razorpay_secret_key',
            'UPI_GATEWAY_URL': 'https://api.upi-gateway.com/v1',
            'GOOGLE_MAPS_API_KEY': 'your_google_maps_api_key',
            
            # SMS/Notification services
            'TWILIO_ACCOUNT_SID': 'your_twilio_account_sid',
            'TWILIO_AUTH_TOKEN': 'your_twilio_auth_token',
            
            # Monitoring
            'GRAFANA_PASSWORD': 'zomato_grafana_admin_2024',
            
            # Environment specific
            'ENVIRONMENT': self.environment,
            'PROJECT_NAME': self.project_name,
            'LOG_LEVEL': 'debug' if self.environment == 'dev' else 'info'
        }
        
        return env_vars
    
    def write_compose_file(self):
        """Write Docker Compose configuration to file"""
        
        compose_config = self.generate_compose_file()
        
        with open(self.compose_file, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Docker Compose file written to {self.compose_file}")
    
    def write_env_file(self):
        """Write environment variables to .env file"""
        
        env_vars = self.generate_env_file()
        
        with open(self.env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"Environment file written to {self.env_file}")
    
    def create_nginx_config(self):
        """Create Nginx configuration for API Gateway"""
        
        nginx_dir = self.compose_dir / "nginx" / "conf.d"
        nginx_dir.mkdir(parents=True, exist_ok=True)
        
        nginx_config = """
upstream user_service {
    server user-service:3001;
}

upstream restaurant_service {
    server restaurant-service:3002;
}

upstream order_service {
    server order-service:3003;
}

upstream payment_service {
    server payment-service:3004;
}

upstream delivery_service {
    server delivery-service:3005;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    server_name zomato-api.local;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Enable gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # User service routes
    location /api/users {
        limit_req zone=api_limit burst=5 nodelay;
        proxy_pass http://user_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Restaurant service routes
    location /api/restaurants {
        limit_req zone=api_limit burst=10 nodelay;
        proxy_pass http://restaurant_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Order service routes
    location /api/orders {
        limit_req zone=api_limit burst=5 nodelay;
        proxy_pass http://order_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Payment service routes
    location /api/payments {
        limit_req zone=api_limit burst=3 nodelay;
        proxy_pass http://payment_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Delivery service routes
    location /api/delivery {
        limit_req zone=api_limit burst=5 nodelay;
        proxy_pass http://delivery_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Serve static files
    location /static/ {
        alias /var/www/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }
}
"""
        
        with open(nginx_dir / "default.conf", 'w') as f:
            f.write(nginx_config)
        
        logger.info("Nginx configuration created")
    
    def create_monitoring_config(self):
        """Create Prometheus monitoring configuration"""
        
        monitoring_dir = self.compose_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {'targets': ['localhost:9090']}
                    ]
                },
                {
                    'job_name': 'user-service',
                    'static_configs': [
                        {'targets': ['user-service:3001']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'restaurant-service',
                    'static_configs': [
                        {'targets': ['restaurant-service:3002']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'order-service',
                    'static_configs': [
                        {'targets': ['order-service:3003']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'payment-service',
                    'static_configs': [
                        {'targets': ['payment-service:3004']}
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'delivery-service',
                    'static_configs': [
                        {'targets': ['delivery-service:3005']}
                    ],
                    'metrics_path': '/metrics'
                }
            ]
        }
        
        with open(monitoring_dir / "prometheus.yml", 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        logger.info("Prometheus configuration created")
    
    def deploy_stack(self):
        """Deploy the complete Docker Compose stack"""
        
        logger.info(f"Deploying {self.project_name} stack in {self.environment} environment")
        
        try:
            # Change to compose directory
            os.chdir(self.compose_dir)
            
            # Pull images first
            subprocess.run([
                'docker-compose', 'pull'
            ], check=True)
            
            # Build and start services
            subprocess.run([
                'docker-compose', 'up', '-d', '--build'
            ], check=True)
            
            logger.info("Stack deployed successfully!")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to deploy stack: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check health of all services"""
        
        services_to_check = [
            ('postgres', 'http://localhost:5432'),
            ('redis', 'http://localhost:6379'),
            ('elasticsearch', 'http://localhost:9200/_cluster/health'),
            ('user-service', 'http://localhost:3001/health'),
            ('restaurant-service', 'http://localhost:3002/health'),
            ('order-service', 'http://localhost:3003/health'),
            ('payment-service', 'http://localhost:3004/health'),
            ('delivery-service', 'http://localhost:3005/health'),
            ('nginx-gateway', 'http://localhost:80/health')
        ]
        
        all_healthy = True
        
        for service_name, health_url in services_to_check:
            try:
                if service_name in ['postgres', 'redis']:
                    # Check using docker command for database services
                    result = subprocess.run([
                        'docker', 'exec', f'{self.project_name}-{service_name}-{self.environment}',
                        'sh', '-c', 'exit 0'
                    ], capture_output=True)
                    
                    if result.returncode == 0:
                        logger.info(f"✅ {service_name} is healthy")
                    else:
                        logger.warning(f"❌ {service_name} is not healthy")
                        all_healthy = False
                else:
                    # HTTP health check
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ {service_name} is healthy")
                    else:
                        logger.warning(f"❌ {service_name} returned status {response.status_code}")
                        all_healthy = False
                        
            except Exception as e:
                logger.warning(f"❌ {service_name} health check failed: {e}")
                all_healthy = False
        
        return all_healthy
    
    def scale_services(self, service_replicas: Dict[str, int]):
        """Scale specific services"""
        
        for service, replicas in service_replicas.items():
            try:
                subprocess.run([
                    'docker-compose', 'up', '-d', '--scale', f'{service}={replicas}', service
                ], check=True, cwd=self.compose_dir)
                
                logger.info(f"Scaled {service} to {replicas} replicas")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to scale {service}: {e}")
    
    def get_logs(self, service: Optional[str] = None, tail: int = 100):
        """Get logs from services"""
        
        cmd = ['docker-compose', 'logs', '--tail', str(tail)]
        
        if service:
            cmd.append(service)
        
        try:
            result = subprocess.run(cmd, cwd=self.compose_dir, capture_output=True, text=True)
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get logs: {e}")
            return None
    
    def stop_stack(self):
        """Stop the entire stack"""
        
        try:
            subprocess.run([
                'docker-compose', 'down'
            ], check=True, cwd=self.compose_dir)
            
            logger.info("Stack stopped successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop stack: {e}")
    
    def cleanup_stack(self, remove_volumes: bool = False):
        """Clean up the stack and optionally remove volumes"""
        
        try:
            cmd = ['docker-compose', 'down']
            
            if remove_volumes:
                cmd.extend(['--volumes', '--remove-orphans'])
                
            subprocess.run(cmd, check=True, cwd=self.compose_dir)
            
            logger.info("Stack cleaned up successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clean up stack: {e}")

def main():
    """Main function to demonstrate Docker Compose management"""
    
    # Initialize manager for different environments
    dev_manager = DockerComposeManager("zomato-app", "dev")
    prod_manager = DockerComposeManager("zomato-app", "prod")
    
    print("🚀 Setting up Zomato-style Food Delivery Infrastructure")
    print("=" * 60)
    
    # Setup development environment
    print("📝 Generating Docker Compose configurations...")
    dev_manager.write_compose_file()
    dev_manager.write_env_file()
    dev_manager.create_nginx_config()
    dev_manager.create_monitoring_config()
    
    print("📝 Generating production configurations...")
    prod_manager.write_compose_file()
    prod_manager.write_env_file()
    prod_manager.create_nginx_config()
    prod_manager.create_monitoring_config()
    
    # Deploy development stack
    choice = input("\n🤔 Do you want to deploy the development stack? (y/n): ")
    
    if choice.lower() == 'y':
        print("\n🚀 Deploying development stack...")
        dev_manager.deploy_stack()
        
        print("\n⏳ Waiting for services to start...")
        time.sleep(30)
        
        print("\n🏥 Running health checks...")
        if dev_manager.health_check():
            print("✅ All services are healthy!")
        else:
            print("⚠️ Some services may need more time to start")
        
        print("\n📊 Stack deployment summary:")
        print(f"- Environment: development")
        print(f"- Services: 12+ microservices")
        print(f"- Monitoring: Prometheus + Grafana")
        print(f"- API Gateway: Nginx")
        print(f"- Databases: PostgreSQL, MongoDB, Redis")
        print(f"- Message Queue: RabbitMQ")
        print(f"- Search: Elasticsearch")
        
        print(f"\n🌐 Access URLs:")
        print(f"- API Gateway: http://localhost")
        print(f"- User Service: http://localhost:3001")
        print(f"- Restaurant Service: http://localhost:3002") 
        print(f"- Order Service: http://localhost:3003")
        print(f"- Payment Service: http://localhost:3004")
        print(f"- Delivery Service: http://localhost:3005")
        print(f"- Grafana Dashboard: http://localhost:3000")
        print(f"- RabbitMQ Management: http://localhost:15672")
        
        print(f"\n💰 Estimated monthly cost:")
        print(f"- Local development: Free")
        print(f"- Cloud hosting (AWS/Azure/GCP): ₹2,000-5,000/month")
        print(f"- Production scaling: ₹10,000-50,000/month")
        
        # Demonstrate scaling
        scale_choice = input("\n🔧 Do you want to scale services for load testing? (y/n): ")
        if scale_choice.lower() == 'y':
            scaling_config = {
                'user-service': 3,
                'restaurant-service': 2,
                'order-service': 3
            }
            print("📈 Scaling services...")
            dev_manager.scale_services(scaling_config)
    
    print("\n✅ Docker Compose setup completed!")
    print("📖 Check the generated files in docker-compose-dev/ and docker-compose-prod/ directories")

if __name__ == "__main__":
    main()