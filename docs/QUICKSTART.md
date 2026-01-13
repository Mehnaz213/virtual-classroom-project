# Focus Mate - Quick Start Guide

Get Focus Mate up and running in 10 minutes.

## Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Chrome browser** (for extension)
- **Git** (to clone repository)

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd focus-mate
```

## Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## Step 3: Start Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Step 4: Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension/` folder from the repository
5. Extension icon should appear in Chrome toolbar

## Step 5: Create Teacher Account

1. Go to `http://localhost:5173`
2. Click **Sign Up** (or use demo credentials)
3. Create account with role: **Teacher**
4. Login with your credentials

**Demo Teacher:**
- Email: `teacher@example.com`
- Password: `teach123`

## Step 6: Create a Session

1. In teacher dashboard, enter a topic (e.g., "Math Class")
2. Click **Create & Go Live**
3. Note the **session code** (e.g., `A1B2C3`)
4. Share this code with students

## Step 7: Join as Student

Open a new browser window (or incognito):

1. Go to `http://localhost:5173`
2. Login as student (or create student account)
3. Enter the session code from teacher
4. Click **Join Session**
5. Allow webcam access when prompted

**Demo Students:**
- Email: `student1@example.com` / Password: `study123`
- Email: `student2@example.com` / Password: `study123`

## Step 8: Configure Extension (Student)

1. In the student browser, open DevTools (F12)
2. Go to **Application** → **Local Storage** → `http://localhost:5173`
3. Copy the `vc_token` value
4. Click the Focus Mate extension icon
5. Fill in configuration:
   - **API Base URL**: `http://localhost:8000/api`
   - **JWT Token**: Paste the `vc_token`
   - **Session ID**: `1` (or your session ID)
   - **Attendance ID**: Get from teacher dashboard
6. Click **Save Configuration**

### Finding Attendance ID

Teacher can see attendance IDs in the dashboard attendance table.

## Step 9: Test Features

### Test Attention Detection

1. Student should see their video feed
2. Look at different directions (left, right, up, down)
3. Teacher dashboard shows attention labels in real-time
4. Timeline chart updates with color-coded states

### Test Tab Switching

1. Student switches to another tab
2. Extension badge shows count
3. Teacher sees "Tab switch alert" in dashboard
4. Event logged in timeline

### Test Lock Mode

1. Teacher checks "Enforce lock mode for everyone"
2. Student tries to switch tabs
3. Warning overlay appears
4. Violation counted and reported to teacher

## Step 10: View Dashboard

Teacher dashboard shows:

- **Engagement meter** - Overall class engagement %
- **Attention breakdown** - Distribution of attention states
- **Timeline chart** - Historical engagement visualization
- **Alerts** - Sleepy students, tab switches, lock violations
- **Attendance table** - Student status and lock mode

## Optional: Train Custom Model

### Generate Training Data

```bash
cd ml

# Generate synthetic samples
python data_ingest.py ingest synthetic_demo --limit 1000 --output data/processed
```

### Train Model

```bash
python train.py \
  --data data/processed/synthetic_demo/metadata.jsonl \
  --output artifacts/focusmate_model \
  --epochs 10
```

### Export for Browser

```bash
python export_model.py \
  --model artifacts/focusmate_model/saved_model \
  --out ../frontend/public/models/focusmate-attention \
  --format tfjs
```

### Use Custom Model

1. Model files are now in `frontend/public/models/focusmate-attention/tfjs/`
2. Frontend automatically loads model on next page load
3. Predictions replace heuristic fallback

## Docker Quick Start

Alternatively, use Docker Compose:

```bash
# Start all services
docker-compose up --build

# Services:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
# - Database: PostgreSQL on port 5432
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Extension not working

1. Check extension is loaded in `chrome://extensions/`
2. Verify all configuration fields are filled
3. Check JWT token is valid (not expired)
4. Verify API Base URL is correct
5. Check browser console for errors

### Webcam not working

1. Check browser permissions (camera allowed)
2. Verify HTTPS or localhost (required for camera access)
3. Try different browser
4. Check if camera is used by another app

### Model not loading

1. Check `frontend/public/models/focusmate-attention/tfjs/model.json` exists
2. Verify file permissions
3. Check browser console for loading errors
4. System falls back to heuristics if model fails

## Next Steps

- **Read full documentation**: See `README.md` and `docs/FEATURES.md`
- **Configure for production**: Update environment variables
- **Train custom model**: Use real datasets for better accuracy
- **Deploy to cloud**: Follow deployment guide
- **Customize UI**: Modify frontend components
- **Add features**: Extend API and models

## Demo Script

For a guided demo, see `docs/demo-script.md`

## Support

- Check `README.md` for detailed documentation
- Review `docs/FEATURES.md` for feature details
- See `extension/README.md` for extension help
- See `ml/README.md` for ML pipeline details

## Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in config or kill existing process |
| Database locked | Close other connections or delete `classroom.db` |
| CORS errors | Check `allowed_origins` in backend config |
| Token expired | Login again to get new token |
| Model too large | Use quantized version or reduce image size |

## Production Checklist

Before deploying to production:

- [ ] Change `APP_SECRET_KEY` to secure random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/WSS
- [ ] Configure CORS for production domains
- [ ] Set up CDN for static assets
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Review privacy policy and consent flows
- [ ] Test with real users
- [ ] Prepare support documentation

## License

See main project LICENSE file.
