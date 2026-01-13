# 🚀 Get Started with Focus Mate

Welcome to **Focus Mate** - an AI-powered virtual classroom with advanced attention detection and lock mode enforcement!

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

**Windows:**
```powershell
.\scripts\setup.ps1
```

**Mac/Linux:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup** (new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Extension Setup**
   - Open Chrome → `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension/` folder

## 🎯 What You Get

### For Teachers
- ✅ Monitor 11 attention states in real-time
- ✅ Enable/disable lock mode remotely
- ✅ Track tab switches and violations
- ✅ Detect sleepy students automatically
- ✅ Export detailed reports (CSV/PDF)
- ✅ Real-time dashboard with WebSocket updates

### For Students
- ✅ Automatic attention detection via webcam
- ✅ Lock mode enforcement (when enabled)
- ✅ Tab switch monitoring
- ✅ Privacy-focused (low-res frames)
- ✅ Calibration for better accuracy

### For Developers
- ✅ Modern tech stack (FastAPI, React, TensorFlow.js)
- ✅ Comprehensive documentation
- ✅ Docker support
- ✅ Test data generators
- ✅ CI/CD ready

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](docs/QUICKSTART.md)** | Detailed 10-minute setup guide |
| **[FEATURES.md](docs/FEATURES.md)** | Complete feature documentation |
| **[TESTING.md](docs/TESTING.md)** | Testing guide and scenarios |
| **[UPGRADE_SUMMARY.md](docs/UPGRADE_SUMMARY.md)** | What's new in v2.0 |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history |

### Component-Specific Docs
- **Backend**: See `backend/app/` for API code
- **Frontend**: See `frontend/src/` for React components
- **Extension**: See `extension/README.md` for setup
- **ML Pipeline**: See `ml/README.md` for training

## 🧪 Test It Out

### Generate Demo Data

```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python ../scripts/generate_test_data.py
```

This creates:
- 1 teacher account
- 5 student accounts
- 1 active session
- 100 engagement events (all 11 attention labels)
- 30 tab switch events (with lock violations)

### Demo Credentials

**Teacher:**
- Email: `demo.teacher@focusmate.com`
- Password: `teacher123`

**Students:**
- Email: `demo.student1@focusmate.com` (through `demo.student5@focusmate.com`)
- Password: `student123`

**Session Code:** `DEMO01`

## 🎓 Learning Path

### 1. Basic Usage (15 minutes)
1. Start backend and frontend
2. Login as teacher
3. Create a session
4. Login as student (incognito window)
5. Join the session
6. Observe dashboard updates

### 2. Extension Setup (10 minutes)
1. Load extension in Chrome
2. Get JWT token from DevTools
3. Configure extension
4. Test tab switching
5. View alerts in dashboard

### 3. Lock Mode (10 minutes)
1. Enable lock mode in dashboard
2. Try switching tabs as student
3. Observe warning overlays
4. Check violation counts
5. Disable lock mode

### 4. ML Training (30 minutes)
1. Generate synthetic data
2. Train model
3. Export to TF.js
4. Test browser inference
5. Compare with heuristics

## 🔧 Verify Installation

```bash
python scripts/verify_installation.py
```

Expected: 96%+ checks pass (TensorFlow/OpenCV optional)

## 🌐 Access Points

Once running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Extension** | chrome://extensions/ | Chrome extension management |

## 🐛 Troubleshooting

### Backend won't start
```bash
pip install --upgrade -r backend/requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Extension not working
1. Check all config fields filled
2. Verify JWT token valid
3. Check API URL correct
4. Reload extension

### Database issues
```bash
# Reset database
rm backend/classroom.db
cd backend
python -c "from app.db.session import SessionLocal; from app.db.base_class import Base; from app.db import init_db; db = SessionLocal(); Base.metadata.create_all(bind=db.get_bind()); init_db.init_db(db); db.close()"
```

## 📊 Project Structure

```
focus-mate/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── extension/        # Chrome extension
├── ml/              # ML training pipeline
├── docs/            # Documentation
├── scripts/         # Setup and utility scripts
└── Postman/         # API test collection
```

## 🚢 Deployment

### Development
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`
- Extension: Load unpacked

### Production
- Backend: Fly.io, Render, AWS ECS
- Frontend: Netlify, Vercel, S3+CloudFront
- Database: PostgreSQL (RDS, Cloud SQL)
- See `README.md` for detailed deployment guide

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📞 Support

- **Documentation**: Check `docs/` folder
- **Issues**: Review error messages and logs
- **Testing**: See `docs/TESTING.md`
- **Setup**: See `docs/QUICKSTART.md`

## 🎉 What's New in v2.0

- ✅ **11 attention states** (vs 3 in v1.0)
- ✅ **Lock mode enforcement** with violation tracking
- ✅ **Enhanced Chrome extension** with retry logic
- ✅ **MobileNetV3 model** (<10MB, browser-ready)
- ✅ **Comprehensive documentation** (6 new guides)
- ✅ **Test data generators** for easy testing
- ✅ **Setup automation** scripts
- ✅ **Migration scripts** for database updates

See `CHANGELOG.md` for complete details.

## 📄 License

See LICENSE file in repository root.

---

**Focus Mate** - AI-Powered Virtual Classroom  
Version 2.0.0 - November 2025

Ready to get started? Run the setup script and you'll be up in 5 minutes! 🚀
