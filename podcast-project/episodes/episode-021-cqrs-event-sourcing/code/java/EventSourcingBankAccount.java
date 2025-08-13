/*
 * Episode 21: CQRS/Event Sourcing - Event Sourcing Bank Account
 * Author: Code Developer Agent
 * Description: Production-ready Event Sourcing implementation for Indian banking
 * 
 * Event Sourcing में हम सिर्फ events store करते हैं, current state नहीं
 * यह approach banking में बहुत important है audit trail के लिए
 */

package com.flipkart.eventsourcing;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

// Base Event class
abstract class DomainEvent {
    private final String eventId;
    private final String aggregateId;
    private final LocalDateTime occurredOn;
    private final int version;

    public DomainEvent(String aggregateId, int version) {
        this.eventId = UUID.randomUUID().toString();
        this.aggregateId = aggregateId;
        this.occurredOn = LocalDateTime.now();
        this.version = version;
    }

    // Getters
    public String getEventId() { return eventId; }
    public String getAggregateId() { return aggregateId; }
    public LocalDateTime getOccurredOn() { return occurredOn; }
    public int getVersion() { return version; }
}

// Banking Domain Events
class AccountOpenedEvent extends DomainEvent {
    private final String customerId;
    private final String accountNumber;
    private final String ifscCode;
    private final String bankName;

    public AccountOpenedEvent(String aggregateId, int version, String customerId, 
                             String accountNumber, String ifscCode, String bankName) {
        super(aggregateId, version);
        this.customerId = customerId;
        this.accountNumber = accountNumber;
        this.ifscCode = ifscCode;
        this.bankName = bankName;
    }

    public String getCustomerId() { return customerId; }
    public String getAccountNumber() { return accountNumber; }
    public String getIfscCode() { return ifscCode; }
    public String getBankName() { return bankName; }
}

class MoneyDepositedEvent extends DomainEvent {
    private final BigDecimal amount;
    private final String transactionId;
    private final String depositMethod; // CASH, CHEQUE, UPI, NEFT
    private final String reference;

    public MoneyDepositedEvent(String aggregateId, int version, BigDecimal amount,
                              String transactionId, String depositMethod, String reference) {
        super(aggregateId, version);
        this.amount = amount;
        this.transactionId = transactionId;
        this.depositMethod = depositMethod;
        this.reference = reference;
    }

    public BigDecimal getAmount() { return amount; }
    public String getTransactionId() { return transactionId; }
    public String getDepositMethod() { return depositMethod; }
    public String getReference() { return reference; }
}

class MoneyWithdrawnEvent extends DomainEvent {
    private final BigDecimal amount;
    private final String transactionId;
    private final String withdrawalMethod; // ATM, BRANCH, UPI
    private final String reference;

    public MoneyWithdrawnEvent(String aggregateId, int version, BigDecimal amount,
                              String transactionId, String withdrawalMethod, String reference) {
        super(aggregateId, version);
        this.amount = amount;
        this.transactionId = transactionId;
        this.withdrawalMethod = withdrawalMethod;
        this.reference = reference;
    }

    public BigDecimal getAmount() { return amount; }
    public String getTransactionId() { return transactionId; }
    public String getWithdrawalMethod() { return withdrawalMethod; }
    public String getReference() { return reference; }
}

class AccountFrozenEvent extends DomainEvent {
    private final String reason;
    private final String frozenBy;

    public AccountFrozenEvent(String aggregateId, int version, String reason, String frozenBy) {
        super(aggregateId, version);
        this.reason = reason;
        this.frozenBy = frozenBy;
    }

    public String getReason() { return reason; }
    public String getFrozenBy() { return frozenBy; }
}

class AccountUnfrozenEvent extends DomainEvent {
    private final String reason;
    private final String unfrozenBy;

    public AccountUnfrozenEvent(String aggregateId, int version, String reason, String unfrozenBy) {
        super(aggregateId, version);
        this.reason = reason;
        this.unfrozenBy = unfrozenBy;
    }

    public String getReason() { return reason; }
    public String getUnfrozenBy() { return unfrozenBy; }
}

// Bank Account Aggregate - Event Sourced
class BankAccount {
    private String accountId;
    private String customerId;
    private String accountNumber;
    private String ifscCode;
    private String bankName;
    private BigDecimal balance;
    private boolean isFrozen;
    private LocalDateTime openedOn;
    private int version;
    
    private List<DomainEvent> uncommittedEvents;

    // Constructor for new account
    public BankAccount() {
        this.balance = BigDecimal.ZERO;
        this.isFrozen = false;
        this.version = 0;
        this.uncommittedEvents = new ArrayList<>();
    }

    // Constructor for event replay
    public BankAccount(String accountId, List<DomainEvent> events) {
        this();
        this.accountId = accountId;
        this.replayEvents(events);
    }

    // Command methods - ये business operations हैं
    public void openAccount(String customerId, String accountNumber, String ifscCode, String bankName) {
        if (this.accountId != null) {
            throw new IllegalStateException("Account is already opened");
        }

        this.accountId = UUID.randomUUID().toString();
        
        AccountOpenedEvent event = new AccountOpenedEvent(
            this.accountId, 
            this.version + 1, 
            customerId, 
            accountNumber, 
            ifscCode, 
            bankName
        );
        
        this.applyEvent(event);
    }

    public void depositMoney(BigDecimal amount, String depositMethod, String reference) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive");
        }

        if (this.isFrozen) {
            throw new IllegalStateException("Cannot deposit to frozen account");
        }

        String transactionId = generateTransactionId("DEP");
        
        MoneyDepositedEvent event = new MoneyDepositedEvent(
            this.accountId,
            this.version + 1,
            amount,
            transactionId,
            depositMethod,
            reference
        );
        
        this.applyEvent(event);
    }

    public void withdrawMoney(BigDecimal amount, String withdrawalMethod, String reference) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive");
        }

        if (this.isFrozen) {
            throw new IllegalStateException("Cannot withdraw from frozen account");
        }

        if (this.balance.compareTo(amount) < 0) {
            throw new IllegalStateException("Insufficient balance. Available: ₹" + this.balance);
        }

        String transactionId = generateTransactionId("WTH");
        
        MoneyWithdrawnEvent event = new MoneyWithdrawnEvent(
            this.accountId,
            this.version + 1,
            amount,
            transactionId,
            withdrawalMethod,
            reference
        );
        
        this.applyEvent(event);
    }

    public void freezeAccount(String reason, String frozenBy) {
        if (this.isFrozen) {
            throw new IllegalStateException("Account is already frozen");
        }

        AccountFrozenEvent event = new AccountFrozenEvent(
            this.accountId,
            this.version + 1,
            reason,
            frozenBy
        );
        
        this.applyEvent(event);
    }

    public void unfreezeAccount(String reason, String unfrozenBy) {
        if (!this.isFrozen) {
            throw new IllegalStateException("Account is not frozen");
        }

        AccountUnfrozenEvent event = new AccountUnfrozenEvent(
            this.accountId,
            this.version + 1,
            reason,
            unfrozenBy
        );
        
        this.applyEvent(event);
    }

    // Event application methods - ये state changes करते हैं
    private void applyEvent(DomainEvent event) {
        // State को update करें based on event type
        if (event instanceof AccountOpenedEvent) {
            applyAccountOpened((AccountOpenedEvent) event);
        } else if (event instanceof MoneyDepositedEvent) {
            applyMoneyDeposited((MoneyDepositedEvent) event);
        } else if (event instanceof MoneyWithdrawnEvent) {
            applyMoneyWithdrawn((MoneyWithdrawnEvent) event);
        } else if (event instanceof AccountFrozenEvent) {
            applyAccountFrozen((AccountFrozenEvent) event);
        } else if (event instanceof AccountUnfrozenEvent) {
            applyAccountUnfrozen((AccountUnfrozenEvent) event);
        }

        this.version = event.getVersion();
        this.uncommittedEvents.add(event);
    }

    private void applyAccountOpened(AccountOpenedEvent event) {
        this.customerId = event.getCustomerId();
        this.accountNumber = event.getAccountNumber();
        this.ifscCode = event.getIfscCode();
        this.bankName = event.getBankName();
        this.openedOn = event.getOccurredOn();
    }

    private void applyMoneyDeposited(MoneyDepositedEvent event) {
        this.balance = this.balance.add(event.getAmount());
    }

    private void applyMoneyWithdrawn(MoneyWithdrawnEvent event) {
        this.balance = this.balance.subtract(event.getAmount());
    }

    private void applyAccountFrozen(AccountFrozenEvent event) {
        this.isFrozen = true;
    }

    private void applyAccountUnfrozen(AccountUnfrozenEvent event) {
        this.isFrozen = false;
    }

    // Event replay - यह method historical events से state rebuild करता है
    private void replayEvents(List<DomainEvent> events) {
        for (DomainEvent event : events) {
            this.applyEvent(event);
        }
        
        // Clear uncommitted events because ये historical हैं
        this.uncommittedEvents.clear();
    }

    // Helper methods
    private String generateTransactionId(String prefix) {
        return prefix + System.currentTimeMillis() + 
               String.format("%04d", new Random().nextInt(10000));
    }

    // Getters
    public String getAccountId() { return accountId; }
    public String getCustomerId() { return customerId; }
    public String getAccountNumber() { return accountNumber; }
    public String getIfscCode() { return ifscCode; }
    public String getBankName() { return bankName; }
    public BigDecimal getBalance() { return balance; }
    public boolean isFrozen() { return isFrozen; }
    public LocalDateTime getOpenedOn() { return openedOn; }
    public int getVersion() { return version; }
    
    public List<DomainEvent> getUncommittedEvents() {
        return new ArrayList<>(uncommittedEvents);
    }
    
    public void markEventsAsCommitted() {
        this.uncommittedEvents.clear();
    }
}

// Event Store - Events को store करने के लिए
class EventStore {
    private final Map<String, List<DomainEvent>> eventStreams;

    public EventStore() {
        this.eventStreams = new ConcurrentHashMap<>();
    }

    public void saveEvents(String aggregateId, List<DomainEvent> events, int expectedVersion) {
        List<DomainEvent> existingEvents = eventStreams.getOrDefault(aggregateId, new ArrayList<>());
        
        // Optimistic concurrency check
        if (existingEvents.size() != expectedVersion) {
            throw new IllegalStateException(
                String.format("Concurrency conflict for aggregate %s. Expected version: %d, Actual: %d",
                            aggregateId, expectedVersion, existingEvents.size())
            );
        }

        // Events को append करें
        List<DomainEvent> newEventStream = new ArrayList<>(existingEvents);
        newEventStream.addAll(events);
        
        eventStreams.put(aggregateId, newEventStream);
        
        System.out.println(String.format("📝 Saved %d events for aggregate %s", 
                                        events.size(), aggregateId));
    }

    public List<DomainEvent> getEvents(String aggregateId) {
        return new ArrayList<>(eventStreams.getOrDefault(aggregateId, new ArrayList<>()));
    }

    public List<DomainEvent> getEventsByType(Class<? extends DomainEvent> eventType) {
        return eventStreams.values().stream()
                .flatMap(List::stream)
                .filter(event -> eventType.isInstance(event))
                .collect(Collectors.toList());
    }
}

// Repository for Bank Account
class BankAccountRepository {
    private final EventStore eventStore;

    public BankAccountRepository(EventStore eventStore) {
        this.eventStore = eventStore;
    }

    public void save(BankAccount account) {
        List<DomainEvent> uncommittedEvents = account.getUncommittedEvents();
        
        if (!uncommittedEvents.isEmpty()) {
            int expectedVersion = account.getVersion() - uncommittedEvents.size();
            
            eventStore.saveEvents(account.getAccountId(), uncommittedEvents, expectedVersion);
            account.markEventsAsCommitted();
        }
    }

    public BankAccount getById(String accountId) {
        List<DomainEvent> events = eventStore.getEvents(accountId);
        
        if (events.isEmpty()) {
            return null;
        }

        return new BankAccount(accountId, events);
    }
}

// Demo class
public class EventSourcingBankAccount {
    
    public static void main(String[] args) {
        System.out.println("🏦 Indian Banking Event Sourcing Demo");
        System.out.println("=".repeat(50));
        
        // Setup
        EventStore eventStore = new EventStore();
        BankAccountRepository repository = new BankAccountRepository(eventStore);
        
        try {
            // 1. नया bank account खोलें
            System.out.println("\n👤 Opening new bank account...");
            BankAccount account = new BankAccount();
            account.openAccount(
                "CUST001", 
                "1234567890123456", 
                "HDFC0000123", 
                "HDFC Bank"
            );
            repository.save(account);
            String accountId = account.getAccountId();
            
            // 2. Money deposit करें
            System.out.println("\n💰 Depositing money...");
            account = repository.getById(accountId);
            account.depositMoney(new BigDecimal("50000"), "UPI", "Salary Credit");
            account.depositMoney(new BigDecimal("10000"), "CHEQUE", "Bonus Payment");
            repository.save(account);
            
            System.out.println("Balance after deposits: ₹" + account.getBalance());
            
            // 3. Money withdraw करें
            System.out.println("\n🏧 Withdrawing money...");
            account = repository.getById(accountId);
            account.withdrawMoney(new BigDecimal("5000"), "ATM", "Cash Withdrawal");
            account.withdrawMoney(new BigDecimal("15000"), "UPI", "Flipkart Purchase");
            repository.save(account);
            
            System.out.println("Balance after withdrawals: ₹" + account.getBalance());
            
            // 4. Account को freeze करें
            System.out.println("\n🔒 Freezing account...");
            account = repository.getById(accountId);
            account.freezeAccount("Suspicious activity detected", "SYSTEM");
            repository.save(account);
            
            // 5. Frozen account से transaction try करें
            System.out.println("\n❌ Trying to withdraw from frozen account...");
            try {
                account = repository.getById(accountId);
                account.withdrawMoney(new BigDecimal("1000"), "UPI", "Test Transaction");
            } catch (IllegalStateException e) {
                System.out.println("Transaction failed: " + e.getMessage());
            }
            
            // 6. Account को unfreeze करें
            System.out.println("\n🔓 Unfreezing account...");
            account = repository.getById(accountId);
            account.unfreezeAccount("Manual review completed", "ADMIN");
            repository.save(account);
            
            // 7. Event history check करें
            System.out.println("\n📊 Account Event History:");
            List<DomainEvent> allEvents = eventStore.getEvents(accountId);
            for (int i = 0; i < allEvents.size(); i++) {
                DomainEvent event = allEvents.get(i);
                System.out.println(String.format("  %d. %s (v%d) - %s", 
                    i + 1, 
                    event.getClass().getSimpleName(),
                    event.getVersion(),
                    event.getOccurredOn().toString()
                ));
            }
            
            // 8. Final account state
            System.out.println("\n🏦 Final Account State:");
            account = repository.getById(accountId);
            System.out.println("Account Number: " + account.getAccountNumber());
            System.out.println("IFSC Code: " + account.getIfscCode());
            System.out.println("Bank: " + account.getBankName());
            System.out.println("Balance: ₹" + account.getBalance());
            System.out.println("Status: " + (account.isFrozen() ? "FROZEN" : "ACTIVE"));
            System.out.println("Total Events: " + allEvents.size());
            
            // 9. Event type analysis
            System.out.println("\n📈 Transaction Analysis:");
            List<DomainEvent> deposits = eventStore.getEventsByType(MoneyDepositedEvent.class);
            List<DomainEvent> withdrawals = eventStore.getEventsByType(MoneyWithdrawnEvent.class);
            
            BigDecimal totalDeposits = deposits.stream()
                .map(e -> ((MoneyDepositedEvent) e).getAmount())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
                
            BigDecimal totalWithdrawals = withdrawals.stream()
                .map(e -> ((MoneyWithdrawnEvent) e).getAmount())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            
            System.out.println("Total Deposits: ₹" + totalDeposits + " (" + deposits.size() + " transactions)");
            System.out.println("Total Withdrawals: ₹" + totalWithdrawals + " (" + withdrawals.size() + " transactions)");
            
            System.out.println("\n✅ Event Sourcing Demo completed successfully!");
            
        } catch (Exception e) {
            System.err.println("❌ Demo failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

/*
 * Key Event Sourcing Benefits demonstrated:
 * 
 * 1. Complete Audit Trail: हर transaction का complete history
 * 2. Point-in-time Reconstruction: किसी भी time पर account state देख सकते हैं
 * 3. Event Replay: Events को replay करके bugs debug कर सकते हैं
 * 4. Temporal Queries: Historical analysis और reporting
 * 5. Compliance: Banking regulations के लिए perfect audit trail
 * 6. Scalability: Events को horizontally partition कर सकते हैं
 * 7. Debugging: Production issues को locally reproduce कर सकते हैं
 * 
 * Production Considerations:
 * - Snapshots for performance (हर 100 events के बाद)
 * - Event versioning for schema evolution
 * - GDPR compliance के लिए encryption
 * - Event store partitioning strategy
 * - Concurrent access के लिए proper locking
 */