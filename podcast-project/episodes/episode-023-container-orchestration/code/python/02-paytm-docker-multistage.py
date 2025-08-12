# Paytm Payment Processing App - Multi-stage Docker Build Example
# भारत की सबसे बड़ी digital payment company के लिए optimized container image

"""
Paytm Payment Processing Service
- Handles 2B+ transactions monthly
- Strict RBI compliance requirements
- Multi-stage build for minimal attack surface
- Optimized for Indian payment methods: UPI, Cards, Wallets, Net Banking
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
import redis.asyncio as redis
import httpx
from cryptography.fernet import Fernet
import uvicorn

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("paytm-payment-processor")

@dataclass
class PaytmConfig:
    """Paytm service configuration"""
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    upi_gateway_url: str = os.getenv("UPI_GATEWAY_URL", "https://secure.paytm.in/upi")
    card_gateway_url: str = os.getenv("CARD_GATEWAY_URL", "https://secure.paytm.in/cards")
    wallet_service_url: str = os.getenv("WALLET_SERVICE_URL", "https://wallet.paytm.com")
    rbi_compliance_mode: bool = os.getenv("RBI_COMPLIANCE", "true").lower() == "true"
    timezone: str = "Asia/Kolkata"
    max_transaction_amount: int = 200000  # ₹2 lakhs as per RBI guidelines

# Pydantic models for API
class PaymentRequest(BaseModel):
    """Payment request model with Indian payment method support"""
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    payment_method: str  # UPI, CARD, WALLET, NETBANKING
    description: str
    callback_url: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount as per RBI guidelines"""
        if v <= 0:
            raise ValueError('राशि शून्य से अधिक होनी चाहिए')
        if v > 200000:  # ₹2 lakhs limit
            raise ValueError('अधिकतम राशि ₹2,00,000 है')
        return round(v, 2)
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """Validate Indian payment methods"""
        valid_methods = ['UPI', 'CARD', 'WALLET', 'NETBANKING', 'PAYTM_WALLET']
        if v.upper() not in valid_methods:
            raise ValueError(f'अमान्य भुगतान विधि। मान्य विधियां: {valid_methods}')
        return v.upper()

class PaymentResponse(BaseModel):
    """Payment response model"""
    transaction_id: str
    status: str  # SUCCESS, FAILED, PENDING
    payment_gateway_id: str
    amount: float
    currency: str
    timestamp: datetime
    error_message: Optional[str] = None

class PaytmPaymentProcessor:
    """
    Paytm Payment Processor
    भुगतान प्रक्रिया के लिए मुख्य क्लास
    """
    
    def __init__(self, config: PaytmConfig):
        self.config = config
        self.fernet = Fernet(config.encryption_key.encode())
        self.redis_client = None
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=100)
        )
    
    async def startup(self):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(
            self.config.redis_url,
            decode_responses=True,
            max_connections=50
        )
        logger.info("Paytm Payment Processor initialized successfully")
    
    async def shutdown(self):
        """Cleanup connections"""
        if self.redis_client:
            await self.redis_client.close()
        await self.http_client.aclose()
        logger.info("Paytm Payment Processor shutdown complete")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for RBI compliance"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    async def cache_transaction(self, transaction_id: str, data: Dict) -> None:
        """Cache transaction data in Redis"""
        key = f"paytm:transaction:{transaction_id}"
        await self.redis_client.setex(
            key, 
            3600,  # 1 hour TTL
            self.encrypt_sensitive_data(str(data))
        )
    
    async def get_cached_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get transaction from cache"""
        key = f"paytm:transaction:{transaction_id}"
        cached_data = await self.redis_client.get(key)
        if cached_data:
            return eval(self.decrypt_sensitive_data(cached_data))
        return None
    
    async def process_upi_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process UPI payment - India's most popular payment method
        UPI भुगतान प्रक्रिया - भारत की सबसे लोकप्रिय भुगतान विधि
        """
        logger.info(f"Processing UPI payment for transaction: {request.transaction_id}")
        
        # UPI payment payload
        upi_payload = {
            "merchantId": request.merchant_id,
            "transactionId": request.transaction_id,
            "amount": request.amount,
            "currency": request.currency,
            "description": request.description,
            "callbackUrl": request.callback_url or "https://merchant.paytm.com/callback"
        }
        
        try:
            # Call UPI gateway
            response = await self.http_client.post(
                f"{self.config.upi_gateway_url}/process",
                json=upi_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Paytm-Client": "payment-processor",
                    "X-Request-ID": request.transaction_id
                }
            )
            response.raise_for_status()
            
            gateway_response = response.json()
            
            # Create payment response
            payment_response = PaymentResponse(
                transaction_id=request.transaction_id,
                status=gateway_response.get("status", "PENDING"),
                payment_gateway_id=gateway_response.get("gatewayTransactionId"),
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now(),
                error_message=gateway_response.get("errorMessage")
            )
            
            # Cache for analytics and compliance
            await self.cache_transaction(request.transaction_id, payment_response.dict())
            
            logger.info(f"UPI payment processed: {payment_response.status}")
            return payment_response
            
        except httpx.RequestError as e:
            logger.error(f"UPI gateway error: {e}")
            return PaymentResponse(
                transaction_id=request.transaction_id,
                status="FAILED",
                payment_gateway_id="",
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now(),
                error_message="UPI gateway connection failed"
            )
    
    async def process_card_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process card payment with RBI compliance
        कार्ड भुगतान प्रक्रिया RBI अनुपालन के साथ
        """
        logger.info(f"Processing card payment for transaction: {request.transaction_id}")
        
        # Enhanced security for card payments
        card_payload = {
            "merchantId": request.merchant_id,
            "transactionId": request.transaction_id,
            "amount": request.amount,
            "currency": request.currency,
            "securityCompliance": "RBI_COMPLIANT",
            "encryptionStandard": "AES256",
            "tokenization": True  # Card tokenization as per RBI guidelines
        }
        
        try:
            response = await self.http_client.post(
                f"{self.config.card_gateway_url}/process",
                json=card_payload,
                headers={"X-Compliance": "RBI_GUIDELINES_2022"}
            )
            response.raise_for_status()
            
            gateway_response = response.json()
            
            payment_response = PaymentResponse(
                transaction_id=request.transaction_id,
                status=gateway_response.get("status", "PENDING"),
                payment_gateway_id=gateway_response.get("gatewayTransactionId"),
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now()
            )
            
            await self.cache_transaction(request.transaction_id, payment_response.dict())
            return payment_response
            
        except Exception as e:
            logger.error(f"Card payment error: {e}")
            return PaymentResponse(
                transaction_id=request.transaction_id,
                status="FAILED",
                payment_gateway_id="",
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now(),
                error_message="Card processing failed"
            )
    
    async def process_wallet_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process Paytm Wallet payment
        Paytm Wallet भुगतान प्रक्रिया
        """
        logger.info(f"Processing wallet payment for transaction: {request.transaction_id}")
        
        # Check wallet balance (mock implementation)
        wallet_payload = {
            "userId": request.user_id,
            "amount": request.amount,
            "transactionId": request.transaction_id,
            "merchantId": request.merchant_id
        }
        
        try:
            response = await self.http_client.post(
                f"{self.config.wallet_service_url}/debit",
                json=wallet_payload
            )
            response.raise_for_status()
            
            wallet_response = response.json()
            
            payment_response = PaymentResponse(
                transaction_id=request.transaction_id,
                status="SUCCESS" if wallet_response.get("success") else "FAILED",
                payment_gateway_id=wallet_response.get("walletTransactionId"),
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now()
            )
            
            await self.cache_transaction(request.transaction_id, payment_response.dict())
            return payment_response
            
        except Exception as e:
            logger.error(f"Wallet payment error: {e}")
            return PaymentResponse(
                transaction_id=request.transaction_id,
                status="FAILED",
                payment_gateway_id="",
                amount=request.amount,
                currency=request.currency,
                timestamp=datetime.now(),
                error_message="Insufficient wallet balance"
            )

# FastAPI application
app = FastAPI(
    title="Paytm Payment Processor",
    description="भारत की डिजिटल पेमेंट सेवा",
    version="2.1.0"
)

# Global processor instance
config = PaytmConfig()
processor = PaytmPaymentProcessor(config)

@app.on_event("startup")
async def startup_event():
    await processor.startup()

@app.on_event("shutdown") 
async def shutdown_event():
    await processor.shutdown()

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "paytm-payment-processor"}

@app.post("/api/v1/process-payment", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest) -> PaymentResponse:
    """
    Process payment based on payment method
    भुगतान विधि के आधार पर भुगतान प्रक्रिया
    """
    try:
        # Route to appropriate payment processor
        if request.payment_method == "UPI":
            return await processor.process_upi_payment(request)
        elif request.payment_method == "CARD":
            return await processor.process_card_payment(request)
        elif request.payment_method in ["WALLET", "PAYTM_WALLET"]:
            return await processor.process_wallet_payment(request)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported payment method: {request.payment_method}"
            )
            
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal payment processing error")

@app.get("/api/v1/transaction/{transaction_id}")
async def get_transaction_status(transaction_id: str):
    """Get transaction status"""
    cached_transaction = await processor.get_cached_transaction(transaction_id)
    if not cached_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return cached_transaction

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "paytm_payment_processor:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        access_log=True,
        loop="uvloop"
    )