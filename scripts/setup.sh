#!/bin/bash

# Destin MCP Server Setup Script (New Structure)
# This script sets up the MCP server for production use

set -e

echo "🚀 Setting up Destin MCP Server (Professional Structure)..."
echo "============================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Make scripts executable
chmod +x main.py
chmod +x tests/test_server.py
chmod +x scripts/setup.sh

# Test the server
echo "🧪 Testing server functionality..."
python tests/test_server.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📁 Project Structure:"
    echo "├── src/destin_mcp/          # Main package"
    echo "│   ├── tools/               # MCP tools"
    echo "│   ├── resources/           # MCP resources"
    echo "│   ├── prompts/             # MCP prompts"
    echo "│   ├── models/              # Data models"
    echo "│   ├── utils/               # Utilities"
    echo "│   └── config/              # Configuration"
    echo "├── tests/                   # Test suite"
    echo "├── scripts/                 # Setup scripts"
    echo "└── docs/                    # Documentation"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Install MCP Inspector (optional):"
    echo "   npm install -g @modelcontextprotocol/inspector"
    echo ""
    echo "2. Test with MCP Inspector:"
    echo "   source venv/bin/activate"
    echo "   mcp-inspector python main.py"
    echo ""
    echo "3. Configure Claude Desktop:"
    echo "   Update claude_config.json with main.py path"
    echo ""
    echo "4. Start using the server:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo ""
    echo "🔗 API Base URL: https://supplier-apis-for-travel-tech.vercel.app"
    echo "🏢 Default Supplier: dida"
    echo ""
    echo "🆕 New Features:"
    echo "✅ Modular architecture with tools/resources/prompts"
    echo "✅ Professional project structure"
    echo "✅ Configuration management"
    echo "✅ Comprehensive documentation resources"
    echo "✅ AI-powered prompt templates"
    echo "✅ Type-safe models and validation"
    echo ""
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
