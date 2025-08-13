/*
 * Indian Stock Exchange Consensus System
 * =====================================
 * 
 * NSE/BSE style consensus for trade settlement and price discovery
 * Just like Mumbai's Dalal Street requires consensus among brokers,
 * stock exchanges need consensus for fair price discovery and settlement.
 * 
 * Features:
 * - Price discovery consensus
 * - Trade settlement consensus
 * - Circuit breaker coordination
 * - SEBI compliance validation
 * 
 * Author: Hindi Tech Podcast
 * Episode: 030 - Consensus Protocols
 */

package com.hinditechpodcast.stockexchange;

import java.util.*;
import java.util.concurrent.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.security.SecureRandom;

// Enums for stock exchange operations
enum ExchangeType {
    NSE("National Stock Exchange"),
    BSE("Bombay Stock Exchange"),
    MCX("Multi Commodity Exchange"),
    NCDEX("National Commodity & Derivatives Exchange");
    
    private final String fullName;
    
    ExchangeType(String fullName) {
        this.fullName = fullName;
    }
    
    public String getFullName() {
        return fullName;
    }
}

enum OrderType {
    MARKET, LIMIT, STOP_LOSS, BRACKET, COVER
}

enum OrderSide {
    BUY, SELL
}

enum TradeStatus {
    PENDING, MATCHED, SETTLED, REJECTED, FAILED
}

enum MarketPhase {
    PRE_OPEN, NORMAL, CLOSING, CLOSED, POST_MARKET
}

// Core trading entities
class StockSymbol {
    private final String symbol;
    private final String companyName;
    private final String sector;
    private final BigDecimal faceValue;
    private final long marketCap; // in crores
    
    public StockSymbol(String symbol, String companyName, String sector, 
                       BigDecimal faceValue, long marketCap) {
        this.symbol = symbol;
        this.companyName = companyName;
        this.sector = sector;
        this.faceValue = faceValue;
        this.marketCap = marketCap;
    }
    
    // Getters
    public String getSymbol() { return symbol; }
    public String getCompanyName() { return companyName; }
    public String getSector() { return sector; }
    public BigDecimal getFaceValue() { return faceValue; }
    public long getMarketCap() { return marketCap; }
    
    @Override
    public String toString() {
        return String.format("%s (%s)", symbol, companyName);
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        StockSymbol that = (StockSymbol) o;
        return Objects.equals(symbol, that.symbol);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(symbol);
    }
}

class Order {
    private final String orderId;
    private final String brokerId;
    private final StockSymbol symbol;
    private final OrderType orderType;
    private final OrderSide side;
    private final int quantity;
    private final BigDecimal price; // null for market orders
    private final long timestamp;
    private TradeStatus status;
    
    public Order(String orderId, String brokerId, StockSymbol symbol, 
                 OrderType orderType, OrderSide side, int quantity, BigDecimal price) {
        this.orderId = orderId;
        this.brokerId = brokerId;
        this.symbol = symbol;
        this.orderType = orderType;
        this.side = side;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = System.currentTimeMillis();
        this.status = TradeStatus.PENDING;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getBrokerId() { return brokerId; }
    public StockSymbol getSymbol() { return symbol; }
    public OrderType getOrderType() { return orderType; }
    public OrderSide getSide() { return side; }
    public int getQuantity() { return quantity; }
    public BigDecimal getPrice() { return price; }
    public long getTimestamp() { return timestamp; }
    public TradeStatus getStatus() { return status; }
    public void setStatus(TradeStatus status) { this.status = status; }
    
    public boolean isMarketOrder() {
        return orderType == OrderType.MARKET;
    }
    
    @Override
    public String toString() {
        String priceStr = price != null ? "₹" + price.toString() : "MARKET";
        return String.format("Order{%s: %s %d %s @ %s}", 
                           orderId, side, quantity, symbol.getSymbol(), priceStr);
    }
}

class Trade {
    private final String tradeId;
    private final Order buyOrder;
    private final Order sellOrder;
    private final int quantity;
    private final BigDecimal price;
    private final long timestamp;
    private TradeStatus status;
    
    public Trade(String tradeId, Order buyOrder, Order sellOrder, 
                 int quantity, BigDecimal price) {
        this.tradeId = tradeId;
        this.buyOrder = buyOrder;
        this.sellOrder = sellOrder;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = System.currentTimeMillis();
        this.status = TradeStatus.MATCHED;
    }
    
    // Getters
    public String getTradeId() { return tradeId; }
    public Order getBuyOrder() { return buyOrder; }
    public Order getSellOrder() { return sellOrder; }
    public int getQuantity() { return quantity; }
    public BigDecimal getPrice() { return price; }
    public long getTimestamp() { return timestamp; }
    public TradeStatus getStatus() { return status; }
    public void setStatus(TradeStatus status) { this.status = status; }
    
    public BigDecimal getTradeValue() {
        return price.multiply(BigDecimal.valueOf(quantity));
    }
    
    @Override
    public String toString() {
        return String.format("Trade{%s: %d %s @ ₹%s = ₹%s}", 
                           tradeId, quantity, buyOrder.getSymbol().getSymbol(), 
                           price, getTradeValue());
    }
}

// Broker representing market participants
class StockBroker {
    private final String brokerId;
    private final String brokerName;
    private final ExchangeType primaryExchange;
    private final double reliability; // 0.8 to 1.0
    private final Random random;
    
    // Performance metrics
    private int ordersPlaced = 0;
    private int tradesExecuted = 0;
    private BigDecimal totalTurnover = BigDecimal.ZERO;
    
    public StockBroker(String brokerId, String brokerName, ExchangeType primaryExchange) {
        this.brokerId = brokerId;
        this.brokerName = brokerName;
        this.primaryExchange = primaryExchange;
        this.reliability = 0.8 + new SecureRandom().nextDouble() * 0.19; // 80-99%
        this.random = new SecureRandom();
        
        System.out.printf("📈 Broker %s registered with %s (reliability: %.2f)%n", 
                         brokerName, primaryExchange.getFullName(), reliability);
    }
    
    public Order placeOrder(StockSymbol symbol, OrderType orderType, OrderSide side, 
                           int quantity, BigDecimal price) {
        ordersPlaced++;
        
        String orderId = String.format("ORD_%s_%d", brokerId, ordersPlaced);
        Order order = new Order(orderId, brokerId, symbol, orderType, side, quantity, price);
        
        // Simulate network issues
        if (random.nextDouble() > reliability) {
            order.setStatus(TradeStatus.FAILED);
            System.out.printf("   ❌ Order failed: %s (network issue)%n", orderId);
        } else {
            System.out.printf("   📝 Order placed: %s%n", order);
        }
        
        return order;
    }
    
    public boolean validateTrade(Trade trade) {
        // SEBI compliance checks
        if (!validateSEBICompliance(trade)) {
            return false;
        }
        
        // Risk management checks
        if (!validateRiskLimits(trade)) {
            return false;
        }
        
        // Market manipulation checks
        if (!validateMarketManipulation(trade)) {
            return false;
        }
        
        return true;
    }
    
    private boolean validateSEBICompliance(Trade trade) {
        // Minimum trade value (₹1)
        if (trade.getTradeValue().compareTo(BigDecimal.ONE) < 0) {
            return false;
        }
        
        // Maximum single trade limit (₹100 crores)
        BigDecimal maxTradeValue = BigDecimal.valueOf(1000000000L); // 100 crores
        if (trade.getTradeValue().compareTo(maxTradeValue) > 0) {
            return false;
        }
        
        // Price band validation (±20% from previous close)
        // Simplified: assume previous close is current price ± random variation
        return true;
    }
    
    private boolean validateRiskLimits(Trade trade) {
        // Broker's daily turnover limit
        BigDecimal dailyLimit = BigDecimal.valueOf(500000000L); // 50 crores
        BigDecimal projectedTurnover = totalTurnover.add(trade.getTradeValue());
        
        return projectedTurnover.compareTo(dailyLimit) <= 0;
    }
    
    private boolean validateMarketManipulation(Trade trade) {
        // Check for suspicious price movements
        // Simplified: random validation with high success rate
        return random.nextDouble() > 0.05; // 95% pass rate
    }
    
    public void recordTrade(Trade trade) {
        if (trade.getBuyOrder().getBrokerId().equals(brokerId) || 
            trade.getSellOrder().getBrokerId().equals(brokerId)) {
            tradesExecuted++;
            totalTurnover = totalTurnover.add(trade.getTradeValue());
        }
    }
    
    // Getters
    public String getBrokerId() { return brokerId; }
    public String getBrokerName() { return brokerName; }
    public ExchangeType getPrimaryExchange() { return primaryExchange; }
    public double getReliability() { return reliability; }
    
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("brokerId", brokerId);
        stats.put("brokerName", brokerName);
        stats.put("primaryExchange", primaryExchange.name());
        stats.put("reliability", reliability);
        stats.put("ordersPlaced", ordersPlaced);
        stats.put("tradesExecuted", tradesExecuted);
        stats.put("totalTurnover", totalTurnover);
        return stats;
    }
}

// Price Discovery Engine
class PriceDiscoveryEngine {
    private final Map<StockSymbol, List<Order>> buyOrders;
    private final Map<StockSymbol, List<Order>> sellOrders;
    private final Map<StockSymbol, BigDecimal> lastTradedPrices;
    
    public PriceDiscoveryEngine() {
        this.buyOrders = new ConcurrentHashMap<>();
        this.sellOrders = new ConcurrentHashMap<>();
        this.lastTradedPrices = new ConcurrentHashMap<>();
        
        System.out.println("💰 Price Discovery Engine initialized");
    }
    
    public void addOrder(Order order) {
        StockSymbol symbol = order.getSymbol();
        
        if (order.getSide() == OrderSide.BUY) {
            buyOrders.computeIfAbsent(symbol, k -> new ArrayList<>()).add(order);
            // Sort buy orders by price (descending) and time (ascending)
            buyOrders.get(symbol).sort((a, b) -> {
                if (a.isMarketOrder() && !b.isMarketOrder()) return -1;
                if (!a.isMarketOrder() && b.isMarketOrder()) return 1;
                if (a.isMarketOrder() && b.isMarketOrder()) return Long.compare(a.getTimestamp(), b.getTimestamp());
                int priceCompare = b.getPrice().compareTo(a.getPrice());
                return priceCompare != 0 ? priceCompare : Long.compare(a.getTimestamp(), b.getTimestamp());
            });
        } else {
            sellOrders.computeIfAbsent(symbol, k -> new ArrayList<>()).add(order);
            // Sort sell orders by price (ascending) and time (ascending)
            sellOrders.get(symbol).sort((a, b) -> {
                if (a.isMarketOrder() && !b.isMarketOrder()) return -1;
                if (!a.isMarketOrder() && b.isMarketOrder()) return 1;
                if (a.isMarketOrder() && b.isMarketOrder()) return Long.compare(a.getTimestamp(), b.getTimestamp());
                int priceCompare = a.getPrice().compareTo(b.getPrice());
                return priceCompare != 0 ? priceCompare : Long.compare(a.getTimestamp(), b.getTimestamp());
            });
        }
    }
    
    public List<Trade> matchOrders(StockSymbol symbol) {
        List<Trade> trades = new ArrayList<>();
        
        List<Order> buyOrdersList = buyOrders.get(symbol);
        List<Order> sellOrdersList = sellOrders.get(symbol);
        
        if (buyOrdersList == null || sellOrdersList == null || 
            buyOrdersList.isEmpty() || sellOrdersList.isEmpty()) {
            return trades;
        }
        
        Iterator<Order> buyIterator = buyOrdersList.iterator();
        Iterator<Order> sellIterator = sellOrdersList.iterator();
        
        while (buyIterator.hasNext() && sellIterator.hasNext()) {
            Order buyOrder = buyIterator.next();
            Order sellOrder = sellIterator.next();
            
            // Skip failed orders
            if (buyOrder.getStatus() == TradeStatus.FAILED || 
                sellOrder.getStatus() == TradeStatus.FAILED) {
                continue;
            }
            
            // Check if orders can be matched
            BigDecimal tradePrice = determineTradePrice(buyOrder, sellOrder);
            if (tradePrice == null) {
                break; // No more matches possible
            }
            
            // Determine trade quantity
            int tradeQuantity = Math.min(buyOrder.getQuantity(), sellOrder.getQuantity());
            
            // Create trade
            String tradeId = String.format("TRD_%s_%d", symbol.getSymbol(), 
                                         System.currentTimeMillis() % 10000);
            Trade trade = new Trade(tradeId, buyOrder, sellOrder, tradeQuantity, tradePrice);
            
            trades.add(trade);
            
            // Update last traded price
            lastTradedPrices.put(symbol, tradePrice);
            
            // Update order statuses
            buyOrder.setStatus(TradeStatus.MATCHED);
            sellOrder.setStatus(TradeStatus.MATCHED);
            
            // Remove fully executed orders
            buyIterator.remove();
            sellIterator.remove();
            
            System.out.printf("   🤝 Trade matched: %s%n", trade);
        }
        
        return trades;
    }
    
    private BigDecimal determineTradePrice(Order buyOrder, Order sellOrder) {
        // Market orders execute at best available price
        if (buyOrder.isMarketOrder() && sellOrder.isMarketOrder()) {
            // Use last traded price or a default
            StockSymbol symbol = buyOrder.getSymbol();
            return lastTradedPrices.getOrDefault(symbol, BigDecimal.valueOf(100));
        }
        
        if (buyOrder.isMarketOrder()) {
            return sellOrder.getPrice();
        }
        
        if (sellOrder.isMarketOrder()) {
            return buyOrder.getPrice();
        }
        
        // Both are limit orders - check if they cross
        if (buyOrder.getPrice().compareTo(sellOrder.getPrice()) >= 0) {
            // Price-time priority: earlier order gets preference
            return buyOrder.getTimestamp() < sellOrder.getTimestamp() ? 
                   buyOrder.getPrice() : sellOrder.getPrice();
        }
        
        return null; // Orders don't cross
    }
    
    public BigDecimal getLastTradedPrice(StockSymbol symbol) {
        return lastTradedPrices.get(symbol);
    }
    
    public int getPendingBuyOrders(StockSymbol symbol) {
        List<Order> orders = buyOrders.get(symbol);
        return orders != null ? orders.size() : 0;
    }
    
    public int getPendingSellOrders(StockSymbol symbol) {
        List<Order> orders = sellOrders.get(symbol);
        return orders != null ? orders.size() : 0;
    }
}

// Settlement Consensus System
class SettlementConsensusSystem {
    private final List<StockBroker> brokers;
    private final PriceDiscoveryEngine priceEngine;
    private final double consensusThreshold;
    private final ExecutorService executorService;
    
    // Performance metrics
    private int tradesProcessed = 0;
    private int tradesSettled = 0;
    private int tradesRejected = 0;
    private BigDecimal totalSettlementValue = BigDecimal.ZERO;
    
    public SettlementConsensusSystem(List<StockBroker> brokers, double consensusThreshold) {
        this.brokers = new ArrayList<>(brokers);
        this.priceEngine = new PriceDiscoveryEngine();
        this.consensusThreshold = Math.max(0.5, Math.min(1.0, consensusThreshold));
        this.executorService = Executors.newFixedThreadPool(Math.min(brokers.size(), 20));
        
        System.out.printf("🏛️ Settlement Consensus System initialized%n");
        System.out.printf("   Participating brokers: %d%n", brokers.size());
        System.out.printf("   Consensus threshold: %.1f%%%n", consensusThreshold * 100);
    }
    
    public void submitOrder(Order order) {
        System.out.printf("📝 Order submitted: %s%n", order);
        
        if (order.getStatus() != TradeStatus.FAILED) {
            priceEngine.addOrder(order);
        }
    }
    
    public List<Trade> processTradeMatching(StockSymbol symbol) {
        System.out.printf("%n🔄 PROCESSING TRADE MATCHING for %s%n", symbol);
        System.out.println("─".repeat(50));
        
        List<Trade> matchedTrades = priceEngine.matchOrders(symbol);
        
        if (matchedTrades.isEmpty()) {
            System.out.println("   No trades matched");
            return matchedTrades;
        }
        
        System.out.printf("   %d trades matched%n", matchedTrades.size());
        
        // Process each trade through consensus
        List<Trade> settledTrades = new ArrayList<>();
        for (Trade trade : matchedTrades) {
            if (runSettlementConsensus(trade)) {
                trade.setStatus(TradeStatus.SETTLED);
                settledTrades.add(trade);
                tradesSettled++;
                totalSettlementValue = totalSettlementValue.add(trade.getTradeValue());
                
                // Record trade with brokers
                for (StockBroker broker : brokers) {
                    broker.recordTrade(trade);
                }
            } else {
                trade.setStatus(TradeStatus.REJECTED);
                tradesRejected++;
            }
            tradesProcessed++;
        }
        
        return settledTrades;
    }
    
    private boolean runSettlementConsensus(Trade trade) {
        System.out.printf("   🏛️ Running consensus for trade %s%n", trade.getTradeId());
        
        // Collect validation results from all brokers
        List<Future<Boolean>> validationFutures = new ArrayList<>();
        
        for (StockBroker broker : brokers) {
            validationFutures.add(executorService.submit(() -> {
                try {
                    Thread.sleep(10 + new SecureRandom().nextInt(50)); // Simulate processing time
                    return broker.validateTrade(trade);
                } catch (Exception e) {
                    System.err.printf("     ❌ Validation error for broker %s: %s%n", 
                                    broker.getBrokerId(), e.getMessage());
                    return false;
                }
            }));
        }
        
        // Collect results
        int approvals = 0;
        int totalValidations = 0;
        
        for (Future<Boolean> future : validationFutures) {
            try {
                boolean approved = future.get(5, TimeUnit.SECONDS);
                totalValidations++;
                if (approved) {
                    approvals++;
                }
            } catch (Exception e) {
                totalValidations++;
                // Timeout or error counts as rejection
            }
        }
        
        // Calculate consensus
        double approvalRate = totalValidations > 0 ? (double) approvals / totalValidations : 0.0;
        boolean consensusReached = approvalRate >= consensusThreshold;
        
        String result = consensusReached ? "✅ APPROVED" : "❌ REJECTED";
        System.out.printf("     Consensus: %s (%.1f%% approval)%n", result, approvalRate * 100);
        
        return consensusReached;
    }
    
    public void simulateTradingSession(List<StockSymbol> symbols, int orderCount) {
        System.out.printf("%n📊 TRADING SESSION SIMULATION%n");
        System.out.printf("Symbols: %d, Orders: %d%n", symbols.size(), orderCount);
        System.out.println("=".repeat(60));
        
        Random random = new SecureRandom();
        
        // Generate random orders
        for (int i = 0; i < orderCount; i++) {
            StockSymbol symbol = symbols.get(random.nextInt(symbols.size()));
            StockBroker broker = brokers.get(random.nextInt(brokers.size()));
            
            OrderType orderType = random.nextBoolean() ? OrderType.MARKET : OrderType.LIMIT;
            OrderSide side = random.nextBoolean() ? OrderSide.BUY : OrderSide.SELL;
            int quantity = 100 + random.nextInt(900); // 100-1000 shares
            
            BigDecimal price = null;
            if (orderType == OrderType.LIMIT) {
                // Generate price around ₹100-500
                price = BigDecimal.valueOf(100 + random.nextInt(400))
                               .add(BigDecimal.valueOf(random.nextInt(100)).divide(BigDecimal.valueOf(100)));
            }
            
            Order order = broker.placeOrder(symbol, orderType, side, quantity, price);
            submitOrder(order);
        }
        
        // Process trading for each symbol
        for (StockSymbol symbol : symbols) {
            List<Trade> settledTrades = processTradeMatching(symbol);
            
            System.out.printf("%n📈 %s Summary:%n", symbol.getSymbol());
            System.out.printf("   Pending Buy Orders: %d%n", priceEngine.getPendingBuyOrders(symbol));
            System.out.printf("   Pending Sell Orders: %d%n", priceEngine.getPendingSellOrders(symbol));
            System.out.printf("   Settled Trades: %d%n", settledTrades.size());
            
            BigDecimal ltp = priceEngine.getLastTradedPrice(symbol);
            if (ltp != null) {
                System.out.printf("   Last Traded Price: ₹%s%n", ltp);
            }
        }
    }
    
    public Map<String, Object> getSessionStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("tradesProcessed", tradesProcessed);
        stats.put("tradesSettled", tradesSettled);
        stats.put("tradesRejected", tradesRejected);
        stats.put("settlementRate", tradesProcessed > 0 ? 
                 (double) tradesSettled / tradesProcessed : 0.0);
        stats.put("totalSettlementValue", totalSettlementValue);
        stats.put("participatingBrokers", brokers.size());
        return stats;
    }
    
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

// Main class for Indian Stock Exchange simulation
public class IndianStockExchangeConsensus {
    
    public static void main(String[] args) {
        System.out.println("🚀 INDIAN STOCK EXCHANGE CONSENSUS SIMULATION");
        System.out.println("NSE/BSE Trade Settlement and Price Discovery");
        System.out.println("=".repeat(70));
        
        try {
            simulateStockExchangeTrading();
        } catch (Exception e) {
            System.err.printf("❌ Error in stock exchange simulation: %s%n", e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void simulateStockExchangeTrading() {
        // Create major Indian companies
        List<StockSymbol> niftyStocks = Arrays.asList(
            new StockSymbol("RELIANCE", "Reliance Industries Ltd", "Energy", 
                          BigDecimal.valueOf(10), 1500000L),
            new StockSymbol("TCS", "Tata Consultancy Services", "IT", 
                          BigDecimal.valueOf(1), 1200000L),
            new StockSymbol("HDFCBANK", "HDFC Bank Ltd", "Financial Services", 
                          BigDecimal.valueOf(1), 800000L),
            new StockSymbol("INFY", "Infosys Ltd", "IT", 
                          BigDecimal.valueOf(5), 650000L),
            new StockSymbol("HINDUNILVR", "Hindustan Unilever Ltd", "FMCG", 
                          BigDecimal.valueOf(1), 550000L),
            new StockSymbol("ICICIBANK", "ICICI Bank Ltd", "Financial Services", 
                          BigDecimal.valueOf(2), 500000L),
            new StockSymbol("SBIN", "State Bank of India", "Financial Services", 
                          BigDecimal.valueOf(1), 400000L),
            new StockSymbol("BHARTIARTL", "Bharti Airtel Ltd", "Telecom", 
                          BigDecimal.valueOf(5), 350000L)
        );
        
        // Create participating brokers
        List<StockBroker> brokers = Arrays.asList(
            new StockBroker("BRK001", "Zerodha", ExchangeType.NSE),
            new StockBroker("BRK002", "Angel Broking", ExchangeType.BSE),
            new StockBroker("BRK003", "HDFC Securities", ExchangeType.NSE),
            new StockBroker("BRK004", "ICICI Direct", ExchangeType.NSE),
            new StockBroker("BRK005", "Kotak Securities", ExchangeType.BSE),
            new StockBroker("BRK006", "Sharekhan", ExchangeType.NSE),
            new StockBroker("BRK007", "Motilal Oswal", ExchangeType.BSE),
            new StockBroker("BRK008", "Upstox", ExchangeType.NSE)
        );
        
        // Create settlement consensus system
        SettlementConsensusSystem consensusSystem = 
            new SettlementConsensusSystem(brokers, 0.75); // 75% consensus threshold
        
        System.out.printf("%n📋 MARKET SETUP%n");
        System.out.printf("Stocks: %d (Nifty constituents)%n", niftyStocks.size());
        System.out.printf("Brokers: %d%n", brokers.size());
        System.out.printf("Session time: %s%n", 
                         LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        
        // Simulate trading session
        consensusSystem.simulateTradingSession(niftyStocks, 100); // 100 orders
        
        // Display session summary
        Map<String, Object> sessionStats = consensusSystem.getSessionStats();
        
        System.out.printf("%n📊 TRADING SESSION SUMMARY%n");
        System.out.println("=".repeat(50));
        System.out.printf("Trades processed: %s%n", sessionStats.get("tradesProcessed"));
        System.out.printf("Trades settled: %s%n", sessionStats.get("tradesSettled"));
        System.out.printf("Trades rejected: %s%n", sessionStats.get("tradesRejected"));
        System.out.printf("Settlement rate: %.1f%%%n", 
                         (Double) sessionStats.get("settlementRate") * 100);
        System.out.printf("Total settlement value: ₹%s%n", sessionStats.get("totalSettlementValue"));
        
        // Display broker performance
        System.out.printf("%n🏢 BROKER PERFORMANCE%n");
        System.out.println("─".repeat(40));
        
        for (StockBroker broker : brokers.subList(0, 5)) { // Show top 5 brokers
            Map<String, Object> brokerStats = broker.getStats();
            System.out.printf("%s: %d orders, %d trades, ₹%s turnover%n",
                             brokerStats.get("brokerName"),
                             brokerStats.get("ordersPlaced"),
                             brokerStats.get("tradesExecuted"),
                             brokerStats.get("totalTurnover"));
        }
        
        System.out.printf("%n🎯 Key Insights:%n");
        System.out.println("• Stock exchanges use consensus for fair price discovery");
        System.out.println("• Multiple brokers validate each trade before settlement");
        System.out.println("• SEBI compliance ensures market integrity");
        System.out.println("• Like Mumbai's Dalal Street - trust through consensus!");
        
        System.out.println("\n🎊 Stock Exchange Simulation Completed!");
        
        // Shutdown consensus system
        consensusSystem.shutdown();
    }
}