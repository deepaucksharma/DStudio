#!/bin/bash

# Rust to WASM build script
# WASM module बनाने के लिए complete setup

echo "🦀 Building Rust to WebAssembly for Indian tech companies..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "Installing wasm-pack..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Build for web target (Flipkart, Paytm के web applications के लिए)
echo "Building for web target..."
wasm-pack build --target web --out-dir pkg-web --dev

# Build for Node.js target (server-side processing के लिए)
echo "Building for Node.js target..."  
wasm-pack build --target nodejs --out-dir pkg-node --dev

# Build optimized release version
echo "Building optimized release version..."
wasm-pack build --target web --out-dir pkg-release --release

# Generate TypeScript definitions
echo "Generating TypeScript definitions..."
wasm-pack build --target bundler --out-dir pkg-bundler --release

# Copy to examples directory
mkdir -p ../examples
cp -r pkg-web ../examples/
cp -r pkg-node ../examples/

echo "✅ WASM modules built successfully!"
echo "📁 Web module: pkg-web/"
echo "📁 Node.js module: pkg-node/" 
echo "📁 Release module: pkg-release/"
echo "📁 Bundler module: pkg-bundler/"

echo ""
echo "🧪 To test the modules:"
echo "  cd ../examples && python -m http.server 8000"
echo "  Open http://localhost:8000 in browser"

echo ""
echo "💡 Usage examples:"
echo "  Web: import init, { PaymentProcessor } from './pkg-web/wasm_examples.js'"
echo "  Node: const wasm = require('./pkg-node/wasm_examples.js')"