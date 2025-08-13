#!/usr/bin/env python3
"""
Flux GitOps Payment System Controller
====================================

Razorpay/PhonePe style payment gateway के लिए Flux-based GitOps controller।
UPI, credit cards, और digital wallets के साथ complete payment orchestration।

Features:
- Flux GitOps integration for payment services
- UPI/IMPS real-time payment processing
- RBI compliance और audit trails
- Multi-region payment routing
- Automatic rollback on payment failures
- Festival season traffic handling

Author: Hindi Tech Podcast - Episode 19
Context: Payment Gateway GitOps for Indian Fintech
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import kubernetes
from kubernetes import client, config, watch
import aiohttp
import asyncpg
import redis.asyncio as redis
from pathlib import Path
import tempfile
from decimal import Decimal
import uuid

# Indian payment और timezone support
import pytz
from razorpay import Client as RazorpayClient

IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for payment systems
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('flux_payment_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaymentMethod(Enum):
    """Indian payment methods"""
    UPI = "upi"
    NETBANKING = "netbanking"  
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WALLET = "digital_wallet"
    EMI = "no_cost_emi"
    COD = "cash_on_delivery"

class PaymentStatus(Enum):
    """Payment transaction status"""
    INITIATED = "initiated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

@dataclass
class PaymentTransaction:
    """Payment transaction data model"""
    transaction_id: str
    user_id: str
    amount: Decimal
    currency: str = "INR"
    payment_method: PaymentMethod = PaymentMethod.UPI
    merchant_id: str = ""
    order_id: str = ""
    status: PaymentStatus = PaymentStatus.INITIATED
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FluxPaymentConfig:
    """Flux payment system configuration"""
    namespace: str = "payment-system"
    git_repo: str = "https://github.com/company/payment-configs"
    git_branch: str = "main"
    sync_interval: str = "1m"
    redis_url: str = "redis://redis:6379"
    postgres_url: str = "postgresql://user:pass@postgres:5432/payments"
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    max_retry_attempts: int = 3
    payment_timeout: int = 300  # 5 minutes
    enable_audit: bool = True

class IndianPaymentGateway:
    """
    Indian payment gateways के साथ integration।
    
    Razorpay, Paytm, PhonePe जैसी services के साथ unified interface।
    """
    
    def __init__(self, config: FluxPaymentConfig):
        self.config = config
        self.razorpay_client = None
        if config.razorpay_key_id and config.razorpay_key_secret:
            self.razorpay_client = RazorpayClient(
                auth=(config.razorpay_key_id, config.razorpay_key_secret)
            )
    
    async def process_upi_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """UPI payment processing"""
        try:
            logger.info(f"Processing UPI payment: {transaction.transaction_id}")
            
            if not self.razorpay_client:
                raise ValueError("Razorpay client not configured")
            
            # Create Razorpay order
            order_data = {
                "amount": int(transaction.amount * 100),  # Amount in paise
                "currency": transaction.currency,
                "receipt": transaction.transaction_id,
                "notes": {
                    "user_id": transaction.user_id,
                    "payment_method": transaction.payment_method.value,
                    "merchant_id": transaction.merchant_id
                }
            }
            
            # Simulate API call (in real implementation, use actual Razorpay API)
            await asyncio.sleep(0.1)  # Simulate network latency
            
            # Mock successful response
            mock_response = {
                "id": f"order_{uuid.uuid4().hex[:12]}",
                "entity": "order",
                "amount": int(transaction.amount * 100),
                "currency": transaction.currency,
                "status": "created",
                "receipt": transaction.transaction_id,
                "created_at": int(datetime.now(IST).timestamp())
            }
            
            transaction.gateway_response = mock_response
            transaction.order_id = mock_response["id"]
            transaction.status = PaymentStatus.PROCESSING
            
            # Simulate payment completion
            await asyncio.sleep(2)  # Simulate processing time
            
            # Mock payment success (90% success rate for UPI)
            import random
            success_rate = 0.90
            
            if random.random() < success_rate:
                transaction.status = PaymentStatus.SUCCESS
                transaction.completed_at = datetime.now(IST)
                transaction.gateway_response["payment_id"] = f"pay_{uuid.uuid4().hex[:12]}"
                
                logger.info(f"✅ UPI payment successful: {transaction.transaction_id}")
            else:
                transaction.status = PaymentStatus.FAILED
                transaction.gateway_response["error"] = {
                    "code": "PAYMENT_FAILED",
                    "description": "UPI transaction failed"
                }
                logger.warning(f"❌ UPI payment failed: {transaction.transaction_id}")
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ UPI payment processing error: {e}")
            transaction.status = PaymentStatus.FAILED
            transaction.gateway_response = {"error": str(e)}
            return transaction
    
    async def process_card_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Credit/Debit card payment processing"""
        try:
            logger.info(f"Processing card payment: {transaction.transaction_id}")
            
            # Card payments have different success rates and processing times
            await asyncio.sleep(3)  # Cards take longer to process
            
            # Higher success rate for cards (95%)
            import random
            success_rate = 0.95
            
            if random.random() < success_rate:
                transaction.status = PaymentStatus.SUCCESS
                transaction.completed_at = datetime.now(IST)
                transaction.gateway_response = {
                    "payment_id": f"pay_card_{uuid.uuid4().hex[:12]}",
                    "card_network": random.choice(["VISA", "MASTERCARD", "RUPAY"]),
                    "bank": random.choice(["SBI", "HDFC", "ICICI", "AXIS"])
                }
                logger.info(f"✅ Card payment successful: {transaction.transaction_id}")
            else:
                transaction.status = PaymentStatus.FAILED
                transaction.gateway_response = {
                    "error": {
                        "code": "CARD_DECLINED", 
                        "description": "Card declined by issuing bank"
                    }
                }
                logger.warning(f"❌ Card payment failed: {transaction.transaction_id}")
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Card payment processing error: {e}")
            transaction.status = PaymentStatus.FAILED
            transaction.gateway_response = {"error": str(e)}
            return transaction

class FluxPaymentController:
    """
    Flux GitOps payment system controller।
    
    यह controller payment services को Flux के through manage करता है
    और real-time payment processing ensure करता है।
    """
    
    def __init__(self, config: FluxPaymentConfig):
        self.config = config
        self.k8s_client = None
        self.redis_client = None
        self.pg_pool = None
        self.payment_gateway = IndianPaymentGateway(config)
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Controller initialization"""
        try:
            logger.info("🚀 Initializing Flux Payment Controller...")
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
                logger.info("Using in-cluster Kubernetes config")
            except:
                config.load_kube_config()
                logger.info("Using local Kubernetes config")
            
            self.k8s_client = client.ApiClient()
            
            # Setup Redis connection
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Setup PostgreSQL connection
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            logger.info("✅ PostgreSQL connection pool created")
            
            # Initialize database schema
            await self._initialize_database_schema()
            
            # Setup Flux GitOps configuration
            await self._setup_flux_configuration()
            
            logger.info("✅ Flux Payment Controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Controller initialization failed: {e}")
            return False
    
    async def _initialize_database_schema(self) -> None:
        """Database schema initialization"""
        try:
            logger.info("📊 Initializing payment database schema...")
            
            schema_sql = """
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'INR',
                payment_method VARCHAR(50) NOT NULL,
                merchant_id VARCHAR(255),
                order_id VARCHAR(255),
                status VARCHAR(50) NOT NULL,
                gateway_response JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                metadata JSONB DEFAULT '{}'::jsonb,
                
                -- Indian compliance indexes
                INDEX idx_transaction_created (created_at),
                INDEX idx_user_payments (user_id),
                INDEX idx_merchant_payments (merchant_id),
                INDEX idx_payment_status (status)
            );
            
            CREATE TABLE IF NOT EXISTS payment_audit_logs (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                INDEX idx_audit_transaction (transaction_id),
                INDEX idx_audit_created (created_at)
            );
            
            -- RBI compliance: 7-year data retention
            CREATE TABLE IF NOT EXISTS compliance_archive (
                id SERIAL PRIMARY KEY,
                archived_date DATE NOT NULL,
                transaction_count INTEGER NOT NULL,
                archive_location TEXT NOT NULL,
                checksum VARCHAR(255) NOT NULL,
                
                INDEX idx_archive_date (archived_date)
            );
            """
            
            async with self.pg_pool.acquire() as conn:
                await conn.execute(schema_sql)
            
            logger.info("✅ Database schema initialized")
            
        except Exception as e:
            logger.error(f"❌ Database schema initialization failed: {e}")
            raise e
    
    async def _setup_flux_configuration(self) -> None:
        """Flux GitOps configuration setup"""
        try:
            logger.info("⚡ Setting up Flux GitOps configuration...")
            
            # Create Flux namespace
            v1 = client.CoreV1Api()
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=self.config.namespace,
                    labels={
                        'app': 'flux-payment-system',
                        'compliance': 'rbi-compliant',
                        'data-residency': 'india'
                    }
                )
            )
            
            try:
                v1.create_namespace(body=namespace)
                logger.info(f"✅ Namespace '{self.config.namespace}' created")
            except client.ApiException as e:
                if e.status == 409:
                    logger.info(f"ℹ️ Namespace '{self.config.namespace}' already exists")
                else:
                    raise e
            
            # Create Flux GitRepository
            git_repo_config = {
                'apiVersion': 'source.toolkit.fluxcd.io/v1beta2',
                'kind': 'GitRepository',
                'metadata': {
                    'name': 'payment-system-repo',
                    'namespace': self.config.namespace
                },
                'spec': {
                    'interval': self.config.sync_interval,
                    'url': self.config.git_repo,
                    'ref': {
                        'branch': self.config.git_branch
                    },
                    'secretRef': {
                        'name': 'git-credentials'
                    }
                }
            }
            
            # Create Flux Kustomization
            kustomization_config = {
                'apiVersion': 'kustomize.toolkit.fluxcd.io/v1beta2',
                'kind': 'Kustomization',
                'metadata': {
                    'name': 'payment-system',
                    'namespace': self.config.namespace
                },
                'spec': {
                    'interval': self.config.sync_interval,
                    'sourceRef': {
                        'kind': 'GitRepository',
                        'name': 'payment-system-repo'
                    },
                    'path': './payment-manifests',
                    'prune': True,
                    'validation': 'client',
                    'healthChecks': [
                        {
                            'apiVersion': 'apps/v1',
                            'kind': 'Deployment',
                            'name': 'payment-api',
                            'namespace': self.config.namespace
                        }
                    ]
                }
            }
            
            # Apply Flux configurations
            configs = [git_repo_config, kustomization_config]
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump_all(configs, f)
                flux_config_file = f.name
            
            # Apply using kubectl
            import subprocess
            result = subprocess.run([
                'kubectl', 'apply', '-f', flux_config_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Flux GitOps configuration applied")
            else:
                logger.warning(f"⚠️ Flux config warning: {result.stderr}")
            
            os.unlink(flux_config_file)
            
        except Exception as e:
            logger.error(f"❌ Flux configuration setup failed: {e}")
            raise e
    
    async def start_payment_processing(self) -> None:
        """Payment processing loop start करना"""
        try:
            logger.info("💳 Starting payment processing loop...")
            self.is_running = True
            
            # Create multiple processing tasks for different payment methods
            tasks = [
                asyncio.create_task(self._process_upi_payments()),
                asyncio.create_task(self._process_card_payments()),
                asyncio.create_task(self._process_wallet_payments()),
                asyncio.create_task(self._monitor_payment_health()),
                asyncio.create_task(self._handle_festival_traffic()),
                asyncio.create_task(self._run_compliance_checks())
            ]
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"❌ Payment processing error: {e}")
            self.is_running = False
    
    async def _process_upi_payments(self) -> None:
        """UPI payments की processing"""
        while self.is_running:
            try:
                # Check for pending UPI payments in Redis queue
                upi_queue_key = "payment:queue:upi"
                
                # BLPOP for blocking queue operation
                result = await self.redis_client.blpop(upi_queue_key, timeout=5)
                
                if result:
                    _, payment_data = result
                    payment_json = json.loads(payment_data)
                    
                    # Create transaction object
                    transaction = PaymentTransaction(
                        transaction_id=payment_json['transaction_id'],
                        user_id=payment_json['user_id'],
                        amount=Decimal(str(payment_json['amount'])),
                        payment_method=PaymentMethod.UPI,
                        merchant_id=payment_json.get('merchant_id', ''),
                        metadata=payment_json.get('metadata', {})
                    )
                    
                    # Process the payment
                    processed_transaction = await self.payment_gateway.process_upi_payment(transaction)
                    
                    # Save to database
                    await self._save_transaction(processed_transaction)
                    
                    # Send response back via Redis
                    await self._send_payment_response(processed_transaction)
                
            except Exception as e:
                logger.error(f"❌ UPI payment processing error: {e}")
                await asyncio.sleep(1)
    
    async def _process_card_payments(self) -> None:
        """Credit/Debit card payments की processing"""
        while self.is_running:
            try:
                card_queue_key = "payment:queue:card"
                result = await self.redis_client.blpop(card_queue_key, timeout=5)
                
                if result:
                    _, payment_data = result
                    payment_json = json.loads(payment_data)
                    
                    transaction = PaymentTransaction(
                        transaction_id=payment_json['transaction_id'],
                        user_id=payment_json['user_id'],
                        amount=Decimal(str(payment_json['amount'])),
                        payment_method=PaymentMethod.CREDIT_CARD if payment_json.get('card_type') == 'credit' else PaymentMethod.DEBIT_CARD,
                        merchant_id=payment_json.get('merchant_id', ''),
                        metadata=payment_json.get('metadata', {})
                    )
                    
                    processed_transaction = await self.payment_gateway.process_card_payment(transaction)
                    await self._save_transaction(processed_transaction)
                    await self._send_payment_response(processed_transaction)
                
            except Exception as e:
                logger.error(f"❌ Card payment processing error: {e}")
                await asyncio.sleep(1)
    
    async def _process_wallet_payments(self) -> None:
        """Digital wallet payments की processing"""
        while self.is_running:
            try:
                wallet_queue_key = "payment:queue:wallet"
                result = await self.redis_client.blpop(wallet_queue_key, timeout=5)
                
                if result:
                    _, payment_data = result
                    payment_json = json.loads(payment_data)
                    
                    transaction = PaymentTransaction(
                        transaction_id=payment_json['transaction_id'],
                        user_id=payment_json['user_id'],
                        amount=Decimal(str(payment_json['amount'])),
                        payment_method=PaymentMethod.WALLET,
                        merchant_id=payment_json.get('merchant_id', ''),
                        metadata=payment_json.get('metadata', {})
                    )
                    
                    # Wallet payments are usually instant
                    await asyncio.sleep(0.5)  # Minimal processing time
                    transaction.status = PaymentStatus.SUCCESS
                    transaction.completed_at = datetime.now(IST)
                    transaction.gateway_response = {
                        "wallet_txn_id": f"wallet_{uuid.uuid4().hex[:12]}",
                        "wallet_balance_after": payment_json.get('wallet_balance', 0) - float(transaction.amount)
                    }
                    
                    await self._save_transaction(transaction)
                    await self._send_payment_response(transaction)
                
            except Exception as e:
                logger.error(f"❌ Wallet payment processing error: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_payment_health(self) -> None:
        """Payment system health monitoring"""
        while self.is_running:
            try:
                current_time = datetime.now(IST)
                
                # Check payment success rates
                success_rates = await self._calculate_success_rates()
                
                # Check queue lengths
                queue_lengths = await self._check_queue_lengths()
                
                # Check database connectivity
                db_status = await self._check_database_health()
                
                # Alert if success rates are low
                for method, rate in success_rates.items():
                    if rate < 0.85:  # 85% threshold
                        await self._send_alert(
                            f"Low success rate for {method}: {rate:.2%}",
                            severity="warning"
                        )
                
                # Alert if queues are backing up
                for queue, length in queue_lengths.items():
                    if length > 1000:  # 1000 pending payments
                        await self._send_alert(
                            f"High queue length for {queue}: {length} pending",
                            severity="critical"
                        )
                
                # Log health metrics
                logger.info(f"💊 Health Check - Success Rates: {success_rates}")
                logger.info(f"📊 Queue Lengths: {queue_lengths}")
                logger.info(f"🗄️ Database Status: {'OK' if db_status else 'FAILED'}")
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _handle_festival_traffic(self) -> None:
        """Festival season traffic handling"""
        while self.is_running:
            try:
                current_date = datetime.now(IST).date()
                
                # Check if it's festival season
                festival_periods = [
                    # Diwali season (Oct-Nov)
                    (datetime(current_date.year, 10, 15).date(), 
                     datetime(current_date.year, 11, 15).date()),
                    # Independence Day (August)
                    (datetime(current_date.year, 8, 10).date(),
                     datetime(current_date.year, 8, 20).date()),
                    # New Year (December-January)
                    (datetime(current_date.year, 12, 25).date(),
                     datetime(current_date.year + 1, 1, 5).date())
                ]
                
                is_festival = any(start <= current_date <= end for start, end in festival_periods)
                
                if is_festival:
                    logger.info("🎊 Festival season detected - scaling up payment processing")
                    
                    # Scale up processing (increase worker replicas)
                    await self._scale_payment_workers(replicas=10)
                    
                    # Increase queue monitoring frequency
                    await asyncio.sleep(5)  # More frequent checks during festivals
                else:
                    await asyncio.sleep(300)  # Normal monitoring interval
                
            except Exception as e:
                logger.error(f"❌ Festival traffic handling error: {e}")
                await asyncio.sleep(300)
    
    async def _run_compliance_checks(self) -> None:
        """RBI compliance checks"""
        while self.is_running:
            try:
                current_time = datetime.now(IST)
                
                # Daily compliance report at 6 AM IST
                if current_time.hour == 6 and current_time.minute == 0:
                    await self._generate_daily_compliance_report()
                
                # Check for suspicious transactions
                await self._check_suspicious_transactions()
                
                # Verify audit logs integrity
                await self._verify_audit_logs()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Compliance check error: {e}")
                await asyncio.sleep(3600)
    
    async def _save_transaction(self, transaction: PaymentTransaction) -> None:
        """Transaction को database में save करना"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO payment_transactions 
                    (transaction_id, user_id, amount, currency, payment_method, 
                     merchant_id, order_id, status, gateway_response, created_at, 
                     completed_at, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                transaction.transaction_id, transaction.user_id, transaction.amount,
                transaction.currency, transaction.payment_method.value, 
                transaction.merchant_id, transaction.order_id, transaction.status.value,
                json.dumps(transaction.gateway_response), transaction.created_at,
                transaction.completed_at, json.dumps(transaction.metadata))
                
                # Audit log entry
                if self.config.enable_audit:
                    await conn.execute("""
                        INSERT INTO payment_audit_logs (transaction_id, event_type, event_data)
                        VALUES ($1, $2, $3)
                    """,
                    transaction.transaction_id, "TRANSACTION_SAVED", 
                    json.dumps(asdict(transaction), default=str))
                
        except Exception as e:
            logger.error(f"❌ Failed to save transaction {transaction.transaction_id}: {e}")
    
    async def _send_payment_response(self, transaction: PaymentTransaction) -> None:
        """Payment response को client को send करना"""
        try:
            response_data = {
                'transaction_id': transaction.transaction_id,
                'status': transaction.status.value,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
                'gateway_response': transaction.gateway_response
            }
            
            # Send to response channel in Redis
            response_channel = f"payment:response:{transaction.transaction_id}"
            await self.redis_client.setex(
                response_channel, 
                300,  # 5 minutes expiry
                json.dumps(response_data)
            )
            
            # Also publish to a general payment events channel
            await self.redis_client.publish(
                "payment:events",
                json.dumps({
                    'type': 'PAYMENT_COMPLETED',
                    'data': response_data,
                    'timestamp': datetime.now(IST).isoformat()
                })
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to send payment response: {e}")
    
    async def _calculate_success_rates(self) -> Dict[str, float]:
        """Payment success rates calculate करना"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Last 1 hour success rates by payment method
                query = """
                    SELECT 
                        payment_method,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) as success_rate
                    FROM payment_transactions 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                    GROUP BY payment_method
                """
                
                rows = await conn.fetch(query)
                return {row['payment_method']: row['success_rate']/100 for row in rows}
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate success rates: {e}")
            return {}
    
    async def _check_queue_lengths(self) -> Dict[str, int]:
        """Queue lengths check करना"""
        try:
            queues = ["payment:queue:upi", "payment:queue:card", "payment:queue:wallet"]
            lengths = {}
            
            for queue in queues:
                length = await self.redis_client.llen(queue)
                lengths[queue] = length
            
            return lengths
            
        except Exception as e:
            logger.error(f"❌ Failed to check queue lengths: {e}")
            return {}
    
    async def _check_database_health(self) -> bool:
        """Database health check"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except:
            return False
    
    async def _scale_payment_workers(self, replicas: int) -> None:
        """Payment worker pods को scale करना"""
        try:
            apps_v1 = client.AppsV1Api()
            
            # Scale payment processing deployment
            body = {'spec': {'replicas': replicas}}
            
            apps_v1.patch_namespaced_deployment_scale(
                name="payment-processor",
                namespace=self.config.namespace,
                body=body
            )
            
            logger.info(f"✅ Scaled payment workers to {replicas} replicas")
            
        except Exception as e:
            logger.error(f"❌ Failed to scale payment workers: {e}")
    
    async def _send_alert(self, message: str, severity: str = "info") -> None:
        """Alert send करना"""
        alert_data = {
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(IST).isoformat(),
            'component': 'flux-payment-controller'
        }
        
        # Send to alerts channel
        await self.redis_client.publish("alerts:payment", json.dumps(alert_data))
        
        if severity == "critical":
            logger.error(f"🚨 CRITICAL ALERT: {message}")
        elif severity == "warning":
            logger.warning(f"⚠️ WARNING: {message}")
        else:
            logger.info(f"ℹ️ INFO: {message}")
    
    async def cleanup(self) -> None:
        """Controller cleanup"""
        self.is_running = False
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.pg_pool:
            await self.pg_pool.close()
        
        logger.info("🧹 Flux Payment Controller cleaned up")


async def main():
    """Main function"""
    print("💳 Flux Payment Controller for Indian Fintech")
    print("=" * 50)
    
    # Configuration
    config = FluxPaymentConfig(
        namespace="payment-system",
        git_repo="https://github.com/company/payment-configs",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/payments"),
        razorpay_key_id=os.getenv("RAZORPAY_KEY_ID", ""),
        razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET", ""),
        enable_audit=True
    )
    
    # Initialize controller
    controller = FluxPaymentController(config)
    
    # Setup and start
    try:
        success = await controller.initialize()
        if success:
            print("✅ Payment Controller initialized successfully")
            await controller.start_payment_processing()
        else:
            print("❌ Failed to initialize Payment Controller")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Payment Controller...")
    finally:
        await controller.cleanup()


if __name__ == "__main__":
    asyncio.run(main())