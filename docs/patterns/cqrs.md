# CQRS (Command/Query Responsibility Segregation)

**Read and write paths have different needs**

## THE PROBLEM

```
Traditional CRUD couples opposing forces:
- Writes need: Consistency, validation, audit
- Reads need: Speed, denormalization, caching

One model can't optimize both!
```

## THE SOLUTION

```
Separate models for separate concerns:

Commands (Writes)          Queries (Reads)
    ↓                          ↑
Domain Model              Read Models
    ↓                          ↑
Event Store     →→→→→     Projections
                Async
```

## IMPLEMENTATION

```python
# Command side - rich domain model
class BankAccount:
    def __init__(self, account_id):
        self.id = account_id
        self.balance = 0
        self.events = []
        
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        event = DepositedEvent(self.id, amount, timestamp=now())
        self._apply(event)
        return event
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds()
            
        event = WithdrewEvent(self.id, amount, timestamp=now())
        self._apply(event)
        return event
    
    def _apply(self, event):
        if isinstance(event, DepositedEvent):
            self.balance += event.amount
        elif isinstance(event, WithdrewEvent):
            self.balance -= event.amount
            
        self.events.append(event)

# Query side - denormalized for reads
class AccountReadModel:
    def __init__(self):
        self.accounts_by_id = {}
        self.high_value_accounts = []
        self.recent_transactions = deque(maxlen=1000)
        
    def apply_event(self, event):
        # Update multiple projections
        account_id = event.account_id
        
        # Projection 1: Current balances
        if account_id not in self.accounts_by_id:
            self.accounts_by_id[account_id] = {
                'balance': 0,
                'last_activity': None
            }
            
        account = self.accounts_by_id[account_id]
        
        if isinstance(event, DepositedEvent):
            account['balance'] += event.amount
        elif isinstance(event, WithdrewEvent):
            account['balance'] -= event.amount
            
        account['last_activity'] = event.timestamp
        
        # Projection 2: High value accounts
        if account['balance'] > 100000:
            if account_id not in self.high_value_accounts:
                self.high_value_accounts.append(account_id)
        else:
            if account_id in self.high_value_accounts:
                self.high_value_accounts.remove(account_id)
                
        # Projection 3: Recent activity
        self.recent_transactions.append({
            'account': account_id,
            'type': type(event).__name__,
            'amount': event.amount,
            'timestamp': event.timestamp
        })

# CQRS Command Handler
class CommandHandler:
    def __init__(self, event_store, event_bus):
        self.event_store = event_store
        self.event_bus = event_bus
        
    def handle_deposit(self, account_id, amount):
        # Load aggregate
        events = self.event_store.get_events(account_id)
        account = BankAccount(account_id)
        for event in events:
            account._apply(event)
            
        # Execute command
        event = account.deposit(amount)
        
        # Persist event
        self.event_store.append(account_id, event)
        
        # Publish for read model updates
        self.event_bus.publish(event)
        
        return {'status': 'success', 'new_balance': account.balance}

# CQRS Query Handler  
class QueryHandler:
    def __init__(self, read_model):
        self.read_model = read_model
        
    def get_balance(self, account_id):
        account = self.read_model.accounts_by_id.get(account_id)
        if not account:
            return None
        return account['balance']
    
    def get_high_value_accounts(self):
        return [
            {
                'id': acc_id,
                'balance': self.read_model.accounts_by_id[acc_id]['balance']
            }
            for acc_id in self.read_model.high_value_accounts
        ]
    
    def get_recent_activity(self, limit=100):
        return list(self.read_model.recent_transactions)[-limit:]
```

## Advanced: Multiple Read Models

```python
class CQRSSystem:
    def __init__(self):
        self.event_store = EventStore()
        self.read_models = {
            'account_balance': AccountBalanceProjection(),
            'transaction_history': TransactionHistoryProjection(),
            'risk_analysis': RiskAnalysisProjection(),
            'reporting': ReportingProjection()
        }
        
    def project_event(self, event):
        # Fan out to all projections
        for name, projection in self.read_models.items():
            try:
                projection.apply(event)
            except Exception as e:
                print(f"Projection {name} failed: {e}")
                # Log but don't fail others
```

## ✓ CHOOSE THIS WHEN:
• Read/write patterns differ significantly
• Need multiple read representations  
• Complex queries on large datasets
• Event sourcing architecture
• Read scaling independent of writes

## ⚠️ BEWARE OF:
• Eventual consistency complexity
• Projection lag monitoring
• Storage duplication costs
• Debugging across models
• Schema evolution pain

## REAL EXAMPLES
• **Amazon**: Product catalog vs inventory
• **Banking**: Transactions vs statements  
• **LinkedIn**: Profile edits vs search