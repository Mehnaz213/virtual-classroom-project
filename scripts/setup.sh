#!/bin/bash
# Focus Mate - Setup Script
# Automates initial setup for development environment

set -e

echo "============================================================"
echo "Focus Mate - Setup Script"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

echo ""
echo "============================================================"
echo "Setting up Backend"
echo "============================================================"
echo ""

cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate || . .venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Initialize database
echo "Initializing database..."
if [ ! -f "classroom.db" ]; then
    python -c "from app.db.session import SessionLocal; from app.db.base_class import Base; from app.db import init_db; db = SessionLocal(); Base.metadata.create_all(bind=db.get_bind()); init_db.init_db(db); db.close()"
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠ Database already exists${NC}"
    echo "Run migration: sqlite3 classroom.db < ../scripts/migrations/002_lock_mode_and_enhanced_attention.sql"
fi

cd ..

echo ""
echo "============================================================"
echo "Setting up Frontend"
echo "============================================================"
echo ""

cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ node_modules already exists${NC}"
    echo "Run 'npm install' to update dependencies"
fi

cd ..

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo -e "${GREEN}✓ Backend setup complete${NC}"
echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Start backend:"
echo "   cd backend"
echo "   source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Start frontend (new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Load Chrome extension:"
echo "   - Open chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Click 'Load unpacked'"
echo "   - Select the 'extension' folder"
echo ""
echo "4. Optional: Generate test data:"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   python ../scripts/generate_test_data.py"
echo ""
echo "5. Access the application:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Demo credentials:"
echo "  Teacher: teacher@example.com / teach123"
echo "  Student: student1@example.com / study123"
echo ""
echo "For more information, see docs/QUICKSTART.md"
echo ""
