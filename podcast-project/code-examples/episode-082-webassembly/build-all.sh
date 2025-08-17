#!/bin/bash

# Episode 082: WebAssembly Build Script
# Production-ready build process for Rust→WASM modules

set -e  # Exit on any error

echo "🚀 Episode 082: Building WebAssembly Modules"
echo "=============================================="

# Check if required tools are installed
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    if ! command -v rustc &> /dev/null; then
        echo "❌ Rust is not installed. Please install Rust:"
        echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        exit 1
    fi
    
    if ! command -v wasm-pack &> /dev/null; then
        echo "❌ wasm-pack is not installed. Installing..."
        cargo install wasm-pack
    fi
    
    # Add wasm32 target if not present
    rustup target add wasm32-unknown-unknown
    
    echo "✅ Prerequisites checked"
}

# Build crypto hash module
build_crypto_module() {
    echo ""
    echo "🔐 Building Crypto Hash Module..."
    echo "--------------------------------"
    
    cd 01_crypto_hash_module
    
    # Build for web target (optimized for Indian 3G networks)
    wasm-pack build --target web --out-dir pkg --release
    
    if [ $? -eq 0 ]; then
        echo "✅ Crypto Hash Module built successfully"
        
        # Show file sizes for performance analysis
        echo "📊 Module sizes:"
        ls -lh pkg/*.wasm | awk '{print "   " $9 ": " $5}'
        
        # Verify WASM module
        if command -v wasm-opt &> /dev/null; then
            echo "🔧 Optimizing WASM module..."
            wasm-opt -Os pkg/crypto_hash_wasm.wasm -o pkg/crypto_hash_wasm_optimized.wasm
            echo "   Original: $(ls -lh pkg/crypto_hash_wasm.wasm | awk '{print $5}')"
            echo "   Optimized: $(ls -lh pkg/crypto_hash_wasm_optimized.wasm | awk '{print $5}')"
        fi
    else
        echo "❌ Failed to build Crypto Hash Module"
        exit 1
    fi
    
    cd ..
}

# Build financial calculator module
build_financial_module() {
    echo ""
    echo "📊 Building Financial Calculator Module..."
    echo "----------------------------------------"
    
    cd 02_financial_calculator
    
    # Build for web target with maximum optimization
    wasm-pack build --target web --out-dir pkg --release
    
    if [ $? -eq 0 ]; then
        echo "✅ Financial Calculator Module built successfully"
        
        # Show file sizes
        echo "📊 Module sizes:"
        ls -lh pkg/*.wasm | awk '{print "   " $9 ": " $5}'
        
        # Optimize if wasm-opt is available
        if command -v wasm-opt &> /dev/null; then
            echo "🔧 Optimizing WASM module..."
            wasm-opt -Os pkg/financial_calculator_wasm.wasm -o pkg/financial_calculator_wasm_optimized.wasm
            echo "   Original: $(ls -lh pkg/financial_calculator_wasm.wasm | awk '{print $5}')"
            echo "   Optimized: $(ls -lh pkg/financial_calculator_wasm_optimized.wasm | awk '{print $5}')"
        fi
    else
        echo "❌ Failed to build Financial Calculator Module"
        exit 1
    fi
    
    cd ..
}

# Create integrated demo package
create_demo_package() {
    echo ""
    echo "📦 Creating Demo Package..."
    echo "-------------------------"
    
    # Create demo directory
    mkdir -p demo/wasm-modules
    
    # Copy WASM modules
    if [ -f "01_crypto_hash_module/pkg/crypto_hash_wasm.wasm" ]; then
        cp 01_crypto_hash_module/pkg/* demo/wasm-modules/
    fi
    
    if [ -f "02_financial_calculator/pkg/financial_calculator_wasm.wasm" ]; then
        cp 02_financial_calculator/pkg/* demo/wasm-modules/
    fi
    
    # Copy demo HTML
    cp demo.html demo/index.html
    
    # Create a simple HTTP server script
    cat > demo/serve.py << 'EOF'
#!/usr/bin/env python3
"""
Simple HTTP server for WebAssembly demo
Serves files with proper MIME types for WASM
"""

import http.server
import socketserver
import mimetypes
import os

# Add WASM MIME type
mimetypes.add_type('application/wasm', '.wasm')

class WAMSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        super().end_headers()

PORT = 8000
os.chdir(os.path.dirname(__file__))

with socketserver.TCPServer(("", PORT), WAMSHandler) as httpd:
    print(f"🌐 Serving WebAssembly demo at http://localhost:{PORT}")
    print("📱 Optimized for Indian network conditions")
    print("🔐 Razorpay-style crypto + Zerodha-style financial calculations")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
EOF
    
    chmod +x demo/serve.py
    
    echo "✅ Demo package created in demo/ directory"
}

# Performance analysis
performance_analysis() {
    echo ""
    echo "📈 Performance Analysis..."
    echo "------------------------"
    
    total_size=0
    
    if [ -f "01_crypto_hash_module/pkg/crypto_hash_wasm.wasm" ]; then
        crypto_size=$(stat -f%z "01_crypto_hash_module/pkg/crypto_hash_wasm.wasm" 2>/dev/null || stat -c%s "01_crypto_hash_module/pkg/crypto_hash_wasm.wasm")
        echo "🔐 Crypto Module: $(echo "scale=2; $crypto_size/1024" | bc)KB"
        total_size=$((total_size + crypto_size))
    fi
    
    if [ -f "02_financial_calculator/pkg/financial_calculator_wasm.wasm" ]; then
        financial_size=$(stat -f%z "02_financial_calculator/pkg/financial_calculator_wasm.wasm" 2>/dev/null || stat -c%s "02_financial_calculator/pkg/financial_calculator_wasm.wasm")
        echo "📊 Financial Module: $(echo "scale=2; $financial_size/1024" | bc)KB"
        total_size=$((total_size + financial_size))
    fi
    
    echo "📦 Total WASM Size: $(echo "scale=2; $total_size/1024" | bc)KB"
    
    # Network performance estimates for India
    echo ""
    echo "🌐 Indian Network Performance Estimates:"
    echo "   2G (Edge): $(echo "scale=1; $total_size*8/32000" | bc)s download time"
    echo "   3G: $(echo "scale=1; $total_size*8/384000" | bc)s download time"
    echo "   4G: $(echo "scale=1; $total_size*8/5000000" | bc)s download time"
    echo "   Fiber: $(echo "scale=2; $total_size*8/50000000" | bc)s download time"
}

# Generate production deployment guide
generate_deployment_guide() {
    echo ""
    echo "📚 Generating Deployment Guide..."
    echo "-------------------------------"
    
    cat > DEPLOYMENT.md << 'EOF'
# Episode 082: WebAssembly Deployment Guide

## Production Deployment for Indian FinTech

### CDN Configuration

For optimal performance in India, deploy WASM modules to:

1. **AWS CloudFront** with India edge locations
2. **Cloudflare** with Mumbai data centers
3. **Google Cloud CDN** with Asia-South1 region

### MIME Type Configuration

Ensure your web server serves WASM files with correct MIME types:

#### Nginx Configuration
```nginx
location ~* \.wasm$ {
    add_header Cross-Origin-Embedder-Policy require-corp;
    add_header Cross-Origin-Opener-Policy same-origin;
    add_header Content-Type application/wasm;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### Apache Configuration
```apache
<Files "*.wasm">
    Header set Cross-Origin-Embedder-Policy "require-corp"
    Header set Cross-Origin-Opener-Policy "same-origin"
    Header set Content-Type "application/wasm"
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
</Files>
```

### Progressive Loading Strategy

For Indian networks (often slower 3G):

```javascript
// Progressive WASM loading
async function loadWasmModule() {
    try {
        // Try to load optimized version first
        const wasmModule = await import('./wasm-modules/crypto_hash_wasm_optimized.js');
        return wasmModule;
    } catch {
        // Fallback to regular version
        const wasmModule = await import('./wasm-modules/crypto_hash_wasm.js');
        return wasmModule;
    }
}
```

### Performance Monitoring

Track these metrics for Indian users:

- **Load Time**: Target <500ms on 3G
- **Memory Usage**: <10MB total
- **Execution Speed**: >1000 ops/second
- **Error Rate**: <0.1%

### Security Considerations

For financial applications:

1. **Content Security Policy**:
```http
Content-Security-Policy: script-src 'self' 'wasm-unsafe-eval'
```

2. **WASM Module Integrity**:
```html
<script type="module" integrity="sha384-..." src="./crypto_hash_wasm.js"></script>
```

3. **Input Validation**: Always validate inputs before WASM calls

### Indian Compliance

- **RBI Guidelines**: Ensure cryptographic implementations meet RBI standards
- **Data Localization**: Store sensitive computation results in Indian data centers
- **NPCI Compliance**: UPI-related calculations must follow NPCI guidelines

### Monitoring and Alerting

Set up monitoring for:

- **Regional Performance**: Track metrics by Indian states
- **Network Type**: Monitor 2G/3G/4G performance separately
- **Error Patterns**: Watch for network-related failures
- **User Experience**: Track time-to-interactive metrics

### Scaling Strategy

For Indian user base:

1. **Regional Deployment**: Mumbai, Bangalore, Delhi data centers
2. **Edge Caching**: Cache WASM modules at ISP level
3. **Mobile Optimization**: Prioritize mobile network performance
4. **Offline Support**: Consider service worker caching

### Testing Strategy

Test on representative Indian devices:

- **Low-end Android**: 2GB RAM, slow CPUs
- **Feature Phones**: KaiOS with limited memory
- **Network Conditions**: Simulate 2G/3G variations
- **Regional Testing**: Test from different Indian cities

EOF

    echo "✅ Deployment guide created: DEPLOYMENT.md"
}

# Main build process
main() {
    echo "🇮🇳 Building for Indian FinTech Scale"
    echo "Production-ready Rust→WASM modules"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Build modules
    build_crypto_module
    build_financial_module
    
    # Create demo package
    create_demo_package
    
    # Performance analysis
    performance_analysis
    
    # Generate deployment guide
    generate_deployment_guide
    
    echo ""
    echo "🎉 Build Complete!"
    echo "================="
    echo ""
    echo "📦 Built modules:"
    echo "   🔐 Crypto Hash Module (Razorpay-style)"
    echo "   📊 Financial Calculator (Zerodha-style)"
    echo ""
    echo "🚀 To run demo:"
    echo "   cd demo && python3 serve.py"
    echo "   Open http://localhost:8000"
    echo ""
    echo "📚 See DEPLOYMENT.md for production deployment"
    echo ""
    echo "✅ Ready for Indian FinTech production deployment!"
    echo "🇮🇳 Jai Hind! WebAssembly modules built successfully!"
}

# Run main function
main "$@"