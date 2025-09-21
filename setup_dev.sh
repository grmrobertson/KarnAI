#!/usr/bin/env zsh

# Karn.ai Development Environment Setup
echo "🎯 Setting up Karn.ai development environment..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [[ ! -f .env ]]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Karn.ai Environment Configuration

# Development settings
DEBUG=True
LOG_LEVEL=INFO

# Scryfall API settings
SCRYFALL_API_BASE=https://api.scryfall.com
SCRYFALL_BULK_DATA_URL=https://api.scryfall.com/bulk-data/oracle-cards

# Data directories
DATA_DIR=./data
SCHEMAS_DIR=./schemas
TESTS_DIR=./tests

# Future database settings (Phase 2+)
# POSTGRES_URL=postgresql://localhost:5432/karnai
# MONGODB_URL=mongodb://localhost:27017/karnai
# REDIS_URL=redis://localhost:6379
EOF
    echo "✅ Created .env file with default settings"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "To activate the environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "  1. source venv/bin/activate"
echo "  2. Start working on the card-ir-generator service"
echo "  3. Download sample Scryfall data for testing"