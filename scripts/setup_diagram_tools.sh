#!/bin/bash
# Setup script for Agent 3 diagram rendering tools
# This script helps install the required dependencies

echo "🛠️ Agent 3: Diagram Rendering Tool Setup"
echo "========================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "📍 Detected OS: $OS"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Node.js and npm
echo "1️⃣ Checking Node.js and npm..."
if command_exists node && command_exists npm; then
    echo "✅ Node.js $(node --version) and npm $(npm --version) are installed"
else
    echo "❌ Node.js and npm are required but not found"
    echo "   Please install from: https://nodejs.org/"
    exit 1
fi
echo ""

# Install Mermaid CLI
echo "2️⃣ Installing Mermaid CLI..."
if command_exists mmdc; then
    echo "✅ Mermaid CLI is already installed ($(mmdc --version))"
else
    echo "📦 Installing @mermaid-js/mermaid-cli..."
    npm install -g @mermaid-js/mermaid-cli
    if [ $? -eq 0 ]; then
        echo "✅ Mermaid CLI installed successfully"
    else
        echo "❌ Failed to install Mermaid CLI"
        echo "   Try: sudo npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi
fi
echo ""

# Install ImageMagick
echo "3️⃣ Installing ImageMagick..."
if command_exists convert; then
    echo "✅ ImageMagick is already installed"
else
    if [ "$OS" == "linux" ]; then
        echo "📦 Installing ImageMagick via apt..."
        sudo apt-get update && sudo apt-get install -y imagemagick
    elif [ "$OS" == "macos" ]; then
        echo "📦 Installing ImageMagick via Homebrew..."
        brew install imagemagick
    fi
    
    if command_exists convert; then
        echo "✅ ImageMagick installed successfully"
    else
        echo "❌ Failed to install ImageMagick"
        exit 1
    fi
fi
echo ""

# Install WebP tools
echo "4️⃣ Installing WebP tools..."
if command_exists cwebp; then
    echo "✅ WebP tools are already installed"
else
    if [ "$OS" == "linux" ]; then
        echo "📦 Installing WebP tools via apt..."
        sudo apt-get install -y webp
    elif [ "$OS" == "macos" ]; then
        echo "📦 Installing WebP tools via Homebrew..."
        brew install webp
    fi
    
    if command_exists cwebp; then
        echo "✅ WebP tools installed successfully"
    else
        echo "❌ Failed to install WebP tools"
        exit 1
    fi
fi
echo ""

# Verify all tools
echo "5️⃣ Verifying installation..."
echo ""

all_good=true

if command_exists mmdc; then
    echo "✅ mmdc (Mermaid CLI): $(mmdc --version 2>&1 | head -n1)"
else
    echo "❌ mmdc (Mermaid CLI): Not found"
    all_good=false
fi

if command_exists convert; then
    echo "✅ convert (ImageMagick): $(convert --version | head -n1)"
else
    echo "❌ convert (ImageMagick): Not found"
    all_good=false
fi

if command_exists cwebp; then
    echo "✅ cwebp (WebP): $(cwebp -version 2>&1 | head -n1)"
else
    echo "❌ cwebp (WebP): Not found"
    all_good=false
fi

echo ""

if [ "$all_good" = true ]; then
    echo "🎉 All tools are installed and ready!"
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 scripts/extract_mermaid_diagrams.py"
    echo "2. Run: python3 scripts/render_mermaid_diagrams.py"
    echo "3. Run: python3 scripts/replace_mermaid_blocks.py"
else
    echo "⚠️  Some tools are missing. Please install them manually."
fi