/*
Episode 13: CDC & Real-Time Data Pipelines
Example 7: Stock Market Data Streaming (NSE/BSE)

यह example Indian stock market का real-time data streaming implement करता है।
Zerodha, Groww जैसे trading platforms के लिए live market data।

Author: Distributed Systems Podcast Team
Context: NSE/BSE real-time trading data, order book, tick-by-tick data
*/

package com.distributedpodcast.stockmarket;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import redis.clients.jedis.Jedis;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

/**
 * NSE/BSE Stock Market Data Streamer
 * Mumbai Stock Exchange की real-time data feed simulate करता है
 */
public class IndianStockMarketStreamer {
    
    private static final Logger logger = LoggerFactory.getLogger(IndianStockMarketStreamer.class);
    
    // Indian Stock Market Configuration
    private static final Map<String, StockInfo> NSE_STOCKS = Map.of(
        "RELIANCE", new StockInfo("Reliance Industries", "RELIANCE", new BigDecimal("2450.75"), "NSE"),
        "TCS", new StockInfo("Tata Consultancy Services", "TCS", new BigDecimal("3890.50"), "NSE"),
        "HDFCBANK", new StockInfo("HDFC Bank", "HDFCBANK", new BigDecimal("1540.25"), "NSE"),
        "INFY", new StockInfo("Infosys", "INFY", new BigDecimal("1450.80"), "NSE"),
        "HINDUNILVR", new StockInfo("Hindustan Unilever", "HINDUNILVR", new BigDecimal("2380.90"), "NSE"),
        "ICICIBANK", new StockInfo("ICICI Bank", "ICICIBANK", new BigDecimal("950.45"), "NSE"),
        "SBIN", new StockInfo("State Bank of India", "SBIN", new BigDecimal("575.20"), "NSE"),
        "BHARTIARTL", new StockInfo("Bharti Airtel", "BHARTIARTL", new BigDecimal("820.15"), "NSE"),
        "ITC", new StockInfo("ITC Limited", "ITC", new BigDecimal("390.75"), "NSE"),
        "LT", new StockInfo("Larsen & Toubro", "LT", new BigDecimal("2180.30"), "NSE")
    );
    
    // Kafka और Redis clients
    private final KafkaProducer<String, String> kafkaProducer;
    private final JedisPool jedisPool;
    private final ObjectMapper objectMapper;
    private final ScheduledExecutorService executorService;
    
    // Market state tracking
    private final Map<String, MarketData> currentMarketData;
    private final Map<String, OrderBook> orderBooks;
    private volatile boolean marketOpen;
    
    // Performance metrics
    private long ticksGenerated = 0;
    private long tradesProcessed = 0;
    
    public IndianStockMarketStreamer() {
        // Kafka Producer configuration
        Properties kafkaProps = new Properties();
        kafkaProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        kafkaProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        kafkaProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        kafkaProps.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy"); // Better performance
        kafkaProps.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        kafkaProps.put(ProducerConfig.LINGER_MS_CONFIG, 5);
        kafkaProps.put(ProducerConfig.ACKS_CONFIG, "1"); // Balance between speed and reliability
        
        this.kafkaProducer = new KafkaProducer<>(kafkaProps);
        
        // Redis connection pool
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(20);
        poolConfig.setMaxIdle(10);
        poolConfig.setMinIdle(5);
        this.jedisPool = new JedisPool(poolConfig, "localhost", 6379);
        
        this.objectMapper = new ObjectMapper();
        this.executorService = Executors.newScheduledThreadPool(10);
        
        // Initialize market data
        this.currentMarketData = new ConcurrentHashMap<>();
        this.orderBooks = new ConcurrentHashMap<>();
        
        initializeMarketData();
        
        logger.info("📈 Indian Stock Market Streamer initialized");
    }
    
    /**
     * Market data को initialize करो - opening prices के साथ
     */
    private void initializeMarketData() {
        NSE_STOCKS.forEach((symbol, stockInfo) -> {
            MarketData marketData = new MarketData(
                symbol,
                stockInfo.getExchange(),
                stockInfo.getCurrentPrice(),
                stockInfo.getCurrentPrice(), // Open price same as current
                BigDecimal.ZERO, // Change
                BigDecimal.ZERO, // Change percentage
                0L, // Volume
                stockInfo.getCurrentPrice(), // Day high
                stockInfo.getCurrentPrice(), // Day low
                LocalDateTime.now()
            );
            
            currentMarketData.put(symbol, marketData);
            
            // Initialize order book
            OrderBook orderBook = new OrderBook(symbol);
            generateInitialOrderBook(orderBook, stockInfo.getCurrentPrice());
            orderBooks.put(symbol, orderBook);
        });
        
        logger.info("✅ Initialized market data for {} stocks", NSE_STOCKS.size());
    }
    
    /**
     * Initial order book generate करो - realistic bid/ask spreads
     */
    private void generateInitialOrderBook(OrderBook orderBook, BigDecimal currentPrice) {
        Random random = new Random();
        
        // Generate bid orders (buy orders below current price)
        for (int i = 1; i <= 10; i++) {
            BigDecimal bidPrice = currentPrice.subtract(new BigDecimal(i * 0.25));
            int quantity = 100 + random.nextInt(500);
            orderBook.addBidOrder(new Order(
                UUID.randomUUID().toString(),
                OrderType.BUY,
                bidPrice,
                quantity,
                LocalDateTime.now()
            ));
        }
        
        // Generate ask orders (sell orders above current price)  
        for (int i = 1; i <= 10; i++) {
            BigDecimal askPrice = currentPrice.add(new BigDecimal(i * 0.25));
            int quantity = 100 + random.nextInt(500);
            orderBook.addAskOrder(new Order(
                UUID.randomUUID().toString(),
                OrderType.SELL,
                askPrice,
                quantity,
                LocalDateTime.now()
            ));
        }
    }
    
    /**
     * Market को open करो - trading session start
     */
    public void openMarket() {
        marketOpen = true;
        logger.info("🔔 Market opened - Starting live data streaming");
        
        // Start market data generation
        startMarketDataGeneration();
        
        // Start order book updates
        startOrderBookUpdates();
        
        // Start trade execution simulation
        startTradeExecution();
        
        // Start metrics reporting
        startMetricsReporting();
    }
    
    /**
     * Market data generation start करो - tick by tick data
     */
    private void startMarketDataGeneration() {
        executorService.scheduleAtFixedRate(() -> {
            if (!marketOpen) return;
            
            try {
                NSE_STOCKS.keySet().forEach(this::generateMarketTick);
            } catch (Exception e) {
                logger.error("💥 Market data generation error", e);
            }
        }, 0, 100, TimeUnit.MILLISECONDS); // 10 ticks per second
    }
    
    /**
     * Individual stock के लिए market tick generate करो
     */
    private void generateMarketTick(String symbol) {
        try {
            MarketData currentData = currentMarketData.get(symbol);
            Random random = new Random();
            
            // Price movement simulation - realistic volatility
            double volatility = 0.002; // 0.2% volatility
            double priceChange = (random.nextGaussian() * volatility * currentData.getLastPrice().doubleValue());
            
            // Mumbai market hours में higher volatility
            LocalDateTime now = LocalDateTime.now();
            int hour = now.getHour();
            if (hour >= 9 && hour <= 11) { // Opening hours volatility
                priceChange *= 1.5;
            }
            
            BigDecimal newPrice = currentData.getLastPrice().add(new BigDecimal(priceChange))
                .setScale(2, RoundingMode.HALF_UP);
            
            // Ensure price stays within reasonable bounds
            BigDecimal minPrice = currentData.getOpenPrice().multiply(new BigDecimal("0.8")); // 20% circuit limit
            BigDecimal maxPrice = currentData.getOpenPrice().multiply(new BigDecimal("1.2"));
            
            if (newPrice.compareTo(minPrice) < 0) newPrice = minPrice;
            if (newPrice.compareTo(maxPrice) > 0) newPrice = maxPrice;
            
            // Update market data
            BigDecimal changeAmount = newPrice.subtract(currentData.getOpenPrice());
            BigDecimal changePercent = changeAmount.divide(currentData.getOpenPrice(), 4, RoundingMode.HALF_UP)
                .multiply(new BigDecimal("100"));
            
            long newVolume = currentData.getVolume() + random.nextInt(1000) + 100;
            
            MarketData updatedData = new MarketData(
                symbol,
                currentData.getExchange(),
                newPrice,
                currentData.getOpenPrice(),
                changeAmount,
                changePercent,
                newVolume,
                newPrice.max(currentData.getDayHigh()),
                newPrice.min(currentData.getDayLow()),
                LocalDateTime.now()
            );
            
            currentMarketData.put(symbol, updatedData);
            
            // Send to Kafka
            sendMarketDataToKafka(updatedData);
            
            // Update Redis cache
            updateRedisCache(symbol, updatedData);
            
            ticksGenerated++;
            
        } catch (Exception e) {
            logger.error("💥 Error generating tick for {}", symbol, e);
        }
    }
    
    /**
     * Market data को Kafka में send करो
     */
    private void sendMarketDataToKafka(MarketData marketData) {
        try {
            String topic = "nse.market.ticks";
            String key = marketData.getSymbol();
            String value = objectMapper.writeValueAsString(marketData);
            
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
            kafkaProducer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    logger.error("💥 Failed to send market data for {}", marketData.getSymbol(), exception);
                }
            });
            
        } catch (Exception e) {
            logger.error("💥 Kafka send error", e);
        }
    }
    
    /**
     * Redis cache update करो - fast lookups के लिए
     */
    private void updateRedisCache(String symbol, MarketData marketData) {
        try (Jedis jedis = jedisPool.getResource()) {
            String key = "market:" + symbol;
            String value = objectMapper.writeValueAsString(marketData);
            
            // Set with 60 second expiry
            jedis.setex(key, 60, value);
            
            // Also update sorted set for top gainers/losers
            jedis.zadd("gainers", marketData.getChangePercent().doubleValue(), symbol);
            jedis.zadd("losers", -marketData.getChangePercent().doubleValue(), symbol);
            
        } catch (Exception e) {
            logger.error("💥 Redis update error for {}", symbol, e);
        }
    }
    
    /**
     * Order book updates start करो
     */
    private void startOrderBookUpdates() {
        executorService.scheduleAtFixedRate(() -> {
            if (!marketOpen) return;
            
            try {
                orderBooks.values().forEach(this::updateOrderBook);
            } catch (Exception e) {
                logger.error("💥 Order book update error", e);
            }
        }, 0, 200, TimeUnit.MILLISECONDS); // 5 updates per second
    }
    
    /**
     * Individual order book update करो
     */
    private void updateOrderBook(OrderBook orderBook) {
        try {
            Random random = new Random();
            MarketData currentData = currentMarketData.get(orderBook.getSymbol());
            
            // Add new orders randomly
            if (random.nextDouble() < 0.7) { // 70% chance to add new order
                boolean isBuy = random.nextBoolean();
                BigDecimal basePrice = currentData.getLastPrice();
                
                if (isBuy) {
                    // Add bid order slightly below current price
                    BigDecimal bidPrice = basePrice.subtract(new BigDecimal(random.nextDouble() * 2));
                    int quantity = 50 + random.nextInt(200);
                    
                    Order newOrder = new Order(
                        UUID.randomUUID().toString(),
                        OrderType.BUY,
                        bidPrice,
                        quantity,
                        LocalDateTime.now()
                    );
                    orderBook.addBidOrder(newOrder);
                } else {
                    // Add ask order slightly above current price
                    BigDecimal askPrice = basePrice.add(new BigDecimal(random.nextDouble() * 2));
                    int quantity = 50 + random.nextInt(200);
                    
                    Order newOrder = new Order(
                        UUID.randomUUID().toString(),
                        OrderType.SELL,
                        askPrice,
                        quantity,
                        LocalDateTime.now()
                    );
                    orderBook.addAskOrder(newOrder);
                }
            }
            
            // Send order book snapshot to Kafka
            if (ticksGenerated % 10 == 0) { // Every 10th tick
                sendOrderBookToKafka(orderBook);
            }
            
        } catch (Exception e) {
            logger.error("💥 Order book update error for {}", orderBook.getSymbol(), e);
        }
    }
    
    /**
     * Order book को Kafka में send करो
     */
    private void sendOrderBookToKafka(OrderBook orderBook) {
        try {
            String topic = "nse.orderbook.snapshots";
            String key = orderBook.getSymbol();
            
            // Create order book snapshot
            Map<String, Object> snapshot = Map.of(
                "symbol", orderBook.getSymbol(),
                "timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
                "bids", orderBook.getTopBids(5), // Top 5 bid levels
                "asks", orderBook.getTopAsks(5), // Top 5 ask levels
                "spread", calculateSpread(orderBook)
            );
            
            String value = objectMapper.writeValueAsString(snapshot);
            
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
            kafkaProducer.send(record);
            
        } catch (Exception e) {
            logger.error("💥 Order book send error for {}", orderBook.getSymbol(), e);
        }
    }
    
    /**
     * Bid-ask spread calculate करो
     */
    private BigDecimal calculateSpread(OrderBook orderBook) {
        Order bestBid = orderBook.getBestBid();
        Order bestAsk = orderBook.getBestAsk();
        
        if (bestBid != null && bestAsk != null) {
            return bestAsk.getPrice().subtract(bestBid.getPrice());
        }
        return BigDecimal.ZERO;
    }
    
    /**
     * Trade execution simulation start करो
     */
    private void startTradeExecution() {
        executorService.scheduleAtFixedRate(() -> {
            if (!marketOpen) return;
            
            try {
                // Simulate trades for random stocks
                List<String> symbols = new ArrayList<>(NSE_STOCKS.keySet());
                Collections.shuffle(symbols);
                
                // Execute 1-3 trades per cycle
                int numTrades = 1 + new Random().nextInt(3);
                for (int i = 0; i < numTrades && i < symbols.size(); i++) {
                    simulateTrade(symbols.get(i));
                }
                
            } catch (Exception e) {
                logger.error("💥 Trade execution error", e);
            }
        }, 0, 500, TimeUnit.MILLISECONDS); // Every 500ms
    }
    
    /**
     * Individual stock के लिए trade simulate करो
     */
    private void simulateTrade(String symbol) {
        try {
            OrderBook orderBook = orderBooks.get(symbol);
            MarketData currentData = currentMarketData.get(symbol);
            Random random = new Random();
            
            Order bestBid = orderBook.getBestBid();
            Order bestAsk = orderBook.getBestAsk();
            
            if (bestBid != null && bestAsk != null) {
                // Decide if trade should happen (market orders vs limit orders)
                boolean tradeExecuted = random.nextDouble() < 0.3; // 30% chance of trade
                
                if (tradeExecuted) {
                    boolean isBuyTrade = random.nextBoolean();
                    Order executedOrder = isBuyTrade ? bestAsk : bestBid; // Market order hits best opposite side
                    
                    int tradeQuantity = Math.min(executedOrder.getQuantity(), 50 + random.nextInt(200));
                    BigDecimal tradePrice = executedOrder.getPrice();
                    
                    // Create trade record
                    Trade trade = new Trade(
                        UUID.randomUUID().toString(),
                        symbol,
                        tradePrice,
                        tradeQuantity,
                        isBuyTrade ? OrderType.BUY : OrderType.SELL,
                        LocalDateTime.now()
                    );
                    
                    // Update order book (remove or reduce order)
                    updateOrderAfterTrade(orderBook, executedOrder, tradeQuantity);
                    
                    // Send trade to Kafka
                    sendTradeToKafka(trade);
                    
                    tradesProcessed++;
                    
                    logger.debug("📊 Trade executed: {} {} shares of {} at ₹{}", 
                        trade.getSide(), trade.getQuantity(), symbol, trade.getPrice());
                }
            }
            
        } catch (Exception e) {
            logger.error("💥 Trade simulation error for {}", symbol, e);
        }
    }
    
    /**
     * Trade के बाद order book update करो
     */
    private void updateOrderAfterTrade(OrderBook orderBook, Order order, int tradedQuantity) {
        if (order.getQuantity() <= tradedQuantity) {
            // Order fully executed, remove it
            if (order.getType() == OrderType.BUY) {
                orderBook.removeBidOrder(order);
            } else {
                orderBook.removeAskOrder(order);
            }
        } else {
            // Partial execution, update quantity
            order.setQuantity(order.getQuantity() - tradedQuantity);
        }
    }
    
    /**
     * Trade को Kafka में send करो
     */
    private void sendTradeToKafka(Trade trade) {
        try {
            String topic = "nse.trades";
            String key = trade.getSymbol();
            String value = objectMapper.writeValueAsString(trade);
            
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
            kafkaProducer.send(record);
            
        } catch (Exception e) {
            logger.error("💥 Trade send error", e);
        }
    }
    
    /**
     * Metrics reporting start करो
     */
    private void startMetricsReporting() {
        executorService.scheduleAtFixedRate(() -> {
            try {
                // Calculate TPS (Ticks Per Second)
                long currentTime = System.currentTimeMillis();
                
                // Log current metrics
                logger.info("📊 Market Metrics - Ticks: {}, Trades: {}, Active Stocks: {}", 
                    ticksGenerated, tradesProcessed, currentMarketData.size());
                
                // Send metrics to Kafka for monitoring
                Map<String, Object> metrics = Map.of(
                    "timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
                    "ticks_generated", ticksGenerated,
                    "trades_processed", tradesProcessed,
                    "active_stocks", currentMarketData.size(),
                    "market_status", marketOpen ? "OPEN" : "CLOSED"
                );
                
                String value = objectMapper.writeValueAsString(metrics);
                ProducerRecord<String, String> record = new ProducerRecord<>("nse.metrics", "system", value);
                kafkaProducer.send(record);
                
            } catch (Exception e) {
                logger.error("💥 Metrics reporting error", e);
            }
        }, 10, 10, TimeUnit.SECONDS);
    }
    
    /**
     * Market को close करो
     */
    public void closeMarket() {
        marketOpen = false;
        logger.info("🔔 Market closed - Stopping data streaming");
    }
    
    /**
     * System को shutdown करो
     */
    public void shutdown() {
        logger.info("🛑 Shutting down Indian Stock Market Streamer");
        
        closeMarket();
        
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
        }
        
        kafkaProducer.close();
        jedisPool.close();
        
        logger.info("✅ Stock Market Streamer shutdown complete");
    }
    
    // Data classes
    public static class StockInfo {
        private final String companyName;
        private final String symbol;
        private final BigDecimal currentPrice;
        private final String exchange;
        
        public StockInfo(String companyName, String symbol, BigDecimal currentPrice, String exchange) {
            this.companyName = companyName;
            this.symbol = symbol;
            this.currentPrice = currentPrice;
            this.exchange = exchange;
        }
        
        // Getters
        public String getCompanyName() { return companyName; }
        public String getSymbol() { return symbol; }
        public BigDecimal getCurrentPrice() { return currentPrice; }
        public String getExchange() { return exchange; }
    }
    
    public static class MarketData {
        private final String symbol;
        private final String exchange;
        private final BigDecimal lastPrice;
        private final BigDecimal openPrice;
        private final BigDecimal change;
        private final BigDecimal changePercent;
        private final long volume;
        private final BigDecimal dayHigh;
        private final BigDecimal dayLow;
        private final LocalDateTime timestamp;
        
        public MarketData(String symbol, String exchange, BigDecimal lastPrice, BigDecimal openPrice,
                         BigDecimal change, BigDecimal changePercent, long volume,
                         BigDecimal dayHigh, BigDecimal dayLow, LocalDateTime timestamp) {
            this.symbol = symbol;
            this.exchange = exchange;
            this.lastPrice = lastPrice;
            this.openPrice = openPrice;
            this.change = change;
            this.changePercent = changePercent;
            this.volume = volume;
            this.dayHigh = dayHigh;
            this.dayLow = dayLow;
            this.timestamp = timestamp;
        }
        
        // Getters
        public String getSymbol() { return symbol; }
        public String getExchange() { return exchange; }
        public BigDecimal getLastPrice() { return lastPrice; }
        public BigDecimal getOpenPrice() { return openPrice; }
        public BigDecimal getChange() { return change; }
        public BigDecimal getChangePercent() { return changePercent; }
        public long getVolume() { return volume; }
        public BigDecimal getDayHigh() { return dayHigh; }
        public BigDecimal getDayLow() { return dayLow; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    public static class Order {
        private final String orderId;
        private final OrderType type;
        private final BigDecimal price;
        private int quantity;
        private final LocalDateTime timestamp;
        
        public Order(String orderId, OrderType type, BigDecimal price, int quantity, LocalDateTime timestamp) {
            this.orderId = orderId;
            this.type = type;
            this.price = price;
            this.quantity = quantity;
            this.timestamp = timestamp;
        }
        
        // Getters and setters
        public String getOrderId() { return orderId; }
        public OrderType getType() { return type; }
        public BigDecimal getPrice() { return price; }
        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    public static class Trade {
        private final String tradeId;
        private final String symbol;
        private final BigDecimal price;
        private final int quantity;
        private final OrderType side;
        private final LocalDateTime timestamp;
        
        public Trade(String tradeId, String symbol, BigDecimal price, int quantity, OrderType side, LocalDateTime timestamp) {
            this.tradeId = tradeId;
            this.symbol = symbol;
            this.price = price;
            this.quantity = quantity;
            this.side = side;
            this.timestamp = timestamp;
        }
        
        // Getters
        public String getTradeId() { return tradeId; }
        public String getSymbol() { return symbol; }
        public BigDecimal getPrice() { return price; }
        public int getQuantity() { return quantity; }
        public OrderType getSide() { return side; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    public enum OrderType {
        BUY, SELL
    }
    
    /**
     * Order Book implementation
     */
    public static class OrderBook {
        private final String symbol;
        private final TreeMap<BigDecimal, List<Order>> bidOrders; // Price descending
        private final TreeMap<BigDecimal, List<Order>> askOrders; // Price ascending
        
        public OrderBook(String symbol) {
            this.symbol = symbol;
            this.bidOrders = new TreeMap<>(Collections.reverseOrder()); // Highest price first
            this.askOrders = new TreeMap<>(); // Lowest price first
        }
        
        public void addBidOrder(Order order) {
            bidOrders.computeIfAbsent(order.getPrice(), k -> new ArrayList<>()).add(order);
        }
        
        public void addAskOrder(Order order) {
            askOrders.computeIfAbsent(order.getPrice(), k -> new ArrayList<>()).add(order);
        }
        
        public void removeBidOrder(Order order) {
            List<Order> orders = bidOrders.get(order.getPrice());
            if (orders != null) {
                orders.remove(order);
                if (orders.isEmpty()) {
                    bidOrders.remove(order.getPrice());
                }
            }
        }
        
        public void removeAskOrder(Order order) {
            List<Order> orders = askOrders.get(order.getPrice());
            if (orders != null) {
                orders.remove(order);
                if (orders.isEmpty()) {
                    askOrders.remove(order.getPrice());
                }
            }
        }
        
        public Order getBestBid() {
            if (bidOrders.isEmpty()) return null;
            List<Order> orders = bidOrders.firstEntry().getValue();
            return orders.isEmpty() ? null : orders.get(0);
        }
        
        public Order getBestAsk() {
            if (askOrders.isEmpty()) return null;
            List<Order> orders = askOrders.firstEntry().getValue();
            return orders.isEmpty() ? null : orders.get(0);
        }
        
        public List<Order> getTopBids(int count) {
            return bidOrders.entrySet().stream()
                .limit(count)
                .flatMap(entry -> entry.getValue().stream())
                .collect(Collectors.toList());
        }
        
        public List<Order> getTopAsks(int count) {
            return askOrders.entrySet().stream()
                .limit(count)
                .flatMap(entry -> entry.getValue().stream())
                .collect(Collectors.toList());
        }
        
        public String getSymbol() { return symbol; }
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) {
        IndianStockMarketStreamer streamer = new IndianStockMarketStreamer();
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("🛑 Received shutdown signal");
            streamer.closeMarket();
            streamer.shutdown();
        }));
        
        try {
            // Open market for trading
            streamer.openMarket();
            
            // Run for demo (in production, this would run during market hours)
            Thread.sleep(60000); // Run for 1 minute
            
        } catch (InterruptedException e) {
            logger.info("📊 Demo interrupted");
        } finally {
            streamer.shutdown();
        }
    }
}

/*
Production Deployment Guide:

1. Market Data Infrastructure:
   - Dedicated market data vendors (Thomson Reuters, Bloomberg)
   - Low-latency network connections to exchanges
   - Colocation services for minimum latency
   - Redundant data feeds for reliability

2. Real-time Processing:
   - Stream processing with Apache Flink/Kafka Streams
   - In-memory databases for order books (Redis, Hazelcast)
   - Event sourcing for audit trails
   - CQRS for read/write separation

3. Regulatory Compliance:
   - SEBI regulations compliance
   - Trade reporting requirements
   - Audit trails for all transactions
   - Risk management systems integration

4. Performance Requirements:
   - Sub-millisecond latencies for order processing
   - Thousands of messages per second throughput
   - 99.99% uptime during market hours
   - Zero data loss guarantees

5. Integration Points:
   - NSE/BSE APIs for real market data
   - Trading platforms (Zerodha, Groww, Angel Broking)
   - Risk management systems
   - Settlement and clearing systems

6. Monitoring & Alerting:
   - Real-time latency monitoring
   - Market data quality checks  
   - Trading system health monitoring
   - Regulatory compliance monitoring
*/