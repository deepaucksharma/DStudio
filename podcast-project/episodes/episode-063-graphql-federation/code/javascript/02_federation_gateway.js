// 02_federation_gateway.js
// Apollo Federation Gateway - यह सारे subgraphs को combine करता है
// यह हमारा main entry point है clients के लिए

const { ApolloServer } = require('apollo-server-express');
const { ApolloGateway, IntrospectAndCompose, RemoteGraphQLDataSource } = require('@apollo/gateway');
const express = require('express');

// Custom DataSource class for authentication और logging
class AuthenticatedDataSource extends RemoteGraphQLDataSource {
  constructor(config) {
    super(config);
    this.config = config;
  }

  // Request को modify करते हैं before sending to subgraph
  willSendRequest({ request, context }) {
    // Authentication token forward करते हैं
    if (context.authToken) {
      request.http.headers.set('authorization', context.authToken);
    }
    
    // Request ID भी forward करते हैं for tracing
    if (context.requestId) {
      request.http.headers.set('x-request-id', context.requestId);
    }
    
    // User info भी forward कर सकते हैं
    if (context.userId) {
      request.http.headers.set('x-user-id', context.userId);
    }
    
    console.log(`📤 Forwarding request to ${this.config.name}:`, {
      operation: request.query.substr(0, 100), // First 100 chars
      variables: request.variables,
      serviceName: this.config.name
    });
  }

  // Response को process करते हैं after receiving from subgraph
  didReceiveResponse({ response, request, context }) {
    console.log(`📥 Received response from ${this.config.name}:`, {
      status: response.http.status,
      hasErrors: response.errors && response.errors.length > 0,
      serviceName: this.config.name
    });
    
    // Response time log कर सकते हैं
    if (context.startTime) {
      const responseTime = Date.now() - context.startTime;
      console.log(`⏱️ ${this.config.name} response time: ${responseTime}ms`);
    }
    
    return response;
  }

  // Error handling के लिए
  didEncounterError(error, request, context) {
    console.error(`❌ Error from ${this.config.name}:`, {
      error: error.message,
      serviceName: this.config.name,
      operation: request.query.substr(0, 100)
    });
    
    // Error metrics यहाँ send कर सकते हैं
    // Example: sendErrorMetrics(this.config.name, error);
  }
}

// Gateway configuration
const gateway = new ApolloGateway({
  // Subgraphs की list - production में service discovery से आएगी
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: [
      // Products service - inventory management के लिए
      {
        name: 'products',
        url: process.env.PRODUCTS_SERVICE_URL || 'http://localhost:4001/graphql'
      },
      // Users service - user management के लिए
      {
        name: 'users', 
        url: process.env.USERS_SERVICE_URL || 'http://localhost:4002/graphql'
      },
      // Orders service - order processing के लिए
      {
        name: 'orders',
        url: process.env.ORDERS_SERVICE_URL || 'http://localhost:4003/graphql'
      },
      // Reviews service - product reviews के लिए
      {
        name: 'reviews',
        url: process.env.REVIEWS_SERVICE_URL || 'http://localhost:4004/graphql'
      },
      // Inventory service - stock management के लिए
      {
        name: 'inventory',
        url: process.env.INVENTORY_SERVICE_URL || 'http://localhost:4005/graphql'
      }
    ],
    // Polling interval for schema updates
    pollIntervalInMs: process.env.SCHEMA_POLL_INTERVAL || 30000, // 30 seconds
  }),
  
  // Custom DataSource के लिए
  buildService({ url, name }) {
    return new AuthenticatedDataSource({ 
      url,
      name,
      // Connection pooling और timeout settings
      requestTimeout: 10000, // 10 seconds
      maxRetries: 3,
      retryDelayMs: 1000
    });
  },

  // Service health check के लिए
  serviceHealthCheck: true,
  
  // Debug mode for development
  debug: process.env.NODE_ENV !== 'production',
  
  // Schema composition options
  introspectionHeaders: {
    'User-Agent': 'Apollo-Gateway/1.0'
  }
});

// Request ID generator
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// JWT token validator (mock implementation)
function validateAuthToken(token) {
  try {
    // Production में proper JWT validation होगी
    if (!token || !token.startsWith('Bearer ')) {
      return null;
    }
    
    // Mock validation - real में JWT decode करेंगे
    const mockUser = {
      id: 'user_123',
      email: 'customer@flipkart.com',
      role: 'customer',
      permissions: ['read:products', 'write:orders']
    };
    
    return mockUser;
  } catch (error) {
    console.error('Token validation error:', error);
    return null;
  }
}

async function startGateway() {
  try {
    const app = express();
    
    // Request logging middleware
    app.use((req, res, next) => {
      req.startTime = Date.now();
      req.requestId = generateRequestId();
      
      console.log(`📞 Incoming request:`, {
        method: req.method,
        path: req.path,
        requestId: req.requestId,
        userAgent: req.get('User-Agent'),
        ip: req.ip
      });
      
      next();
    });
    
    // CORS handling for web clients
    app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      
      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
      } else {
        next();
      }
    });

    // Apollo Server with Gateway
    const server = new ApolloServer({
      gateway,
      
      // Context function - यहाँ authentication और request info set करते हैं
      context: ({ req }) => {
        const authToken = req.headers.authorization || '';
        const requestId = req.requestId || generateRequestId();
        const startTime = req.startTime || Date.now();
        
        // Token validate करते हैं
        const user = validateAuthToken(authToken);
        
        console.log(`🔐 Request context:`, {
          requestId,
          hasAuth: !!authToken,
          userId: user?.id,
          userRole: user?.role
        });
        
        return {
          authToken,
          requestId,
          startTime,
          user,
          // Additional context data
          clientInfo: {
            userAgent: req.get('User-Agent'),
            ip: req.ip,
            referer: req.get('Referer')
          }
        };
      },
      
      // Subscriptions के लिए (WebSocket support)
      subscriptions: {
        path: '/graphql',
        onConnect: (connectionParams, webSocket, context) => {
          console.log('🔌 WebSocket connection established');
          
          // WebSocket के लिए authentication
          const authToken = connectionParams.authorization || '';
          const user = validateAuthToken(authToken);
          
          if (!user) {
            throw new Error('Authentication required for subscriptions');
          }
          
          return {
            authToken,
            user,
            connectionId: generateRequestId()
          };
        },
        onDisconnect: (webSocket, context) => {
          console.log('🔌 WebSocket connection closed');
        }
      },
      
      // Error formatting
      formatError: (error) => {
        console.error(`❌ GraphQL Gateway Error:`, {
          message: error.message,
          code: error.extensions?.code,
          serviceName: error.extensions?.serviceName,
          stack: process.env.NODE_ENV !== 'production' ? error.stack : undefined
        });
        
        // Error metrics भेज सकते हैं यहाँ से
        // sendErrorMetrics(error);
        
        return {
          message: error.message,
          code: error.extensions?.code || 'INTERNAL_ERROR',
          ...(process.env.NODE_ENV !== 'production' && { stack: error.stack })
        };
      },
      
      // Response formatting
      formatResponse: (response, { context }) => {
        if (context.startTime) {
          const responseTime = Date.now() - context.startTime;
          console.log(`⏱️ Total response time: ${responseTime}ms`);
          
          // Response time metrics
          response.extensions = {
            ...response.extensions,
            responseTime: `${responseTime}ms`,
            requestId: context.requestId
          };
        }
        
        return response;
      },
      
      // Plugin for metrics और monitoring
      plugins: [
        {
          requestDidStart() {
            return {
              didResolveOperation(requestContext) {
                console.log(`🎯 Operation: ${requestContext.request.operationName || 'Anonymous'}`);
              },
              
              didEncounterErrors(requestContext) {
                console.error(`💥 Request completed with errors:`, requestContext.errors);
              },
              
              willSendResponse(requestContext) {
                // Response metrics log करते हैं
                const { response, context } = requestContext;
                console.log(`📊 Response sent:`, {
                  hasData: !!response.data,
                  hasErrors: !!(response.errors && response.errors.length > 0),
                  requestId: context.requestId
                });
              }
            };
          }
        }
      ],
      
      // Development settings
      introspection: process.env.NODE_ENV !== 'production',
      playground: process.env.NODE_ENV !== 'production' ? {
        settings: {
          'request.credentials': 'include'
        }
      } : false
    });

    // Apply middleware
    server.applyMiddleware({ 
      app, 
      path: '/graphql',
      cors: false // हमने खुद handle किया है
    });
    
    const PORT = process.env.PORT || 4000;
    
    // Health check endpoint
    app.get('/health', async (req, res) => {
      try {
        // Gateway health check
        const gatewayHealth = await gateway.executor ? 'healthy' : 'unhealthy';
        
        res.status(200).json({
          status: 'healthy',
          gateway: gatewayHealth,
          timestamp: new Date().toISOString(),
          uptime: process.uptime(),
          version: process.env.npm_package_version || '1.0.0'
        });
      } catch (error) {
        res.status(503).json({
          status: 'unhealthy',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Metrics endpoint (simplified)
    app.get('/metrics', (req, res) => {
      res.json({
        requests_total: 'Metrics implementation needed',
        response_time_avg: 'Metrics implementation needed',
        errors_total: 'Metrics implementation needed'
      });
    });

    // Start server
    const httpServer = app.listen(PORT, () => {
      console.log(`🚀 Gateway ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
      console.log(`📊 Metrics at http://localhost:${PORT}/metrics`);
      
      if (process.env.NODE_ENV !== 'production') {
        console.log(`🎮 GraphQL Playground available at http://localhost:${PORT}${server.graphqlPath}`);
      }
    });

    // Install subscription handlers
    server.installSubscriptionHandlers(httpServer);
    
  } catch (error) {
    console.error('❌ Gateway startup error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
let isShuttingDown = false;

async function gracefulShutdown(signal) {
  if (isShuttingDown) return;
  isShuttingDown = true;
  
  console.log(`📴 ${signal} received, starting graceful shutdown...`);
  
  try {
    // Gateway को stop करते हैं
    if (gateway) {
      await gateway.stop();
      console.log('✅ Gateway stopped successfully');
    }
    
    console.log('✅ Graceful shutdown completed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start the gateway
startGateway();