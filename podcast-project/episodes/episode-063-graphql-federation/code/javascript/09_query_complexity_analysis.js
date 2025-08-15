// 09_query_complexity_analysis.js
// GraphQL Query Complexity Analysis और Cost Analysis
// भारी queries से server को DoS attacks से बचाने के लिए

const { ApolloServer, gql, AuthenticationError, ForbiddenError } = require('apollo-server-express');
const { createComplexityLimitRule } = require('graphql-query-complexity');
const depthLimit = require('graphql-depth-limit');
const costAnalysis = require('graphql-cost-analysis');
const express = require('express');

// Query Complexity Configuration
const COMPLEXITY_CONFIG = {
  // Maximum allowed complexity per query
  maximumComplexity: 1000,
  
  // Different limits for different user roles
  guestMaxComplexity: 300,
  customerMaxComplexity: 800,
  sellerMaxComplexity: 1500,
  adminMaxComplexity: 5000,
  
  // Maximum query depth
  maxDepth: 10,
  
  // Field cost mapping - कितनी cost है हर field की
  fieldCosts: {
    // Simple fields - कम cost
    id: 0,
    name: 1,
    email: 1,
    price: 1,
    status: 1,
    
    // Database queries - medium cost
    products: 5,
    orders: 8,
    users: 6,
    reviews: 3,
    
    // Expensive operations - high cost
    search: 50,
    analytics: 100,
    recommendations: 80,
    reports: 150,
    
    // Computed fields - varying costs
    averageRating: 10,
    totalSales: 15,
    popularProducts: 25,
    
    // List fields with multipliers
    productList: 3, // per item
    orderList: 5,   // per item
    userList: 4,    // per item
    
    // Complex relationships
    userOrders: 12,
    productReviews: 8,
    orderItems: 6
  }
};

// Mock data for testing
const mockData = {
  products: Array.from({length: 1000}, (_, i) => ({
    id: String(i + 1),
    name: `Product ${i + 1}`,
    price: 1000 + (i * 100),
    category: ['Electronics', 'Fashion', 'Books', 'Home'][i % 4],
    sellerId: String((i % 50) + 1)
  })),
  
  users: Array.from({length: 100}, (_, i) => ({
    id: String(i + 1),
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    role: ['guest', 'customer', 'seller', 'admin'][i % 4],
    city: ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'][i % 4]
  })),
  
  orders: Array.from({length: 500}, (_, i) => ({
    id: String(i + 1),
    userId: String((i % 100) + 1),
    productIds: [String((i % 1000) + 1), String(((i + 1) % 1000) + 1)],
    total: 2000 + (i * 50),
    status: ['pending', 'shipped', 'delivered', 'cancelled'][i % 4],
    createdAt: new Date(Date.now() - (i * 86400000)) // i days ago
  })),
  
  reviews: Array.from({length: 2000}, (_, i) => ({
    id: String(i + 1),
    productId: String((i % 1000) + 1),
    userId: String((i % 100) + 1),
    rating: Math.floor(Math.random() * 5) + 1,
    comment: `Review comment ${i + 1}`,
    helpful: Math.floor(Math.random() * 20)
  }))
};

// GraphQL Schema with complexity annotations
const typeDefs = gql`
  type Product {
    id: ID!
    name: String!
    price: Float!
    category: String!
    sellerId: ID!
    
    # Medium complexity fields
    reviews: [Review!]!
    averageRating: Float
    totalReviews: Int!
    
    # High complexity computed fields
    salesStats: ProductSalesStats
    recommendations: [Product!]!
  }
  
  type User {
    id: ID!
    name: String!
    email: String!
    role: String!
    city: String!
    
    # Medium complexity relationships
    orders: [Order!]!
    reviews: [Review!]!
    
    # High complexity analytics
    statistics: UserStats
    recommendations: [Product!]!
  }
  
  type Order {
    id: ID!
    userId: ID!
    productIds: [ID!]!
    total: Float!
    status: String!
    createdAt: String!
    
    # Relationships with costs
    user: User!
    products: [Product!]!
    invoice: Invoice
  }
  
  type Review {
    id: ID!
    productId: ID!
    userId: ID!
    rating: Int!
    comment: String
    helpful: Int!
    
    # Related entities
    product: Product!
    user: User!
  }
  
  # Expensive computed types
  type ProductSalesStats {
    totalSold: Int!
    revenue: Float!
    averageOrderValue: Float!
    conversionRate: Float!
  }
  
  type UserStats {
    totalOrders: Int!
    totalSpent: Float!
    averageOrderValue: Float!
    favoriteCategory: String!
    loyaltyScore: Float!
  }
  
  type Invoice {
    id: ID!
    orderId: ID!
    amount: Float!
    taxAmount: Float!
    pdfUrl: String!
  }
  
  type SearchResult {
    products: [Product!]!
    users: [User!]!
    totalCount: Int!
    facets: SearchFacets!
  }
  
  type SearchFacets {
    categories: [CategoryFacet!]!
    priceRanges: [PriceRangeFacet!]!
    brands: [BrandFacet!]!
  }
  
  type CategoryFacet {
    name: String!
    count: Int!
  }
  
  type PriceRangeFacet {
    range: String!
    count: Int!
  }
  
  type BrandFacet {
    name: String!
    count: Int!
  }

  type Query {
    # Simple queries - Low complexity
    product(id: ID!): Product
    user(id: ID!): User
    order(id: ID!): Order
    
    # List queries - Medium complexity (depends on limit)
    products(limit: Int = 10, offset: Int = 0): [Product!]!
    users(limit: Int = 10): [User!]!
    orders(limit: Int = 10): [Order!]!
    
    # Search queries - High complexity
    search(
      query: String!
      limit: Int = 20
      includeFacets: Boolean = false
    ): SearchResult!
    
    # Analytics queries - Very high complexity
    analytics(dateFrom: String, dateTo: String): AnalyticsReport!
    salesReport(period: String!): SalesReport!
    userBehaviorAnalysis(userId: ID!): UserBehaviorReport!
    
    # Recommendation queries - High complexity
    productRecommendations(
      userId: ID
      productId: ID
      limit: Int = 10
    ): [Product!]!
    
    # Complex aggregations
    topProducts(
      category: String
      period: String = "month"
      limit: Int = 10
    ): [ProductRanking!]!
    
    topCustomers(limit: Int = 10): [CustomerRanking!]!
  }
  
  type AnalyticsReport {
    totalRevenue: Float!
    totalOrders: Int!
    averageOrderValue: Float!
    topProducts: [ProductRanking!]!
    topCategories: [CategoryStats!]!
    customerMetrics: CustomerMetrics!
  }
  
  type SalesReport {
    period: String!
    totalSales: Float!
    orderCount: Int!
    averageOrderValue: Float!
    topSellingProducts: [Product!]!
    salesTrend: [DailySales!]!
  }
  
  type UserBehaviorReport {
    userId: ID!
    browsingPattern: BrowsingPattern!
    purchaseHistory: [Order!]!
    preferences: UserPreferences!
    engagementScore: Float!
  }
  
  type ProductRanking {
    product: Product!
    rank: Int!
    score: Float!
    salesCount: Int!
    revenue: Float!
  }
  
  type CustomerRanking {
    user: User!
    rank: Int!
    totalSpent: Float!
    orderCount: Int!
    loyaltyScore: Float!
  }
  
  type CategoryStats {
    name: String!
    revenue: Float!
    orderCount: Int!
    productCount: Int!
  }
  
  type CustomerMetrics {
    newCustomers: Int!
    returningCustomers: Int!
    churnRate: Float!
    lifetimeValue: Float!
  }
  
  type DailySales {
    date: String!
    sales: Float!
    orderCount: Int!
  }
  
  type BrowsingPattern {
    sessionCount: Int!
    averageSessionDuration: Float!
    pagesViewed: Int!
    bounceRate: Float!
  }
  
  type UserPreferences {
    favoriteCategories: [String!]!
    priceRange: String!
    brandPreferences: [String!]!
  }
`;

// Complexity analysis function
function createComplexityAnalyzer() {
  return {
    // Field complexity calculator
    fieldComplexity: (args, childComplexity) => {
      const fieldName = args.field.name;
      const baseCost = COMPLEXITY_CONFIG.fieldCosts[fieldName] || 1;
      
      // Handle list fields with multipliers
      if (args.args.limit) {
        const limit = args.args.limit;
        return baseCost * Math.min(limit, 100) + childComplexity;
      }
      
      // Special handling for expensive operations
      if (fieldName === 'search' && args.args.includeFacets) {
        return baseCost * 2 + childComplexity; // Facets double the cost
      }
      
      if (fieldName === 'recommendations') {
        const limit = args.args.limit || 10;
        return baseCost * Math.min(limit, 50) + childComplexity;
      }
      
      return baseCost + childComplexity;
    },
    
    // Object type complexity
    objectComplexity: (args, childComplexity) => {
      return childComplexity;
    },
    
    // Scalar complexity
    scalarComplexity: 1,
    
    // Introspection complexity
    introspectionComplexity: 1000, // High cost to discourage introspection abuse
    
    // Create rule with user-based limits
    createRule: (context) => {
      const user = context.user;
      let maxComplexity = COMPLEXITY_CONFIG.guestMaxComplexity;
      
      if (user) {
        switch (user.role) {
          case 'admin':
            maxComplexity = COMPLEXITY_CONFIG.adminMaxComplexity;
            break;
          case 'seller':
            maxComplexity = COMPLEXITY_CONFIG.sellerMaxComplexity;
            break;
          case 'customer':
            maxComplexity = COMPLEXITY_CONFIG.customerMaxComplexity;
            break;
        }
      }
      
      console.log(`🧮 Complexity limit for ${user?.role || 'guest'}: ${maxComplexity}`);
      
      return createComplexityLimitRule(maxComplexity, {
        fieldComplexity: this.fieldComplexity,
        objectComplexity: this.objectComplexity,
        scalarComplexity: this.scalarComplexity,
        introspectionComplexity: this.introspectionComplexity,
        
        onComplete: (complexity) => {
          console.log(`📊 Query complexity: ${complexity}/${maxComplexity}`);
          
          // Log expensive queries
          if (complexity > maxComplexity * 0.8) {
            console.warn(`⚠️ High complexity query: ${complexity}/${maxComplexity}`);
          }
        }
      });
    }
  };
}

// Resolvers with simulated expensive operations
const resolvers = {
  Query: {
    // Simple resolvers
    product: (parent, { id }) => {
      console.log(`🎯 Product query: ${id}`);
      return mockData.products.find(p => p.id === id);
    },
    
    user: (parent, { id }) => {
      console.log(`👤 User query: ${id}`);
      return mockData.users.find(u => u.id === id);
    },
    
    order: (parent, { id }) => {
      console.log(`📦 Order query: ${id}`);
      return mockData.orders.find(o => o.id === id);
    },
    
    // List resolvers with pagination
    products: (parent, { limit, offset }) => {
      console.log(`🛍️ Products list: limit=${limit}, offset=${offset}`);
      return mockData.products.slice(offset, offset + limit);
    },
    
    users: (parent, { limit }) => {
      console.log(`👥 Users list: limit=${limit}`);
      return mockData.users.slice(0, limit);
    },
    
    orders: (parent, { limit }) => {
      console.log(`📦 Orders list: limit=${limit}`);
      return mockData.orders.slice(0, limit);
    },
    
    // Expensive search resolver
    search: async (parent, { query, limit, includeFacets }, context) => {
      console.log(`🔍 Search query: "${query}", limit=${limit}, facets=${includeFacets}`);
      
      // Simulate expensive search operation
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const searchTerm = query.toLowerCase();
      
      const matchingProducts = mockData.products
        .filter(p => p.name.toLowerCase().includes(searchTerm))
        .slice(0, limit);
      
      const matchingUsers = mockData.users
        .filter(u => u.name.toLowerCase().includes(searchTerm))
        .slice(0, Math.floor(limit / 2));
      
      let facets = {
        categories: [],
        priceRanges: [],
        brands: []
      };
      
      if (includeFacets) {
        console.log('📊 Computing search facets (expensive operation)');
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Simulate facet computation
        facets = {
          categories: [
            { name: 'Electronics', count: Math.floor(Math.random() * 100) },
            { name: 'Fashion', count: Math.floor(Math.random() * 80) },
            { name: 'Books', count: Math.floor(Math.random() * 50) }
          ],
          priceRanges: [
            { range: '0-1000', count: Math.floor(Math.random() * 200) },
            { range: '1000-5000', count: Math.floor(Math.random() * 300) },
            { range: '5000+', count: Math.floor(Math.random() * 100) }
          ],
          brands: [
            { name: 'Apple', count: Math.floor(Math.random() * 50) },
            { name: 'Samsung', count: Math.floor(Math.random() * 80) },
            { name: 'OnePlus', count: Math.floor(Math.random() * 30) }
          ]
        };
      }
      
      return {
        products: matchingProducts,
        users: matchingUsers,
        totalCount: matchingProducts.length + matchingUsers.length,
        facets
      };
    },
    
    // Very expensive analytics resolver
    analytics: async (parent, { dateFrom, dateTo }, context) => {
      console.log(`📊 Analytics query: ${dateFrom} to ${dateTo}`);
      
      // Check if user has permission for analytics
      if (!context.user || !['admin', 'seller'].includes(context.user.role)) {
        throw new ForbiddenError('Analytics access requires admin or seller role');
      }
      
      // Simulate very expensive analytics computation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        totalRevenue: mockData.orders.reduce((sum, order) => sum + order.total, 0),
        totalOrders: mockData.orders.length,
        averageOrderValue: mockData.orders.reduce((sum, order) => sum + order.total, 0) / mockData.orders.length,
        topProducts: mockData.products.slice(0, 5).map((product, index) => ({
          product,
          rank: index + 1,
          score: 100 - (index * 10),
          salesCount: Math.floor(Math.random() * 1000),
          revenue: Math.floor(Math.random() * 100000)
        })),
        topCategories: [
          { name: 'Electronics', revenue: 500000, orderCount: 200, productCount: 150 },
          { name: 'Fashion', revenue: 300000, orderCount: 150, productCount: 100 }
        ],
        customerMetrics: {
          newCustomers: 150,
          returningCustomers: 300,
          churnRate: 0.15,
          lifetimeValue: 5000
        }
      };
    },
    
    // Expensive recommendation resolver
    productRecommendations: async (parent, { userId, productId, limit }) => {
      console.log(`🤖 Product recommendations: userId=${userId}, productId=${productId}, limit=${limit}`);
      
      // Simulate ML recommendation engine
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return mockData.products.slice(0, limit);
    },
    
    // Complex aggregation resolver
    topProducts: async (parent, { category, period, limit }) => {
      console.log(`🏆 Top products: category=${category}, period=${period}, limit=${limit}`);
      
      // Simulate complex database aggregation
      await new Promise(resolve => setTimeout(resolve, 300));
      
      let products = mockData.products;
      
      if (category) {
        products = products.filter(p => p.category === category);
      }
      
      return products.slice(0, limit).map((product, index) => ({
        product,
        rank: index + 1,
        score: 100 - (index * 5),
        salesCount: Math.floor(Math.random() * 500),
        revenue: Math.floor(Math.random() * 50000)
      }));
    }
  },
  
  // Field resolvers with complexity
  Product: {
    // Medium complexity - product reviews
    reviews: async (product) => {
      console.log(`⭐ Loading reviews for product ${product.id}`);
      await new Promise(resolve => setTimeout(resolve, 50));
      
      return mockData.reviews.filter(r => r.productId === product.id);
    },
    
    averageRating: async (product) => {
      console.log(`📊 Computing average rating for product ${product.id}`);
      await new Promise(resolve => setTimeout(resolve, 30));
      
      const productReviews = mockData.reviews.filter(r => r.productId === product.id);
      if (productReviews.length === 0) return 0;
      
      const sum = productReviews.reduce((acc, review) => acc + review.rating, 0);
      return sum / productReviews.length;
    },
    
    totalReviews: async (product) => {
      const productReviews = mockData.reviews.filter(r => r.productId === product.id);
      return productReviews.length;
    },
    
    // High complexity - sales statistics
    salesStats: async (product, args, context) => {
      console.log(`💰 Computing sales stats for product ${product.id}`);
      
      // Expensive computation
      await new Promise(resolve => setTimeout(resolve, 200));
      
      return {
        totalSold: Math.floor(Math.random() * 1000),
        revenue: Math.floor(Math.random() * 100000),
        averageOrderValue: Math.floor(Math.random() * 5000),
        conversionRate: Math.random() * 0.1
      };
    },
    
    // High complexity - product recommendations
    recommendations: async (product) => {
      console.log(`🎯 Computing recommendations for product ${product.id}`);
      await new Promise(resolve => setTimeout(resolve, 400));
      
      return mockData.products
        .filter(p => p.id !== product.id && p.category === product.category)
        .slice(0, 5);
    }
  },
  
  User: {
    // User's orders - medium complexity
    orders: async (user) => {
      console.log(`📦 Loading orders for user ${user.id}`);
      await new Promise(resolve => setTimeout(resolve, 80));
      
      return mockData.orders.filter(o => o.userId === user.id);
    },
    
    // User's reviews - low complexity
    reviews: async (user) => {
      console.log(`⭐ Loading reviews by user ${user.id}`);
      await new Promise(resolve => setTimeout(resolve, 40));
      
      return mockData.reviews.filter(r => r.userId === user.id);
    },
    
    // High complexity - user statistics
    statistics: async (user) => {
      console.log(`📊 Computing statistics for user ${user.id}`);
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const userOrders = mockData.orders.filter(o => o.userId === user.id);
      const totalSpent = userOrders.reduce((sum, order) => sum + order.total, 0);
      
      return {
        totalOrders: userOrders.length,
        totalSpent,
        averageOrderValue: userOrders.length > 0 ? totalSpent / userOrders.length : 0,
        favoriteCategory: 'Electronics', // Simplified
        loyaltyScore: Math.random() * 10
      };
    },
    
    // High complexity - user recommendations
    recommendations: async (user) => {
      console.log(`🎯 Computing recommendations for user ${user.id}`);
      await new Promise(resolve => setTimeout(resolve, 350));
      
      return mockData.products.slice(0, 10);
    }
  },
  
  Order: {
    user: async (order) => {
      return mockData.users.find(u => u.id === order.userId);
    },
    
    products: async (order) => {
      console.log(`🛍️ Loading products for order ${order.id}`);
      await new Promise(resolve => setTimeout(resolve, 60));
      
      return order.productIds
        .map(id => mockData.products.find(p => p.id === id))
        .filter(Boolean);
    },
    
    // Expensive invoice generation
    invoice: async (order) => {
      console.log(`📄 Generating invoice for order ${order.id}`);
      await new Promise(resolve => setTimeout(resolve, 150));
      
      return {
        id: `inv_${order.id}`,
        orderId: order.id,
        amount: order.total,
        taxAmount: order.total * 0.18, // 18% GST
        pdfUrl: `https://invoices.example.com/${order.id}.pdf`
      };
    }
  },
  
  Review: {
    product: async (review) => {
      return mockData.products.find(p => p.id === review.productId);
    },
    
    user: async (review) => {
      return mockData.users.find(u => u.id === review.userId);
    }
  }
};

// Create complexity analyzer
const complexityAnalyzer = createComplexityAnalyzer();

async function startComplexityAnalysisServer() {
  try {
    const app = express();
    
    // Request logging with timing
    app.use((req, res, next) => {
      req.startTime = Date.now();
      console.log(`📞 Request: ${req.method} ${req.path}`);
      next();
    });

    const server = new ApolloServer({
      typeDefs,
      resolvers,
      
      // Validation rules for complexity and depth
      validationRules: [
        depthLimit(COMPLEXITY_CONFIG.maxDepth),
        // Complexity rule created per request with user context
      ],
      
      context: ({ req }) => {
        // Mock user authentication - production में proper auth होगी
        const authHeader = req.headers.authorization || '';
        const userRole = req.headers['x-user-role'] || 'guest';
        const userId = req.headers['x-user-id'];
        
        let user = null;
        if (userId) {
          user = mockData.users.find(u => u.id === userId) || { 
            id: userId, 
            role: userRole 
          };
        }
        
        return {
          user,
          requestId: `req_${Date.now()}`,
          startTime: req.startTime
        };
      },
      
      // Custom validation rules including complexity
      validationRules: ({ context }) => [
        depthLimit(COMPLEXITY_CONFIG.maxDepth),
        complexityAnalyzer.createRule(context)
      ],
      
      formatError: (error) => {
        console.error(`❌ GraphQL Error:`, error.message);
        
        // Handle complexity errors specially
        if (error.message.includes('exceeds maximum operation complexity')) {
          console.warn(`🚫 Query complexity exceeded for ${error.extensions?.exception?.context?.user?.role || 'guest'}`);
        }
        
        return {
          message: error.message,
          locations: error.locations,
          path: error.path,
          extensions: {
            ...error.extensions,
            timestamp: new Date().toISOString()
          }
        };
      },
      
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
        {
          requestDidStart() {
            return {
              didResolveOperation(requestContext) {
                const { document, context } = requestContext;
                console.log(`🎯 Operation: ${requestContext.request.operationName || 'Anonymous'}`);
                console.log(`👤 User: ${context.user?.role || 'guest'}`);
              },
              
              didEncounterErrors(requestContext) {
                const complexityErrors = requestContext.errors.filter(error => 
                  error.message.includes('complexity') || error.message.includes('depth')
                );
                
                if (complexityErrors.length > 0) {
                  console.error(`💥 Complexity/Depth errors:`, complexityErrors.map(e => e.message));
                }
              }
            };
          }
        }
      ],
      
      introspection: process.env.NODE_ENV !== 'production',
      playground: process.env.NODE_ENV !== 'production'
    });

    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4024;
    
    // Health check
    app.get('/health', (req, res) => {
      res.json({
        service: 'graphql-complexity-analysis',
        status: 'healthy',
        complexity_limits: {
          guest: COMPLEXITY_CONFIG.guestMaxComplexity,
          customer: COMPLEXITY_CONFIG.customerMaxComplexity,
          seller: COMPLEXITY_CONFIG.sellerMaxComplexity,
          admin: COMPLEXITY_CONFIG.adminMaxComplexity
        },
        max_depth: COMPLEXITY_CONFIG.maxDepth,
        field_costs_sample: {
          simple_fields: 'id, name (0-1 cost)',
          list_fields: 'products, orders (5-8 cost)',
          expensive_operations: 'search, analytics (50-150 cost)'
        }
      });
    });

    // Complexity examples endpoint
    app.get('/complexity-examples', (req, res) => {
      res.json({
        examples: {
          low_complexity: {
            query: `{
              products(limit: 5) {
                id
                name
                price
              }
            }`,
            estimated_complexity: 30,
            description: "Simple product list - under guest limit"
          },
          
          medium_complexity: {
            query: `{
              products(limit: 10) {
                id
                name
                price
                reviews {
                  rating
                  comment
                }
                averageRating
              }
            }`,
            estimated_complexity: 200,
            description: "Products with reviews - within customer limit"
          },
          
          high_complexity: {
            query: `{
              search(query: "phone", limit: 20, includeFacets: true) {
                products {
                  id
                  name
                  reviews {
                    rating
                    user {
                      name
                      orders {
                        total
                      }
                    }
                  }
                  salesStats {
                    totalSold
                    revenue
                  }
                }
                facets {
                  categories {
                    name
                    count
                  }
                }
              }
            }`,
            estimated_complexity: 1500,
            description: "Complex search with nested data - requires seller role"
          },
          
          very_high_complexity: {
            query: `{
              analytics {
                totalRevenue
                topProducts {
                  product {
                    reviews {
                      user {
                        statistics {
                          totalSpent
                          favoriteCategory
                        }
                        orders {
                          products {
                            recommendations {
                              name
                              price
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }`,
            estimated_complexity: 5000,
            description: "Deep analytics query - admin only"
          }
        },
        
        testing_headers: {
          "X-User-Role": "guest, customer, seller, or admin",
          "X-User-ID": "User ID for authentication",
          "Authorization": "Bearer token (optional)"
        },
        
        complexity_calculation: {
          base_cost: "Each field has a base cost",
          list_multiplier: "List fields multiply by limit parameter",
          depth_penalty: "Deep nesting increases cost",
          expensive_operations: "Search, analytics have high base costs"
        }
      });
    });

    app.listen(PORT, () => {
      console.log(`🧮 Complexity Analysis Server ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
      console.log(`📊 Complexity examples at http://localhost:${PORT}/complexity-examples`);
      
      console.log(`\n🎯 Complexity Limits:`);
      console.log(`   - Guest: ${COMPLEXITY_CONFIG.guestMaxComplexity}`);
      console.log(`   - Customer: ${COMPLEXITY_CONFIG.customerMaxComplexity}`);
      console.log(`   - Seller: ${COMPLEXITY_CONFIG.sellerMaxComplexity}`);
      console.log(`   - Admin: ${COMPLEXITY_CONFIG.adminMaxComplexity}`);
      console.log(`   - Max Depth: ${COMPLEXITY_CONFIG.maxDepth}`);
      
      console.log(`\n🧪 Testing करने के लिए:`);
      console.log(`   - X-User-Role header use करें`);
      console.log(`   - /complexity-examples से sample queries try करें`);
      console.log(`   - Different roles के साथ same query test करें`);
    });

  } catch (error) {
    console.error('❌ Complexity Analysis Server startup error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🧮 Complexity Analysis Server shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🧮 Complexity Analysis Server shutting down...');
  process.exit(0);
});

// Start the server
startComplexityAnalysisServer();

module.exports = { 
  typeDefs, 
  resolvers, 
  COMPLEXITY_CONFIG, 
  createComplexityAnalyzer 
};