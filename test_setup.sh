#!/bin/bash
# Gate Alert - Setup Verification Script

echo "🚂 Gate Alert - Setup Verification"
echo "===================================="
echo ""

# Check Node.js
echo "✓ Checking Node.js..."
if command -v node &> /dev/null; then
    echo "  Node.js version: $(node --version)"
else
    echo "  ❌ Node.js not found!"
    exit 1
fi

# Check npm
echo "✓ Checking npm..."
if command -v npm &> /dev/null; then
    echo "  npm version: $(npm --version)"
else
    echo "  ❌ npm not found!"
    exit 1
fi

# Check Python
echo "✓ Checking Python..."
if command -v python3 &> /dev/null; then
    echo "  Python version: $(python3 --version)"
else
    echo "  ❌ Python not found!"
    exit 1
fi

# Check if node_modules exists
echo "✓ Checking Node.js dependencies..."
if [ -d "node_modules" ]; then
    echo "  Dependencies installed ✓"
else
    echo "  ⚠️  Dependencies not installed. Run: npm install"
fi

# Check Python dependencies
echo "✓ Checking Python dependencies..."
python3 -c "import requests, websockets" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  Python dependencies installed ✓"
else
    echo "  ⚠️  Python dependencies not installed. Run: pip install -r requirements.txt"
fi

# Test Python processor import
echo "✓ Testing Python processor..."
python3 -c "import train_processor; print('  Python processor imports successfully ✓')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ❌ Python processor has errors!"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ All checks passed!"
echo ""
echo "To start the application:"
echo "  1. Run: npm start"
echo "  2. Open: http://localhost:3000"
echo ""
echo "Optional - To run Python data processor:"
echo "  python3 train_processor.py"
