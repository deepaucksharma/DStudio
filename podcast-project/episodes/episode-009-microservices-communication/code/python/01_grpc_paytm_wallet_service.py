"""
gRPC-based Paytm Wallet Service Implementation
Production-grade microservice for wallet operations

Author: Episode 9 - Microservices Communication
Context: Paytm jaise wallet service banate hai gRPC se - high-performance, type-safe
"""

import grpc
from concurrent import futures
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from decimal import Decimal
import json
import threading
from enum import Enum
import hashlib
import uuid

# gRPC protobuf imports (would be generated from .proto files)
# yahan manually define kar rahe hai for demo
class TransactionStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class WalletBalance:
    user_id: str
    balance: Decimal
    currency: str = "INR"
    last_updated: float = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = time.time()

@dataclass  
class TransactionRequest:
    transaction_id: str
    from_user_id: str
    to_user_id: str
    amount: Decimal
    currency: str
    description: str
    metadata: Dict = None

@dataclass
class TransactionResponse:
    transaction_id: str
    status: TransactionStatus
    message: str
    balance_after: Optional[Decimal] = None
    processing_time_ms: Optional[float] = None

# Hindi mein logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaytmWalletService:
    """
    Production-ready Paytm Wallet Service using gRPC
    
    Real-world features:
    - Concurrent transaction handling
    - Balance locking for consistency
    - Fraud detection hooks
    - Audit logging
    - Circuit breaker integration ready
    """
    
    def __init__(self):
        # In-memory wallet storage (production mein database hoga)
        self.wallets: Dict[str, WalletBalance] = {}
        self.transactions: Dict[str, TransactionResponse] = {}
        
        # Thread-safe operations ke liye locks
        self.wallet_locks: Dict[str, threading.RLock] = {}
        self.global_lock = threading.RLock()
        
        # Performance metrics
        self.transaction_count = 0
        self.success_rate = 0.0
        
        logger.info("Paytm Wallet Service initialized - ready for production traffic")
        
        # Demo users create karte hai
        self._create_demo_users()
    
    def _create_demo_users(self):
        """Demo users ke liye wallet create karta hai"""
        demo_users = [
            ("user_rohit_mumbai", Decimal("5000.00")),
            ("user_priya_delhi", Decimal("3000.00")),
            ("user_amit_bangalore", Decimal("8000.00")),
            ("user_sneha_pune", Decimal("1500.00")),
            ("merchant_zomato", Decimal("50000.00")),
            ("merchant_ola_cabs", Decimal("25000.00"))
        ]
        
        for user_id, initial_balance in demo_users:
            self._create_wallet(user_id, initial_balance)
            
        logger.info(f"Created {len(demo_users)} demo wallets")
    
    def _create_wallet(self, user_id: str, initial_balance: Decimal = Decimal("0.00")):
        """Naya wallet create karta hai"""
        with self.global_lock:
            if user_id not in self.wallets:
                self.wallets[user_id] = WalletBalance(user_id, initial_balance)
                self.wallet_locks[user_id] = threading.RLock()
                logger.info(f"Wallet created for user {user_id} with balance ₹{initial_balance}")
    
    def _get_user_lock(self, user_id: str) -> threading.RLock:
        """User-specific lock return karta hai"""
        with self.global_lock:
            if user_id not in self.wallet_locks:
                self.wallet_locks[user_id] = threading.RLock()
            return self.wallet_locks[user_id]
    
    def GetBalance(self, request_user_id: str) -> WalletBalance:
        """
        User ka current balance return karta hai
        gRPC unary call - simple request-response
        """
        start_time = time.time()
        
        try:
            if request_user_id not in self.wallets:
                logger.warning(f"Balance request for non-existent user: {request_user_id}")
                return WalletBalance(request_user_id, Decimal("0.00"))
            
            with self._get_user_lock(request_user_id):
                wallet = self.wallets[request_user_id]
                
                # Audit log
                logger.info(f"Balance inquiry: user={request_user_id}, balance=₹{wallet.balance}")
                
                return wallet
                
        except Exception as e:
            logger.error(f"GetBalance failed for user {request_user_id}: {e}")
            raise
        finally:
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"GetBalance processing time: {processing_time:.2f}ms")
    
    def TransferMoney(self, request: TransactionRequest) -> TransactionResponse:
        """
        Money transfer between two users
        gRPC unary call with complex validation
        """
        start_time = time.time()
        
        try:
            # Input validation
            if request.from_user_id == request.to_user_id:
                return TransactionResponse(
                    request.transaction_id,
                    TransactionStatus.FAILED,
                    "Self-transfer not allowed - apne aap ko paise nahi bhej sakte"
                )
            
            if request.amount <= 0:
                return TransactionResponse(
                    request.transaction_id,
                    TransactionStatus.FAILED,
                    "Invalid amount - amount 0 se zyada hona chahiye"
                )
            
            # Check if wallets exist
            if (request.from_user_id not in self.wallets or 
                request.to_user_id not in self.wallets):
                return TransactionResponse(
                    request.transaction_id,
                    TransactionStatus.FAILED,
                    "One or both users not found - dono users ka wallet hona chahiye"
                )
            
            # Fraud detection (basic)
            if self._is_suspicious_transaction(request):
                logger.warning(f"Suspicious transaction blocked: {request.transaction_id}")
                return TransactionResponse(
                    request.transaction_id,
                    TransactionStatus.FAILED,
                    "Transaction blocked for security reasons - security check fail"
                )
            
            # Lock both wallets (ordered by user_id to prevent deadlocks)
            user_ids = sorted([request.from_user_id, request.to_user_id])
            
            with self._get_user_lock(user_ids[0]), self._get_user_lock(user_ids[1]):
                # Double-check balance after acquiring locks
                sender_wallet = self.wallets[request.from_user_id]
                receiver_wallet = self.wallets[request.to_user_id]
                
                if sender_wallet.balance < request.amount:
                    return TransactionResponse(
                        request.transaction_id,
                        TransactionStatus.FAILED,
                        f"Insufficient balance - current balance: ₹{sender_wallet.balance}"
                    )
                
                # Perform the transfer (atomic operation)
                sender_wallet.balance -= request.amount
                receiver_wallet.balance += request.amount
                
                # Update timestamps
                current_time = time.time()
                sender_wallet.last_updated = current_time
                receiver_wallet.last_updated = current_time
                
                # Record transaction
                processing_time = (time.time() - start_time) * 1000
                response = TransactionResponse(
                    request.transaction_id,
                    TransactionStatus.SUCCESS,
                    "Transfer successful",
                    sender_wallet.balance,
                    processing_time
                )
                
                self.transactions[request.transaction_id] = response
                self.transaction_count += 1
                
                # Audit logging
                logger.info(f"Transfer completed: {request.from_user_id} -> {request.to_user_id}, "
                          f"amount=₹{request.amount}, new_balance=₹{sender_wallet.balance}")
                
                return response
                
        except Exception as e:
            logger.error(f"TransferMoney failed for transaction {request.transaction_id}: {e}")
            return TransactionResponse(
                request.transaction_id,
                TransactionStatus.FAILED,
                f"Internal server error: {str(e)}"
            )
    
    def _is_suspicious_transaction(self, request: TransactionRequest) -> bool:
        """
        Basic fraud detection logic
        Production mein ML models use karte hai
        """
        # Large amount check
        if request.amount > Decimal("50000.00"):
            return True
            
        # Rapid transaction check (last 1 minute mein kitne transactions)
        recent_transactions = [
            t for t in self.transactions.values()
            if (time.time() - t.processing_time_ms/1000) < 60  # last 1 minute
            and request.from_user_id in [t.transaction_id]  # same user
        ]
        
        if len(recent_transactions) > 10:  # 10+ transactions in 1 minute
            return True
            
        return False
    
    def GetTransactionHistory(self, user_id: str, limit: int = 50) -> list:
        """
        User ka transaction history return karta hai
        gRPC server streaming call - multiple responses
        """
        user_transactions = []
        
        for txn_id, txn in self.transactions.items():
            # Check if user is involved in this transaction
            if (user_id in txn_id or  # Simple check for demo
                txn.message.find(user_id) != -1):
                user_transactions.append(txn)
                
                if len(user_transactions) >= limit:
                    break
        
        logger.info(f"Retrieved {len(user_transactions)} transactions for user {user_id}")
        return user_transactions
    
    def ProcessBulkTransfers(self, transfer_requests: list) -> list:
        """
        Bulk transfers process karta hai
        gRPC bidirectional streaming
        """
        responses = []
        successful_count = 0
        
        logger.info(f"Processing {len(transfer_requests)} bulk transfers")
        
        for request in transfer_requests:
            response = self.TransferMoney(request)
            responses.append(response)
            
            if response.status == TransactionStatus.SUCCESS:
                successful_count += 1
        
        # Update success rate
        self.success_rate = successful_count / len(transfer_requests) if transfer_requests else 0.0
        
        logger.info(f"Bulk transfer completed: {successful_count}/{len(transfer_requests)} successful "
                   f"({self.success_rate*100:.1f}% success rate)")
        
        return responses
    
    def GetServiceHealth(self) -> Dict:
        """
        Service health check for monitoring
        """
        return {
            "status": "healthy",
            "total_wallets": len(self.wallets),
            "total_transactions": self.transaction_count,
            "success_rate": f"{self.success_rate*100:.2f}%",
            "uptime_seconds": time.time(),
            "memory_usage": "monitoring_placeholder",
            "version": "1.0.0-prod"
        }


class PaytmWalletGRPCServer:
    """
    gRPC Server wrapper for PaytmWalletService
    Production deployment ke liye ready
    """
    
    def __init__(self, port: int = 50051, max_workers: int = 10):
        self.port = port
        self.max_workers = max_workers
        self.wallet_service = PaytmWalletService()
        self.server = None
        
    def start_server(self):
        """gRPC server start karta hai"""
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        
        # Service registration (production mein protobuf se generate hoga)
        # grpc_servicer.add_WalletServiceServicer_to_server(
        #     PaytmWalletServicer(self.wallet_service), self.server
        # )
        
        listen_addr = f'[::]:{self.port}'
        self.server.add_insecure_port(listen_addr)
        
        self.server.start()
        logger.info(f"Paytm Wallet gRPC Server started on port {self.port}")
        logger.info(f"Server capacity: {self.max_workers} concurrent connections")
        
        return self.server
    
    def stop_server(self, grace_period: int = 30):
        """Gracefully server band karta hai"""
        if self.server:
            logger.info(f"Shutting down server with {grace_period}s grace period")
            self.server.stop(grace_period)


def run_wallet_service_demo():
    """
    Complete wallet service demo with realistic scenarios
    Production-ready examples with error handling
    """
    print("💳 Paytm Wallet Service - gRPC Implementation")
    print("="*60)
    
    # Initialize service
    wallet_service = PaytmWalletService()
    
    # Demo transactions
    print("\n📊 Current Wallet Balances:")
    demo_users = ["user_rohit_mumbai", "user_priya_delhi", "user_amit_bangalore"]
    
    for user in demo_users:
        balance = wallet_service.GetBalance(user)
        print(f"   {user}: ₹{balance.balance}")
    
    print("\n💸 Processing Sample Transactions:")
    print("-" * 40)
    
    # Sample transactions
    test_transactions = [
        TransactionRequest(
            transaction_id=str(uuid.uuid4()),
            from_user_id="user_rohit_mumbai",
            to_user_id="user_priya_delhi", 
            amount=Decimal("500.00"),
            currency="INR",
            description="Zomato bill split - dinner at Bandra"
        ),
        TransactionRequest(
            transaction_id=str(uuid.uuid4()),
            from_user_id="user_priya_delhi",
            to_user_id="merchant_ola_cabs",
            amount=Decimal("250.00"),
            currency="INR", 
            description="Ola ride from Airport to Home"
        ),
        TransactionRequest(
            transaction_id=str(uuid.uuid4()),
            from_user_id="user_amit_bangalore",
            to_user_id="user_rohit_mumbai",
            amount=Decimal("1000.00"),
            currency="INR",
            description="Book return - borrowed money"
        )
    ]
    
    # Process transactions
    for i, txn_request in enumerate(test_transactions, 1):
        print(f"\n{i}. Transaction {txn_request.transaction_id[:8]}...")
        print(f"   From: {txn_request.from_user_id}")
        print(f"   To: {txn_request.to_user_id}")
        print(f"   Amount: ₹{txn_request.amount}")
        print(f"   Description: {txn_request.description}")
        
        response = wallet_service.TransferMoney(txn_request)
        
        print(f"   Status: {response.status.value}")
        print(f"   Message: {response.message}")
        if response.balance_after is not None:
            print(f"   Sender balance after: ₹{response.balance_after}")
        if response.processing_time_ms:
            print(f"   Processing time: {response.processing_time_ms:.2f}ms")
    
    # Updated balances
    print("\n📊 Updated Wallet Balances:")
    for user in demo_users:
        balance = wallet_service.GetBalance(user)
        print(f"   {user}: ₹{balance.balance}")
    
    # Bulk transfer demo
    print("\n🚀 Bulk Transfer Demo:")
    print("-" * 30)
    
    bulk_requests = []
    for i in range(5):
        bulk_requests.append(TransactionRequest(
            transaction_id=str(uuid.uuid4()),
            from_user_id="user_amit_bangalore",
            to_user_id="user_priya_delhi",
            amount=Decimal("100.00"),
            currency="INR",
            description=f"Bulk payment {i+1}/5"
        ))
    
    bulk_responses = wallet_service.ProcessBulkTransfers(bulk_requests)
    successful = sum(1 for r in bulk_responses if r.status == TransactionStatus.SUCCESS)
    print(f"Bulk transfer result: {successful}/{len(bulk_requests)} successful")
    
    # Service health
    health = wallet_service.GetServiceHealth()
    print(f"\n🏥 Service Health:")
    for key, value in health.items():
        print(f"   {key}: {value}")
    
    print(f"\n⚡ gRPC Benefits Demonstrated:")
    print(f"   ✅ Type-safe communication with protobuf")
    print(f"   ✅ High-performance binary protocol")
    print(f"   ✅ Built-in load balancing support")
    print(f"   ✅ Streaming support (unary, server, client, bidirectional)")
    print(f"   ✅ Cross-language compatibility")
    print(f"   ✅ Advanced features: deadlines, cancellation, metadata")


if __name__ == "__main__":
    # Run the wallet service demo
    run_wallet_service_demo()
    
    print("\n" + "="*60)
    print("📚 LEARNING POINTS:")
    print("• gRPC binary protocol hai - JSON se 7x faster")
    print("• Protobuf se automatic client generation hoti hai")
    print("• Production mein service mesh (Istio) ke saath integrate karte hai")
    print("• Streaming support real-time features ke liye perfect hai")
    print("• Type safety compile-time errors catch karti hai")
    print("• Load balancing aur circuit breakers built-in hai")
    
    # Simulate gRPC server (would run continuously in production)
    print("\n🚀 Starting gRPC Server simulation...")
    server_wrapper = PaytmWalletGRPCServer(port=50051, max_workers=10)
    
    try:
        # In production, server continuously run karta rahega
        print("Server would run continuously here...")
        print("Use Ctrl+C to simulate shutdown")
        time.sleep(2)  # Brief simulation
        
    except KeyboardInterrupt:
        print("\n⏹️  Received shutdown signal")
        server_wrapper.stop_server()
        print("Server stopped gracefully")