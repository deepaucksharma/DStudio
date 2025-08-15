// 04_schema_stitching.js
// Schema Stitching - Federation का alternative approach
// Multiple GraphQL schemas को manually combine करता है

const { ApolloServer, gql } = require('apollo-server-express');
const { stitchSchemas } = require('@graphql-tools/stitch');
const { introspectSchema, wrapSchema } = require('@graphql-tools/wrap');
const { print } = require('graphql');
const fetch = require('node-fetch');
const express = require('express');

// HTTP executor for remote schemas
const executor = async ({ document, variables, context }) => {
  const query = print(document);
  
  // Service URL determination
  let serviceUrl;
  const operationName = document.definitions[0]?.name?.value;
  
  // Route queries based on operation or field names
  if (query.includes('products') || query.includes('Product')) {
    serviceUrl = process.env.PRODUCTS_SERVICE_URL || 'http://localhost:4001/graphql';
  } else if (query.includes('users') || query.includes('User')) {
    serviceUrl = process.env.USERS_SERVICE_URL || 'http://localhost:4002/graphql';
  } else if (query.includes('orders') || query.includes('Order')) {
    serviceUrl = process.env.ORDERS_SERVICE_URL || 'http://localhost:4003/graphql';
  } else {
    // Default to products service
    serviceUrl = process.env.PRODUCTS_SERVICE_URL || 'http://localhost:4001/graphql';
  }
  
  console.log(`🎯 Routing query to: ${serviceUrl}`);
  console.log(`📝 Query preview: ${query.substring(0, 100)}...`);
  
  try {
    const fetchResult = await fetch(serviceUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward authentication headers
        'Authorization': context.authToken || '',
        'x-request-id': context.requestId || '',
        'x-user-id': context.userId || ''
      },
      body: JSON.stringify({
        query,
        variables,
        operationName
      })
    });

    const result = await fetchResult.json();
    
    if (!fetchResult.ok) {
      console.error(`❌ Service error from ${serviceUrl}:`, result);
      throw new Error(`Service error: ${result.error || 'Unknown error'}`);
    }
    
    console.log(`✅ Response from ${serviceUrl}:`, {
      hasData: !!result.data,
      hasErrors: !!(result.errors && result.errors.length > 0)
    });
    
    return result;
    
  } catch (error) {
    console.error(`❌ Network error for ${serviceUrl}:`, error.message);
    throw new Error(`Failed to fetch from ${serviceUrl}: ${error.message}`);
  }
};

// Type definitions for stitched schema
const stitchingTypeDefs = gql`
  # Additional types for schema stitching
  type Query {
    # Health check for stitched schema
    _schemaHealth: SchemaHealth!
    
    # Cross-service queries (stitching specific)
    userWithRecentOrders(userId: ID!): UserWithOrders
    productWithReviews(productId: ID!): ProductWithReviews
    orderSummary(orderId: ID!): OrderSummary
  }

  type SchemaHealth {
    status: String!
    services: [ServiceHealth!]!
    timestamp: String!
  }

  type ServiceHealth {
    name: String!
    url: String!
    status: String!
    responseTime: String
  }

  # Combined types for cross-service data
  type UserWithOrders {
    user: User
    recentOrders: [Order!]!
    totalOrders: Int!
  }

  type ProductWithReviews {
    product: Product
    reviews: [Review!]!
    averageRating: Float
    totalReviews: Int!
  }

  type OrderSummary {
    order: Order
    user: User
    products: [Product!]!
    totalAmount: Float!
  }

  # Mock types (would come from actual services)
  type User {
    id: ID!
    name: String!
    email: String!
    createdAt: String!
  }

  type Order {
    id: ID!
    userId: ID!
    status: String!
    totalAmount: Float!
    createdAt: String!
    items: [OrderItem!]!
  }

  type OrderItem {
    productId: ID!
    quantity: Int!
    price: Float!
  }

  type Review {
    id: ID!
    productId: ID!
    userId: ID!
    rating: Int!
    comment: String
    createdAt: String!
  }

  # Product type reference (should match products service)
  type Product {
    id: ID!
    name: String!
    price: Float!
    description: String
    category: String!
  }
`;

// Resolvers for stitched schema
const stitchingResolvers = {
  Query: {
    _schemaHealth: async (parent, args, context) => {
      console.log('🏥 Schema health check requested');
      
      const services = [
        { name: 'products', url: process.env.PRODUCTS_SERVICE_URL || 'http://localhost:4001/graphql' },
        { name: 'users', url: process.env.USERS_SERVICE_URL || 'http://localhost:4002/graphql' },
        { name: 'orders', url: process.env.ORDERS_SERVICE_URL || 'http://localhost:4003/graphql' }
      ];

      const healthChecks = await Promise.allSettled(
        services.map(async (service) => {
          const startTime = Date.now();
          try {
            const response = await fetch(service.url.replace('/graphql', '/health'), {
              timeout: 5000
            });
            const responseTime = Date.now() - startTime;
            
            return {
              name: service.name,
              url: service.url,
              status: response.ok ? 'healthy' : 'unhealthy',
              responseTime: `${responseTime}ms`
            };
          } catch (error) {
            const responseTime = Date.now() - startTime;
            return {
              name: service.name,
              url: service.url,
              status: 'error',
              responseTime: `${responseTime}ms`
            };
          }
        })
      );

      const serviceHealths = healthChecks.map(result => 
        result.status === 'fulfilled' ? result.value : {
          name: 'unknown',
          url: 'unknown',
          status: 'error',
          responseTime: 'timeout'
        }
      );

      return {
        status: serviceHealths.every(s => s.status === 'healthy') ? 'healthy' : 'degraded',
        services: serviceHealths,
        timestamp: new Date().toISOString()
      };
    },

    userWithRecentOrders: async (parent, { userId }, context) => {
      console.log(`👤 Fetching user ${userId} with recent orders`);
      
      try {
        // Parallel queries to different services
        const [userResponse, ordersResponse] = await Promise.all([
          // Query users service
          executor({
            document: gql`
              query GetUser($userId: ID!) {
                user(id: $userId) {
                  id
                  name
                  email
                  createdAt
                }
              }
            `,
            variables: { userId },
            context
          }),
          // Query orders service
          executor({
            document: gql`
              query GetUserOrders($userId: ID!) {
                ordersByUser(userId: $userId, limit: 5) {
                  id
                  status
                  totalAmount
                  createdAt
                }
              }
            `,
            variables: { userId },
            context
          })
        ]);

        return {
          user: userResponse.data?.user,
          recentOrders: ordersResponse.data?.ordersByUser || [],
          totalOrders: ordersResponse.data?.ordersByUser?.length || 0
        };
        
      } catch (error) {
        console.error('❌ Error fetching user with orders:', error);
        throw error;
      }
    },

    productWithReviews: async (parent, { productId }, context) => {
      console.log(`🛍️ Fetching product ${productId} with reviews`);
      
      try {
        // Parallel queries
        const [productResponse, reviewsResponse] = await Promise.all([
          // Query products service
          executor({
            document: gql`
              query GetProduct($productId: ID!) {
                product(id: $productId) {
                  id
                  name
                  price
                  description
                  category
                }
              }
            `,
            variables: { productId },
            context
          }),
          // Query reviews service (mock)
          Promise.resolve({
            data: {
              reviews: [
                {
                  id: '1',
                  productId,
                  userId: 'user1',
                  rating: 5,
                  comment: 'बहुत अच्छा product है!',
                  createdAt: '2024-01-15T10:30:00Z'
                }
              ]
            }
          })
        ]);

        const reviews = reviewsResponse.data?.reviews || [];
        const averageRating = reviews.length > 0 
          ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length 
          : 0;

        return {
          product: productResponse.data?.product,
          reviews,
          averageRating,
          totalReviews: reviews.length
        };
        
      } catch (error) {
        console.error('❌ Error fetching product with reviews:', error);
        throw error;
      }
    },

    orderSummary: async (parent, { orderId }, context) => {
      console.log(`📦 Fetching order summary for ${orderId}`);
      
      try {
        // Step 1: Get order details
        const orderResponse = await executor({
          document: gql`
            query GetOrder($orderId: ID!) {
              order(id: $orderId) {
                id
                userId
                status
                totalAmount
                createdAt
                items {
                  productId
                  quantity
                  price
                }
              }
            }
          `,
          variables: { orderId },
          context
        });

        const order = orderResponse.data?.order;
        if (!order) {
          throw new Error(`Order ${orderId} not found`);
        }

        // Step 2: Get user details
        const userResponse = await executor({
          document: gql`
            query GetUser($userId: ID!) {
              user(id: $userId) {
                id
                name
                email
              }
            }
          `,
          variables: { userId: order.userId },
          context
        });

        // Step 3: Get product details for all items
        const productIds = order.items.map(item => item.productId);
        const productQueries = productIds.map(productId =>
          executor({
            document: gql`
              query GetProduct($productId: ID!) {
                product(id: $productId) {
                  id
                  name
                  price
                  category
                }
              }
            `,
            variables: { productId },
            context
          })
        );

        const productResponses = await Promise.all(productQueries);
        const products = productResponses
          .map(response => response.data?.product)
          .filter(Boolean);

        return {
          order,
          user: userResponse.data?.user,
          products,
          totalAmount: order.totalAmount
        };
        
      } catch (error) {
        console.error('❌ Error fetching order summary:', error);
        throw error;
      }
    }
  }
};

// Create stitched schema
async function createStitchedSchema() {
  console.log('🧵 Creating stitched schema...');
  
  try {
    const schemas = [];
    const serviceConfigs = [
      {
        name: 'products',
        url: process.env.PRODUCTS_SERVICE_URL || 'http://localhost:4001/graphql'
      },
      {
        name: 'users', 
        url: process.env.USERS_SERVICE_URL || 'http://localhost:4002/graphql'
      },
      {
        name: 'orders',
        url: process.env.ORDERS_SERVICE_URL || 'http://localhost:4003/graphql'
      }
    ];

    // Introspect each service schema
    for (const config of serviceConfigs) {
      try {
        console.log(`🔍 Introspecting ${config.name} service at ${config.url}`);
        
        const schema = await introspectSchema(async ({ document, variables }) => {
          const query = print(document);
          
          const response = await fetch(config.url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, variables })
          });
          
          return response.json();
        });

        // Wrap schema with executor
        const wrappedSchema = wrapSchema({
          schema,
          executor: ({ document, variables, context }) => {
            return executor({ document, variables, context });
          }
        });

        schemas.push({
          schema: wrappedSchema,
          config
        });

        console.log(`✅ ${config.name} schema introspected successfully`);
        
      } catch (error) {
        console.warn(`⚠️ Failed to introspect ${config.name}: ${error.message}`);
        // Continue without this service
      }
    }

    if (schemas.length === 0) {
      console.warn('⚠️ No schemas available, using local types only');
    }

    // Create stitched schema
    const stitchedSchema = stitchSchemas({
      subschemas: schemas.map(s => ({ schema: s.schema })),
      typeDefs: stitchingTypeDefs,
      resolvers: stitchingResolvers,
      
      // Schema transformation
      schemaTransforms: [],
      
      // Merge types configuration
      mergeTypes: true,
      
      // Error handling for schema stitching
      onTypeConflict: (left, right, info) => {
        console.log(`🔄 Type conflict: ${info.typeName}`);
        return left; // Use left schema's type
      }
    });

    console.log('✅ Stitched schema created successfully');
    return stitchedSchema;
    
  } catch (error) {
    console.error('❌ Error creating stitched schema:', error);
    throw error;
  }
}

async function startStitchingServer() {
  try {
    const app = express();
    
    // Request logging
    app.use((req, res, next) => {
      console.log(`📞 Schema Stitching - ${req.method} ${req.path}`);
      next();
    });

    // Create stitched schema
    const schema = await createStitchedSchema();
    
    const server = new ApolloServer({
      schema,
      
      context: ({ req }) => {
        const authToken = req.headers.authorization || '';
        const requestId = req.headers['x-request-id'] || `req_${Date.now()}`;
        const userId = req.headers['x-user-id'] || '';
        
        return {
          authToken,
          requestId,
          userId,
          approach: 'schema-stitching'
        };
      },
      
      formatError: (error) => {
        console.error('❌ Schema Stitching Error:', error.message);
        return {
          message: error.message,
          locations: error.locations,
          path: error.path,
          extensions: {
            ...error.extensions,
            approach: 'schema-stitching'
          }
        };
      },
      
      introspection: true,
      playground: process.env.NODE_ENV !== 'production' ? {
        settings: {
          'request.credentials': 'include'
        }
      } : false
    });

    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4010;
    
    // Health check
    app.get('/health', (req, res) => {
      res.json({
        service: 'schema-stitching',
        status: 'healthy',
        approach: 'Schema Stitching',
        timestamp: new Date().toISOString()
      });
    });

    // Schema info endpoint
    app.get('/schema-info', (req, res) => {
      res.json({
        approach: 'Schema Stitching',
        description: 'Multiple GraphQL schemas combined using graphql-tools stitching',
        features: [
          'Cross-service queries',
          'Schema introspection',
          'Dynamic routing',
          'Error handling'
        ]
      });
    });

    app.listen(PORT, () => {
      console.log(`🧵 Schema Stitching Server ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
      console.log(`📋 Schema info at http://localhost:${PORT}/schema-info`);
      
      if (process.env.NODE_ENV !== 'production') {
        console.log(`🎮 GraphQL Playground at http://localhost:${PORT}${server.graphqlPath}`);
      }
    });

  } catch (error) {
    console.error('❌ Schema Stitching Server startup error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🧵 Schema Stitching Server shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🧵 Schema Stitching Server shutting down...');
  process.exit(0);
});

// Start the server
startStitchingServer();

module.exports = { stitchingTypeDefs, stitchingResolvers, createStitchedSchema };