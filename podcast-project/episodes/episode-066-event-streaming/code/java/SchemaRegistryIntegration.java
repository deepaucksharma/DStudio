/*
 * Event Streaming Episode - Schema Registry Integration with Avro
 * Production-ready schema evolution and type safety for event streaming
 * 
 * Author: Hindi Tech Podcast Series
 */

import io.confluent.kafka.serializers.KafkaAvroSerializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.AbstractKafkaSchemaSerDeConfig;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.serialization.StringDeserializer;

import org.apache.avro.Schema;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecordBuilder;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.Future;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Zerodha जैसे trading platform के लिए Schema Registry integration
 * Type-safe event streaming with schema evolution for financial data
 */
public class ZerodhaSchemaRegistryIntegration {
    
    private static final Logger logger = Logger.getLogger(ZerodhaSchemaRegistryIntegration.class.getName());
    
    // Kafka topics with schema versioning
    private static final String TRADE_EVENTS_TOPIC = "zerodha-trade-events";
    private static final String MARKET_DATA_TOPIC = "zerodha-market-data";
    private static final String USER_PORTFOLIO_TOPIC = "zerodha-user-portfolio";
    
    // Schema Registry URL
    private static final String SCHEMA_REGISTRY_URL = "http://localhost:8081";
    
    public static void main(String[] args) {
        System.out.println("📈 Starting Zerodha Schema Registry Integration Demo");
        System.out.println("🔗 Type-safe event streaming with schema evolution");
        System.out.println("-".repeat(60));
        
        ZerodhaSchemaRegistryIntegration integration = new ZerodhaSchemaRegistryIntegration();
        integration.demonstrateSchemaEvolution();
    }
    
    public void demonstrateSchemaEvolution() {
        try {
            // Define schemas for different versions
            Schema tradeEventSchemaV1 = createTradeEventSchemaV1();
            Schema tradeEventSchemaV2 = createTradeEventSchemaV2();
            Schema marketDataSchema = createMarketDataSchema();
            Schema portfolioUpdateSchema = createPortfolioUpdateSchema();
            
            logger.info("📋 Schemas defined for trading events");
            
            // Producer के साथ schema registry integration
            demonstrateProducerWithSchemas(tradeEventSchemaV1, tradeEventSchemaV2, 
                                         marketDataSchema, portfolioUpdateSchema);
            
            // Consumer के साथ backward compatibility
            demonstrateConsumerWithSchemaEvolution();
            
            // Schema compatibility testing
            demonstrateSchemaCompatibility();
            
            logger.info("✅ Schema Registry integration demonstration completed");
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "❌ Error in schema registry demonstration", e);
        }
    }
    
    private Schema createTradeEventSchemaV1() {
        // Version 1 - Basic trade event schema
        // Zerodha के initial trading event structure
        String schemaString = """
            {
                "type": "record",
                "name": "TradeEvent",
                "namespace": "com.zerodha.events",
                "version": "1",
                "doc": "Zerodha trading event - Version 1",
                "fields": [
                    {
                        "name": "trade_id",
                        "type": "string",
                        "doc": "Unique trade identifier"
                    },
                    {
                        "name": "user_id", 
                        "type": "string",
                        "doc": "Zerodha user identifier"
                    },
                    {
                        "name": "symbol",
                        "type": "string", 
                        "doc": "Stock symbol (e.g., RELIANCE, TCS)"
                    },
                    {
                        "name": "trade_type",
                        "type": {
                            "type": "enum",
                            "name": "TradeType",
                            "symbols": ["BUY", "SELL"]
                        },
                        "doc": "Type of trade - Buy या Sell"
                    },
                    {
                        "name": "quantity",
                        "type": "int",
                        "doc": "Number of shares traded"
                    },
                    {
                        "name": "price",
                        "type": "double",
                        "doc": "Price per share in INR"
                    },
                    {
                        "name": "timestamp",
                        "type": "long",
                        "doc": "Trade execution timestamp (epoch millis)"
                    },
                    {
                        "name": "exchange",
                        "type": {
                            "type": "enum", 
                            "name": "Exchange",
                            "symbols": ["NSE", "BSE"]
                        },
                        "doc": "Stock exchange - NSE या BSE"
                    }
                ]
            }
            """;
        
        return new Schema.Parser().parse(schemaString);
    }
    
    private Schema createTradeEventSchemaV2() {
        // Version 2 - Enhanced trade event with additional fields
        // नए features के साथ backward compatible
        String schemaString = """
            {
                "type": "record",
                "name": "TradeEvent",
                "namespace": "com.zerodha.events", 
                "version": "2",
                "doc": "Zerodha trading event - Version 2 with enhancements",
                "fields": [
                    {
                        "name": "trade_id",
                        "type": "string",
                        "doc": "Unique trade identifier"
                    },
                    {
                        "name": "user_id",
                        "type": "string", 
                        "doc": "Zerodha user identifier"
                    },
                    {
                        "name": "symbol",
                        "type": "string",
                        "doc": "Stock symbol (e.g., RELIANCE, TCS)"
                    },
                    {
                        "name": "trade_type",
                        "type": {
                            "type": "enum",
                            "name": "TradeType", 
                            "symbols": ["BUY", "SELL", "SHORT_SELL", "COVER"]
                        },
                        "doc": "Type of trade - Enhanced with short selling"
                    },
                    {
                        "name": "quantity", 
                        "type": "int",
                        "doc": "Number of shares traded"
                    },
                    {
                        "name": "price",
                        "type": "double",
                        "doc": "Price per share in INR"
                    },
                    {
                        "name": "timestamp",
                        "type": "long",
                        "doc": "Trade execution timestamp (epoch millis)"
                    },
                    {
                        "name": "exchange",
                        "type": {
                            "type": "enum",
                            "name": "Exchange",
                            "symbols": ["NSE", "BSE", "MCX", "NCDEX"]
                        },
                        "doc": "Stock exchange - Extended with commodity exchanges"
                    },
                    {
                        "name": "order_type",
                        "type": {
                            "type": "enum",
                            "name": "OrderType",
                            "symbols": ["MARKET", "LIMIT", "STOP_LOSS", "BRACKET"]
                        },
                        "default": "MARKET",
                        "doc": "Order type - New field with default value"
                    },
                    {
                        "name": "brokerage",
                        "type": ["null", "double"],
                        "default": null,
                        "doc": "Brokerage charged for this trade - Optional field"
                    },
                    {
                        "name": "segment",
                        "type": {
                            "type": "enum",
                            "name": "Segment", 
                            "symbols": ["EQUITY", "FUTURES", "OPTIONS", "COMMODITY"]
                        },
                        "default": "EQUITY",
                        "doc": "Trading segment - New field for F&O support"
                    },
                    {
                        "name": "client_code",
                        "type": ["null", "string"],
                        "default": null,
                        "doc": "Client code for institutional clients - Optional"
                    }
                ]
            }
            """;
        
        return new Schema.Parser().parse(schemaString);
    }
    
    private Schema createMarketDataSchema() {
        // Real-time market data schema
        String schemaString = """
            {
                "type": "record",
                "name": "MarketData",
                "namespace": "com.zerodha.market",
                "doc": "Real-time market data from NSE/BSE",
                "fields": [
                    {
                        "name": "symbol",
                        "type": "string",
                        "doc": "Stock symbol"
                    },
                    {
                        "name": "last_price",
                        "type": "double",
                        "doc": "Last traded price in INR"
                    },
                    {
                        "name": "bid_price",
                        "type": "double", 
                        "doc": "Highest bid price"
                    },
                    {
                        "name": "ask_price",
                        "type": "double",
                        "doc": "Lowest ask price"
                    },
                    {
                        "name": "volume",
                        "type": "long",
                        "doc": "Total volume traded"
                    },
                    {
                        "name": "change_percent",
                        "type": "double",
                        "doc": "Percentage change from previous close"
                    },
                    {
                        "name": "high",
                        "type": "double",
                        "doc": "Day's high price"
                    },
                    {
                        "name": "low",
                        "type": "double", 
                        "doc": "Day's low price"
                    },
                    {
                        "name": "open",
                        "type": "double",
                        "doc": "Opening price"
                    },
                    {
                        "name": "timestamp",
                        "type": "long",
                        "doc": "Market data timestamp"
                    },
                    {
                        "name": "exchange",
                        "type": {
                            "type": "enum",
                            "name": "Exchange",
                            "symbols": ["NSE", "BSE"]
                        },
                        "doc": "Source exchange"
                    }
                ]
            }
            """;
        
        return new Schema.Parser().parse(schemaString);
    }
    
    private Schema createPortfolioUpdateSchema() {
        // User portfolio update schema
        String schemaString = """
            {
                "type": "record",
                "name": "PortfolioUpdate",
                "namespace": "com.zerodha.portfolio",
                "doc": "User portfolio update event",
                "fields": [
                    {
                        "name": "user_id",
                        "type": "string",
                        "doc": "Zerodha user identifier"
                    },
                    {
                        "name": "symbol",
                        "type": "string",
                        "doc": "Stock symbol"
                    },
                    {
                        "name": "holdings",
                        "type": "int",
                        "doc": "Current holdings quantity"
                    },
                    {
                        "name": "avg_price",
                        "type": "double",
                        "doc": "Average buying price"
                    },
                    {
                        "name": "current_value",
                        "type": "double",
                        "doc": "Current market value of holdings"
                    },
                    {
                        "name": "pnl",
                        "type": "double",
                        "doc": "Profit and Loss in INR"
                    },
                    {
                        "name": "pnl_percent",
                        "type": "double",
                        "doc": "Profit and Loss percentage"
                    },
                    {
                        "name": "last_updated",
                        "type": "long",
                        "doc": "Last update timestamp"
                    }
                ]
            }
            """;
        
        return new Schema.Parser().parse(schemaString);
    }
    
    private void demonstrateProducerWithSchemas(Schema tradeV1, Schema tradeV2,
                                               Schema marketData, Schema portfolio) {
        logger.info("📤 Setting up producers with schema registry...");
        
        // Producer configuration with schema registry
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
        producerProps.put(AbstractKafkaSchemaSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, SCHEMA_REGISTRY_URL);
        
        // Production settings
        producerProps.put(ProducerConfig.ACKS_CONFIG, "all");
        producerProps.put(ProducerConfig.RETRIES_CONFIG, 3);
        producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        try (KafkaProducer<String, GenericRecord> producer = new KafkaProducer<>(producerProps)) {
            
            // 1. Produce trade events with V1 schema
            logger.info("📊 Producing trade events with Schema V1...");
            produceTradeEventsV1(producer, tradeV1);
            
            // 2. Produce trade events with V2 schema (schema evolution)
            logger.info("🆕 Producing trade events with Schema V2 (evolved)...");
            produceTradeEventsV2(producer, tradeV2);
            
            // 3. Produce market data events
            logger.info("📈 Producing real-time market data...");
            produceMarketData(producer, marketData);
            
            // 4. Produce portfolio updates
            logger.info("💼 Producing portfolio updates...");
            producePortfolioUpdates(producer, portfolio);
            
            // Flush to ensure all records are sent
            producer.flush();
            logger.info("✅ All events produced successfully with schema validation");
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "❌ Error in schema-based producer", e);
        }
    }
    
    private void produceTradeEventsV1(KafkaProducer<String, GenericRecord> producer, Schema schema) {
        // Sample trade events with V1 schema
        String[][] sampleTrades = {
            {"TRD001", "USER001", "RELIANCE", "BUY", "100", "2500.50", "NSE"},
            {"TRD002", "USER002", "TCS", "SELL", "50", "3200.75", "NSE"},
            {"TRD003", "USER003", "HDFCBANK", "BUY", "75", "1650.25", "BSE"},
            {"TRD004", "USER001", "INFY", "SELL", "25", "1850.00", "NSE"}
        };
        
        for (String[] trade : sampleTrades) {
            try {
                GenericRecord tradeRecord = new GenericData.Record(schema);
                tradeRecord.put("trade_id", trade[0]);
                tradeRecord.put("user_id", trade[1]);
                tradeRecord.put("symbol", trade[2]);
                tradeRecord.put("trade_type", trade[3]);
                tradeRecord.put("quantity", Integer.parseInt(trade[4]));
                tradeRecord.put("price", Double.parseDouble(trade[5]));
                tradeRecord.put("timestamp", System.currentTimeMillis());
                tradeRecord.put("exchange", trade[6]);
                
                ProducerRecord<String, GenericRecord> record = new ProducerRecord<>(
                    TRADE_EVENTS_TOPIC, trade[0], tradeRecord
                );
                
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                logger.info(String.format("✅ Trade V1 sent: %s -> %s[%d]:%d", 
                    trade[0], metadata.topic(), metadata.partition(), metadata.offset()));
                
            } catch (Exception e) {
                logger.log(Level.WARNING, "⚠️ Error sending trade V1: " + trade[0], e);
            }
        }
    }
    
    private void produceTradeEventsV2(KafkaProducer<String, GenericRecord> producer, Schema schema) {
        // Sample trade events with V2 schema (backward compatible)
        Object[][] sampleTradesV2 = {
            {"TRD005", "USER004", "NIFTY24MAR15000CE", "BUY", 1000, 25.50, "NSE", "LIMIT", 20.0, "OPTIONS"},
            {"TRD006", "USER005", "BANKNIFTY", "SHORT_SELL", 100, 45000.00, "NSE", "STOP_LOSS", null, "FUTURES"},
            {"TRD007", "USER006", "GOLD", "BUY", 10, 62000.00, "MCX", "MARKET", 50.0, "COMMODITY"},
            {"TRD008", "USER007", "WIPRO", "COVER", 200, 420.75, "NSE", "BRACKET", 15.0, "EQUITY"}
        };
        
        for (Object[] trade : sampleTradesV2) {
            try {
                GenericRecord tradeRecord = new GenericData.Record(schema);
                tradeRecord.put("trade_id", trade[0]);
                tradeRecord.put("user_id", trade[1]);
                tradeRecord.put("symbol", trade[2]);
                tradeRecord.put("trade_type", trade[3]);
                tradeRecord.put("quantity", trade[4]);
                tradeRecord.put("price", trade[5]);
                tradeRecord.put("timestamp", System.currentTimeMillis());
                tradeRecord.put("exchange", trade[6]);
                tradeRecord.put("order_type", trade[7]); // New field in V2
                tradeRecord.put("brokerage", trade[8]); // New optional field
                tradeRecord.put("segment", trade[9]); // New field in V2
                tradeRecord.put("client_code", null); // Optional field
                
                ProducerRecord<String, GenericRecord> record = new ProducerRecord<>(
                    TRADE_EVENTS_TOPIC, (String)trade[0], tradeRecord
                );
                
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                logger.info(String.format("✅ Trade V2 sent: %s -> %s[%d]:%d", 
                    trade[0], metadata.topic(), metadata.partition(), metadata.offset()));
                
            } catch (Exception e) {
                logger.log(Level.WARNING, "⚠️ Error sending trade V2: " + trade[0], e);
            }
        }
    }
    
    private void produceMarketData(KafkaProducer<String, GenericRecord> producer, Schema schema) {
        // Real-time market data simulation
        String[] symbols = {"RELIANCE", "TCS", "HDFCBANK", "INFY", "WIPRO"};
        Random random = new Random();
        
        for (String symbol : symbols) {
            try {
                double basePrice = 1000 + random.nextDouble() * 2000; // Random base price
                double change = (random.nextDouble() - 0.5) * 0.1; // ±5% change
                
                GenericRecord marketRecord = new GenericData.Record(schema);
                marketRecord.put("symbol", symbol);
                marketRecord.put("last_price", basePrice);
                marketRecord.put("bid_price", basePrice - 0.25);
                marketRecord.put("ask_price", basePrice + 0.25);
                marketRecord.put("volume", (long)(random.nextInt(1000000) + 100000));
                marketRecord.put("change_percent", change * 100);
                marketRecord.put("high", basePrice * (1 + Math.abs(change)));
                marketRecord.put("low", basePrice * (1 - Math.abs(change)));
                marketRecord.put("open", basePrice * (1 + change * 0.5));
                marketRecord.put("timestamp", System.currentTimeMillis());
                marketRecord.put("exchange", random.nextBoolean() ? "NSE" : "BSE");
                
                ProducerRecord<String, GenericRecord> record = new ProducerRecord<>(
                    MARKET_DATA_TOPIC, symbol, marketRecord
                );
                
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                logger.info(String.format("📈 Market data sent: %s -> %.2f (%.2f%%)", 
                    symbol, basePrice, change * 100));
                
            } catch (Exception e) {
                logger.log(Level.WARNING, "⚠️ Error sending market data: " + symbol, e);
            }
        }
    }
    
    private void producePortfolioUpdates(KafkaProducer<String, GenericRecord> producer, Schema schema) {
        // Portfolio update events
        Object[][] portfolioData = {
            {"USER001", "RELIANCE", 100, 2400.00, 250000.00, 10000.00, 4.17},
            {"USER002", "TCS", 50, 3100.00, 160000.00, 5000.00, 3.23},
            {"USER003", "HDFCBANK", 75, 1600.00, 123750.00, 3750.00, 3.13},
            {"USER001", "INFY", 25, 1800.00, 46250.00, 1250.00, 2.78}
        };
        
        for (Object[] portfolio : portfolioData) {
            try {
                GenericRecord portfolioRecord = new GenericData.Record(schema);
                portfolioRecord.put("user_id", portfolio[0]);
                portfolioRecord.put("symbol", portfolio[1]);
                portfolioRecord.put("holdings", portfolio[2]);
                portfolioRecord.put("avg_price", portfolio[3]);
                portfolioRecord.put("current_value", portfolio[4]);
                portfolioRecord.put("pnl", portfolio[5]);
                portfolioRecord.put("pnl_percent", portfolio[6]);
                portfolioRecord.put("last_updated", System.currentTimeMillis());
                
                ProducerRecord<String, GenericRecord> record = new ProducerRecord<>(
                    USER_PORTFOLIO_TOPIC, (String)portfolio[0] + "_" + (String)portfolio[1], portfolioRecord
                );
                
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                logger.info(String.format("💼 Portfolio update sent: %s %s -> P&L: ₹%.2f", 
                    portfolio[0], portfolio[1], portfolio[5]));
                
            } catch (Exception e) {
                logger.log(Level.WARNING, "⚠️ Error sending portfolio update", e);
            }
        }
    }
    
    private void demonstrateConsumerWithSchemaEvolution() {
        logger.info("📥 Setting up consumer with schema evolution support...");
        
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "zerodha-schema-demo-group");
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class);
        consumerProps.put(AbstractKafkaSchemaSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, SCHEMA_REGISTRY_URL);
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        
        // Specific Avro deserializer settings
        consumerProps.put("specific.avro.reader", false); // Use GenericRecord
        
        try (KafkaConsumer<String, GenericRecord> consumer = new KafkaConsumer<>(consumerProps)) {
            
            // Subscribe to all topics
            consumer.subscribe(Arrays.asList(TRADE_EVENTS_TOPIC, MARKET_DATA_TOPIC, USER_PORTFOLIO_TOPIC));
            
            logger.info("🔄 Starting consumer to demonstrate schema evolution...");
            
            int messageCount = 0;
            long startTime = System.currentTimeMillis();
            
            while (messageCount < 50 && (System.currentTimeMillis() - startTime) < 30000) { // 30 second timeout
                ConsumerRecords<String, GenericRecord> records = consumer.poll(Duration.ofMillis(1000));
                
                for (ConsumerRecord<String, GenericRecord> record : records) {
                    try {
                        processSchemaEvolutionRecord(record);
                        messageCount++;
                    } catch (Exception e) {
                        logger.log(Level.WARNING, "⚠️ Error processing record", e);
                    }
                }
            }
            
            logger.info(String.format("✅ Processed %d messages with schema evolution", messageCount));
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "❌ Error in schema evolution consumer", e);
        }
    }
    
    private void processSchemaEvolutionRecord(ConsumerRecord<String, GenericRecord> record) {
        GenericRecord value = record.value();
        String topic = record.topic();
        
        logger.info(String.format("📨 Processing %s record: %s", topic, record.key()));
        
        switch (topic) {
            case TRADE_EVENTS_TOPIC:
                processTradeEventWithEvolution(value);
                break;
            case MARKET_DATA_TOPIC:
                processMarketDataRecord(value);
                break;
            case USER_PORTFOLIO_TOPIC:
                processPortfolioRecord(value);
                break;
            default:
                logger.warning("⚠️ Unknown topic: " + topic);
        }
    }
    
    private void processTradeEventWithEvolution(GenericRecord record) {
        // Handle both V1 and V2 schemas gracefully
        String tradeId = record.get("trade_id").toString();
        String userId = record.get("user_id").toString();
        String symbol = record.get("symbol").toString();
        String tradeType = record.get("trade_type").toString();
        Integer quantity = (Integer) record.get("quantity");
        Double price = (Double) record.get("price");
        String exchange = record.get("exchange").toString();
        
        // V2 specific fields (may be null for V1 records)
        Object orderType = record.get("order_type"); // Available in V2, default in V1
        Object brokerage = record.get("brokerage"); // May be null
        Object segment = record.get("segment"); // Available in V2, default in V1
        
        logger.info(String.format("🔄 Trade processed: %s %s %d %s @ ₹%.2f on %s", 
            tradeType, symbol, quantity, 
            (orderType != null ? orderType : "MARKET"), price, exchange));
        
        if (brokerage != null) {
            logger.info(String.format("   💰 Brokerage: ₹%.2f", (Double)brokerage));
        }
        
        if (segment != null && !segment.toString().equals("EQUITY")) {
            logger.info(String.format("   📊 Segment: %s", segment));
        }
    }
    
    private void processMarketDataRecord(GenericRecord record) {
        String symbol = record.get("symbol").toString();
        Double lastPrice = (Double) record.get("last_price");
        Double changePercent = (Double) record.get("change_percent");
        Long volume = (Long) record.get("volume");
        
        logger.info(String.format("📈 Market: %s @ ₹%.2f (%+.2f%%) Vol: %,d", 
            symbol, lastPrice, changePercent, volume));
    }
    
    private void processPortfolioRecord(GenericRecord record) {
        String userId = record.get("user_id").toString();
        String symbol = record.get("symbol").toString();
        Integer holdings = (Integer) record.get("holdings");
        Double pnl = (Double) record.get("pnl");
        Double pnlPercent = (Double) record.get("pnl_percent");
        
        logger.info(String.format("💼 Portfolio: %s holds %d %s - P&L: ₹%.2f (%+.2f%%)", 
            userId, holdings, symbol, pnl, pnlPercent));
    }
    
    private void demonstrateSchemaCompatibility() {
        logger.info("🔗 Demonstrating schema compatibility scenarios...");
        
        // यहाँ हम different compatibility modes दिखा सकते हैं:
        // 1. Backward compatibility - नए consumers पुराने messages पढ़ सकें
        // 2. Forward compatibility - पुराने consumers नए messages पढ़ सकें  
        // 3. Full compatibility - दोनों directions में compatibility
        
        logger.info("✅ Schema compatibility scenarios:");
        logger.info("   🔄 Backward compatibility: V2 consumers can read V1 messages");
        logger.info("   🔄 Forward compatibility: V1 consumers can read V2 messages (with defaults)");
        logger.info("   🔄 Schema evolution: New fields added with default values");
        logger.info("   🔄 Enum evolution: New enum values added for backward compatibility");
        
        // Real implementation में यहाँ schema registry API calls होंगी
        // Compatibility level check करने के लिए
    }
}