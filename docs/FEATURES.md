# Focus Mate - Feature Documentation

## Advanced Attention Detection

Focus Mate uses a sophisticated AI model to detect and classify student attention states in real-time.

### Attention Labels

The system classifies attention into 11 distinct states:

| Label | Description | Gaze Characteristics |
|-------|-------------|---------------------|
| **focused** | Looking directly at screen, centered gaze | \|yaw\| < 5°, \|pitch\| < 5° |
| **looking_left** | Gaze directed to the left | yaw ≤ -8° |
| **looking_right** | Gaze directed to the right | yaw ≥ 8° |
| **looking_up** | Gaze directed upward | pitch ≥ 6° |
| **looking_down** | Gaze directed downward | pitch ≤ -6° |
| **engaged** | Generally attentive, slight gaze variation | \|yaw\| < 8°, \|pitch\| < 8° |
| **partial_engaged** | Partially attentive | Moderate gaze deviation |
| **sleepy** | Eyes closing, drowsy appearance | eyes_open_prob < 0.2 |
| **distracted_by_multi_face** | Multiple faces detected in frame | face_count > 1 |
| **no_face** | No face detected | face_count = 0 |
| **unknown** | Low confidence prediction | confidence < 0.3 |

### AI Model Architecture

```
Input: 160×120×3 RGB image
  ↓
MobileNetV3-Small Backbone
  ↓
Global Average Pooling
  ↓
Multi-Head Outputs:
  ├─ Gaze Yaw (regression, degrees)
  ├─ Gaze Pitch (regression, degrees)
  ├─ Head Yaw (regression, degrees)
  ├─ Head Pitch (regression, degrees)
  ├─ Eyes Open Probability (sigmoid, 0-1)
  └─ Attention Label (softmax, 11 classes)
```

**Model Specifications:**
- Architecture: MobileNetV3-Small
- Input size: 160×120×3
- Model size: <10MB (quantized)
- Inference time: <50ms (browser)
- Framework: TensorFlow.js

### Training Pipeline

1. **Data Ingestion**
   ```bash
   python ml/data_ingest.py ingest synthetic_demo --limit 1000
   ```

2. **Training**
   ```bash
   python ml/train.py \
     --data data/processed/synthetic_demo/metadata.jsonl \
     --epochs 10 \
     --batch-size 32
   ```

3. **Export**
   ```bash
   python ml/export_model.py \
     --model artifacts/focusmate_model/saved_model \
     --out frontend/public/models/focusmate-attention \
     --format tfjs
   ```

### Supported Datasets

- **GazeCapture** - Mobile gaze dataset (MIT)
- **MPIIGaze** - Laptop gaze with head pose
- **Columbia Gaze** - Discrete directional gaze
- **ETH-XGaze** - Multi-view head pose
- **OpenEDS** - Eye segmentation and openness
- **Synthetic Demo** - Generated training data
- **Local Calibration** - User-specific captures

See `ml/README.md` for detailed dataset information.

### Calibration

User-specific calibration improves accuracy:

1. Student runs calibration flow (center, left, right, up, down)
2. Calibration offsets stored in localStorage
3. Applied to all gaze predictions
4. Can be exported and aggregated for model fine-tuning

### Fallback Heuristics

If the TF.js model fails to load, the system falls back to MediaPipe-based heuristics:
- Face mesh landmark detection
- Eye aspect ratio for drowsiness
- Head pose estimation from landmarks
- Simple rule-based classification

## Lock Mode

Lock mode restricts student browser activity during class sessions.

### Features

#### Tab Switch Blocking
- Detects and blocks tab activation changes
- Monitors window focus/blur events
- Tracks visibility state changes
- Counts and reports all attempts

#### Navigation Blocking
- Blocks external site navigation
- Intercepts link clicks
- Prevents new tab/window creation
- Allows same-origin navigation

#### Keyboard Shortcut Blocking
- **Ctrl+T** - New tab
- **Ctrl+W** - Close tab
- **Ctrl+N** - New window
- **Alt+Tab** - Window switching
- **Alt+F4** - Close window

#### Visual Feedback
- Red warning overlays for blocked actions
- Slide-down animation
- Auto-dismiss after 3 seconds
- Clear messaging about restrictions

### Implementation

Lock mode is enforced through three components:

1. **Chrome Extension** (`extension/`)
   - Background service worker monitors tab events
   - Content script enforces restrictions
   - Badge shows violation count

2. **Frontend Web App** (`frontend/`)
   - Visibility API monitoring
   - Lock mode UI indicators
   - Calibration and setup flows

3. **Backend API** (`backend/`)
   - Lock mode state management
   - Violation logging
   - Teacher controls

### Teacher Controls

Teachers can control lock mode from the dashboard:

```typescript
// Enable for all students
POST /api/class/{sessionId}/lock
{
  "enabled": true
}

// Enable for specific student
POST /api/class/{sessionId}/lock
{
  "enabled": true,
  "student_id": 5
}
```

### Violation Tracking

All lock mode violations are logged:

```sql
CREATE TABLE tab_switch_events (
  id INTEGER PRIMARY KEY,
  session_id INTEGER,
  attendance_id INTEGER,
  event_type TEXT,
  timestamp DATETIME,
  tab_count INTEGER,
  tab_visible BOOLEAN,
  lock_mode_active BOOLEAN,
  lock_mode_violation BOOLEAN,
  meta JSON
);
```

Dashboard displays:
- Total violations per student
- Violation timeline
- Alert notifications
- Exportable reports

## Chrome Extension

The Focus Mate Extension provides robust tab monitoring and lock mode enforcement.

### Installation

1. Load unpacked extension from `extension/` folder
2. Configure with API URL, JWT token, session ID, attendance ID
3. Enable lock mode if required
4. Extension monitors and reports all activity

### Configuration

| Field | Source | Example |
|-------|--------|---------|
| API Base URL | Deployment config | `http://localhost:8000/api` |
| JWT Token | DevTools → Local Storage → `vc_token` | `eyJhbGc...` |
| Session ID | URL or teacher | `1` |
| Attendance ID | Teacher dashboard | `5` |

### Features

- **Badge Counter** - Shows total tab switches
- **Lock Mode Toggle** - Enable/disable locally
- **Statistics Display** - Tab switches and violations
- **Retry Queue** - Handles offline scenarios
- **Persistent Config** - Saved across sessions

See `extension/README.md` for detailed documentation.

## Dashboard Features

### Teacher Dashboard

- **Live Engagement Meter** - Real-time engagement percentage
- **Attention Label Breakdown** - Distribution of attention states
- **Timeline Chart** - Historical engagement visualization
- **Sleepy Alerts** - Notifications for drowsy students
- **Tab Switch Alerts** - Tab switching notifications
- **Lock Violation Alerts** - Lock mode violation tracking
- **Attendance Table** - Student status and lock mode state
- **Lock Mode Controls** - Enable/disable for all or specific students
- **Report Export** - CSV/PDF downloads

### Student View

- **Video Feed** - Webcam capture with privacy controls
- **Calibration Flow** - Guided gaze calibration
- **Lock Mode Indicator** - Visual feedback when locked
- **Session Code Entry** - Join sessions easily
- **Attention Feedback** - Optional self-monitoring

### Labeling UI

- **Manual Labeling** - Review and label captured frames
- **Keyboard Shortcuts** - Fast labeling workflow
- **Active Learning Queue** - Low-confidence predictions
- **Export Labels** - JSON export for training
- **Batch Operations** - Label multiple frames

## API Endpoints

### Authentication
- `POST /api/auth/login/json` - Login and get JWT
- `GET /api/auth/me` - Get current user profile

### Classroom
- `POST /api/class/create` - Create new session
- `GET /api/class/mine` - List teacher's sessions
- `GET /api/class/code/{code}` - Lookup session by code
- `POST /api/class/{id}/join` - Student joins session
- `POST /api/class/{id}/lock` - Toggle lock mode
- `POST /api/class/{id}/end` - End session
- `GET /api/class/{id}/dashboard` - Get dashboard data

### Events
- `POST /api/events/frame` - Upload frame + attention data
- `POST /api/events/tab-switch` - Report tab switch event

### Reports
- `GET /api/reports/{id}?format=csv` - Download CSV report
- `GET /api/reports/{id}?format=pdf` - Download PDF report

### WebSocket
- `WS /ws/session/{id}?token=` - Live updates stream

## Privacy & Security

### Data Minimization
- Frames reduced to 160×120 resolution
- JPEG quality ~50%
- Only metadata sent by default
- Optional frame upload for debugging

### Token Security
- JWT tokens with expiration
- Stored in httpOnly cookies (backend)
- localStorage for extension (encrypted by Chrome)
- Short-lived tokens recommended

### CORS & CSP
- Strict CORS origins in production
- CSP headers for XSS protection
- Extension ID whitelisting
- HTTPS/WSS required in production

### Data Retention
- Aggregate statistics retained
- Raw frames optional (consent required)
- Configurable retention periods
- GDPR compliance ready

### Consent & Transparency
- Clear privacy policy
- Opt-in for frame storage
- Student awareness of monitoring
- Teacher controls and oversight

## Performance

### Frontend
- React 18 with TypeScript
- Vite for fast builds
- Code splitting and lazy loading
- Optimized bundle size

### Backend
- FastAPI with async/await
- SQLAlchemy 2 with connection pooling
- WebSocket for real-time updates
- Efficient database queries

### ML Inference
- Client-side TF.js inference
- <50ms per frame
- Quantized model <10MB
- Web Worker for non-blocking

### Scalability
- Horizontal scaling ready
- Redis for WebSocket pub/sub
- PostgreSQL for production
- CDN for static assets

## Deployment

### Development
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Extension
Load unpacked from extension/ folder
```

### Docker
```bash
docker-compose up --build
```

### Production
- Backend: Fly.io, Render, AWS ECS
- Frontend: Netlify, Vercel, S3+CloudFront
- Database: RDS, Cloud SQL, managed PostgreSQL
- CDN: CloudFlare, CloudFront

See main README for detailed deployment instructions.
