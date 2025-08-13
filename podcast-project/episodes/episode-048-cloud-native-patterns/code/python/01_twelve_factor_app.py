#!/usr/bin/env python3
"""
12-Factor App Implementation - Jio Platform Style
Cloud Native Architecture Pattern for building scalable applications

Ye example Jio ke platform architecture se inspired hai
12-factor methodology ko follow karta hai for cloud-native apps
"""

import os
import json
import logging
import signal
import sys
from dataclasses import dataclass
from typing import Dict, Any, Optional
import redis
import psycopg2
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix


# Factor 1: Codebase - One codebase tracked in revision control
class AppConfig:
    """Configuration management following 12-factor principles"""
    
    def __init__(self):
        # Factor 3: Config - Store configuration in environment
        self.database_url = os.environ.get('DATABASE_URL', 
                                         'postgresql://localhost:5432/jio_app')
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        self.port = int(os.environ.get('PORT', '8000'))
        self.debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
        
        # Jio specific configurations
        self.jio_api_key = os.environ.get('JIO_API_KEY', '')
        self.jio_service_tier = os.environ.get('JIO_SERVICE_TIER', 'premium')
        
        # Factor 2: Dependencies - Explicitly declare and isolate dependencies
        self.validate_dependencies()
    
    def validate_dependencies(self):
        """Validate all required dependencies are available"""
        required_vars = ['DATABASE_URL', 'REDIS_URL', 'JIO_API_KEY']
        missing = [var for var in required_vars if not os.environ.get(var)]
        
        if missing:
            raise ValueError(f"Missing environment variables: {missing}")


# Factor 4: Backing Services - Treat backing services as attached resources
class BackingServices:
    """Backing services like database, cache, message queue"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.db_connection = None
        self.redis_client = None
        self.setup_services()
    
    def setup_services(self):
        """Initialize all backing services"""
        try:
            # Database connection
            self.db_connection = psycopg2.connect(self.config.database_url)
            logging.info("✅ Database connected successfully")
            
            # Redis connection  
            self.redis_client = redis.from_url(self.config.redis_url)
            self.redis_client.ping()
            logging.info("✅ Redis connected successfully")
            
        except Exception as e:
            logging.error(f"❌ Failed to connect to backing services: {e}")
            raise
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Jio user data retrieval with caching"""
        # First check cache (Redis)
        cached = self.redis_client.get(f"user:{user_id}")
        if cached:
            logging.info(f"📱 User {user_id} data retrieved from cache")
            return json.loads(cached)
        
        # Fallback to database
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM jio_users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        if result:
            user_data = {
                'user_id': result[0],
                'mobile_number': result[1],
                'service_plan': result[2],
                'data_usage': result[3]
            }
            # Cache for 5 minutes
            self.redis_client.setex(f"user:{user_id}", 300, json.dumps(user_data))
            logging.info(f"📱 User {user_id} data retrieved from database")
            return user_data
        
        return None


# Factor 5: Build, Release, Run - Strictly separate build and run stages
class AppBuilder:
    """Build stage - compile, package, and prepare deployment artifact"""
    
    @staticmethod
    def build_info() -> Dict[str, str]:
        """Build information for deployment tracking"""
        return {
            'build_time': os.environ.get('BUILD_TIME', 'unknown'),
            'git_commit': os.environ.get('GIT_COMMIT', 'unknown'),
            'version': os.environ.get('APP_VERSION', '1.0.0'),
            'builder': 'jio-platform-builder'
        }


# Factor 6: Processes - Execute as one or more stateless processes
class StatelessProcessor:
    """Stateless process handling for horizontal scaling"""
    
    def __init__(self, backing_services: BackingServices):
        self.backing_services = backing_services
        # No local state stored in process memory
        # All state goes to backing services
    
    def process_jio_recharge(self, request_data: Dict) -> Dict:
        """
        Process Jio recharge request - stateless operation
        Mumbai mein ek user recharge kar raha hai, process karte hain
        """
        user_id = request_data.get('user_id')
        amount = request_data.get('amount')
        plan_type = request_data.get('plan_type', 'data')
        
        # Get user data from backing service
        user_data = self.backing_services.get_user_data(user_id)
        if not user_data:
            return {'error': 'User not found', 'success': False}
        
        # Process recharge (stateless operation)
        recharge_id = f"JIO_{user_id}_{amount}_{os.getpid()}"
        
        # Store transaction in backing service
        self.backing_services.redis_client.hset(
            f"recharge:{recharge_id}",
            mapping={
                'user_id': user_id,
                'amount': amount,
                'plan_type': plan_type,
                'status': 'completed',
                'timestamp': str(os.times()),
                'processed_by': f"pod-{os.getpid()}"  # For tracking which pod processed
            }
        )
        
        logging.info(f"💰 Recharge processed: {recharge_id} for user {user_id}")
        return {
            'recharge_id': recharge_id,
            'success': True,
            'message': f'Recharge of ₹{amount} successful for {user_data["mobile_number"]}'
        }


# Factor 7: Port Binding - Export services via port binding
# Factor 11: Logs - Treat logs as event streams
class JioCloudNativeApp:
    """Main application class following 12-factor principles"""
    
    def __init__(self):
        self.config = AppConfig()
        self.backing_services = BackingServices(self.config)
        self.processor = StatelessProcessor(self.backing_services)
        
        # Factor 11: Logs - Configure structured logging
        self.setup_logging()
        
        # Factor 12: Admin Processes - Admin tasks as one-off processes
        self.flask_app = self.create_flask_app()
        
        # Factor 9: Disposability - Maximize robustness with fast startup and graceful shutdown
        self.setup_signal_handlers()
    
    def setup_logging(self):
        """Setup structured logging for cloud environment"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)  # Factor 11: Logs to stdout
            ]
        )
        
        # Jio platform logging
        logging.info("🚀 Jio Cloud Native App initializing...")
        logging.info(f"📍 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        logging.info(f"🏗️  Build info: {AppBuilder.build_info()}")
    
    def create_flask_app(self) -> Flask:
        """Create Flask application with 12-factor compliance"""
        app = Flask(__name__)
        
        # Factor 10: Dev/Prod Parity - Keep development and production as similar as possible
        app.wsgi_app = ProxyFix(app.wsgi_app)
        
        @app.route('/health')
        def health_check():
            """Health check endpoint for container orchestration"""
            return jsonify({
                'status': 'healthy',
                'timestamp': str(os.times()),
                'process_id': os.getpid(),
                'service': 'jio-cloud-native-app'
            })
        
        @app.route('/recharge', methods=['POST'])
        def process_recharge():
            """Jio recharge processing endpoint"""
            try:
                request_data = request.get_json()
                result = self.processor.process_jio_recharge(request_data)
                return jsonify(result)
            except Exception as e:
                logging.error(f"❌ Recharge processing failed: {e}")
                return jsonify({'error': str(e), 'success': False}), 500
        
        @app.route('/user/<user_id>')
        def get_user(user_id: str):
            """Get user information"""
            try:
                user_data = self.backing_services.get_user_data(user_id)
                if user_data:
                    return jsonify(user_data)
                else:
                    return jsonify({'error': 'User not found'}), 404
            except Exception as e:
                logging.error(f"❌ User retrieval failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/admin/stats')
        def admin_stats():
            """Factor 12: Admin process - Runtime statistics"""
            stats = {
                'total_processes': 1,  # In production, this would be dynamic
                'uptime': str(os.times()),
                'memory_usage': f"{os.getpid()} MB",  # Simplified
                'active_connections': self.backing_services.redis_client.info().get('connected_clients', 0)
            }
            return jsonify(stats)
        
        return app
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            logging.info(f"🛑 Received signal {signum}, shutting down gracefully...")
            # Close database connections
            if self.backing_services.db_connection:
                self.backing_services.db_connection.close()
            # Close Redis connections  
            if self.backing_services.redis_client:
                self.backing_services.redis_client.close()
            
            logging.info("✅ Shutdown complete")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def run(self):
        """Run the application - Factor 7: Port binding"""
        # Factor 8: Concurrency - Scale out via the process model
        logging.info(f"🌐 Starting Jio Cloud Native App on port {self.config.port}")
        logging.info("📱 Ready to process Jio recharges and user requests")
        
        # In production, use gunicorn or similar WSGI server
        self.flask_app.run(
            host='0.0.0.0',
            port=self.config.port,
            debug=self.config.debug
        )


# Factor 12: Admin Processes - Run admin/management tasks as one-off processes
class AdminTasks:
    """One-off administrative tasks"""
    
    @staticmethod
    def setup_database():
        """Initialize database schema - run once during deployment"""
        config = AppConfig()
        conn = psycopg2.connect(config.database_url)
        cursor = conn.cursor()
        
        # Create Jio users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jio_users (
                user_id VARCHAR(50) PRIMARY KEY,
                mobile_number VARCHAR(15) NOT NULL,
                service_plan VARCHAR(20) NOT NULL,
                data_usage_gb DECIMAL(10,2) DEFAULT 0
            )
        """)
        
        # Insert sample data
        cursor.execute("""
            INSERT INTO jio_users (user_id, mobile_number, service_plan, data_usage_gb)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, ('jio_user_mumbai_1', '+919876543210', 'Premium', 45.5))
        
        conn.commit()
        conn.close()
        print("✅ Database setup completed")


if __name__ == '__main__':
    # Check if running admin task
    if len(sys.argv) > 1 and sys.argv[1] == 'setup-db':
        AdminTasks.setup_database()
    else:
        # Run main application
        app = JioCloudNativeApp()
        app.run()