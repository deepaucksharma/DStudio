// 11_graphql_subscriptions.js
// GraphQL Subscriptions implementation for real-time updates
// Indian e-commerce के लिए real-time notifications और live updates

const { ApolloServer, gql, PubSub, withFilter } = require('apollo-server-express');
const { createServer } = require('http');
const express = require('express');
const { SubscriptionServer } = require('subscriptions-transport-ws');
const { execute, subscribe } = require('graphql');

// PubSub instance - Production में Redis PubSub use करेंगे
const pubsub = new PubSub();

// Subscription event types - India-specific events
const SUBSCRIPTION_EVENTS = {
  // Order related events
  ORDER_CREATED: 'ORDER_CREATED',
  ORDER_STATUS_UPDATED: 'ORDER_STATUS_UPDATED',
  ORDER_DELIVERED: 'ORDER_DELIVERED',
  
  // Product related events  
  PRODUCT_ADDED: 'PRODUCT_ADDED',
  PRODUCT_PRICE_CHANGED: 'PRODUCT_PRICE_CHANGED',
  PRODUCT_OUT_OF_STOCK: 'PRODUCT_OUT_OF_STOCK',
  PRODUCT_BACK_IN_STOCK: 'PRODUCT_BACK_IN_STOCK',
  
  // Seller related events
  SELLER_ONLINE: 'SELLER_ONLINE',
  SELLER_OFFLINE: 'SELLER_OFFLINE',
  NEW_SELLER_JOINED: 'NEW_SELLER_JOINED',
  
  // Live events - Indian context
  FLASH_SALE_STARTED: 'FLASH_SALE_STARTED',
  FESTIVAL_OFFER_ACTIVATED: 'FESTIVAL_OFFER_ACTIVATED',
  CRICKET_MATCH_OFFER: 'CRICKET_MATCH_OFFER',
  IPL_SPECIAL_DEAL: 'IPL_SPECIAL_DEAL',
  
  // System events
  PAYMENT_STATUS_UPDATE: 'PAYMENT_STATUS_UPDATE',
  DELIVERY_TRACKING_UPDATE: 'DELIVERY_TRACKING_UPDATE',
  CUSTOMER_SUPPORT_MESSAGE: 'CUSTOMER_SUPPORT_MESSAGE',
  
  // Analytics events
  POPULAR_PRODUCT_ALERT: 'POPULAR_PRODUCT_ALERT',
  TRENDING_CATEGORY: 'TRENDING_CATEGORY'
};

// Mock data stores
const activeUsers = new Map(); // Connected users
const userSubscriptions = new Map(); // User-specific subscriptions
const liveOrders = new Map(); // Active orders tracking
const flashSales = new Map(); // Active flash sales

// Mock data - would come from database in production
const mockData = {
  users: new Map([
    ['1', { id: '1', name: 'राहुल शर्मा', city: 'Delhi', preferredLanguage: 'hindi' }],
    ['2', { id: '2', name: 'प्रिया पटेल', city: 'Mumbai', preferredLanguage: 'gujarati' }],
    ['3', { id: '3', name: 'अमित कुमार', city: 'Bangalore', preferredLanguage: 'english' }],
    ['4', { id: '4', name: 'सुनीता देवी', city: 'Chennai', preferredLanguage: 'tamil' }]
  ]),
  
  products: new Map([
    ['1', { id: '1', name: 'iPhone 15 Pro', price: 134900, stock: 10, category: 'phones' }],
    ['2', { id: '2', name: 'Samsung Galaxy S24', price: 84999, stock: 5, category: 'phones' }],
    ['3', { id: '3', name: 'MacBook Air M2', price: 114900, stock: 8, category: 'laptops' }],
    ['4', { id: '4', name: 'OnePlus 12', price: 64999, stock: 15, category: 'phones' }]
  ]),
  
  sellers: new Map([
    ['1', { id: '1', name: 'TechZone Delhi', status: 'online', city: 'Delhi' }],
    ['2', { id: '2', name: 'Mumbai Electronics', status: 'online', city: 'Mumbai' }],
    ['3', { id: '3', name: 'Bangalore Gadgets', status: 'offline', city: 'Bangalore' }]
  ])
};

// GraphQL Schema with Subscriptions
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    city: String!
    preferredLanguage: String!
    isOnline: Boolean!
  }
  
  type Product {
    id: ID!
    name: String!
    price: Float!
    stock: Int!
    category: String!
    isInStock: Boolean!
  }
  
  type Seller {
    id: ID!
    name: String!
    city: String!
    status: String!
    lastSeen: String
  }
  
  type Order {
    id: ID!
    userId: ID!
    productIds: [ID!]!
    totalAmount: Float!
    status: String!
    createdAt: String!
    estimatedDelivery: String
    trackingId: String
  }
  
  # Flash Sale type for Indian festivals
  type FlashSale {
    id: ID!
    name: String!
    description: String!
    discountPercentage: Float!
    startTime: String!
    endTime: String!
    productIds: [ID!]!
    festival: String
    remainingTime: Int # seconds remaining
  }
  
  # Cricket Match Offer - भारत में cricket बहुत popular है
  type CricketOffer {
    id: ID!
    matchName: String!
    team1: String!
    team2: String!
    discountPercentage: Float!
    validTill: String!
    offerCode: String!
    description: String!
  }
  
  # Payment Status Update
  type PaymentUpdate {
    orderId: ID!
    status: String!
    paymentMethod: String!
    amount: Float!
    timestamp: String!
    gatewayResponse: String
  }
  
  # Delivery Tracking Update
  type DeliveryUpdate {
    orderId: ID!
    trackingId: String!
    status: String!
    location: String!
    expectedDelivery: String
    deliveryPartner: String!
    timestamp: String!
  }
  
  # Customer Support Message
  type SupportMessage {
    id: ID!
    userId: ID!
    message: String!
    type: String! # info, warning, urgent
    timestamp: String!
    supportAgentName: String
  }
  
  # Popular Product Alert
  type PopularProductAlert {
    productId: ID!
    productName: String!
    viewCount: Int!
    orderCount: Int!
    trendingScore: Float!
    category: String!
    timestamp: String!
  }
  
  type Query {
    users: [User!]!
    products: [Product!]!
    sellers: [Seller!]!
    orders: [Order!]!
    activeFlashSales: [FlashSale!]!
    user(id: ID!): User
    product(id: ID!): Product
    order(id: ID!): Order
  }
  
  type Mutation {
    # Order mutations
    createOrder(userId: ID!, productIds: [ID!]!, totalAmount: Float!): Order!
    updateOrderStatus(orderId: ID!, status: String!): Order!
    
    # Product mutations
    updateProductPrice(productId: ID!, newPrice: Float!): Product!
    updateProductStock(productId: ID!, newStock: Int!): Product!
    
    # Seller mutations
    updateSellerStatus(sellerId: ID!, status: String!): Seller!
    
    # Flash sale mutations
    startFlashSale(
      name: String!, 
      discountPercentage: Float!, 
      durationMinutes: Int!,
      productIds: [ID!]!,
      festival: String
    ): FlashSale!
    
    # Cricket offer
    createCricketOffer(
      matchName: String!,
      team1: String!,
      team2: String!,
      discountPercentage: Float!
    ): CricketOffer!
    
    # User connection tracking
    userConnected(userId: ID!): Boolean!
    userDisconnected(userId: ID!): Boolean!
    
    # Test mutations for demo
    simulateOrderUpdate(orderId: ID!): Boolean!
    simulateDelivery(orderId: ID!): Boolean!
    simulateProductAlert(productId: ID!): Boolean!
  }
  
  type Subscription {
    # Order subscriptions - User को अपने orders की updates
    orderStatusUpdated(userId: ID!): Order!
    orderDelivered(userId: ID!): Order!
    paymentStatusUpdate(userId: ID!): PaymentUpdate!
    deliveryTracking(orderId: ID!): DeliveryUpdate!
    
    # Product subscriptions - Price drops, stock updates
    productPriceChanged(productId: ID): Product!
    productBackInStock(productId: ID): Product!
    productOutOfStock(productId: ID): Product!
    
    # Seller subscriptions
    sellerStatusChanged(sellerId: ID): Seller!
    newSellerJoined: Seller!
    
    # Live events - Indian context के साथ
    flashSaleStarted: FlashSale!
    festivalOfferActivated(festival: String): FlashSale!
    cricketMatchOffer: CricketOffer!
    iplSpecialDeal: CricketOffer!
    
    # Customer support
    supportMessage(userId: ID!): SupportMessage!
    
    # Analytics subscriptions
    popularProductAlert(category: String): PopularProductAlert!
    trendingCategory: String!
    
    # System-wide notifications
    systemAnnouncement: String!
    maintenanceAlert: String!
    
    # User activity
    userOnline: User!
    userOffline: User!
  }
`;

// Helper functions
function generateId() {
  return Math.random().toString(36).substr(2, 9);
}

function getCurrentTimestamp() {
  return new Date().toISOString();
}

function getEstimatedDelivery() {
  const deliveryDate = new Date();
  deliveryDate.setDate(deliveryDate.getDate() + Math.floor(Math.random() * 7) + 1);
  return deliveryDate.toISOString();
}

// Resolvers
const resolvers = {
  Query: {
    users: () => Array.from(mockData.users.values()),
    products: () => Array.from(mockData.products.values()),
    sellers: () => Array.from(mockData.sellers.values()),
    orders: () => Array.from(liveOrders.values()),
    activeFlashSales: () => Array.from(flashSales.values()),
    
    user: (_, { id }) => mockData.users.get(id),
    product: (_, { id }) => {
      const product = mockData.products.get(id);
      if (product) {
        product.isInStock = product.stock > 0;
      }
      return product;
    },
    order: (_, { id }) => liveOrders.get(id)
  },

  Mutation: {
    createOrder: (_, { userId, productIds, totalAmount }) => {
      console.log(`📦 Creating order for user ${userId}: products=${productIds}, amount=${totalAmount}`);
      
      const orderId = generateId();
      const order = {
        id: orderId,
        userId,
        productIds,
        totalAmount,
        status: 'pending',
        createdAt: getCurrentTimestamp(),
        estimatedDelivery: getEstimatedDelivery(),
        trackingId: `TRK${orderId.toUpperCase()}`
      };
      
      liveOrders.set(orderId, order);
      
      // Publish order created event
      pubsub.publish(SUBSCRIPTION_EVENTS.ORDER_CREATED, {
        orderStatusUpdated: order
      });
      
      console.log(`✅ Order created: ${orderId}`);
      return order;
    },
    
    updateOrderStatus: (_, { orderId, status }) => {
      console.log(`🔄 Updating order ${orderId} status to: ${status}`);
      
      const order = liveOrders.get(orderId);
      if (!order) {
        throw new Error(`Order ${orderId} not found`);
      }
      
      order.status = status;
      order.updatedAt = getCurrentTimestamp();
      
      // Publish status update
      pubsub.publish(SUBSCRIPTION_EVENTS.ORDER_STATUS_UPDATED, {
        orderStatusUpdated: order
      });
      
      // If delivered, publish separate event
      if (status === 'delivered') {
        pubsub.publish(SUBSCRIPTION_EVENTS.ORDER_DELIVERED, {
          orderDelivered: order
        });
        
        // Send delivery update
        pubsub.publish(SUBSCRIPTION_EVENTS.DELIVERY_TRACKING_UPDATE, {
          deliveryTracking: {
            orderId: order.id,
            trackingId: order.trackingId,
            status: 'delivered',
            location: 'Customer\'s Address',
            deliveryPartner: 'Delhivery',
            timestamp: getCurrentTimestamp()
          }
        });
      }
      
      console.log(`✅ Order status updated: ${orderId} -> ${status}`);
      return order;
    },
    
    updateProductPrice: (_, { productId, newPrice }) => {
      console.log(`💰 Updating product ${productId} price to: ₹${newPrice}`);
      
      const product = mockData.products.get(productId);
      if (!product) {
        throw new Error(`Product ${productId} not found`);
      }
      
      const oldPrice = product.price;
      product.price = newPrice;
      
      // Publish price change event
      pubsub.publish(SUBSCRIPTION_EVENTS.PRODUCT_PRICE_CHANGED, {
        productPriceChanged: product
      });
      
      console.log(`✅ Price updated: ${product.name} ₹${oldPrice} -> ₹${newPrice}`);
      return product;
    },
    
    updateProductStock: (_, { productId, newStock }) => {
      console.log(`📦 Updating product ${productId} stock to: ${newStock}`);
      
      const product = mockData.products.get(productId);
      if (!product) {
        throw new Error(`Product ${productId} not found`);
      }
      
      const oldStock = product.stock;
      product.stock = newStock;
      product.isInStock = newStock > 0;
      
      // Publish stock events
      if (oldStock === 0 && newStock > 0) {
        pubsub.publish(SUBSCRIPTION_EVENTS.PRODUCT_BACK_IN_STOCK, {
          productBackInStock: product
        });
        console.log(`🎉 Product back in stock: ${product.name}`);
      } else if (oldStock > 0 && newStock === 0) {
        pubsub.publish(SUBSCRIPTION_EVENTS.PRODUCT_OUT_OF_STOCK, {
          productOutOfStock: product
        });
        console.log(`⚠️ Product out of stock: ${product.name}`);
      }
      
      return product;
    },
    
    startFlashSale: (_, { name, discountPercentage, durationMinutes, productIds, festival }) => {
      console.log(`⚡ Starting flash sale: ${name} (${discountPercentage}% off for ${durationMinutes} minutes)`);
      
      const saleId = generateId();
      const startTime = new Date();
      const endTime = new Date(startTime.getTime() + durationMinutes * 60000);
      
      const flashSale = {
        id: saleId,
        name,
        description: festival ? 
          `${festival} special flash sale! ${discountPercentage}% off on selected items` : 
          `Flash sale: ${discountPercentage}% off!`,
        discountPercentage,
        startTime: startTime.toISOString(),
        endTime: endTime.toISOString(),
        productIds,
        festival: festival || null,
        remainingTime: durationMinutes * 60
      };
      
      flashSales.set(saleId, flashSale);
      
      // Publish flash sale events
      pubsub.publish(SUBSCRIPTION_EVENTS.FLASH_SALE_STARTED, {
        flashSaleStarted: flashSale
      });
      
      if (festival) {
        pubsub.publish(SUBSCRIPTION_EVENTS.FESTIVAL_OFFER_ACTIVATED, {
          festivalOfferActivated: flashSale
        });
      }
      
      // Auto-end flash sale after duration
      setTimeout(() => {
        flashSales.delete(saleId);
        console.log(`⏰ Flash sale ended: ${name}`);
      }, durationMinutes * 60000);
      
      console.log(`✅ Flash sale started: ${name}`);
      return flashSale;
    },
    
    createCricketOffer: (_, { matchName, team1, team2, discountPercentage }) => {
      console.log(`🏏 Creating cricket match offer: ${team1} vs ${team2} - ${discountPercentage}% off`);
      
      const offer = {
        id: generateId(),
        matchName,
        team1,
        team2,
        discountPercentage,
        validTill: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), // 3 hours
        offerCode: `CRICKET${discountPercentage}`,
        description: `${team1} vs ${team2} match special! Get ${discountPercentage}% off with code CRICKET${discountPercentage}`
      };
      
      // Publish cricket offer
      if (matchName.includes('IPL')) {
        pubsub.publish(SUBSCRIPTION_EVENTS.IPL_SPECIAL_DEAL, {
          iplSpecialDeal: offer
        });
      } else {
        pubsub.publish(SUBSCRIPTION_EVENTS.CRICKET_MATCH_OFFER, {
          cricketMatchOffer: offer
        });
      }
      
      console.log(`✅ Cricket offer created: ${offer.offerCode}`);
      return offer;
    },
    
    userConnected: (_, { userId }) => {
      console.log(`👤 User connected: ${userId}`);
      activeUsers.set(userId, { connectedAt: new Date(), isOnline: true });
      
      const user = mockData.users.get(userId);
      if (user) {
        user.isOnline = true;
        pubsub.publish(SUBSCRIPTION_EVENTS.USER_ONLINE, { userOnline: user });
      }
      
      return true;
    },
    
    userDisconnected: (_, { userId }) => {
      console.log(`👤 User disconnected: ${userId}`);
      activeUsers.delete(userId);
      
      const user = mockData.users.get(userId);
      if (user) {
        user.isOnline = false;
        pubsub.publish(SUBSCRIPTION_EVENTS.USER_OFFLINE, { userOffline: user });
      }
      
      return true;
    },
    
    // Demo simulation mutations
    simulateOrderUpdate: (_, { orderId }) => {
      const order = liveOrders.get(orderId);
      if (!order) return false;
      
      const statuses = ['confirmed', 'preparing', 'shipped', 'out_for_delivery', 'delivered'];
      const currentIndex = statuses.indexOf(order.status);
      const nextStatus = statuses[Math.min(currentIndex + 1, statuses.length - 1)];
      
      // Update status
      order.status = nextStatus;
      pubsub.publish(SUBSCRIPTION_EVENTS.ORDER_STATUS_UPDATED, { orderStatusUpdated: order });
      
      // Simulate payment update
      pubsub.publish(SUBSCRIPTION_EVENTS.PAYMENT_STATUS_UPDATE, {
        paymentStatusUpdate: {
          orderId: order.id,
          status: 'completed',
          paymentMethod: 'UPI',
          amount: order.totalAmount,
          timestamp: getCurrentTimestamp(),
          gatewayResponse: 'Payment successful via Paytm UPI'
        }
      });
      
      return true;
    },
    
    simulateDelivery: (_, { orderId }) => {
      const locations = [
        'Delhi Sorting Facility',
        'Mumbai Hub',
        'Local Delivery Center',
        'Out for Delivery',
        'Delivered'
      ];
      
      let currentLocation = 0;
      const interval = setInterval(() => {
        pubsub.publish(SUBSCRIPTION_EVENTS.DELIVERY_TRACKING_UPDATE, {
          deliveryTracking: {
            orderId,
            trackingId: `TRK${orderId.toUpperCase()}`,
            status: currentLocation < 4 ? 'in_transit' : 'delivered',
            location: locations[currentLocation],
            deliveryPartner: 'Delhivery Express',
            timestamp: getCurrentTimestamp(),
            expectedDelivery: currentLocation < 4 ? 'Today 6 PM' : null
          }
        });
        
        currentLocation++;
        if (currentLocation >= locations.length) {
          clearInterval(interval);
        }
      }, 2000);
      
      return true;
    },
    
    simulateProductAlert: (_, { productId }) => {
      const product = mockData.products.get(productId);
      if (!product) return false;
      
      pubsub.publish(SUBSCRIPTION_EVENTS.POPULAR_PRODUCT_ALERT, {
        popularProductAlert: {
          productId: product.id,
          productName: product.name,
          viewCount: Math.floor(Math.random() * 10000) + 1000,
          orderCount: Math.floor(Math.random() * 500) + 100,
          trendingScore: Math.random() * 10,
          category: product.category,
          timestamp: getCurrentTimestamp()
        }
      });
      
      return true;
    }
  },

  Subscription: {
    // Order subscriptions - User-specific filtering
    orderStatusUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.ORDER_STATUS_UPDATED),
        (payload, variables) => {
          return payload.orderStatusUpdated.userId === variables.userId;
        }
      )
    },
    
    orderDelivered: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.ORDER_DELIVERED),
        (payload, variables) => {
          return payload.orderDelivered.userId === variables.userId;
        }
      )
    },
    
    paymentStatusUpdate: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.PAYMENT_STATUS_UPDATE),
        (payload, variables) => {
          const order = liveOrders.get(payload.paymentStatusUpdate.orderId);
          return order && order.userId === variables.userId;
        }
      )
    },
    
    deliveryTracking: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.DELIVERY_TRACKING_UPDATE),
        (payload, variables) => {
          return payload.deliveryTracking.orderId === variables.orderId;
        }
      )
    },
    
    // Product subscriptions - Optional filtering by productId
    productPriceChanged: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.PRODUCT_PRICE_CHANGED),
        (payload, variables) => {
          return !variables.productId || payload.productPriceChanged.id === variables.productId;
        }
      )
    },
    
    productBackInStock: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.PRODUCT_BACK_IN_STOCK),
        (payload, variables) => {
          return !variables.productId || payload.productBackInStock.id === variables.productId;
        }
      )
    },
    
    productOutOfStock: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.PRODUCT_OUT_OF_STOCK),
        (payload, variables) => {
          return !variables.productId || payload.productOutOfStock.id === variables.productId;
        }
      )
    },
    
    // Seller subscriptions
    sellerStatusChanged: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.SELLER_ONLINE),
        (payload, variables) => {
          return !variables.sellerId || payload.sellerStatusChanged.id === variables.sellerId;
        }
      )
    },
    
    newSellerJoined: {
      subscribe: () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.NEW_SELLER_JOINED)
    },
    
    // Live events - Indian context
    flashSaleStarted: {
      subscribe: () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.FLASH_SALE_STARTED)
    },
    
    festivalOfferActivated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.FESTIVAL_OFFER_ACTIVATED),
        (payload, variables) => {
          return !variables.festival || payload.festivalOfferActivated.festival === variables.festival;
        }
      )
    },
    
    cricketMatchOffer: {
      subscribe: () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.CRICKET_MATCH_OFFER)
    },
    
    iplSpecialDeal: {
      subscribe: () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.IPL_SPECIAL_DEAL)
    },
    
    // Customer support
    supportMessage: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.CUSTOMER_SUPPORT_MESSAGE),
        (payload, variables) => {
          return payload.supportMessage.userId === variables.userId;
        }
      )
    },
    
    // Analytics subscriptions
    popularProductAlert: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.POPULAR_PRODUCT_ALERT),
        (payload, variables) => {
          return !variables.category || payload.popularProductAlert.category === variables.category;
        }
      )
    },
    
    trendingCategory: {
      subscribe: () => pubsub.asyncIterator(SUBSCRIPTION_EVENTS.TRENDING_CATEGORY)
    },
    
    // System notifications
    systemAnnouncement: {
      subscribe: () => pubsub.asyncIterator('SYSTEM_ANNOUNCEMENT')
    },
    
    maintenanceAlert: {
      subscribe: () => pubsub.asyncIterator('MAINTENANCE_ALERT')
    },
    
    // User activity
    userOnline: {
      subscribe: () => pubsub.asyncIterator('USER_ONLINE')
    },
    
    userOffline: {
      subscribe: () => pubsub.asyncIterator('USER_OFFLINE')
    }
  }
};

async function startSubscriptionServer() {
  const app = express();
  const httpServer = createServer(app);
  
  // Apollo Server
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    context: ({ req, connection }) => {
      // WebSocket connection context
      if (connection) {
        return {
          ...connection.context,
          pubsub
        };
      }
      
      // HTTP request context
      return {
        user: req.headers['x-user-id'] ? {
          id: req.headers['x-user-id'],
          role: req.headers['x-user-role'] || 'customer'
        } : null,
        pubsub
      };
    },
    subscriptions: {
      path: '/subscriptions',
      onConnect: (connectionParams, webSocket, context) => {
        console.log('🔌 WebSocket connected');
        console.log('Connection params:', connectionParams);
        
        // Authentication check
        const authToken = connectionParams.Authorization || connectionParams.authorization;
        const userId = connectionParams['x-user-id'] || connectionParams.userId;
        
        if (userId) {
          // Track user connection
          activeUsers.set(userId, { 
            connectedAt: new Date(), 
            webSocket,
            isOnline: true 
          });
          
          console.log(`👤 User ${userId} connected to subscriptions`);
          
          return {
            userId,
            authToken,
            connectedAt: new Date()
          };
        }
        
        return {
          connectedAt: new Date()
        };
      },
      onDisconnect: (webSocket, context) => {
        console.log('🔌 WebSocket disconnected');
        
        // Clean up user connections
        for (const [userId, userData] of activeUsers.entries()) {
          if (userData.webSocket === webSocket) {
            activeUsers.delete(userId);
            console.log(`👤 User ${userId} disconnected from subscriptions`);
            break;
          }
        }
      }
    },
    
    formatError: (error) => {
      console.error('❌ GraphQL Subscription Error:', error);
      return {
        message: error.message,
        code: error.extensions?.code || 'SUBSCRIPTION_ERROR',
        timestamp: new Date().toISOString()
      };
    }
  });
  
  server.applyMiddleware({ app, path: '/graphql' });
  
  const PORT = process.env.PORT || 4025;
  
  // Health endpoint
  app.get('/health', (req, res) => {
    res.json({
      service: 'graphql-subscriptions',
      status: 'healthy',
      activeUsers: activeUsers.size,
      activeOrders: liveOrders.size,
      activeFlashSales: flashSales.size,
      features: [
        'Real-time order tracking',
        'Live product updates',
        'Flash sale notifications',
        'Cricket match offers',
        'Festival-specific deals',
        'Delivery tracking'
      ]
    });
  });
  
  // Demo endpoints
  app.get('/demo', (req, res) => {
    res.json({
      title: 'GraphQL Subscriptions Demo',
      description: 'Real-time updates for Indian e-commerce',
      subscription_examples: {
        order_tracking: `
          subscription OrderTracking($userId: ID!) {
            orderStatusUpdated(userId: $userId) {
              id
              status
              estimatedDelivery
            }
            deliveryTracking(orderId: "ORDER_ID") {
              trackingId
              location
              status
            }
          }
        `,
        
        product_alerts: `
          subscription ProductAlerts($productId: ID) {
            productPriceChanged(productId: $productId) {
              id
              name
              price
            }
            productBackInStock(productId: $productId) {
              id
              name
              stock
            }
          }
        `,
        
        live_events: `
          subscription LiveEvents {
            flashSaleStarted {
              name
              discountPercentage
              remainingTime
            }
            cricketMatchOffer {
              matchName
              team1
              team2
              offerCode
            }
          }
        `,
        
        user_activity: `
          subscription UserActivity {
            userOnline {
              id
              name
              city
            }
            userOffline {
              id
              name
            }
          }
        `
      },
      
      test_mutations: {
        create_order: `
          mutation {
            createOrder(userId: "1", productIds: ["1", "2"], totalAmount: 219899) {
              id
              status
              trackingId
            }
          }
        `,
        
        start_flash_sale: `
          mutation {
            startFlashSale(
              name: "Diwali Dhamaka Sale"
              discountPercentage: 50
              durationMinutes: 60
              productIds: ["1", "2", "3"]
              festival: "Diwali"
            ) {
              id
              name
              remainingTime
            }
          }
        `,
        
        cricket_offer: `
          mutation {
            createCricketOffer(
              matchName: "IPL 2024 Final"
              team1: "Mumbai Indians"
              team2: "Chennai Super Kings"
              discountPercentage: 30
            ) {
              offerCode
              description
            }
          }
        `
      },
      
      websocket_connection: {
        url: `ws://localhost:${PORT}/subscriptions`,
        protocol: 'graphql-ws',
        connection_params: {
          'x-user-id': 'USER_ID',
          'x-user-role': 'customer'
        }
      }
    });
  });
  
  // Start server
  httpServer.listen(PORT, () => {
    console.log(`🚀 GraphQL Subscriptions Server ready at http://localhost:${PORT}${server.graphqlPath}`);
    console.log(`🔌 WebSocket subscriptions at ws://localhost:${PORT}${server.subscriptionsPath}`);
    console.log(`🏥 Health check at http://localhost:${PORT}/health`);
    console.log(`🎮 Demo guide at http://localhost:${PORT}/demo`);
    
    console.log(`\n🇮🇳 Indian E-commerce Features:`);
    console.log(`   - Festival flash sales (Diwali, Holi, etc.)`);
    console.log(`   - Cricket match offers (IPL, World Cup)`);
    console.log(`   - Real-time delivery tracking`);
    console.log(`   - UPI payment notifications`);
    console.log(`   - Multi-language support ready`);
    
    // Demo data generation
    startDemoDataGeneration();
  });
}

// Generate demo events for testing
function startDemoDataGeneration() {
  console.log('🎯 Starting demo data generation...');
  
  // Simulate periodic events
  setInterval(() => {
    // Random product price changes
    const products = Array.from(mockData.products.values());
    const randomProduct = products[Math.floor(Math.random() * products.length)];
    
    if (Math.random() < 0.3) { // 30% chance
      const priceChange = (Math.random() - 0.5) * 10000; // ±₹5000 change
      const newPrice = Math.max(1000, randomProduct.price + priceChange);
      
      randomProduct.price = newPrice;
      pubsub.publish(SUBSCRIPTION_EVENTS.PRODUCT_PRICE_CHANGED, {
        productPriceChanged: randomProduct
      });
      
      console.log(`💰 Demo: Price changed for ${randomProduct.name}: ₹${newPrice}`);
    }
    
  }, 30000); // Every 30 seconds
  
  // Simulate popular product alerts
  setInterval(() => {
    const products = Array.from(mockData.products.values());
    const randomProduct = products[Math.floor(Math.random() * products.length)];
    
    pubsub.publish(SUBSCRIPTION_EVENTS.POPULAR_PRODUCT_ALERT, {
      popularProductAlert: {
        productId: randomProduct.id,
        productName: randomProduct.name,
        viewCount: Math.floor(Math.random() * 5000) + 1000,
        orderCount: Math.floor(Math.random() * 200) + 50,
        trendingScore: Math.random() * 10,
        category: randomProduct.category,
        timestamp: getCurrentTimestamp()
      }
    });
    
  }, 45000); // Every 45 seconds
  
  // Simulate cricket offers during matches (demo)
  setInterval(() => {
    if (Math.random() < 0.1) { // 10% chance every minute
      const teams = [
        ['Mumbai Indians', 'Chennai Super Kings'],
        ['Royal Challengers Bangalore', 'Delhi Capitals'],
        ['India', 'Pakistan'],
        ['India', 'Australia']
      ];
      
      const [team1, team2] = teams[Math.floor(Math.random() * teams.length)];
      const discount = [15, 20, 25, 30][Math.floor(Math.random() * 4)];
      
      const offer = {
        id: generateId(),
        matchName: `${team1} vs ${team2}`,
        team1,
        team2,
        discountPercentage: discount,
        validTill: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
        offerCode: `CRICKET${discount}`,
        description: `${team1} vs ${team2} match special! ${discount}% off`
      };
      
      pubsub.publish(SUBSCRIPTION_EVENTS.CRICKET_MATCH_OFFER, {
        cricketMatchOffer: offer
      });
      
      console.log(`🏏 Demo: Cricket offer generated - ${team1} vs ${team2} (${discount}% off)`);
    }
  }, 60000); // Every minute
  
  console.log('✅ Demo data generation started');
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🔌 GraphQL Subscriptions Server shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🔌 GraphQL Subscriptions Server shutting down...');
  process.exit(0);
});

// Start the server
startSubscriptionServer();

module.exports = { typeDefs, resolvers, SUBSCRIPTION_EVENTS };