"""
Webhook Signature Verification System
====================================

यह system webhook signatures को verify करता है secure communication
के लिए। GitHub, Stripe, PayPal जैसे services अपने webhooks में 
इसी तरह की signature verification use करते हैं।

Features:
- HMAC-SHA256 Signature Verification
- Timestamp Validation
- Replay Attack Prevention
- Multiple Signature Support
- Automatic Key Rotation

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import hmac
import hashlib
import time
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import redis

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignatureAlgorithm(Enum):
    """Signature algorithms"""
    HMAC_SHA256 = "sha256"
    HMAC_SHA512 = "sha512"
    HMAC_MD5 = "md5"

@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    signature: str
    client_id: str
    verified: bool = False

@dataclass
class WebhookClient:
    """Webhook client configuration"""
    client_id: str
    client_name: str
    secret_key: str
    algorithm: SignatureAlgorithm
    webhook_url: str
    events: List[str]
    active: bool = True
    
class WebhookSignatureVerifier:
    """
    Production-grade Webhook Signature Verification
    
    Stripe, GitHub, PayPal level की security के साथ webhook verification
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.tolerance_seconds = 300  # 5 minutes tolerance for timestamp
        
        # Registered webhook clients
        self.clients = {
            "razorpay_client": WebhookClient(
                client_id="razorpay_client",
                client_name="Razorpay Payment Gateway",
                secret_key="rzp_webhook_secret_2024",
                algorithm=SignatureAlgorithm.HMAC_SHA256,
                webhook_url="https://api.razorpay.com/webhooks",
                events=["payment.captured", "payment.failed", "subscription.charged"]
            ),
            "paytm_client": WebhookClient(
                client_id="paytm_client",
                client_name="Paytm Business",
                secret_key="paytm_webhook_key_secure",
                algorithm=SignatureAlgorithm.HMAC_SHA256,
                webhook_url="https://business.paytm.com/webhooks",
                events=["payment.success", "payment.failure", "wallet.debit"]
            ),
            "phonepe_client": WebhookClient(
                client_id="phonepe_client",
                client_name="PhonePe Merchant",
                secret_key="phonepe_merchant_webhook_2024",
                algorithm=SignatureAlgorithm.HMAC_SHA512,
                webhook_url="https://mercury.phonepe.com/webhooks",
                events=["payment.completed", "refund.processed", "settlement.done"]
            ),
            "github_integration": WebhookClient(
                client_id="github_integration",
                client_name="GitHub CI/CD Integration", 
                secret_key="github_webhook_secret_key",
                algorithm=SignatureAlgorithm.HMAC_SHA256,
                webhook_url="https://api.github.com/webhooks",
                events=["push", "pull_request", "release"]
            )
        }
    
    def generate_signature(
        self, 
        payload: str, 
        secret: str, 
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256,
        timestamp: Optional[int] = None
    ) -> str:
        """
        Webhook signature generate करता है
        
        Stripe-style signature generation:
        signature = HMAC-SHA256(secret, timestamp + "." + payload)
        """
        
        if timestamp is None:
            timestamp = int(time.time())
        
        # Create signing string: timestamp.payload
        signing_string = f"{timestamp}.{payload}"
        
        # Select hash algorithm
        hash_func = {
            SignatureAlgorithm.HMAC_SHA256: hashlib.sha256,
            SignatureAlgorithm.HMAC_SHA512: hashlib.sha512,
            SignatureAlgorithm.HMAC_MD5: hashlib.md5
        }[algorithm]
        
        # Generate HMAC signature
        signature = hmac.new(
            secret.encode('utf-8'),
            signing_string.encode('utf-8'),
            hash_func
        ).hexdigest()
        
        return f"{algorithm.value}={signature}"
    
    def verify_signature(
        self, 
        payload: str, 
        signature: str, 
        secret: str,
        timestamp: int,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    ) -> bool:
        """
        Webhook signature verify करता है
        
        GitHub, Stripe style verification:
        1. Extract algorithm and signature from header
        2. Recreate expected signature
        3. Compare using secure comparison
        """
        
        try:
            # Parse signature header (format: "sha256=abc123,sha256=def456")
            signatures = {}
            for sig_part in signature.split(','):
                if '=' in sig_part:
                    algo, sig_value = sig_part.strip().split('=', 1)
                    signatures[algo] = sig_value
            
            # Get signature for the specified algorithm
            provided_signature = signatures.get(algorithm.value)
            if not provided_signature:
                logger.warning(f"No signature found for algorithm {algorithm.value}")
                return False
            
            # Generate expected signature
            expected_signature = self.generate_signature(payload, secret, algorithm, timestamp)
            expected_value = expected_signature.split('=', 1)[1]
            
            # Secure comparison to prevent timing attacks
            return hmac.compare_digest(provided_signature, expected_value)
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def verify_webhook(
        self, 
        request: Request,
        signature_header: str,
        timestamp_header: str,
        client_id: str
    ) -> WebhookEvent:
        """
        Complete webhook verification process
        
        1. Client validation
        2. Timestamp validation  
        3. Replay attack prevention
        4. Signature verification
        """
        
        # Get client configuration
        client = self.clients.get(client_id)
        if not client or not client.active:
            raise HTTPException(status_code=400, detail="Invalid or inactive webhook client")
        
        # Get request payload
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        # Parse timestamp
        try:
            timestamp = int(timestamp_header)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid timestamp")
        
        # Validate timestamp (prevent replay attacks)
        current_time = int(time.time())
        if abs(current_time - timestamp) > self.tolerance_seconds:
            raise HTTPException(
                status_code=400, 
                detail=f"Timestamp outside tolerance window of {self.tolerance_seconds} seconds"
            )
        
        # Check for replay attacks
        event_id = hashlib.sha256(f"{client_id}{timestamp}{payload_str}".encode()).hexdigest()
        replay_key = f"webhook_replay:{event_id}"
        
        if self.redis.exists(replay_key):
            raise HTTPException(status_code=400, detail="Replay attack detected")
        
        # Mark event as processed (prevent replay)
        self.redis.setex(replay_key, self.tolerance_seconds * 2, "processed")
        
        # Verify signature
        signature_valid = self.verify_signature(
            payload_str,
            signature_header,
            client.secret_key,
            timestamp,
            client.algorithm
        )
        
        if not signature_valid:
            await self._log_security_event("signature_verification_failed", {
                "client_id": client_id,
                "timestamp": timestamp,
                "payload_length": len(payload_str)
            })
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        try:
            payload_data = json.loads(payload_str)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Create webhook event
        webhook_event = WebhookEvent(
            event_id=event_id,
            event_type=payload_data.get("event_type", "unknown"),
            timestamp=datetime.fromtimestamp(timestamp),
            payload=payload_data,
            signature=signature_header,
            client_id=client_id,
            verified=True
        )
        
        # Log successful verification
        await self._log_security_event("webhook_verified", {
            "event_id": event_id,
            "client_id": client_id,
            "event_type": webhook_event.event_type,
            "timestamp": timestamp
        })
        
        # Store webhook event for processing
        await self._store_webhook_event(webhook_event)
        
        logger.info(f"Webhook verified successfully: {event_id} from {client_id}")
        return webhook_event
    
    async def process_webhook_event(self, webhook_event: WebhookEvent) -> Dict[str, Any]:
        """
        Webhook event को process करता है
        
        यहाँ business logic implement करते हैं
        """
        
        client = self.clients[webhook_event.client_id]
        event_type = webhook_event.event_type
        payload = webhook_event.payload
        
        # Check if client is subscribed to this event type
        if event_type not in client.events:
            logger.warning(f"Client {webhook_event.client_id} not subscribed to event {event_type}")
            return {"status": "ignored", "reason": "not_subscribed"}
        
        # Process based on client and event type
        if webhook_event.client_id == "razorpay_client":
            return await self._process_razorpay_webhook(event_type, payload)
        elif webhook_event.client_id == "paytm_client":
            return await self._process_paytm_webhook(event_type, payload)
        elif webhook_event.client_id == "phonepe_client":
            return await self._process_phonepe_webhook(event_type, payload)
        elif webhook_event.client_id == "github_integration":
            return await self._process_github_webhook(event_type, payload)
        else:
            return await self._process_generic_webhook(event_type, payload)
    
    async def _process_razorpay_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Razorpay webhook processing"""
        
        if event_type == "payment.captured":
            # Payment successful - update order status
            payment_id = payload.get("payment", {}).get("entity", {}).get("id")
            amount = payload.get("payment", {}).get("entity", {}).get("amount", 0) / 100  # Paise to rupees
            
            logger.info(f"Razorpay payment captured: {payment_id}, Amount: ₹{amount}")
            
            # Update database, send confirmation email, etc.
            await self._update_payment_status(payment_id, "completed", amount)
            
            return {"status": "processed", "action": "payment_completed"}
        
        elif event_type == "payment.failed":
            # Payment failed - handle failure
            payment_id = payload.get("payment", {}).get("entity", {}).get("id")
            error_reason = payload.get("payment", {}).get("entity", {}).get("error_reason")
            
            logger.warning(f"Razorpay payment failed: {payment_id}, Reason: {error_reason}")
            
            await self._update_payment_status(payment_id, "failed", 0, error_reason)
            
            return {"status": "processed", "action": "payment_failed"}
        
        return {"status": "processed", "action": "unknown_event"}
    
    async def _process_paytm_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Paytm webhook processing"""
        
        if event_type == "payment.success":
            order_id = payload.get("ORDERID")
            txn_id = payload.get("TXNID") 
            amount = float(payload.get("TXNAMOUNT", 0))
            
            logger.info(f"Paytm payment success: Order {order_id}, Txn {txn_id}, Amount: ₹{amount}")
            
            await self._update_payment_status(txn_id, "completed", amount)
            
            return {"status": "processed", "action": "payment_success"}
        
        elif event_type == "payment.failure":
            order_id = payload.get("ORDERID")
            txn_id = payload.get("TXNID")
            reason = payload.get("RESPMSG")
            
            logger.warning(f"Paytm payment failed: Order {order_id}, Reason: {reason}")
            
            await self._update_payment_status(txn_id, "failed", 0, reason)
            
            return {"status": "processed", "action": "payment_failure"}
        
        return {"status": "processed", "action": "unknown_event"}
    
    async def _process_phonepe_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """PhonePe webhook processing"""
        
        if event_type == "payment.completed":
            merchant_transaction_id = payload.get("data", {}).get("merchantTransactionId")
            amount = payload.get("data", {}).get("amount", 0) / 100  # Paise to rupees
            
            logger.info(f"PhonePe payment completed: {merchant_transaction_id}, Amount: ₹{amount}")
            
            await self._update_payment_status(merchant_transaction_id, "completed", amount)
            
            return {"status": "processed", "action": "payment_completed"}
        
        return {"status": "processed", "action": "unknown_event"}
    
    async def _process_github_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub webhook processing"""
        
        if event_type == "push":
            repository = payload.get("repository", {}).get("full_name")
            branch = payload.get("ref", "").replace("refs/heads/", "")
            commits = len(payload.get("commits", []))
            
            logger.info(f"GitHub push: {repository} on {branch}, {commits} commits")
            
            # Trigger CI/CD pipeline
            if branch == "main":
                await self._trigger_deployment(repository, "production")
            elif branch == "develop":
                await self._trigger_deployment(repository, "staging")
            
            return {"status": "processed", "action": "ci_cd_triggered"}
        
        elif event_type == "pull_request":
            action = payload.get("action")
            pr_number = payload.get("number")
            repository = payload.get("repository", {}).get("full_name")
            
            logger.info(f"GitHub PR {action}: #{pr_number} in {repository}")
            
            if action == "opened":
                await self._trigger_pr_checks(repository, pr_number)
            
            return {"status": "processed", "action": "pr_processed"}
        
        return {"status": "processed", "action": "unknown_event"}
    
    async def _process_generic_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic webhook processing"""
        
        logger.info(f"Processing generic webhook: {event_type}")
        
        # Store for manual processing
        await self._store_for_manual_processing(event_type, payload)
        
        return {"status": "queued", "action": "manual_processing"}
    
    async def _update_payment_status(
        self, 
        payment_id: str, 
        status: str, 
        amount: float, 
        error_reason: Optional[str] = None
    ):
        """Payment status update करता है database में"""
        
        payment_data = {
            "payment_id": payment_id,
            "status": status,
            "amount": amount,
            "updated_at": datetime.utcnow().isoformat(),
            "error_reason": error_reason
        }
        
        # Store in Redis (production में proper database use करें)
        self.redis.hset(f"payment:{payment_id}", mapping=payment_data)
        
        logger.info(f"Updated payment {payment_id} status to {status}")
    
    async def _trigger_deployment(self, repository: str, environment: str):
        """CI/CD deployment trigger करता है"""
        
        deployment_data = {
            "repository": repository,
            "environment": environment,
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }
        
        # Queue deployment
        self.redis.lpush("deployment_queue", json.dumps(deployment_data))
        
        logger.info(f"Queued deployment for {repository} to {environment}")
    
    async def _trigger_pr_checks(self, repository: str, pr_number: int):
        """PR checks trigger करता है"""
        
        check_data = {
            "repository": repository,
            "pr_number": pr_number,
            "triggered_at": datetime.utcnow().isoformat(),
            "checks": ["lint", "test", "security_scan"]
        }
        
        # Queue PR checks
        self.redis.lpush("pr_check_queue", json.dumps(check_data))
        
        logger.info(f"Queued PR checks for {repository}#{pr_number}")
    
    async def _store_for_manual_processing(self, event_type: str, payload: Dict[str, Any]):
        """Manual processing के लिए event store करता है"""
        
        manual_event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        self.redis.lpush("manual_processing_queue", json.dumps(manual_event))
    
    async def _store_webhook_event(self, webhook_event: WebhookEvent):
        """Webhook event को store करता है audit के लिए"""
        
        event_data = asdict(webhook_event)
        event_data["timestamp"] = event_data["timestamp"].isoformat()
        
        # Store in Redis with expiration
        self.redis.setex(
            f"webhook_event:{webhook_event.event_id}",
            86400 * 30,  # 30 days
            json.dumps(event_data)
        )
        
        # Add to client's event history
        self.redis.lpush(
            f"webhook_history:{webhook_event.client_id}",
            webhook_event.event_id
        )
        self.redis.ltrim(f"webhook_history:{webhook_event.client_id}", 0, 999)  # Keep last 1000
    
    async def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Security events को log करता है"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "service": "webhook_verifier"
        }
        
        logger.info(f"Webhook Security Event: {json.dumps(log_entry)}")
        
        # Store for security monitoring
        self.redis.lpush("webhook_security_events", json.dumps(log_entry))
        self.redis.ltrim("webhook_security_events", 0, 9999)  # Keep last 10K events
    
    def rotate_client_secret(self, client_id: str) -> str:
        """Client secret को rotate करता है"""
        
        client = self.clients.get(client_id)
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Generate new secret
        new_secret = secrets.token_urlsafe(32)
        old_secret = client.secret_key
        
        # Update client configuration
        client.secret_key = new_secret
        
        # Log rotation
        logger.info(f"Rotated secret for client {client_id}")
        
        return new_secret

# FastAPI application
app = FastAPI(title="Webhook Signature Verification Service")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Webhook verifier
webhook_verifier = WebhookSignatureVerifier(redis_client)

@app.post("/webhooks/{client_id}")
async def receive_webhook(
    client_id: str,
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
    x_timestamp: str = Header(..., alias="X-Timestamp")
):
    """
    Webhook endpoint with signature verification
    
    Headers required:
    - X-Signature: HMAC signature (format: sha256=abc123)
    - X-Timestamp: Unix timestamp
    """
    
    try:
        # Verify webhook
        webhook_event = await webhook_verifier.verify_webhook(
            request=request,
            signature_header=x_signature,
            timestamp_header=x_timestamp,
            client_id=client_id
        )
        
        # Process webhook event
        result = await webhook_verifier.process_webhook_event(webhook_event)
        
        return {
            "status": "success",
            "event_id": webhook_event.event_id,
            "processing_result": result
        }
        
    except HTTPException as e:
        logger.error(f"Webhook verification failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/webhooks/test/{client_id}")
async def test_webhook_signature(client_id: str):
    """Test webhook signature generation"""
    
    client = webhook_verifier.clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate test payload
    test_payload = {
        "event_type": "test.event",
        "data": {
            "test_id": "test_123",
            "amount": 1000,
            "status": "success"
        }
    }
    
    payload_str = json.dumps(test_payload, separators=(',', ':'))
    timestamp = int(time.time())
    
    # Generate signature
    signature = webhook_verifier.generate_signature(
        payload_str,
        client.secret_key,
        client.algorithm,
        timestamp
    )
    
    return {
        "client_id": client_id,
        "test_payload": test_payload,
        "timestamp": timestamp,
        "signature": signature,
        "curl_command": f"""curl -X POST http://localhost:8007/webhooks/{client_id} \\
  -H "Content-Type: application/json" \\
  -H "X-Signature: {signature}" \\
  -H "X-Timestamp: {timestamp}" \\
  -d '{payload_str}'"""
    }

@app.get("/webhooks/history/{client_id}")
async def get_webhook_history(client_id: str, limit: int = 10):
    """Client के webhook history return करता है"""
    
    event_ids = redis_client.lrange(f"webhook_history:{client_id}", 0, limit - 1)
    
    events = []
    for event_id in event_ids:
        event_data = redis_client.get(f"webhook_event:{event_id}")
        if event_data:
            event = json.loads(event_data)
            # Remove sensitive payload data
            event["payload"] = {"event_type": event["payload"].get("event_type")}
            events.append(event)
    
    return {
        "client_id": client_id,
        "events": events,
        "total_events": len(events)
    }

@app.post("/webhooks/rotate-secret/{client_id}")
async def rotate_webhook_secret(client_id: str):
    """Client secret rotate करता है"""
    
    try:
        new_secret = webhook_verifier.rotate_client_secret(client_id)
        
        return {
            "status": "success",
            "client_id": client_id,
            "new_secret": new_secret,
            "message": "Secret rotated successfully. Update your webhook configuration."
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/webhooks/clients")
async def list_webhook_clients():
    """All webhook clients की list return करता है"""
    
    clients = []
    for client in webhook_verifier.clients.values():
        clients.append({
            "client_id": client.client_id,
            "client_name": client.client_name,
            "algorithm": client.algorithm.value,
            "events": client.events,
            "active": client.active
        })
    
    return {"clients": clients}

if __name__ == "__main__":
    import uvicorn
    
    print("🔗 Webhook Signature Verification Service")
    print("🔐 GitHub, Stripe, Razorpay level security")
    print("⏰ Timestamp validation और replay protection")
    print("🔄 Automatic secret rotation support")
    print("📊 Complete audit trail")
    
    uvicorn.run(app, host="0.0.0.0", port=8007)

"""
Production Implementation Notes:
===============================

1. Security Best Practices:
   - Use HTTPS only for webhook endpoints
   - Implement proper secret management (AWS Secrets Manager, etc.)
   - Regular secret rotation schedule
   - Monitor for suspicious patterns

2. Reliability:
   - Implement retry mechanism for failed processing
   - Dead letter queue for unprocessable events
   - Idempotency handling for duplicate events
   - Circuit breaker for downstream services

3. Monitoring:
   - Webhook success/failure rates
   - Processing latency metrics
   - Security event alerting
   - Client-wise analytics

4. Scalability:
   - Async processing with queues
   - Rate limiting per client
   - Database sharding for event storage
   - Load balancing for high volume

यह implementation GitHub, Stripe, PayPal level की webhook security provide करता है!
"""