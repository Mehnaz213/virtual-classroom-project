# Focus Mate - Testing Guide

Comprehensive testing guide for Focus Mate features.

## Quick Test

Run the verification script:
```bash
python scripts/verify_installation.py
```

## Backend Testing

### Unit Tests

```bash
cd backend
pytest --maxfail=1 --disable-warnings --cov=app
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### API Testing

#### Using Postman

1. Import collection: `Postman/virtual-classroom.postman_collection.json`
2. Set environment variables:
   - `baseUrl`: `http://localhost:8000`
   - `token`: (obtained from login)
3. Run collection tests

#### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@example.com","password":"teach123"}'

# Create session
curl -X POST http://localhost:8000/api/class/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test Session"}'

# Get dashboard
curl http://localhost:8000/api/class/1/dashboard \
  -H "Authorization: Bearer <token>"
```

## Frontend Testing

### Unit Tests

```bash
cd frontend
npm run test
```

### Linting

```bash
npm run lint
```

### Build Test

```bash
npm run build
npm run preview
```

### Component Testing

Test individual components:

```bash
npm run test -- VideoProcessor.test.ts
```

## Extension Testing

### Manual Testing

1. **Load Extension**
   - Go to `chrome://extensions/`
   - Enable Developer mode
   - Click "Load unpacked"
   - Select `extension/` folder

2. **Test Configuration**
   - Click extension icon
   - Fill in all fields:
     - API Base: `http://localhost:8000/api`
     - JWT Token: (from DevTools → Local Storage)
     - Session ID: `1`
     - Attendance ID: (from teacher dashboard)
   - Click "Save Configuration"
   - Verify status shows "Configured and active"

3. **Test Tab Switching**
   - Switch to another tab
   - Badge counter should increment
   - Check backend logs for received event
   - Verify event appears in teacher dashboard

4. **Test Lock Mode**
   - Enable lock mode in popup
   - Try switching tabs → should be blocked
   - Try Ctrl+T → should be blocked
   - Warning overlay should appear
   - Violation count should increment

5. **Test Retry Logic**
   - Stop backend server
   - Switch tabs (events queued)
   - Start backend server
   - Verify queued events are sent

### Extension Logs

**Background Worker:**
1. Go to `chrome://extensions/`
2. Find Focus Mate Extension
3. Click "service worker" link
4. Console shows background.js logs

**Content Script:**
1. Open any page
2. Open DevTools (F12)
3. Console shows content.js logs

## ML Pipeline Testing

### Synthetic Data Generation

```bash
cd ml
python data_ingest.py ingest synthetic_demo --limit 100
```

Verify:
- `data/processed/synthetic_demo/metadata.jsonl` created
- `data/processed/synthetic_demo/frames/` contains images
- All 11 attention labels represented

### Model Training

```bash
python train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --epochs 1 \
  --batch-size 16
```

Verify:
- Training completes without errors
- Model saved to `artifacts/focusmate_model/saved_model/`
- Checkpoints created
- TensorBoard logs available

### Model Export

```bash
python export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out test_export \
  --format tfjs
```

Verify:
- `test_export/tfjs/model.json` created
- `test_export/tfjs/*.bin` files created
- Model size < 15MB

### Model Evaluation

```bash
python eval.py \
  --model artifacts/focusmate_model/saved_model \
  --data data/processed/synthetic_demo/metadata.jsonl
```

Verify:
- Metrics printed (accuracy, MAE, etc.)
- Per-label precision/recall shown

## Integration Testing

### End-to-End Test Scenario

**Setup:**
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Load extension in Chrome
4. Generate test data: `python scripts/generate_test_data.py`

**Test Flow:**

1. **Teacher Login**
   - Go to `http://localhost:5173`
   - Login as `demo.teacher@focusmate.com` / `teacher123`
   - Verify dashboard loads

2. **Create Session**
   - Enter topic: "Integration Test"
   - Click "Create & Go Live"
   - Note session code

3. **Student Join (Incognito Window)**
   - Open incognito window
   - Go to `http://localhost:5173`
   - Login as `demo.student1@focusmate.com` / `student123`
   - Enter session code
   - Click "Join Session"
   - Allow webcam access

4. **Configure Extension**
   - Open DevTools → Application → Local Storage
   - Copy `vc_token`
   - Click extension icon
   - Fill configuration
   - Save

5. **Test Attention Detection**
   - Student: Look at different directions
   - Teacher: Verify labels update in dashboard
   - Check timeline chart updates
   - Verify label breakdown statistics

6. **Test Tab Switching**
   - Student: Switch to another tab
   - Extension badge increments
   - Teacher sees tab switch alert
   - Timeline shows tab switch event

7. **Test Lock Mode**
   - Teacher: Enable lock mode
   - Student: Try switching tabs
   - Warning overlay appears
   - Violation counted
   - Teacher sees lock violation alert

8. **Test WebSocket Updates**
   - Keep teacher dashboard open
   - Student performs actions
   - Dashboard updates in real-time
   - No page refresh needed

9. **Test Report Export**
   - Teacher: Click "Export Report"
   - Select CSV format
   - Verify download
   - Open CSV and verify data

## Performance Testing

### Backend Load Test

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class FocusMateUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        response = self.client.post("/api/auth/login/json", json={
            "email": "teacher@example.com",
            "password": "teach123"
        })
        self.token = response.json()["access_token"]
    
    @task
    def get_dashboard(self):
        self.client.get("/api/class/1/dashboard", headers={
            "Authorization": f"Bearer {self.token}"
        })
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

Open `http://localhost:8089` and configure:
- Number of users: 10
- Spawn rate: 1
- Run test and monitor performance

### Frontend Performance

```bash
cd frontend
npm run build
npm run preview

# Use Chrome DevTools:
# 1. Open http://localhost:4173
# 2. Open DevTools → Lighthouse
# 3. Run performance audit
# 4. Verify scores > 80
```

### Model Inference Performance

```javascript
// In browser console
const start = performance.now();
// Trigger inference
const end = performance.now();
console.log(`Inference time: ${end - start}ms`);
// Should be < 100ms
```

## Database Testing

### Migration Test

```bash
# Backup database
cp backend/classroom.db backend/classroom.db.backup

# Run migration
sqlite3 backend/classroom.db < scripts/migrations/002_lock_mode_and_enhanced_attention.sql

# Verify schema
sqlite3 backend/classroom.db ".schema attendance"
sqlite3 backend/classroom.db ".schema tab_switch_events"

# Restore if needed
cp backend/classroom.db.backup backend/classroom.db
```

### Data Integrity Test

```bash
cd backend
python << 'EOF'
from app.db.session import SessionLocal
from app.models import *

db = SessionLocal()

# Check relationships
session = db.query(ClassSession).first()
print(f"Session: {session.topic}")
print(f"Attendance count: {len(session.attendance)}")
print(f"Events count: {len(session.events)}")

# Check lock mode
attendance = db.query(Attendance).first()
print(f"Lock mode: {attendance.lock_mode}")

# Check violations
violations = db.query(TabSwitchEventLog).filter(
    TabSwitchEventLog.lock_mode_violation == True
).count()
print(f"Lock violations: {violations}")

db.close()
EOF
```

## Security Testing

### Authentication Test

```bash
# Test without token
curl http://localhost:8000/api/class/mine
# Should return 401

# Test with invalid token
curl http://localhost:8000/api/class/mine \
  -H "Authorization: Bearer invalid_token"
# Should return 401

# Test with valid token
curl http://localhost:8000/api/class/mine \
  -H "Authorization: Bearer <valid_token>"
# Should return 200
```

### CORS Test

```bash
# Test from different origin
curl http://localhost:8000/api/auth/me \
  -H "Origin: http://evil.com" \
  -H "Authorization: Bearer <token>"
# Should be blocked or allowed based on CORS config
```

### SQL Injection Test

```bash
# Test SQL injection in login
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com OR 1=1--","password":"anything"}'
# Should return 401, not succeed
```

## Troubleshooting Tests

### Common Issues

| Issue | Test | Expected Result |
|-------|------|-----------------|
| Backend won't start | `uvicorn app.main:app` | Server starts on port 8000 |
| Frontend won't start | `npm run dev` | Dev server starts on port 5173 |
| Extension not loading | Check `chrome://extensions/` | Extension appears, no errors |
| Model not loading | Check browser console | Falls back to heuristics |
| WebSocket not connecting | Check browser Network tab | WS connection established |

### Debug Mode

**Backend:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

**Frontend:**
```bash
# Enable source maps
npm run dev -- --mode development
```

**Extension:**
```javascript
// In background.js, add:
console.log('[Focus Mate Debug]', message);
```

## Continuous Integration

### GitHub Actions

The project includes `.github/workflows/ci.yml` that runs:
- Backend linting and tests
- Frontend linting and tests
- Build verification

Trigger manually:
```bash
git push origin main
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Test Data Cleanup

```bash
# Remove test database
rm backend/classroom.db

# Remove test exports
rm -rf test_export/

# Remove synthetic data
rm -rf ml/data/processed/synthetic_demo/

# Regenerate clean database
cd backend
python -c "from app.db.session import SessionLocal; from app.db.base_class import Base; from app.db import init_db; db = SessionLocal(); Base.metadata.create_all(bind=db.get_bind()); init_db.init_db(db); db.close()"
```

## Test Checklist

Before deploying:

- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] Extension loads without errors
- [ ] Can create and join sessions
- [ ] Attention detection works
- [ ] Tab switching tracked
- [ ] Lock mode enforces restrictions
- [ ] Dashboard updates in real-time
- [ ] Reports export correctly
- [ ] WebSocket connections stable
- [ ] No console errors
- [ ] Performance acceptable
- [ ] Security tests pass

## Support

For testing issues:
- Check logs in backend/frontend/extension
- Review error messages carefully
- Verify all dependencies installed
- Try with fresh database
- Check network connectivity
- Review browser console

See `docs/QUICKSTART.md` for setup help.
