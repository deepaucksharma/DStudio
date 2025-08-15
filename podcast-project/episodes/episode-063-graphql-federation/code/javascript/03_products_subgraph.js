// 03_products_subgraph.js
// Products Subgraph - Federation का हिस्सा
// यह products की information manage करता है

const { ApolloServer, gql } = require('apollo-server-express');
const { buildFederatedSchema } = require('@apollo/federation');
const express = require('express');

// Federation type definitions
const typeDefs = gql`
  # Product entity को federation के लिए extend करते हैं
  type Product @key(fields: "id") {
    id: ID!
    name: String!
    price: Float!
    description: String
    category: String!
    brand: String
    imageUrls: [String!]
    specifications: ProductSpecifications
    availability: ProductAvailability!
    createdAt: String!
    updatedAt: String!
  }

  # Product specifications - detailed product info
  type ProductSpecifications {
    dimensions: String
    weight: Float
    color: String
    material: String
    warranty: String
    # Electronics के लिए specific fields
    batteryLife: String
    screenSize: String
    storage: String
    # Fashion के लिए specific fields
    size: String
    fabric: String
  }

  # Product availability status
  type ProductAvailability {
    inStock: Boolean!
    stockCount: Int!
    estimatedDelivery: String
    lastUpdated: String!
  }

  # Category type
  type Category @key(fields: "id") {
    id: ID!
    name: String!
    parentId: ID
    level: Int!
  }

  extend type Query {
    # सारे products की list
    products(
      limit: Int = 10
      offset: Int = 0
      category: String
      brand: String
      priceRange: PriceRange
      searchTerm: String
    ): ProductConnection!
    
    # Single product by ID
    product(id: ID!): Product
    
    # Products by category
    productsByCategory(categoryId: ID!, limit: Int = 10): [Product!]!
    
    # Search products
    searchProducts(query: String!, limit: Int = 10): [Product!]!
    
    # Get all categories
    categories: [Category!]!
    
    # Featured products for homepage
    featuredProducts(limit: Int = 5): [Product!]!
  }

  # Pagination के लिए connection pattern
  type ProductConnection {
    edges: [ProductEdge!]!
    pageInfo: PageInfo!
    totalCount: Int!
  }

  type ProductEdge {
    node: Product!
    cursor: String!
  }

  type PageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }

  # Price range filter के लिए
  input PriceRange {
    min: Float!
    max: Float!
  }

  extend type Mutation {
    # Product management (admin only)
    createProduct(input: CreateProductInput!): Product!
    updateProduct(id: ID!, input: UpdateProductInput!): Product
    deleteProduct(id: ID!): Boolean!
    
    # Stock management
    updateStock(productId: ID!, quantity: Int!): ProductAvailability!
  }

  input CreateProductInput {
    name: String!
    price: Float!
    description: String
    category: String!
    brand: String!
    imageUrls: [String!]
    specifications: ProductSpecificationsInput
  }

  input UpdateProductInput {
    name: String
    price: Float
    description: String
    category: String
    brand: String
    imageUrls: [String!]
    specifications: ProductSpecificationsInput
  }

  input ProductSpecificationsInput {
    dimensions: String
    weight: Float
    color: String
    material: String
    warranty: String
    batteryLife: String
    screenSize: String
    storage: String
    size: String
    fabric: String
  }
`;

// Mock database - Production में proper database होगा
const products = [
  {
    id: '1',
    name: 'iPhone 15 Pro Max',
    price: 159900.0,
    description: 'Apple का flagship smartphone with titanium design',
    category: 'smartphones',
    brand: 'Apple',
    imageUrls: ['https://cdn.flipkart.com/iphone15pro.jpg'],
    specifications: {
      dimensions: '159.9 x 76.7 x 8.25 mm',
      weight: 221.0,
      color: 'Natural Titanium',
      screenSize: '6.7 inch',
      storage: '256GB',
      batteryLife: '29 hours video',
      warranty: '1 year'
    },
    availability: {
      inStock: true,
      stockCount: 45,
      estimatedDelivery: '2-3 days',
      lastUpdated: new Date().toISOString()
    },
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Samsung Galaxy S24 Ultra',
    price: 129999.0,
    description: 'Samsung का premium flagship with S Pen',
    category: 'smartphones',
    brand: 'Samsung',
    imageUrls: ['https://cdn.flipkart.com/galaxys24ultra.jpg'],
    specifications: {
      dimensions: '162.3 x 79.0 x 8.6 mm',
      weight: 232.0,
      color: 'Titanium Black',
      screenSize: '6.8 inch',
      storage: '512GB',
      batteryLife: '30+ hours',
      warranty: '1 year'
    },
    availability: {
      inStock: true,
      stockCount: 32,
      estimatedDelivery: '1-2 days',
      lastUpdated: new Date().toISOString()
    },
    createdAt: '2024-02-01T09:15:00Z',
    updatedAt: new Date().toISOString()
  },
  {
    id: '3',
    name: 'Nike Air Jordan 1',
    price: 12795.0,
    description: 'Classic basketball shoes, iconic design',
    category: 'footwear',
    brand: 'Nike',
    imageUrls: ['https://cdn.nike.com/airjordan1.jpg'],
    specifications: {
      color: 'Chicago Red/White',
      material: 'Leather',
      size: '42',
      warranty: '6 months'
    },
    availability: {
      inStock: false,
      stockCount: 0,
      estimatedDelivery: '7-10 days',
      lastUpdated: new Date().toISOString()
    },
    createdAt: '2024-01-20T14:22:00Z',
    updatedAt: new Date().toISOString()
  }
];

const categories = [
  { id: '1', name: 'Electronics', parentId: null, level: 1 },
  { id: '2', name: 'Smartphones', parentId: '1', level: 2 },
  { id: '3', name: 'Fashion', parentId: null, level: 1 },
  { id: '4', name: 'Footwear', parentId: '3', level: 2 }
];

// Utility functions
function encodeCursor(id) {
  return Buffer.from(id.toString()).toString('base64');
}

function decodeCursor(cursor) {
  return Buffer.from(cursor, 'base64').toString();
}

function paginate(items, limit, offset) {
  const edges = items.slice(offset, offset + limit).map(item => ({
    node: item,
    cursor: encodeCursor(item.id)
  }));

  return {
    edges,
    pageInfo: {
      hasNextPage: offset + limit < items.length,
      hasPreviousPage: offset > 0,
      startCursor: edges[0]?.cursor,
      endCursor: edges[edges.length - 1]?.cursor
    },
    totalCount: items.length
  };
}

// Resolvers
const resolvers = {
  Query: {
    // सारे products with pagination और filtering
    products: (parent, { limit, offset, category, brand, priceRange, searchTerm }) => {
      console.log('🔍 Products query:', { limit, offset, category, brand, priceRange, searchTerm });
      
      let filteredProducts = [...products];
      
      // Category filter
      if (category) {
        filteredProducts = filteredProducts.filter(p => p.category === category);
      }
      
      // Brand filter
      if (brand) {
        filteredProducts = filteredProducts.filter(p => p.brand === brand);
      }
      
      // Price range filter
      if (priceRange) {
        filteredProducts = filteredProducts.filter(p => 
          p.price >= priceRange.min && p.price <= priceRange.max
        );
      }
      
      // Search filter
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filteredProducts = filteredProducts.filter(p => 
          p.name.toLowerCase().includes(term) || 
          p.description.toLowerCase().includes(term) ||
          p.brand.toLowerCase().includes(term)
        );
      }
      
      return paginate(filteredProducts, limit, offset);
    },

    product: (parent, { id }) => {
      console.log(`🎯 Product query for ID: ${id}`);
      const product = products.find(p => p.id === id);
      
      if (!product) {
        throw new Error(`Product with ID ${id} not found`);
      }
      
      return product;
    },

    productsByCategory: (parent, { categoryId, limit }) => {
      console.log(`📱 Products by category: ${categoryId}`);
      const category = categories.find(c => c.id === categoryId);
      
      if (!category) {
        throw new Error(`Category with ID ${categoryId} not found`);
      }
      
      return products
        .filter(p => p.category === category.name.toLowerCase())
        .slice(0, limit);
    },

    searchProducts: (parent, { query, limit }) => {
      console.log(`🔎 Search products: ${query}`);
      const term = query.toLowerCase();
      
      return products
        .filter(p => 
          p.name.toLowerCase().includes(term) || 
          p.description.toLowerCase().includes(term) ||
          p.brand.toLowerCase().includes(term)
        )
        .slice(0, limit);
    },

    categories: () => {
      console.log('📂 Categories query');
      return categories;
    },

    featuredProducts: (parent, { limit }) => {
      console.log(`⭐ Featured products: ${limit}`);
      // Mock logic - highest priced या popular products
      return products
        .sort((a, b) => b.price - a.price)
        .slice(0, limit);
    }
  },

  Mutation: {
    createProduct: (parent, { input }, context) => {
      console.log('➕ Creating new product:', input);
      
      // Authorization check
      if (!context.user || !context.user.permissions?.includes('write:products')) {
        throw new Error('Unauthorized: Product creation requires admin privileges');
      }
      
      const newProduct = {
        id: String(products.length + 1),
        ...input,
        availability: {
          inStock: true,
          stockCount: 0,
          estimatedDelivery: '5-7 days',
          lastUpdated: new Date().toISOString()
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      products.push(newProduct);
      console.log('✅ Product created successfully:', newProduct.id);
      
      return newProduct;
    },

    updateProduct: (parent, { id, input }, context) => {
      console.log(`✏️ Updating product ${id}:`, input);
      
      // Authorization check
      if (!context.user || !context.user.permissions?.includes('write:products')) {
        throw new Error('Unauthorized: Product update requires admin privileges');
      }
      
      const productIndex = products.findIndex(p => p.id === id);
      if (productIndex === -1) {
        throw new Error(`Product with ID ${id} not found`);
      }
      
      products[productIndex] = {
        ...products[productIndex],
        ...input,
        updatedAt: new Date().toISOString()
      };
      
      console.log('✅ Product updated successfully');
      return products[productIndex];
    },

    deleteProduct: (parent, { id }, context) => {
      console.log(`🗑️ Deleting product: ${id}`);
      
      // Authorization check
      if (!context.user || !context.user.permissions?.includes('delete:products')) {
        throw new Error('Unauthorized: Product deletion requires admin privileges');
      }
      
      const productIndex = products.findIndex(p => p.id === id);
      if (productIndex === -1) {
        return false;
      }
      
      products.splice(productIndex, 1);
      console.log('✅ Product deleted successfully');
      
      return true;
    },

    updateStock: (parent, { productId, quantity }, context) => {
      console.log(`📦 Updating stock for product ${productId}: ${quantity}`);
      
      // Authorization check
      if (!context.user || !context.user.permissions?.includes('write:inventory')) {
        throw new Error('Unauthorized: Stock update requires inventory privileges');
      }
      
      const product = products.find(p => p.id === productId);
      if (!product) {
        throw new Error(`Product with ID ${productId} not found`);
      }
      
      product.availability = {
        ...product.availability,
        stockCount: Math.max(0, quantity),
        inStock: quantity > 0,
        lastUpdated: new Date().toISOString()
      };
      
      console.log('✅ Stock updated successfully');
      return product.availability;
    }
  },

  // Federation resolver - दूसरे services से Product reference resolve करने के लिए
  Product: {
    __resolveReference: (product) => {
      console.log(`🔗 Resolving Product reference: ${product.id}`);
      return products.find(p => p.id === product.id);
    }
  },

  Category: {
    __resolveReference: (category) => {
      console.log(`🔗 Resolving Category reference: ${category.id}`);
      return categories.find(c => c.id === category.id);
    }
  }
};

async function startProductsService() {
  try {
    const app = express();
    
    // Request logging
    app.use((req, res, next) => {
      console.log(`📞 Products Service - ${req.method} ${req.path}`);
      next();
    });

    // Build federated schema
    const schema = buildFederatedSchema([{ typeDefs, resolvers }]);
    
    const server = new ApolloServer({
      schema,
      context: ({ req }) => {
        // Gateway से forwarded headers को process करते हैं
        const authToken = req.headers.authorization || '';
        const requestId = req.headers['x-request-id'] || '';
        const userId = req.headers['x-user-id'] || '';
        
        // Mock user for demonstration
        const user = userId ? {
          id: userId,
          permissions: ['read:products', 'write:products', 'write:inventory']
        } : null;
        
        return {
          authToken,
          requestId,
          user,
          service: 'products'
        };
      },
      
      formatError: (error) => {
        console.error(`❌ Products Service Error:`, error.message);
        return error;
      },
      
      introspection: true,
      playground: process.env.NODE_ENV !== 'production'
    });

    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4001;
    
    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({
        service: 'products',
        status: 'healthy',
        timestamp: new Date().toISOString(),
        productsCount: products.length
      });
    });

    app.listen(PORT, () => {
      console.log(`🛒 Products Service ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log(`🏥 Health check at http://localhost:${PORT}/health`);
    });

  } catch (error) {
    console.error('❌ Products Service startup error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛒 Products Service shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🛒 Products Service shutting down...');
  process.exit(0);
});

// Start the service
startProductsService();

module.exports = { typeDefs, resolvers, products };