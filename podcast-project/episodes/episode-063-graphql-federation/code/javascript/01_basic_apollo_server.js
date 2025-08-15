// 01_basic_apollo_server.js
// बेसिक Apollo GraphQL Server setup - यहाँ से शुरू करते हैं
// यह हमारा foundation है GraphQL federation के लिए

const { ApolloServer, gql } = require('apollo-server-express');
const express = require('express');

// Type definitions - यह बताता है कि हमारा schema कैसा दिखेगा
const typeDefs = gql`
  type Product {
    id: ID!
    name: String!
    price: Float!
    description: String
    category: String!
  }

  type Query {
    # सारे products की list देता है
    products: [Product!]!
    # किसी specific product को ID से ढूंढता है
    product(id: ID!): Product
    # Category के हिसाब से products filter करता है
    productsByCategory(category: String!): [Product!]!
  }

  type Mutation {
    # नया product add करने के लिए
    addProduct(name: String!, price: Float!, description: String, category: String!): Product!
  }
`;

// Mock data - Real application में यह database से आएगा
const products = [
  {
    id: '1',
    name: 'iPhone 15 Pro',
    price: 134900.0,
    description: 'Apple का latest flagship phone',
    category: 'Electronics'
  },
  {
    id: '2', 
    name: 'Samsung Galaxy S24',
    price: 74999.0,
    description: 'Samsung का premium Android phone',
    category: 'Electronics'
  },
  {
    id: '3',
    name: 'Levi\'s Jeans',
    price: 2999.0,
    description: 'Classic denim jeans',
    category: 'Fashion'
  }
];

// Resolvers - यहाँ actual business logic होता है
const resolvers = {
  Query: {
    // सारे products return करता है
    products: () => {
      console.log('Fetching सारे products...');
      return products;
    },
    
    // ID से specific product find करता है
    product: (parent, { id }) => {
      console.log(`Searching for product with ID: ${id}`);
      const product = products.find(p => p.id === id);
      if (!product) {
        throw new Error(`Product with ID ${id} नहीं मिला`);
      }
      return product;
    },
    
    // Category के हिसाब से filter करता है
    productsByCategory: (parent, { category }) => {
      console.log(`Filtering products by category: ${category}`);
      return products.filter(p => p.category === category);
    }
  },
  
  Mutation: {
    // नया product add करता है
    addProduct: (parent, { name, price, description, category }) => {
      console.log(`Adding new product: ${name}`);
      
      const newProduct = {
        id: String(products.length + 1),
        name,
        price,
        description,
        category
      };
      
      products.push(newProduct);
      console.log('Product successfully add हुआ:', newProduct);
      
      return newProduct;
    }
  }
};

async function startServer() {
  try {
    // Express app create करते हैं
    const app = express();
    
    // Apollo Server initialize करते हैं
    const server = new ApolloServer({
      typeDefs,
      resolvers,
      // Development में introspection और playground enable करते हैं
      introspection: process.env.NODE_ENV !== 'production',
      playground: process.env.NODE_ENV !== 'production',
      // Context function - यहाँ authentication, database connections etc. आते हैं
      context: ({ req }) => {
        // Request headers से user info निकाल सकते हैं
        const authToken = req.headers.authorization || '';
        console.log('Request received with auth token:', authToken ? 'Present' : 'Missing');
        
        return {
          authToken,
          // यहाँ database connections, user info etc. pass कर सकते हैं
        };
      },
      // Error handling
      formatError: (error) => {
        console.error('GraphQL Error:', error);
        return {
          message: error.message,
          // Production में stack trace hide करना चाहिए
          ...(process.env.NODE_ENV !== 'production' && { stack: error.stack })
        };
      }
    });

    // Apollo Server को Express के साथ integrate करते हैं
    server.applyMiddleware({ app, path: '/graphql' });
    
    const PORT = process.env.PORT || 4000;
    
    // Server start करते हैं
    app.listen(PORT, () => {
      console.log(`🚀 Apollo Server ready at http://localhost:${PORT}${server.graphqlPath}`);
      console.log('📊 GraphQL Playground available in development mode');
      
      // Health check endpoint
      app.get('/health', (req, res) => {
        res.status(200).json({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          uptime: process.uptime()
        });
      });
      
      console.log(`🏥 Health check available at http://localhost:${PORT}/health`);
    });
    
  } catch (error) {
    console.error('Server start करने में error आया:', error);
    process.exit(1);
  }
}

// Graceful shutdown handling
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});

// Server start करते हैं
startServer();

module.exports = { typeDefs, resolvers };