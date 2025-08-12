"""
CQRS का Basic Separation - Paytm Wallet Example
यह example दिखाता है कि कैसे Commands और Queries को अलग करते हैं
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
import asyncio
from datetime import datetime
import logging

# Configure logging - Hindi में भी messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Paytm Wallet CQRS", version="1.0.0")

# Domain Models - व्यावसायिक logic के लिए
class WalletBalance:
    def __init__(self, user_id: str, balance: float = 0.0):
        self.user_id = user_id
        self.balance = balance
        self.last_updated = datetime.now()
    
    def add_money(self, amount: float, source: str) -> bool:
        """पैसे जोड़ने का business logic"""
        if amount <= 0:
            raise ValueError("राशि शून्य से अधिक होनी चाहिए")
        
        # UPI से 1 लाख, Card से 50 हजार की limit
        if source == "UPI" and amount > 100000:
            raise ValueError("UPI से एक बार में 1 लाख से ज्यादा नहीं जोड़ सकते")
        elif source == "CARD" and amount > 50000:
            raise ValueError("Card से एक बार में 50 हजार से ज्यादा नहीं जोड़ सकते")
        
        self.balance += amount
        self.last_updated = datetime.now()
        logger.info(f"User {self.user_id} को {amount} रुपये {source} से जोड़े गए")
        return True
    
    def deduct_money(self, amount: float, purpose: str) -> bool:
        """पैसे काटने का business logic"""
        if amount <= 0:
            raise ValueError("राशि शून्य से अधिक होनी चाहिए")
        
        if self.balance < amount:
            raise ValueError("पर्याप्त balance नहीं है")
        
        self.balance -= amount
        self.last_updated = datetime.now()
        logger.info(f"User {self.user_id} से {amount} रुपये {purpose} के लिए काटे गए")
        return True

# Command Models - सिर्फ write operations के लिए
class AddMoneyCommand(BaseModel):
    user_id: str
    amount: float
    source: str  # UPI, CARD, NETBANKING
    transaction_id: str = None
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())

class DeductMoneyCommand(BaseModel):
    user_id: str
    amount: float
    purpose: str  # PAYMENT, TRANSFER, WITHDRAWAL
    transaction_id: str = None
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())

# Query Models - सिर्फ read operations के लिए
class BalanceQuery(BaseModel):
    user_id: str

class TransactionHistoryQuery(BaseModel):
    user_id: str
    limit: int = 50
    offset: int = 0

# Response Models
class BalanceResponse(BaseModel):
    user_id: str
    balance: float
    last_updated: datetime

class TransactionResponse(BaseModel):
    transaction_id: str
    amount: float
    type: str
    timestamp: datetime
    description: str

# In-memory storage - Production में database होगा
wallet_storage = {}
transaction_log = []

# Command Handlers - Write operations handle करते हैं
class CommandHandler:
    
    @staticmethod
    async def handle_add_money(command: AddMoneyCommand) -> dict:
        """पैसे जोड़ने का command handle करता है"""
        try:
            # User का wallet मिलाते हैं या नया बनाते हैं
            if command.user_id not in wallet_storage:
                wallet_storage[command.user_id] = WalletBalance(command.user_id)
            
            wallet = wallet_storage[command.user_id]
            wallet.add_money(command.amount, command.source)
            
            # Transaction log में entry करते हैं
            transaction_log.append({
                "transaction_id": command.transaction_id or str(uuid.uuid4()),
                "user_id": command.user_id,
                "amount": command.amount,
                "type": "CREDIT",
                "source": command.source,
                "timestamp": datetime.now(),
                "description": f"{command.source} से {command.amount} रुपये जोड़े गए"
            })
            
            return {
                "success": True,
                "message": f"सफलतापूर्वक {command.amount} रुपये जोड़े गए",
                "new_balance": wallet.balance
            }
            
        except Exception as e:
            logger.error(f"Add money command failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def handle_deduct_money(command: DeductMoneyCommand) -> dict:
        """पैसे काटने का command handle करता है"""
        try:
            if command.user_id not in wallet_storage:
                raise ValueError("User का wallet नहीं मिला")
            
            wallet = wallet_storage[command.user_id]
            wallet.deduct_money(command.amount, command.purpose)
            
            # Transaction log में entry करते हैं
            transaction_log.append({
                "transaction_id": command.transaction_id or str(uuid.uuid4()),
                "user_id": command.user_id,
                "amount": command.amount,
                "type": "DEBIT",
                "purpose": command.purpose,
                "timestamp": datetime.now(),
                "description": f"{command.purpose} के लिए {command.amount} रुपये काटे गए"
            })
            
            return {
                "success": True,
                "message": f"सफलतापूर्वक {command.amount} रुपये काटे गए",
                "new_balance": wallet.balance
            }
            
        except Exception as e:
            logger.error(f"Deduct money command failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

# Query Handlers - Read operations handle करते हैं
class QueryHandler:
    
    @staticmethod
    async def handle_balance_query(query: BalanceQuery) -> BalanceResponse:
        """Balance का query handle करता है"""
        if query.user_id not in wallet_storage:
            raise HTTPException(status_code=404, detail="User का wallet नहीं मिला")
        
        wallet = wallet_storage[query.user_id]
        return BalanceResponse(
            user_id=wallet.user_id,
            balance=wallet.balance,
            last_updated=wallet.last_updated
        )
    
    @staticmethod
    async def handle_transaction_history_query(query: TransactionHistoryQuery) -> List[TransactionResponse]:
        """Transaction history का query handle करता है"""
        user_transactions = [
            tx for tx in transaction_log 
            if tx["user_id"] == query.user_id
        ]
        
        # Pagination apply करते हैं
        start = query.offset
        end = start + query.limit
        paginated_transactions = user_transactions[start:end]
        
        return [
            TransactionResponse(
                transaction_id=tx["transaction_id"],
                amount=tx["amount"],
                type=tx["type"],
                timestamp=tx["timestamp"],
                description=tx["description"]
            )
            for tx in paginated_transactions
        ]

# Command Endpoints - Write operations के लिए
@app.post("/commands/add-money")
async def add_money_endpoint(command: AddMoneyCommand):
    """पैसे जोड़ने का API endpoint"""
    return await CommandHandler.handle_add_money(command)

@app.post("/commands/deduct-money")
async def deduct_money_endpoint(command: DeductMoneyCommand):
    """पैसे काटने का API endpoint"""
    return await CommandHandler.handle_deduct_money(command)

# Query Endpoints - Read operations के लिए
@app.get("/queries/balance/{user_id}")
async def get_balance_endpoint(user_id: str) -> BalanceResponse:
    """Balance check करने का API endpoint"""
    query = BalanceQuery(user_id=user_id)
    return await QueryHandler.handle_balance_query(query)

@app.get("/queries/transactions/{user_id}")
async def get_transaction_history_endpoint(
    user_id: str, 
    limit: int = 50, 
    offset: int = 0
) -> List[TransactionResponse]:
    """Transaction history का API endpoint"""
    query = TransactionHistoryQuery(user_id=user_id, limit=limit, offset=offset)
    return await QueryHandler.handle_transaction_history_query(query)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "total_wallets": len(wallet_storage),
        "total_transactions": len(transaction_log),
        "message": "Paytm Wallet CQRS service चल रही है"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Test data - Demo के लिए
    print("Test data बना रहे हैं...")
    test_command = AddMoneyCommand(
        user_id="user_123",
        amount=1000.0,
        source="UPI"
    )
    
    # Async function को manually run करते हैं
    async def setup_test_data():
        await CommandHandler.handle_add_money(test_command)
        print("Test wallet तैयार है!")
    
    asyncio.run(setup_test_data())
    
    print("Server शुरू कर रहे हैं...")
    print("APIs available at:")
    print("- POST /commands/add-money")
    print("- POST /commands/deduct-money") 
    print("- GET /queries/balance/{user_id}")
    print("- GET /queries/transactions/{user_id}")
    print("- GET /health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)