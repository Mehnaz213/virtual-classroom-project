# Focus Mate - Setup Script (PowerShell)
# Automates initial setup for development environment on Windows

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Blue
Write-Host "Focus Mate - Setup Script" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.11 or higher from python.org"
    exit 1
}

# Check Node version
Write-Host "Checking Node.js version..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 18 or higher from nodejs.org"
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "Setting up Backend" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

Set-Location backend

# Create virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment already exists" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Cyan
if (-not (Test-Path "classroom.db")) {
    python -c "from app.db.session import SessionLocal; from app.db.base_class import Base; from app.db import init_db; db = SessionLocal(); Base.metadata.create_all(bind=db.get_bind()); init_db.init_db(db); db.close()"
    Write-Host "✓ Database initialized" -ForegroundColor Green
} else {
    Write-Host "⚠ Database already exists" -ForegroundColor Yellow
    Write-Host "Run migration: sqlite3 classroom.db < ..\scripts\migrations\002_lock_mode_and_enhanced_attention.sql"
}

Set-Location ..

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "Setting up Frontend" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""

Set-Location frontend

# Install dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
    npm install
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ node_modules already exists" -ForegroundColor Yellow
    Write-Host "Run 'npm install' to update dependencies"
}

Set-Location ..

Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "Setup Complete!" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue
Write-Host ""
Write-Host "✓ Backend setup complete" -ForegroundColor Green
Write-Host "✓ Frontend setup complete" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start backend:" -ForegroundColor White
Write-Host "   cd backend"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   uvicorn app.main:app --reload"
Write-Host ""
Write-Host "2. Start frontend (new terminal):" -ForegroundColor White
Write-Host "   cd frontend"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. Load Chrome extension:" -ForegroundColor White
Write-Host "   - Open chrome://extensions/"
Write-Host "   - Enable Developer mode"
Write-Host "   - Click 'Load unpacked'"
Write-Host "   - Select the 'extension' folder"
Write-Host ""
Write-Host "4. Optional: Generate test data:" -ForegroundColor White
Write-Host "   cd backend"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python ..\scripts\generate_test_data.py"
Write-Host ""
Write-Host "5. Access the application:" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:5173"
Write-Host "   - Backend API: http://localhost:8000"
Write-Host "   - API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Demo credentials:" -ForegroundColor Yellow
Write-Host "  Teacher: teacher@example.com / teach123"
Write-Host "  Student: student1@example.com / study123"
Write-Host ""
Write-Host "For more information, see docs\QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
