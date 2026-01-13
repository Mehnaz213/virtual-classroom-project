# Focus Mate - Quick Reference Card

## 🚀 Start Commands

```powershell
# Backend
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev
```

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Teacher | demo.teacher@focusmate.com | teacher123 |
| Student 1-5 | demo.student1@focusmate.com | student123 |
| Teacher | teacher@example.com | teach123 |
| Student | student1@example.com | study123 |

**Demo Session Code:** DEMO01

## 🌐 URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Extension: chrome://extensions/

## 🎯 Attention Labels

1. focused
2. looking_left
3. looking_right
4. looking_up
5. looking_down
6. engaged
7. partial_engaged
8. sleepy
9. distracted_by_multi_face
10. no_face
11. unknown

## 🔧 Useful Commands

```powershell
# Verify installation
python scripts\verify_installation.py

# Generate test data
cd backend
.\.venv\Scripts\python.exe ..\scripts\generate_test_data.py

# Reset database
Remove-Item backend\classroom.db
cd backend
.\.venv\Scripts\python.exe -c "from app.db.session import SessionLocal; from app.db.base_class import Base; from app.db import init_db; db = SessionLocal(); Base.metadata.create_all(bind=db.get_bind()); init_db.init_db(db); db.close()"

# Run tests
cd backend
pytest

cd frontend
npm run test
```

## 📚 Documentation

- GET_STARTED.md - Quick start
- docs/QUICKSTART.md - Detailed setup
- docs/FEATURES.md - Feature list
- docs/TESTING.md - Testing guide
- extension/README.md - Extension setup
- ml/README.md - ML training

## 🐛 Quick Fixes

**Backend won't start:**
```powershell
cd backend
.\.venv\Scripts\pip.exe install -r requirements.txt
```

**Frontend won't start:**
```powershell
cd frontend
npm install
```

**Extension not working:**
- Check all config fields filled
- Verify JWT token valid
- Reload extension

## 📊 Status Check

96% Complete ✅
- Backend: ✅
- Frontend: ✅
- Extension: ✅
- Database: ✅
- Test Data: ✅
- Documentation: ✅
- ML (Optional): ⚠️

## 🎓 Quick Test

1. Start backend & frontend
2. Login as demo.teacher@focusmate.com
3. View dashboard with demo data
4. Open incognito → login as demo.student1@focusmate.com
5. Join session DEMO01
6. Configure extension
7. Test features

## 💡 Pro Tips

- Use demo data to learn the system
- Heuristic fallback works without ML
- Test lock mode before production use
- Monitor violations regularly
- Export reports for compliance

---

**Focus Mate v2.0.0** - Ready to use! 🚀
