"""
Event Sourcing Bank Account - SBI Digital Banking Example
यह example दिखाता है कि कैसे banking operations को events के साथ handle करते हैं
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Banking Event Types
class BankEventType(Enum):
    """Banking events के types"""
    ACCOUNT_OPENED = "ACCOUNT_OPENED"
    MONEY_DEPOSITED = "MONEY_DEPOSITED"
    MONEY_WITHDRAWN = "MONEY_WITHDRAWN"
    MONEY_TRANSFERRED = "MONEY_TRANSFERRED"
    INTEREST_CREDITED = "INTEREST_CREDITED"
    CHARGES_DEBITED = "CHARGES_DEBITED"
    ACCOUNT_BLOCKED = "ACCOUNT_BLOCKED"
    ACCOUNT_UNBLOCKED = "ACCOUNT_UNBLOCKED"
    ACCOUNT_CLOSED = "ACCOUNT_CLOSED"

class AccountStatus(Enum):
    """Account का status"""
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"

class TransactionType(Enum):
    """Transaction types"""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    INTEREST = "INTEREST"
    CHARGES = "CHARGES"

# Base Event Structure
@dataclass
class BankEvent:
    """Banking events का base structure"""
    event_id: str
    account_number: str
    event_type: BankEventType
    timestamp: datetime
    version: int
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# Specific Banking Events
class AccountOpenedEvent(BankEvent):
    """नया account खोला गया"""
    def __init__(self, account_number: str, customer_name: str, initial_deposit: Decimal,
                 account_type: str, branch_code: str, customer_id: str):
        super().__init__(
            event_id=str(uuid.uuid4()),
            account_number=account_number,
            event_type=BankEventType.ACCOUNT_OPENED,
            timestamp=datetime.now(),
            version=1,
            data={
                "customer_name": customer_name,
                "customer_id": customer_id,
                "account_type": account_type,  # SAVINGS, CURRENT, FIXED_DEPOSIT
                "initial_deposit": str(initial_deposit),
                "branch_code": branch_code,
                "interest_rate": "4.0",  # 4% per annum for savings
                "min_balance": "1000" if account_type == "SAVINGS" else "10000"
            },
            metadata={
                "channel": "branch",
                "officer_id": "EMP_001",
                "kyc_verified": True
            }
        )

class MoneyDepositedEvent(BankEvent):
    """पैसे deposit किए गए"""
    def __init__(self, account_number: str, amount: Decimal, deposit_mode: str,
                 reference_number: str = None, depositor_name: str = None):
        super().__init__(
            event_id=str(uuid.uuid4()),
            account_number=account_number,
            event_type=BankEventType.MONEY_DEPOSITED,
            timestamp=datetime.now(),
            version=1,
            data={
                "amount": str(amount),
                "deposit_mode": deposit_mode,  # CASH, CHEQUE, UPI, NEFT, RTGS
                "reference_number": reference_number or f"DEP_{uuid.uuid4().hex[:8]}",
                "depositor_name": depositor_name
            },
            metadata={
                "channel": "atm" if deposit_mode == "CASH" else "online",
                "location": "Mumbai_Andheri" if deposit_mode == "CASH" else "digital"
            }
        )

class MoneyWithdrawnEvent(BankEvent):
    """पैसे withdraw किए गए"""
    def __init__(self, account_number: str, amount: Decimal, withdrawal_mode: str,
                 atm_id: str = None, charges: Decimal = Decimal('0')):
        super().__init__(
            event_id=str(uuid.uuid4()),
            account_number=account_number,
            event_type=BankEventType.MONEY_WITHDRAWN,
            timestamp=datetime.now(),
            version=1,
            data={
                "amount": str(amount),
                "withdrawal_mode": withdrawal_mode,  # ATM, BRANCH, UPI
                "atm_id": atm_id,
                "charges": str(charges)
            },
            metadata={
                "daily_limit_used": str(amount),
                "remaining_limit": "45000"  # SBI daily limit is ₹50,000
            }
        )

class MoneyTransferredEvent(BankEvent):
    """Money transfer - outgoing"""
    def __init__(self, account_number: str, amount: Decimal, to_account: str,
                 to_bank: str, transfer_mode: str, reference_number: str):
        super().__init__(
            event_id=str(uuid.uuid4()),
            account_number=account_number,
            event_type=BankEventType.MONEY_TRANSFERRED,
            timestamp=datetime.now(),
            version=1,
            data={
                "amount": str(amount),
                "to_account": to_account,
                "to_bank": to_bank,
                "transfer_mode": transfer_mode,  # UPI, NEFT, RTGS, IMPS
                "reference_number": reference_number,
                "charges": "5" if transfer_mode == "NEFT" else "25" if transfer_mode == "RTGS" else "0"
            },
            metadata={
                "beneficiary_verified": True,
                "fraud_check_passed": True
            }
        )

# Bank Account Aggregate
class BankAccount:
    """SBI Bank Account - Event Sourced"""
    
    def __init__(self, account_number: str):
        self.account_number = account_number
        self.version = 0
        
        # Current state fields
        self.customer_name = ""
        self.customer_id = ""
        self.account_type = ""
        self.branch_code = ""
        self.balance = Decimal('0')
        self.status = AccountStatus.ACTIVE
        self.interest_rate = Decimal('0')
        self.min_balance = Decimal('0')
        self.created_at = None
        self.last_transaction_at = None
        
        # Statistics
        self.total_deposits = Decimal('0')
        self.total_withdrawals = Decimal('0')
        self.transaction_count = 0
        
        # Uncommitted events
        self.uncommitted_events: List[BankEvent] = []
    
    def open_account(self, customer_name: str, customer_id: str, initial_deposit: Decimal,
                    account_type: str, branch_code: str):
        """नया account खोलता है"""
        if self.version > 0:
            raise ValueError("Account पहले से खुला है")
        
        if initial_deposit < Decimal('1000'):
            raise ValueError("न्यूनतम ₹1,000 की जमा राशि आवश्यक है")
        
        event = AccountOpenedEvent(
            self.account_number, customer_name, initial_deposit,
            account_type, branch_code, customer_id
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        # Initial deposit event भी add करते हैं
        deposit_event = MoneyDepositedEvent(
            self.account_number, initial_deposit, "CASH", 
            f"INITIAL_DEP_{uuid.uuid4().hex[:8]}", customer_name
        )
        
        self._apply_event(deposit_event)
        self.uncommitted_events.append(deposit_event)
    
    def deposit_money(self, amount: Decimal, deposit_mode: str, 
                     depositor_name: str = None) -> str:
        """पैसे deposit करता है"""
        if self.status != AccountStatus.ACTIVE:
            raise ValueError(f"Account {self.status.value} है, transaction नहीं कर सकते")
        
        if amount <= 0:
            raise ValueError("Deposit amount शून्य से अधिक होना चाहिए")
        
        # Cash deposit के लिए limit check करते हैं
        if deposit_mode == "CASH" and amount > Decimal('200000'):
            raise ValueError("Cash deposit की दैनिक सीमा ₹2,00,000 है")
        
        event = MoneyDepositedEvent(
            self.account_number, amount, deposit_mode, 
            depositor_name=depositor_name or self.customer_name
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        return event.data["reference_number"]
    
    def withdraw_money(self, amount: Decimal, withdrawal_mode: str, 
                      atm_id: str = None) -> str:
        """पैसे withdraw करता है"""
        if self.status != AccountStatus.ACTIVE:
            raise ValueError(f"Account {self.status.value} है, transaction नहीं कर सकते")
        
        if amount <= 0:
            raise ValueError("Withdrawal amount शून्य से अधिक होना चाहिए")
        
        # Charges calculate करते हैं
        charges = Decimal('0')
        if withdrawal_mode == "ATM" and atm_id and not atm_id.startswith("SBI"):
            charges = Decimal('21')  # Other bank ATM charges
        
        total_deduction = amount + charges
        
        # Balance check करते हैं
        if self.balance < total_deduction:
            raise ValueError(f"Insufficient balance. Available: ₹{self.balance}")
        
        # Minimum balance check करते हैं
        if (self.balance - total_deduction) < self.min_balance:
            raise ValueError(f"Minimum balance ₹{self.min_balance} maintain करना आवश्यक है")
        
        # Daily limit check करते हैं
        if withdrawal_mode == "ATM" and amount > Decimal('50000'):
            raise ValueError("ATM daily limit ₹50,000 है")
        
        event = MoneyWithdrawnEvent(
            self.account_number, amount, withdrawal_mode, atm_id, charges
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        return event.event_id
    
    def transfer_money(self, amount: Decimal, to_account: str, to_bank: str,
                      transfer_mode: str, beneficiary_name: str) -> str:
        """दूसरे account में पैसे transfer करता है"""
        if self.status != AccountStatus.ACTIVE:
            raise ValueError(f"Account {self.status.value} है, transaction नहीं कर सकते")
        
        if amount <= 0:
            raise ValueError("Transfer amount शून्य से अधिक होना चाहिए")
        
        # Transfer charges calculate करते हैं
        charges = Decimal('0')
        if transfer_mode == "NEFT":
            charges = Decimal('5')
        elif transfer_mode == "RTGS":
            charges = Decimal('25')
            if amount < Decimal('200000'):
                raise ValueError("RTGS minimum amount ₹2,00,000 है")
        
        total_deduction = amount + charges
        
        # Balance और minimum balance check करते हैं
        if self.balance < total_deduction:
            raise ValueError(f"Insufficient balance. Available: ₹{self.balance}")
        
        if (self.balance - total_deduction) < self.min_balance:
            raise ValueError(f"Minimum balance ₹{self.min_balance} maintain करना आवश्यक है")
        
        reference_number = f"{transfer_mode}_{uuid.uuid4().hex[:12].upper()}"
        
        event = MoneyTransferredEvent(
            self.account_number, amount, to_account, to_bank,
            transfer_mode, reference_number
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
        
        return reference_number
    
    def credit_interest(self, interest_amount: Decimal, period: str):
        """Interest credit करता है"""
        if interest_amount <= 0:
            return
        
        event = BankEvent(
            event_id=str(uuid.uuid4()),
            account_number=self.account_number,
            event_type=BankEventType.INTEREST_CREDITED,
            timestamp=datetime.now(),
            version=self.version + 1,
            data={
                "amount": str(interest_amount),
                "period": period,
                "interest_rate": str(self.interest_rate),
                "calculation_method": "daily_balance"
            },
            metadata={
                "system_generated": True,
                "processor": "interest_calculation_batch"
            }
        )
        
        self._apply_event(event)
        self.uncommitted_events.append(event)
    
    def _apply_event(self, event: BankEvent):
        """Event को current state पर apply करता है"""
        
        if event.event_type == BankEventType.ACCOUNT_OPENED:
            self.customer_name = event.data["customer_name"]
            self.customer_id = event.data["customer_id"]
            self.account_type = event.data["account_type"]
            self.branch_code = event.data["branch_code"]
            self.interest_rate = Decimal(event.data["interest_rate"])
            self.min_balance = Decimal(event.data["min_balance"])
            self.created_at = event.timestamp
            self.status = AccountStatus.ACTIVE
            
        elif event.event_type == BankEventType.MONEY_DEPOSITED:
            amount = Decimal(event.data["amount"])
            self.balance += amount
            self.total_deposits += amount
            self.last_transaction_at = event.timestamp
            self.transaction_count += 1
            
        elif event.event_type == BankEventType.MONEY_WITHDRAWN:
            amount = Decimal(event.data["amount"])
            charges = Decimal(event.data.get("charges", "0"))
            self.balance -= (amount + charges)
            self.total_withdrawals += amount
            self.last_transaction_at = event.timestamp
            self.transaction_count += 1
            
        elif event.event_type == BankEventType.MONEY_TRANSFERRED:
            amount = Decimal(event.data["amount"])
            charges = Decimal(event.data.get("charges", "0"))
            self.balance -= (amount + charges)
            self.total_withdrawals += amount
            self.last_transaction_at = event.timestamp
            self.transaction_count += 1
            
        elif event.event_type == BankEventType.INTEREST_CREDITED:
            amount = Decimal(event.data["amount"])
            self.balance += amount
            self.total_deposits += amount
            self.last_transaction_at = event.timestamp
            
        elif event.event_type == BankEventType.ACCOUNT_BLOCKED:
            self.status = AccountStatus.BLOCKED
            
        elif event.event_type == BankEventType.ACCOUNT_UNBLOCKED:
            self.status = AccountStatus.ACTIVE
            
        elif event.event_type == BankEventType.ACCOUNT_CLOSED:
            self.status = AccountStatus.CLOSED
        
        self.version += 1
    
    def load_from_history(self, events: List[BankEvent]):
        """Event history से account state rebuild करता है"""
        for event in sorted(events, key=lambda e: e.version):
            self._apply_event(event)
        self.uncommitted_events = []
    
    def get_uncommitted_events(self) -> List[BankEvent]:
        """अभी तक save नहीं हुए events return करता है"""
        return self.uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Events को committed mark करता है"""
        self.uncommitted_events.clear()
    
    def get_account_summary(self) -> Dict:
        """Account का summary return करता है"""
        return {
            "account_number": self.account_number,
            "customer_name": self.customer_name,
            "account_type": self.account_type,
            "current_balance": str(self.balance),
            "status": self.status.value,
            "total_deposits": str(self.total_deposits),
            "total_withdrawals": str(self.total_withdrawals),
            "transaction_count": self.transaction_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_transaction_at": self.last_transaction_at.isoformat() if self.last_transaction_at else None
        }

# Event Store for Banking
class BankingEventStore:
    """Banking events के लिए specialized event store"""
    
    def __init__(self, db_path: str = "sbi_banking.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Database setup करता है"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS banking_events (
                    event_id TEXT PRIMARY KEY,
                    account_number TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_account_number (account_number),
                    INDEX idx_event_type (event_type),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS account_snapshots (
                    account_number TEXT PRIMARY KEY,
                    version INTEGER NOT NULL,
                    balance TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        logger.info("Banking Event Store initialized")
    
    async def append_event(self, event: BankEvent) -> bool:
        """Event को store में save करता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO banking_events 
                    (event_id, account_number, event_type, timestamp, version, data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.account_number,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    event.version,
                    json.dumps(event.data),
                    json.dumps(event.metadata) if event.metadata else None
                ))
            
            logger.info(f"Banking event stored: {event.event_type.value} for account {event.account_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store banking event: {str(e)}")
            raise
    
    async def get_account_events(self, account_number: str) -> List[BankEvent]:
        """Account के सभी events retrieve करता है"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM banking_events 
                    WHERE account_number = ?
                    ORDER BY version ASC
                """, (account_number,))
                
                events = []
                for row in cursor.fetchall():
                    event = BankEvent(
                        event_id=row['event_id'],
                        account_number=row['account_number'],
                        event_type=BankEventType(row['event_type']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        version=row['version'],
                        data=json.loads(row['data']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get account events: {str(e)}")
            raise

# Banking Repository
class BankAccountRepository:
    """Bank Account के लिए repository"""
    
    def __init__(self, event_store: BankingEventStore):
        self.event_store = event_store
    
    async def save(self, account: BankAccount):
        """Account के events को save करता है"""
        uncommitted_events = account.get_uncommitted_events()
        
        for event in uncommitted_events:
            await self.event_store.append_event(event)
        
        account.mark_events_as_committed()
        logger.info(f"Saved {len(uncommitted_events)} events for account {account.account_number}")
    
    async def get_by_account_number(self, account_number: str) -> Optional[BankAccount]:
        """Account number से account load करता है"""
        events = await self.event_store.get_account_events(account_number)
        
        if not events:
            return None
        
        account = BankAccount(account_number)
        account.load_from_history(events)
        
        return account

# Demo और Testing
async def demo_sbi_banking():
    """SBI Banking का comprehensive demo"""
    print("🏦 SBI Digital Banking Event Sourcing Demo")
    print("=" * 60)
    
    # Setup
    event_store = BankingEventStore("sbi_demo.db")
    repository = BankAccountRepository(event_store)
    
    # नया account खोलते हैं
    account_number = f"SBI{uuid.uuid4().hex[:10].upper()}"
    account = BankAccount(account_number)
    
    print(f"\n📝 Account Opening Process")
    print(f"Account Number: {account_number}")
    
    account.open_account(
        customer_name="राहुल शर्मा",
        customer_id="AADHAAR_123456789012",
        initial_deposit=Decimal('25000'),
        account_type="SAVINGS",
        branch_code="SBI_ANDHERI_001"
    )
    
    await repository.save(account)
    print(f"✅ Account opened with ₹25,000 initial deposit")
    
    # Multiple transactions करते हैं
    print(f"\n💰 Transaction Processing")
    
    # Salary deposit
    ref1 = account.deposit_money(Decimal('75000'), "NEFT", "Infosys Ltd")
    print(f"📥 Salary deposited: ₹75,000 (Ref: {ref1})")
    
    # ATM withdrawal
    txn1 = account.withdraw_money(Decimal('5000'), "ATM", "SBI_ATM_12345")
    print(f"🏧 ATM withdrawal: ₹5,000")
    
    # UPI payment for groceries
    ref2 = account.transfer_money(
        Decimal('2500'), "9876543210@paytm", "PAYTM_BANK", 
        "UPI", "BigBasket"
    )
    print(f"📱 UPI payment: ₹2,500 to BigBasket")
    
    # NEFT transfer to family
    ref3 = account.transfer_money(
        Decimal('15000'), "1234567890", "HDFC_BANK",
        "NEFT", "Priya Sharma"
    )
    print(f"🏦 NEFT transfer: ₹15,000 to family member")
    
    # Interest credit (quarterly)
    quarterly_interest = (account.balance * account.interest_rate / 100) / 4
    account.credit_interest(quarterly_interest, "Q4_2024")
    print(f"💎 Interest credited: ₹{quarterly_interest:.2f}")
    
    await repository.save(account)
    
    # Account summary display करते हैं
    print(f"\n📊 Account Summary")
    summary = account.get_account_summary()
    print(f"Customer: {summary['customer_name']}")
    print(f"Account Type: {summary['account_type']}")
    print(f"Current Balance: ₹{summary['current_balance']}")
    print(f"Total Deposits: ₹{summary['total_deposits']}")
    print(f"Total Withdrawals: ₹{summary['total_withdrawals']}")
    print(f"Total Transactions: {summary['transaction_count']}")
    print(f"Account Status: {summary['status']}")
    
    # Event history display करते हैं
    print(f"\n📜 Transaction History (Event Sourced)")
    events = await event_store.get_account_events(account_number)
    
    for i, event in enumerate(events, 1):
        event_time = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i:2d}. [{event_time}] {event.event_type.value}")
        
        if event.event_type == BankEventType.MONEY_DEPOSITED:
            amount = event.data['amount']
            mode = event.data['deposit_mode']
            print(f"    💰 Deposited ₹{amount} via {mode}")
            
        elif event.event_type == BankEventType.MONEY_WITHDRAWN:
            amount = event.data['amount']
            mode = event.data['withdrawal_mode']
            charges = event.data.get('charges', '0')
            print(f"    💸 Withdrew ₹{amount} via {mode} (Charges: ₹{charges})")
            
        elif event.event_type == BankEventType.MONEY_TRANSFERRED:
            amount = event.data['amount']
            to_account = event.data['to_account']
            mode = event.data['transfer_mode']
            print(f"    🔄 Transferred ₹{amount} to {to_account} via {mode}")
            
        elif event.event_type == BankEventType.INTEREST_CREDITED:
            amount = event.data['amount']
            period = event.data['period']
            print(f"    💎 Interest ₹{amount} for {period}")
    
    # Account को दोबारा load करके verify करते हैं
    print(f"\n🔄 Account Reconstruction from Events")
    reconstructed_account = await repository.get_by_account_number(account_number)
    
    if reconstructed_account:
        reconstructed_summary = reconstructed_account.get_account_summary()
        print(f"✅ Account reconstructed successfully")
        print(f"Balance matches: {summary['current_balance'] == reconstructed_summary['current_balance']}")
        print(f"Transaction count matches: {summary['transaction_count'] == reconstructed_summary['transaction_count']}")
    
    return account

async def demo_compliance_reporting():
    """Compliance और reporting के लिए event sourcing का use"""
    print("\n" + "="*60)
    print("📋 Compliance & Regulatory Reporting Demo")
    print("="*60)
    
    event_store = BankingEventStore("sbi_demo.db")
    
    # High-value transactions report करते हैं
    print(f"\n🔍 High-Value Transactions (>₹50,000)")
    
    with sqlite3.connect(event_store.db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT account_number, event_type, data, timestamp 
            FROM banking_events 
            WHERE event_type IN ('MONEY_DEPOSITED', 'MONEY_TRANSFERRED')
            AND json_extract(data, '$.amount') > '50000'
            ORDER BY timestamp DESC
        """)
        
        for row in cursor.fetchall():
            data = json.loads(row['data'])
            amount = data['amount']
            event_time = row['timestamp']
            
            print(f"⚠️  {row['account_number']}: ₹{amount} on {event_time}")
            
            if row['event_type'] == 'MONEY_TRANSFERRED':
                to_account = data.get('to_account', 'Unknown')
                print(f"   → Transferred to: {to_account}")
    
    print(f"\n✅ Compliance report generated from immutable event history")

if __name__ == "__main__":
    import asyncio
    
    print("Event Sourcing Bank Account Demo")
    print("="*50)
    
    # Main banking demo
    asyncio.run(demo_sbi_banking())
    
    # Compliance demo
    asyncio.run(demo_compliance_reporting())