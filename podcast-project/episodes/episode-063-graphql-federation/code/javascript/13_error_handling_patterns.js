// 13_error_handling_patterns.js
// GraphQL Error Handling Patterns और Production-ready error management
// Indian e-commerce context के साथ comprehensive error handling

const { ApolloServer, gql, AuthenticationError, ForbiddenError, UserInputError, ApolloError } = require('apollo-server-express');
const express = require('express');
const winston = require('winston');
const rateLimit = require('express-rate-limit');

// Custom Error Classes - Indian context के लिए
class PaymentGatewayError extends ApolloError {
  constructor(message, gatewayCode, amount) {
    super(message, 'PAYMENT_GATEWAY_ERROR', { gatewayCode, amount });
    
    // Indian payment gateways के लिए specific handling
    this.name = 'PaymentGatewayError';
    this.gatewayCode = gatewayCode;
    this.amount = amount;
  }
}

class InventoryError extends ApolloError {
  constructor(message, productId, requestedQty, availableQty) {
    super(message, 'INVENTORY_ERROR', { productId, requestedQty, availableQty });
    
    this.name = 'InventoryError';
    this.productId = productId;
    this.requestedQty = requestedQty;
    this.availableQty = availableQty;
  }
}

class DeliveryError extends ApolloError {
  constructor(message, pincode, serviceable, alternateServices = []) {
    super(message, 'DELIVERY_ERROR', { pincode, serviceable, alternateServices });
    
    this.name = 'DeliveryError';
    this.pincode = pincode;
    this.serviceable = serviceable;
    this.alternateServices = alternateServices;
  }
}

class KYCError extends ApolloError {
  constructor(message, documentType, rejectionReason) {
    super(message, 'KYC_ERROR', { documentType, rejectionReason });
    
    this.name = 'KYCError';
    this.documentType = documentType;
    this.rejectionReason = rejectionReason;
  }
}

class GST_Error extends ApolloError {
  constructor(message, gstNumber, validationStage) {
    super(message, 'GST_VALIDATION_ERROR', { gstNumber, validationStage });
    
    this.name = 'GST_Error';
    this.gstNumber = gstNumber;
    this.validationStage = validationStage;
  }
}

// Logger Configuration - Production-ready logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'graphql-api' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Mock services - Production में real services होंगी
class PaymentService {
  static async processPayment(amount, method, upiId = null) {
    console.log(`💳 Processing payment: ₹${amount} via ${method}`);
    
    // Simulate different payment scenarios
    const scenarios = Math.random();
    
    if (scenarios < 0.1) {
      // 10% - Payment gateway failure
      throw new PaymentGatewayError(
        `Payment gateway ${method} is temporarily unavailable. कृपया कुछ समय बाद प्रयास करें।`,
        'GATEWAY_DOWN',
        amount
      );
    } else if (scenarios < 0.2) {
      // 10% - Insufficient balance
      throw new PaymentGatewayError(
        method === 'UPI' ? 
          `UPI ID ${upiId} में insufficient balance है। कृपया अपना balance check करें।` :
          'Insufficient funds in the selected payment method.',
        'INSUFFICIENT_FUNDS',
        amount
      );
    } else if (scenarios < 0.25) {
      // 5% - Daily limit exceeded
      throw new PaymentGatewayError(
        `Daily transaction limit exceeded for ${method}. कल फिर से प्रयास करें।`,
        'DAILY_LIMIT_EXCEEDED',
        amount
      );
    }
    
    // Successful payment
    return {
      transactionId: `TXN${Date.now()}${Math.random().toString(36).substr(2, 5)}`,
      status: 'SUCCESS',
      method,
      amount,
      timestamp: new Date().toISOString()
    };
  }
}

class InventoryService {
  static products = new Map([
    ['1', { id: '1', name: 'iPhone 15 Pro', stock: 5, reserved: 2 }],
    ['2', { id: '2', name: 'Samsung Galaxy S24', stock: 0, reserved: 0 }],
    ['3', { id: '3', name: 'OnePlus 12', stock: 15, reserved: 3 }],
    ['4', { id: '4', name: 'Nothing Phone 2', stock: 8, reserved: 1 }]
  ]);
  
  static async checkAvailability(productId, quantity) {
    console.log(`📦 Checking inventory for product ${productId}: quantity ${quantity}`);
    
    const product = this.products.get(productId);
    if (!product) {
      throw new UserInputError(`Product ${productId} not found in inventory`);
    }
    
    const availableStock = product.stock - product.reserved;
    
    if (availableStock < quantity) {
      throw new InventoryError(
        `केवल ${availableStock} units available हैं ${product.name} के लिए। आपने ${quantity} units request की हैं।`,
        productId,
        quantity,
        availableStock
      );
    }
    
    return {
      productId,
      productName: product.name,
      requestedQuantity: quantity,
      availableStock,
      canFulfill: true
    };
  }
  
  static async reserveStock(productId, quantity) {
    const product = this.products.get(productId);
    product.reserved += quantity;
    
    console.log(`✅ Stock reserved: ${product.name} - ${quantity} units`);
    return true;
  }
}

class DeliveryService {
  static serviceablePincodes = new Set([
    '110001', '400001', '560001', '600001', '700001', // Metro cities
    '226001', '302001', '500001', '382001', '641001'  // Tier-2 cities
  ]);
  
  static async checkDeliverability(pincode, productId) {
    console.log(`🚚 Checking delivery for pincode: ${pincode}`);
    
    // Validate pincode format
    if (!/^\d{6}$/.test(pincode)) {
      throw new UserInputError('Invalid pincode format. कृपया 6-digit pincode enter करें।');
    }
    
    const isServiceable = this.serviceablePincodes.has(pincode);
    
    if (!isServiceable) {
      // Suggest alternate services
      const alternateServices = [
        'India Post (7-10 days)',
        'Local courier pickup available',
        'Delivery to nearest metro city'
      ];
      
      throw new DeliveryError(
        `Currently हम ${pincode} pincode पर direct delivery नहीं करते। Alternative options available हैं।`,
        pincode,
        false,
        alternateServices
      );
    }
    
    return {
      pincode,
      serviceable: true,
      estimatedDelivery: '2-3 days',
      shippingCost: productId === '1' ? 0 : 40 // Free shipping for expensive items
    };
  }
}

class KYCService {
  static async validateDocument(documentType, documentNumber, userId) {
    console.log(`📋 KYC validation: ${documentType} for user ${userId}`);
    
    // Simulate different KYC scenarios
    const scenarios = Math.random();
    
    if (scenarios < 0.2) {
      // 20% - Document rejection scenarios
      const rejectionReasons = {
        'PAN': 'PAN number format invalid या image quality poor है',
        'AADHAAR': 'Aadhaar number invalid या name mismatch detected',
        'DRIVING_LICENSE': 'License expired या state verification failed',
        'PASSPORT': 'Passport number invalid या nationality verification failed'
      };
      
      throw new KYCError(
        `${documentType} verification failed: ${rejectionReasons[documentType]}`,
        documentType,
        rejectionReasons[documentType]
      );
    }
    
    return {
      documentType,
      documentNumber: documentNumber.replace(/\d/g, '*'), // Mask sensitive data
      status: 'VERIFIED',
      verifiedAt: new Date().toISOString()
    };
  }
}

class GSTService {
  static async validateGSTIN(gstin) {
    console.log(`🧾 Validating GSTIN: ${gstin}`);
    
    // Basic GSTIN format validation
    const gstinPattern = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    
    if (!gstinPattern.test(gstin)) {
      throw new GST_Error(
        'GSTIN format invalid है। Valid format: 22AAAAA0000A1Z5',
        gstin,
        'FORMAT_VALIDATION'
      );
    }
    
    // Simulate GST API validation failure
    if (Math.random() < 0.15) {
      throw new GST_Error(
        'GST validation service temporarily unavailable। कृपया बाद में प्रयास करें।',
        gstin,
        'API_VALIDATION'
      );
    }
    
    // Check if GSTIN is active (simulation)
    if (gstin.includes('99999')) {
      throw new GST_Error(
        'GSTIN inactive या cancelled status में है। कृपया valid GSTIN provide करें।',
        gstin,
        'STATUS_VALIDATION'
      );
    }
    
    return {
      gstin: gstin,
      businessName: 'Sample Business Pvt Ltd',
      status: 'ACTIVE',
      registrationDate: '2020-04-01',
      state: 'Maharashtra',
      validatedAt: new Date().toISOString()
    };
  }
}

// GraphQL Schema with Error-prone operations
const typeDefs = gql`
  scalar DateTime
  
  type User {
    id: ID!
    name: String!
    email: String!
    phone: String!
    kycStatus: String!
    gstNumber: String
  }
  
  type Product {
    id: ID!
    name: String!
    price: Float!
    stock: Int!
    category: String!
  }
  
  type Order {
    id: ID!
    userId: ID!
    items: [OrderItem!]!
    totalAmount: Float!
    status: String!
    paymentId: String
    deliveryAddress: Address!
  }
  
  type OrderItem {
    productId: ID!
    productName: String!
    quantity: Int!
    price: Float!
  }
  
  type Address {
    street: String!
    city: String!
    state: String!
    pincode: String!
    country: String!
  }
  
  type PaymentResult {
    transactionId: String!
    status: String!
    method: String!
    amount: Float!
    timestamp: DateTime!
  }
  
  type InventoryCheck {
    productId: ID!
    productName: String!
    requestedQuantity: Int!
    availableStock: Int!
    canFulfill: Boolean!
  }
  
  type DeliveryCheck {
    pincode: String!
    serviceable: Boolean!
    estimatedDelivery: String
    shippingCost: Float
    alternateServices: [String!]
  }
  
  type KYCResult {
    documentType: String!
    status: String!
    verifiedAt: DateTime
    rejectionReason: String
  }
  
  type GSTValidation {
    gstin: String!
    businessName: String
    status: String!
    state: String
    validatedAt: DateTime!
  }
  
  # Error types for structured error responses
  type ValidationError {
    field: String!
    message: String!
    code: String!
  }
  
  type BusinessError {
    type: String!
    message: String!
    code: String!
    details: String
  }
  
  type Query {
    user(id: ID!): User
    product(id: ID!): Product
    order(id: ID!): Order
    
    # Error-prone queries for demonstration
    checkInventory(productId: ID!, quantity: Int!): InventoryCheck!
    checkDelivery(pincode: String!, productId: ID!): DeliveryCheck!
    validateGST(gstin: String!): GSTValidation!
    
    # Queries that may fail due to business rules
    getOrderHistory(userId: ID!, limit: Int = 10): [Order!]!
    searchProducts(query: String!, priceRange: PriceRangeInput): [Product!]!
  }
  
  input PriceRangeInput {
    min: Float!
    max: Float!
  }
  
  input CreateOrderInput {
    userId: ID!
    items: [OrderItemInput!]!
    deliveryAddress: AddressInput!
    paymentMethod: String!
    upiId: String
  }
  
  input OrderItemInput {
    productId: ID!
    quantity: Int!
  }
  
  input AddressInput {
    street: String!
    city: String!
    state: String!
    pincode: String!
    country: String!
  }
  
  input KYCDocumentInput {
    documentType: String!
    documentNumber: String!
    userId: ID!
  }
  
  type Mutation {
    # Payment processing - high chance of errors
    processPayment(
      amount: Float!
      method: String!
      upiId: String
    ): PaymentResult!
    
    # Order creation - multiple failure points
    createOrder(input: CreateOrderInput!): Order!
    
    # KYC verification - regulatory compliance errors
    submitKYCDocument(input: KYCDocumentInput!): KYCResult!
    
    # Business registration
    registerGSTIN(gstin: String!, userId: ID!): GSTValidation!
    
    # Inventory operations
    reserveInventory(productId: ID!, quantity: Int!): Boolean!
    
    # Error simulation for testing
    simulateError(errorType: String!): String!
  }
`;

// Mock data
const users = new Map([
  ['1', { id: '1', name: 'राज शर्मा', email: 'raj@example.com', phone: '+919876543210', kycStatus: 'PENDING' }],
  ['2', { id: '2', name: 'प्रिया पटेल', email: 'priya@example.com', phone: '+919876543211', kycStatus: 'VERIFIED' }]
]);

const products = new Map([
  ['1', { id: '1', name: 'iPhone 15 Pro', price: 134900, stock: 5, category: 'smartphones' }],
  ['2', { id: '2', name: 'Samsung Galaxy S24', price: 84999, stock: 0, category: 'smartphones' }],
  ['3', { id: '3', name: 'OnePlus 12', price: 64999, stock: 15, category: 'smartphones' }]
]);

const orders = new Map();

// Resolvers with comprehensive error handling
const resolvers = {
  Query: {
    user: async (parent, { id }, context) => {
      logger.info(`Fetching user: ${id}`);
      
      const user = users.get(id);
      if (!user) {
        logger.warn(`User not found: ${id}`);
        throw new UserInputError(`User with ID ${id} not found`);
      }
      
      return user;
    },
    
    product: async (parent, { id }) => {
      const product = products.get(id);
      if (!product) {
        throw new UserInputError(`Product ${id} not found`);
      }
      return product;
    },
    
    checkInventory: async (parent, { productId, quantity }, context) => {
      try {
        return await InventoryService.checkAvailability(productId, quantity);
      } catch (error) {
        logger.error('Inventory check failed', { productId, quantity, error: error.message });
        throw error;
      }
    },
    
    checkDelivery: async (parent, { pincode, productId }) => {
      try {
        return await DeliveryService.checkDeliverability(pincode, productId);
      } catch (error) {
        logger.error('Delivery check failed', { pincode, productId, error: error.message });
        throw error;
      }
    },
    
    validateGST: async (parent, { gstin }) => {
      try {
        return await GSTService.validateGSTIN(gstin);
      } catch (error) {
        logger.error('GST validation failed', { gstin, error: error.message });
        throw error;
      }
    },
    
    getOrderHistory: async (parent, { userId, limit }, context) => {
      // Check user exists
      if (!users.has(userId)) {
        throw new UserInputError(`User ${userId} not found`);
      }
      
      // Check authorization (simplified)
      if (context.user?.id !== userId && context.user?.role !== 'admin') {
        throw new ForbiddenError('You can only access your own order history');
      }
      
      const userOrders = Array.from(orders.values())
        .filter(order => order.userId === userId)
        .slice(0, limit);
      
      return userOrders;
    },
    
    searchProducts: async (parent, { query, priceRange }) => {
      if (!query || query.length < 2) {
        throw new UserInputError('Search query must be at least 2 characters');
      }
      
      let results = Array.from(products.values())
        .filter(product => 
          product.name.toLowerCase().includes(query.toLowerCase())
        );
      
      if (priceRange) {
        if (priceRange.min > priceRange.max) {
          throw new UserInputError('Price range minimum cannot be greater than maximum');
        }
        
        results = results.filter(product => 
          product.price >= priceRange.min && product.price <= priceRange.max
        );
      }
      
      return results;
    }
  },

  Mutation: {
    processPayment: async (parent, { amount, method, upiId }, context) => {
      logger.info('Processing payment', { amount, method, upiId: upiId ? '***masked***' : null });
      
      // Validation
      if (amount <= 0) {
        throw new UserInputError('Payment amount must be greater than zero');
      }
      
      if (amount > 200000) {
        throw new UserInputError('Single transaction limit exceeded. Maximum allowed: ₹2,00,000');
      }
      
      if (method === 'UPI' && !upiId) {
        throw new UserInputError('UPI ID is required for UPI payments');
      }
      
      try {
        const result = await PaymentService.processPayment(amount, method, upiId);
        
        logger.info('Payment processed successfully', {
          transactionId: result.transactionId,
          amount,
          method
        });
        
        return result;
      } catch (error) {
        logger.error('Payment processing failed', {
          amount,
          method,
          error: error.message,
          errorCode: error.extensions?.code
        });
        throw error;
      }
    },
    
    createOrder: async (parent, { input }, context) => {
      logger.info('Creating order', { userId: input.userId, itemCount: input.items.length });
      
      try {
        // Validate user
        if (!users.has(input.userId)) {
          throw new UserInputError(`User ${input.userId} not found`);
        }
        
        // Validate delivery address
        await DeliveryService.checkDeliverability(input.deliveryAddress.pincode, input.items[0].productId);
        
        // Check inventory for all items
        const inventoryChecks = await Promise.all(
          input.items.map(item => 
            InventoryService.checkAvailability(item.productId, item.quantity)
          )
        );
        
        // Calculate total amount
        let totalAmount = 0;
        const orderItems = [];
        
        for (const item of input.items) {
          const product = products.get(item.productId);
          if (!product) {
            throw new UserInputError(`Product ${item.productId} not found`);
          }
          
          const itemTotal = product.price * item.quantity;
          totalAmount += itemTotal;
          
          orderItems.push({
            productId: item.productId,
            productName: product.name,
            quantity: item.quantity,
            price: product.price
          });
        }
        
        // Reserve inventory
        await Promise.all(
          input.items.map(item =>
            InventoryService.reserveStock(item.productId, item.quantity)
          )
        );
        
        // Process payment
        const paymentResult = await PaymentService.processPayment(
          totalAmount,
          input.paymentMethod,
          input.upiId
        );
        
        // Create order
        const orderId = `ORD${Date.now()}`;
        const order = {
          id: orderId,
          userId: input.userId,
          items: orderItems,
          totalAmount,
          status: 'CONFIRMED',
          paymentId: paymentResult.transactionId,
          deliveryAddress: input.deliveryAddress,
          createdAt: new Date().toISOString()
        };
        
        orders.set(orderId, order);
        
        logger.info('Order created successfully', {
          orderId,
          userId: input.userId,
          totalAmount,
          transactionId: paymentResult.transactionId
        });
        
        return order;
        
      } catch (error) {
        logger.error('Order creation failed', {
          userId: input.userId,
          error: error.message,
          errorCode: error.extensions?.code
        });
        throw error;
      }
    },
    
    submitKYCDocument: async (parent, { input }) => {
      logger.info('KYC document submitted', {
        userId: input.userId,
        documentType: input.documentType
      });
      
      try {
        const result = await KYCService.validateDocument(
          input.documentType,
          input.documentNumber,
          input.userId
        );
        
        // Update user KYC status
        const user = users.get(input.userId);
        if (user) {
          user.kycStatus = result.status;
        }
        
        logger.info('KYC verification completed', {
          userId: input.userId,
          documentType: input.documentType,
          status: result.status
        });
        
        return result;
        
      } catch (error) {
        logger.error('KYC verification failed', {
          userId: input.userId,
          documentType: input.documentType,
          error: error.message
        });
        throw error;
      }
    },
    
    registerGSTIN: async (parent, { gstin, userId }) => {
      try {
        const result = await GSTService.validateGSTIN(gstin);
        
        // Update user with GST number
        const user = users.get(userId);
        if (user) {
          user.gstNumber = gstin;
        }
        
        logger.info('GSTIN registered successfully', {
          userId,
          gstin,
          businessName: result.businessName
        });
        
        return result;
        
      } catch (error) {
        logger.error('GSTIN registration failed', {
          userId,
          gstin,
          error: error.message
        });
        throw error;
      }
    },
    
    reserveInventory: async (parent, { productId, quantity }) => {
      try {
        await InventoryService.checkAvailability(productId, quantity);
        await InventoryService.reserveStock(productId, quantity);
        return true;
      } catch (error) {
        logger.error('Inventory reservation failed', { productId, quantity, error: error.message });
        throw error;
      }
    },
    
    simulateError: async (parent, { errorType }) => {
      logger.warn('Simulating error', { errorType });
      
      switch (errorType) {
        case 'AUTHENTICATION':
          throw new AuthenticationError('User authentication required');
          
        case 'AUTHORIZATION':
          throw new ForbiddenError('Insufficient permissions for this operation');
          
        case 'VALIDATION':
          throw new UserInputError('Invalid input provided', {
            validationErrors: [
              { field: 'email', message: 'Email format is invalid' },
              { field: 'phone', message: 'Phone number must be 10 digits' }
            ]
          });
          
        case 'PAYMENT_FAILURE':
          throw new PaymentGatewayError('Payment gateway timeout', 'GATEWAY_TIMEOUT', 5000);
          
        case 'INVENTORY_OUT_OF_STOCK':
          throw new InventoryError('Product out of stock', '1', 5, 0);
          
        case 'DELIVERY_NOT_SERVICEABLE':
          throw new DeliveryError('Pincode not serviceable', '999999', false, ['India Post']);
          
        case 'KYC_REJECTED':
          throw new KYCError('Document verification failed', 'PAN', 'Invalid document');
          
        case 'GST_INVALID':
          throw new GST_Error('Invalid GSTIN format', '99AAAAA9999A9Z9', 'FORMAT_VALIDATION');
          
        case 'INTERNAL_SERVER':
          throw new ApolloError('Internal server error occurred', 'INTERNAL_ERROR');
          
        default:
          return 'Unknown error type';
      }
    }
  }
};

// Error formatting function
function formatError(error) {
  // Log all errors for monitoring
  logger.error('GraphQL Error', {
    message: error.message,
    code: error.extensions?.code,
    path: error.path,
    locations: error.locations,
    stack: process.env.NODE_ENV !== 'production' ? error.stack : undefined
  });
  
  // Custom error formatting for Indian context
  const formattedError = {
    message: error.message,
    code: error.extensions?.code || 'UNKNOWN_ERROR',
    timestamp: new Date().toISOString(),
    path: error.path,
    locations: error.locations
  };
  
  // Add custom fields based on error type
  if (error instanceof PaymentGatewayError) {
    formattedError.gatewayCode = error.gatewayCode;
    formattedError.amount = error.amount;
    formattedError.supportMessage = 'कृपया customer support से संपर्क करें या दूसरा payment method try करें।';
  }
  
  if (error instanceof InventoryError) {
    formattedError.productId = error.productId;
    formattedError.requestedQty = error.requestedQty;
    formattedError.availableQty = error.availableQty;
    formattedError.supportMessage = 'Available quantity के साथ order करें या stock restock का wait करें।';
  }
  
  if (error instanceof DeliveryError) {
    formattedError.pincode = error.pincode;
    formattedError.alternateServices = error.alternateServices;
    formattedError.supportMessage = 'Alternative delivery options available हैं।';
  }
  
  if (error instanceof KYCError) {
    formattedError.documentType = error.documentType;
    formattedError.rejectionReason = error.rejectionReason;
    formattedError.supportMessage = 'कृपया valid documents के साथ re-submit करें।';
  }
  
  if (error instanceof GST_Error) {
    formattedError.gstNumber = error.gstNumber;
    formattedError.validationStage = error.validationStage;
    formattedError.supportMessage = 'कृपया valid GSTIN provide करें या GST team से contact करें।';
  }
  
  // Remove sensitive information in production
  if (process.env.NODE_ENV === 'production') {
    delete formattedError.locations;
    delete formattedError.extensions;
  }
  
  return formattedError;
}

async function startErrorHandlingServer() {
  try {
    const app = express();
    
    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, कृपया कुछ समय बाद प्रयास करें।'
    });
    
    app.use('/graphql', limiter);
    
    // Request logging middleware
    app.use((req, res, next) => {
      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
      req.requestId = requestId;
      
      logger.info('Incoming request', {
        requestId,
        method: req.method,
        url: req.url,
        userAgent: req.get('User-Agent'),
        ip: req.ip
      });
      
      next();
    });

    const server = new ApolloServer({
      typeDefs,
      resolvers,
      
      context: ({ req }) => {
        return {
          requestId: req.requestId,
          user: req.headers['x-user-id'] ? {
            id: req.headers['x-user-id'],
            role: req.headers['x-user-role'] || 'customer'
          } : null,
          ip: req.ip,
          userAgent: req.get('User-Agent')
        };
      },
      
      formatError,
      
      plugins: [
        {
          requestDidStart() {
            return {
              didResolveOperation(requestContext) {
                logger.info('GraphQL Operation', {
                  requestId: requestContext.context.requestId,
                  operationName: requestContext.request.operationName,
                  query: requestContext.request.query?.substring(0, 200) + '...'
                });
              },
              
              didEncounterErrors(requestContext) {
                const { errors, context } = requestContext;
                
                errors.forEach(error => {
                  logger.error('GraphQL Execution Error', {
                    requestId: context.requestId,
                    errorMessage: error.message,
                    errorCode: error.extensions?.code,
                    path: error.path
                  });
                });
              },
              
              willSendResponse(requestContext) {
                logger.info('Response sent', {
                  requestId: requestContext.context.requestId,
                  hasData: !!requestContext.response.data,
                  hasErrors: !!(requestContext.response.errors && requestContext.response.errors.length > 0)
                });
              }
            };
          }
        }
      ],
      
      introspection: process.env.NODE_ENV !== 'production',
      playground: process.env.NODE_ENV !== 'production'
    });

    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4027;
    
    // Health check
    app.get('/health', (req, res) => {
      res.json({
        service: 'graphql-error-handling',
        status: 'healthy',
        timestamp: new Date().toISOString(),
        features: [
          'Structured error handling',
          'Indian business context errors',
          'Comprehensive logging',
          'Payment gateway error handling',
          'Inventory management errors',
          'KYC and GST validation errors'
        ]
      });
    });
    
    // Error simulation endpoint
    app.get('/error-examples', (req, res) => {
      res.json({
        title: 'GraphQL Error Handling Examples',
        description: 'Comprehensive error handling for Indian e-commerce',
        
        error_types: {
          payment_errors: [
            'PAYMENT_GATEWAY_ERROR - Gateway unavailable',
            'INSUFFICIENT_FUNDS - UPI/Card balance low',
            'DAILY_LIMIT_EXCEEDED - Transaction limits'
          ],
          
          inventory_errors: [
            'INVENTORY_ERROR - Stock unavailable',
            'PRODUCT_NOT_FOUND - Invalid product ID',
            'RESERVATION_FAILED - Concurrent orders'
          ],
          
          delivery_errors: [
            'DELIVERY_ERROR - Pincode not serviceable',
            'INVALID_ADDRESS - Address validation failed'
          ],
          
          business_errors: [
            'KYC_ERROR - Document verification failed',
            'GST_VALIDATION_ERROR - Invalid GSTIN',
            'COMPLIANCE_ERROR - Regulatory issues'
          ],
          
          system_errors: [
            'AUTHENTICATION_ERROR - Login required',
            'AUTHORIZATION_ERROR - Insufficient permissions',
            'VALIDATION_ERROR - Input validation failed',
            'RATE_LIMIT_ERROR - Too many requests'
          ]
        },
        
        test_mutations: {
          payment_failure: `
            mutation {
              processPayment(amount: 50000, method: "UPI", upiId: "user@paytm") {
                transactionId
                status
              }
            }
          `,
          
          inventory_check: `
            mutation {
              reserveInventory(productId: "2", quantity: 5) 
            }
          `,
          
          delivery_check: `
            query {
              checkDelivery(pincode: "999999", productId: "1") {
                serviceable
                alternateServices
              }
            }
          `,
          
          kyc_submission: `
            mutation {
              submitKYCDocument(input: {
                documentType: "PAN"
                documentNumber: "INVALID123"
                userId: "1"
              }) {
                status
                rejectionReason
              }
            }
          `,
          
          error_simulation: `
            mutation {
              simulateError(errorType: "PAYMENT_FAILURE")
            }
          `
        },
        
        error_response_structure: {
          message: "Human-readable error message (Hindi + English)",
          code: "ERROR_CODE for programmatic handling",
          timestamp: "ISO timestamp",
          path: "GraphQL path where error occurred",
          supportMessage: "User guidance in Hindi/English",
          customFields: "Error-specific fields (amount, productId, etc.)"
        }
      });
    });

    app.listen(PORT, () => {
      console.log(`🚨 GraphQL Error Handling Server ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
      console.log(`📋 Error examples at http://localhost:${PORT}/error-examples`);
      
      console.log(`\n🇮🇳 Indian E-commerce Error Handling Features:`);
      console.log(`   - Payment gateway errors (UPI, Cards, NetBanking)`);
      console.log(`   - Inventory and stock management errors`);
      console.log(`   - Delivery pincode validation errors`);
      console.log(`   - KYC document verification errors`);
      console.log(`   - GST validation errors`);
      console.log(`   - Structured error responses with Hindi messages`);
      
      console.log(`\n🧪 Test Error Scenarios:`);
      console.log(`   - Use simulateError mutation with different errorType values`);
      console.log(`   - Try invalid payments, out-of-stock products`);
      console.log(`   - Test unserviceable pincodes`);
      console.log(`   - Submit invalid KYC documents`);
    });

  } catch (error) {
    logger.error('Server startup failed', { error: error.message, stack: error.stack });
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

// Unhandled errors
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection', { reason, promise });
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception', { error: error.message, stack: error.stack });
  process.exit(1);
});

// Start the server
startErrorHandlingServer();

module.exports = { 
  PaymentGatewayError,
  InventoryError,
  DeliveryError,
  KYCError,
  GST_Error,
  formatError,
  typeDefs,
  resolvers
};