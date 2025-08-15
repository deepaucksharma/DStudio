// 05_dataloader_implementation.js
// DataLoader Implementation - N+1 queries का solution
// Batch loading और caching के लिए Facebook का popular library

const DataLoader = require('dataloader');
const { ApolloServer, gql } = require('apollo-server-express');
const express = require('express');

// Mock database functions - Production में actual DB calls होंगी
const mockDatabase = {
  // Users table
  users: new Map([
    ['1', { id: '1', name: 'Rahul Sharma', email: 'rahul@flipkart.com', role: 'customer' }],
    ['2', { id: '2', name: 'Priya Singh', email: 'priya@amazon.in', role: 'seller' }],
    ['3', { id: '3', name: 'Amit Kumar', email: 'amit@paytm.com', role: 'admin' }],
    ['4', { id: '4', name: 'Sneha Patel', email: 'sneha@zomato.com', role: 'customer' }]
  ]),
  
  // Orders table
  orders: new Map([
    ['1', { id: '1', userId: '1', productIds: ['1', '2'], total: 15000, status: 'delivered' }],
    ['2', { id: '2', userId: '2', productIds: ['1'], total: 8000, status: 'shipped' }],
    ['3', { id: '3', userId: '1', productIds: ['3', '4'], total: 3500, status: 'processing' }],
    ['4', { id: '4', userId: '4', productIds: ['2', '3'], total: 12000, status: 'delivered' }]
  ]),
  
  // Products table
  products: new Map([
    ['1', { id: '1', name: 'iPhone 15 Pro', price: 134900, category: 'phones' }],
    ['2', { id: '2', name: 'MacBook Air M2', price: 114900, category: 'laptops' }],
    ['3', { id: '3', name: 'AirPods Pro', price: 24900, category: 'accessories' }],
    ['4', { id: '4', name: 'iPad Air', price: 59900, category: 'tablets' }]
  ]),
  
  // Reviews table
  reviews: [
    { id: '1', userId: '1', productId: '1', rating: 5, comment: 'बहुत बढ़िया phone है!' },
    { id: '2', userId: '2', productId: '1', rating: 4, comment: 'Good performance but expensive' },
    { id: '3', userId: '1', productId: '2', rating: 5, comment: 'Best laptop for development' },
    { id: '4', userId: '4', productId: '3', rating: 4, comment: 'Sound quality अच्छी है' }
  ]
};

// DataLoader factory functions
function createDataLoaders() {
  console.log('🏭 Creating DataLoaders...');
  
  // User DataLoader - users को batch में load करता है
  const userLoader = new DataLoader(
    async (userIds) => {
      console.log(`👥 Batch loading ${userIds.length} users:`, userIds);
      
      // Simulate database query delay
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Database query simulation - real में एक ही query होगी
      const users = userIds.map(id => mockDatabase.users.get(id) || null);
      
      console.log(`✅ Loaded ${users.filter(Boolean).length} users from database`);
      return users;
    },
    {
      // Caching options
      cache: true,
      cacheKeyFn: (key) => `user:${key}`,
      maxBatchSize: 100, // Maximum batch size
      batchScheduleFn: (callback) => setTimeout(callback, 10) // 10ms delay
    }
  );

  // Product DataLoader - products को batch में load करता है
  const productLoader = new DataLoader(
    async (productIds) => {
      console.log(`🛍️ Batch loading ${productIds.length} products:`, productIds);
      
      await new Promise(resolve => setTimeout(resolve, 30));
      
      const products = productIds.map(id => mockDatabase.products.get(id) || null);
      
      console.log(`✅ Loaded ${products.filter(Boolean).length} products from database`);
      return products;
    },
    {
      cache: true,
      cacheKeyFn: (key) => `product:${key}`,
      maxBatchSize: 50
    }
  );

  // Orders by User DataLoader - एक user के सारे orders
  const ordersByUserLoader = new DataLoader(
    async (userIds) => {
      console.log(`📦 Batch loading orders for ${userIds.length} users:`, userIds);
      
      await new Promise(resolve => setTimeout(resolve, 40));
      
      // Group orders by userId
      const ordersByUser = userIds.map(userId => {
        const userOrders = Array.from(mockDatabase.orders.values())
          .filter(order => order.userId === userId);
        return userOrders;
      });
      
      console.log(`✅ Loaded orders for ${userIds.length} users`);
      return ordersByUser;
    },
    {
      cache: true,
      cacheKeyFn: (key) => `orders_by_user:${key}`
    }
  );

  // Reviews by Product DataLoader - एक product के सारे reviews
  const reviewsByProductLoader = new DataLoader(
    async (productIds) => {
      console.log(`⭐ Batch loading reviews for ${productIds.length} products:`, productIds);
      
      await new Promise(resolve => setTimeout(resolve, 25));
      
      const reviewsByProduct = productIds.map(productId => {
        return mockDatabase.reviews.filter(review => review.productId === productId);
      });
      
      console.log(`✅ Loaded reviews for ${productIds.length} products`);
      return reviewsByProduct;
    },
    {
      cache: true,
      cacheKeyFn: (key) => `reviews_by_product:${key}`
    }
  );

  // User Stats DataLoader - complex calculations को cache करता है
  const userStatsLoader = new DataLoader(
    async (userIds) => {
      console.log(`📊 Calculating stats for ${userIds.length} users:`, userIds);
      
      await new Promise(resolve => setTimeout(resolve, 60));
      
      const stats = userIds.map(userId => {
        const userOrders = Array.from(mockDatabase.orders.values())
          .filter(order => order.userId === userId);
        
        const totalSpent = userOrders.reduce((sum, order) => sum + order.total, 0);
        const totalOrders = userOrders.length;
        
        return {
          userId,
          totalOrders,
          totalSpent,
          averageOrderValue: totalOrders > 0 ? totalSpent / totalOrders : 0,
          lastOrderDate: userOrders.length > 0 ? new Date().toISOString() : null
        };
      });
      
      console.log(`✅ Calculated stats for ${userIds.length} users`);
      return stats;
    },
    {
      cache: true,
      cacheKeyFn: (key) => `user_stats:${key}`,
      cacheMap: new Map(), // Custom cache implementation
      maxBatchSize: 10
    }
  );

  return {
    userLoader,
    productLoader,
    ordersByUserLoader,
    reviewsByProductLoader,
    userStatsLoader
  };
}

// GraphQL Schema
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    role: String!
    # DataLoader से load होने वाले fields
    orders: [Order!]!
    stats: UserStats!
    reviews: [Review!]!
  }

  type Product {
    id: ID!
    name: String!
    price: Float!
    category: String!
    # DataLoader से load होने वाले fields
    reviews: [Review!]!
    averageRating: Float
    reviewsCount: Int!
  }

  type Order {
    id: ID!
    userId: ID!
    total: Float!
    status: String!
    # DataLoader resolved fields
    user: User!
    products: [Product!]!
  }

  type Review {
    id: ID!
    userId: ID!
    productId: ID!
    rating: Int!
    comment: String
    # DataLoader resolved fields
    user: User!
    product: Product!
  }

  type UserStats {
    userId: ID!
    totalOrders: Int!
    totalSpent: Float!
    averageOrderValue: Float!
    lastOrderDate: String
  }

  type Query {
    # Simple queries
    user(id: ID!): User
    product(id: ID!): Product
    order(id: ID!): Order
    
    # List queries - यहाँ N+1 problem होती है without DataLoader
    users: [User!]!
    products: [Product!]!
    orders: [Order!]!
    reviews: [Review!]!
    
    # Performance test queries
    usersWithStats: [User!]!
    productsWithReviews: [Product!]!
  }

  type Mutation {
    # Cache invalidation test
    updateUser(id: ID!, name: String, email: String): User
    clearCache: Boolean!
  }
`;

const resolvers = {
  Query: {
    // Single entity queries - DataLoader automatically batches
    user: (parent, { id }, { dataloaders }) => {
      console.log(`🎯 Single user query: ${id}`);
      return dataloaders.userLoader.load(id);
    },

    product: (parent, { id }, { dataloaders }) => {
      console.log(`🎯 Single product query: ${id}`);
      return dataloaders.productLoader.load(id);
    },

    order: (parent, { id }) => {
      console.log(`🎯 Single order query: ${id}`);
      return mockDatabase.orders.get(id);
    },

    // List queries - यहाँ DataLoader की power दिखती है
    users: (parent, args, { dataloaders }) => {
      console.log('👥 All users query - triggering batch load');
      const userIds = Array.from(mockDatabase.users.keys());
      
      // DataLoader automatically batches these requests
      return Promise.all(userIds.map(id => dataloaders.userLoader.load(id)));
    },

    products: (parent, args, { dataloaders }) => {
      console.log('🛍️ All products query - triggering batch load');
      const productIds = Array.from(mockDatabase.products.keys());
      
      return Promise.all(productIds.map(id => dataloaders.productLoader.load(id)));
    },

    orders: () => {
      console.log('📦 All orders query');
      return Array.from(mockDatabase.orders.values());
    },

    reviews: () => {
      console.log('⭐ All reviews query');
      return mockDatabase.reviews;
    },

    // Performance test queries
    usersWithStats: (parent, args, { dataloaders }) => {
      console.log('📊 Users with stats query - complex DataLoader usage');
      const userIds = Array.from(mockDatabase.users.keys());
      
      return Promise.all(userIds.map(id => dataloaders.userLoader.load(id)));
    },

    productsWithReviews: (parent, args, { dataloaders }) => {
      console.log('⭐ Products with reviews query - relationship loading');
      const productIds = Array.from(mockDatabase.products.keys());
      
      return Promise.all(productIds.map(id => dataloaders.productLoader.load(id)));
    }
  },

  Mutation: {
    updateUser: async (parent, { id, name, email }, { dataloaders }) => {
      console.log(`✏️ Updating user ${id}`);
      
      // Update in mock database
      const user = mockDatabase.users.get(id);
      if (!user) {
        throw new Error(`User ${id} not found`);
      }
      
      const updatedUser = { ...user, ...(name && { name }), ...(email && { email }) };
      mockDatabase.users.set(id, updatedUser);
      
      // Clear DataLoader cache for this user
      dataloaders.userLoader.clear(id);
      console.log(`🧹 Cleared cache for user ${id}`);
      
      return updatedUser;
    },

    clearCache: (parent, args, { dataloaders }) => {
      console.log('🧹 Clearing all DataLoader caches');
      
      // Clear all DataLoader caches
      dataloaders.userLoader.clearAll();
      dataloaders.productLoader.clearAll();
      dataloaders.ordersByUserLoader.clearAll();
      dataloaders.reviewsByProductLoader.clearAll();
      dataloaders.userStatsLoader.clearAll();
      
      console.log('✅ All caches cleared');
      return true;
    }
  },

  // Field resolvers - यहाँ DataLoader का असली फायदा है
  User: {
    orders: (user, args, { dataloaders }) => {
      console.log(`📦 Loading orders for user ${user.id}`);
      return dataloaders.ordersByUserLoader.load(user.id);
    },

    stats: (user, args, { dataloaders }) => {
      console.log(`📊 Loading stats for user ${user.id}`);
      return dataloaders.userStatsLoader.load(user.id);
    },

    reviews: (user) => {
      console.log(`⭐ Loading reviews by user ${user.id}`);
      return mockDatabase.reviews.filter(review => review.userId === user.id);
    }
  },

  Product: {
    reviews: (product, args, { dataloaders }) => {
      console.log(`⭐ Loading reviews for product ${product.id}`);
      return dataloaders.reviewsByProductLoader.load(product.id);
    },

    averageRating: async (product, args, { dataloaders }) => {
      console.log(`📊 Calculating average rating for product ${product.id}`);
      const reviews = await dataloaders.reviewsByProductLoader.load(product.id);
      
      if (reviews.length === 0) return 0;
      
      const sum = reviews.reduce((total, review) => total + review.rating, 0);
      return sum / reviews.length;
    },

    reviewsCount: async (product, args, { dataloaders }) => {
      const reviews = await dataloaders.reviewsByProductLoader.load(product.id);
      return reviews.length;
    }
  },

  Order: {
    user: (order, args, { dataloaders }) => {
      console.log(`👤 Loading user for order ${order.id}`);
      return dataloaders.userLoader.load(order.userId);
    },

    products: (order, args, { dataloaders }) => {
      console.log(`🛍️ Loading products for order ${order.id}`);
      // Batch load all products for this order
      return Promise.all(
        order.productIds.map(productId => dataloaders.productLoader.load(productId))
      );
    }
  },

  Review: {
    user: (review, args, { dataloaders }) => {
      console.log(`👤 Loading user for review ${review.id}`);
      return dataloaders.userLoader.load(review.userId);
    },

    product: (review, args, { dataloaders }) => {
      console.log(`🛍️ Loading product for review ${review.id}`);
      return dataloaders.productLoader.load(review.productId);
    }
  }
};

async function startDataLoaderServer() {
  try {
    const app = express();
    
    // Request logging with timing
    app.use((req, res, next) => {
      req.startTime = Date.now();
      console.log(`📞 DataLoader Server - ${req.method} ${req.path} - Started`);
      next();
    });

    const server = new ApolloServer({
      typeDefs,
      resolvers,
      
      // Context function - यहाँ हर request के लिए नए DataLoaders create करते हैं
      context: ({ req }) => {
        // Request के लिए fresh DataLoaders
        const dataloaders = createDataLoaders();
        
        console.log(`🏭 Created fresh DataLoaders for request`);
        
        return {
          dataloaders,
          requestId: `dl_${Date.now()}`,
          startTime: req.startTime
        };
      },
      
      formatError: (error) => {
        console.error('❌ DataLoader Error:', error.message);
        return error;
      },
      
      // Response timing
      formatResponse: (response, { context }) => {
        if (context.startTime) {
          const duration = Date.now() - context.startTime;
          console.log(`⏱️ Request completed in ${duration}ms`);
          
          response.extensions = {
            ...response.extensions,
            responseTime: `${duration}ms`,
            requestId: context.requestId
          };
        }
        
        return response;
      },
      
      plugins: [
        // Performance monitoring plugin
        {
          requestDidStart() {
            return {
              willSendResponse(requestContext) {
                const { context } = requestContext;
                
                // Log DataLoader statistics
                if (context.dataloaders) {
                  const stats = {
                    userLoaderCacheSize: context.dataloaders.userLoader._promiseCache.size,
                    productLoaderCacheSize: context.dataloaders.productLoader._promiseCache.size,
                    ordersByUserCacheSize: context.dataloaders.ordersByUserLoader._promiseCache.size
                  };
                  
                  console.log('📊 DataLoader Cache Stats:', stats);
                }
              }
            };
          }
        }
      ],
      
      introspection: true,
      playground: process.env.NODE_ENV !== 'production'
    });

    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4020;
    
    // Health check
    app.get('/health', (req, res) => {
      res.json({
        service: 'dataloader-demo',
        status: 'healthy',
        features: ['DataLoader batching', 'Request-scoped caching', 'N+1 prevention'],
        timestamp: new Date().toISOString()
      });
    });

    // DataLoader stats endpoint
    app.get('/dataloader-stats', (req, res) => {
      res.json({
        description: 'DataLoader Implementation Stats',
        benefits: [
          'Batch loading reduces database queries',
          'Request-scoped caching prevents duplicate loads',
          'Automatic N+1 query problem resolution',
          'Configurable cache strategies'
        ],
        implementation: {
          userLoader: 'Batches user queries with 100ms window',
          productLoader: 'Batches product queries with 50ms cache',
          ordersByUserLoader: 'Groups orders by user ID',
          reviewsByProductLoader: 'Groups reviews by product ID',
          userStatsLoader: 'Caches complex calculations'
        }
      });
    });

    app.listen(PORT, () => {
      console.log(`⚡ DataLoader Server ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
      console.log(`📊 DataLoader stats at http://localhost:${PORT}/dataloader-stats`);
      
      // Performance testing suggestions
      console.log(`\n🧪 Test queries to demonstrate DataLoader benefits:`);
      console.log(`1. Query all users with orders: { users { id name orders { id total } } }`);
      console.log(`2. Query products with reviews: { products { id name reviews { rating comment } } }`);
      console.log(`3. Query orders with user and products: { orders { id user { name } products { name } } }`);
      console.log(`\nWithout DataLoader: N+1 queries`);
      console.log(`With DataLoader: Batched queries + caching 🚀\n`);
    });

  } catch (error) {
    console.error('❌ DataLoader Server startup error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('⚡ DataLoader Server shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('⚡ DataLoader Server shutting down...');
  process.exit(0);
});

// Start the server
startDataLoaderServer();

module.exports = { createDataLoaders, typeDefs, resolvers };