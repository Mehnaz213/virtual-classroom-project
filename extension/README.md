# Focus Mate Extension

Chrome browser extension for Focus Mate virtual classroom system. Monitors tab switches, enforces lock mode, and reports attention metrics to the backend.

## Features

### 📊 Tab Switch Monitoring
- Detects when students switch tabs or windows
- Tracks visibility changes and blur/focus events
- Displays badge counter with total switches
- Reports events to Focus Mate backend API

### 🔒 Lock Mode Enforcement
- Blocks tab switches when enabled
- Prevents navigation to external sites
- Disables keyboard shortcuts (Ctrl+T, Ctrl+W, etc.)
- Shows warning overlays for violations
- Counts and reports lock mode violations

### 🔄 Automatic Retry
- Queues failed API requests
- Exponential backoff retry logic
- Persists configuration across sessions
- Handles offline scenarios gracefully

### ⚙️ Easy Configuration
- Simple popup UI for setup
- Fields: API Base URL, JWT Token, Session ID, Attendance ID
- Lock mode toggle
- Real-time statistics display

## Installation

### For Students

1. **Download Extension**
   - Clone or download the Focus Mate repository
   - Navigate to the `extension/` folder

2. **Load in Chrome**
   - Open Chrome and go to `chrome://extensions/`
   - Enable **Developer mode** (toggle in top-right)
   - Click **Load unpacked**
   - Select the `extension/` folder

3. **Configure Extension**
   - Log into Focus Mate as a student
   - Join a session
   - Open browser DevTools (F12) → **Application** tab → **Local Storage**
   - Find `http://localhost:5173` and copy the `vc_token` value
   - Ask your teacher for your **Attendance ID** (visible in teacher dashboard)
   - Click the Focus Mate extension icon in Chrome toolbar
   - Fill in the configuration:
     - **API Base URL**: `http://localhost:8000/api` (or your server URL)
     - **JWT Token**: Paste the `vc_token` from Local Storage
     - **Session ID**: Your current session ID (e.g., `1`)
     - **Attendance ID**: Provided by teacher
   - Click **Save Configuration**

4. **Verify Setup**
   - Status should show: "Configured and active"
   - Tab switches will now be tracked
   - Badge will show count of switches

### For Teachers

Teachers can enable lock mode for all students or specific students via the dashboard:

1. Open the teacher dashboard
2. Select an active session
3. Check "Enforce lock mode for everyone"
4. Students will receive lock mode updates automatically

## Configuration

### Popup Fields

| Field | Description | Example |
|-------|-------------|---------|
| **API Base URL** | Focus Mate backend API endpoint | `http://localhost:8000/api` |
| **JWT Token** | Student's access token (vc_token) | `eyJhbGciOiJIUzI1Ni...` |
| **Session ID** | Current classroom session ID | `1` |
| **Attendance ID** | Student's attendance record ID | `5` |
| **Lock Mode** | Enable/disable lock mode locally | Checkbox |

### Finding Your Configuration Values

#### JWT Token (vc_token)
1. Log into Focus Mate
2. Open DevTools (F12)
3. Go to **Application** → **Local Storage** → `http://localhost:5173`
4. Copy the value of `vc_token`

#### Session ID
- Visible in the URL when you join a session
- Or ask your teacher

#### Attendance ID
- Provided by teacher from the dashboard
- Visible in the attendance table

## Lock Mode

### What is Lock Mode?

Lock mode restricts student browser activity during class:

- **Blocks tab switches** - Students cannot switch to other tabs
- **Blocks new tabs** - Ctrl+T and similar shortcuts are disabled
- **Blocks external navigation** - Links to external sites are blocked
- **Blocks window switching** - Alt+Tab attempts are detected
- **Shows warnings** - Visual feedback for blocked actions
- **Reports violations** - All attempts are logged and sent to teacher

### How to Enable

**For Teachers:**
- Check "Enforce lock mode for everyone" in dashboard
- Or enable for specific students via API

**For Students:**
- Lock mode is controlled by the teacher
- You'll see a warning overlay when lock mode is active
- The extension badge turns red when lock mode is on

### Lock Mode Violations

Violations are tracked and reported:
- Tab switch attempts
- Navigation attempts
- Keyboard shortcut attempts
- Window focus changes

Teachers can see violation counts in the dashboard.

## API Integration

### Endpoints Used

#### POST /api/events/tab-switch

Reports tab switch events to the backend.

**Request:**
```json
{
  "session_id": 1,
  "attendance_id": 5,
  "event_type": "tab_switch",
  "tab_visible": false,
  "tab_count": 3,
  "timestamp": "2025-11-19T10:30:00Z",
  "note": "chrome-extension",
  "lock_mode_active": true,
  "lock_mode_violation": false
}
```

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Retry Logic

Failed requests are automatically retried:
- Initial retry: 1 second
- Second retry: 3 seconds
- Third retry: 5 seconds
- Fourth retry: 10 seconds
- Maximum 3 retry attempts per request

## Development

### File Structure

```
extension/
├── manifest.json       # Extension manifest (v3)
├── popup.html         # Configuration UI
├── popup.js           # Popup logic
├── background.js      # Service worker (event handling)
├── content.js         # Content script (page monitoring)
├── icons/             # Extension icons
└── README.md          # This file
```

### Key Components

**background.js** - Service worker that:
- Manages extension state
- Handles tab/window events
- Posts events to backend API
- Implements retry logic
- Updates badge counter

**content.js** - Content script that:
- Monitors page visibility
- Detects blur/focus events
- Enforces lock mode restrictions
- Shows warning overlays
- Communicates with background worker

**popup.js** - Popup UI that:
- Loads/saves configuration
- Displays statistics
- Updates lock mode toggle
- Shows connection status

### Testing

1. **Load Extension**
   ```bash
   # In Chrome, go to chrome://extensions/
   # Enable Developer mode
   # Click "Load unpacked" and select extension/ folder
   ```

2. **Test Tab Switching**
   - Configure extension with valid credentials
   - Switch tabs and verify badge counter increments
   - Check backend logs for received events

3. **Test Lock Mode**
   - Enable lock mode in popup
   - Try switching tabs (should be blocked)
   - Try Ctrl+T (should be blocked)
   - Verify warning overlays appear

4. **Test Retry Logic**
   - Stop backend server
   - Switch tabs (events queued)
   - Start backend server
   - Verify queued events are sent

### Debugging

**View Extension Logs:**
1. Go to `chrome://extensions/`
2. Find Focus Mate Extension
3. Click "service worker" link
4. Console shows background.js logs

**View Content Script Logs:**
1. Open any page
2. Open DevTools (F12)
3. Console shows content.js logs

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Badge not updating | Check JWT token is valid |
| Events not sending | Verify API Base URL is correct |
| Lock mode not working | Reload the page after enabling |
| "Not configured" status | Fill in all required fields |

## Privacy & Security

- **JWT tokens** are stored in `chrome.storage.local` (encrypted by Chrome)
- **No data collection** - Extension only sends data to your configured backend
- **HTTPS recommended** - Use HTTPS in production for secure token transmission
- **Clear tokens** - Use "Clear Configuration" button when done with class

## Permissions

The extension requires these permissions:

- `storage` - Save configuration locally
- `tabs` - Monitor tab switches
- `activeTab` - Access current tab info
- `webNavigation` - Detect navigation in lock mode
- `<all_urls>` - Monitor visibility on all pages

## Production Deployment

### 1. Update Manifest

Edit `manifest.json`:
```json
{
  "host_permissions": [
    "https://your-focusmate-domain.com/*"
  ]
}
```

### 2. Package Extension

```bash
# Zip the extension folder
cd extension
zip -r focus-mate-extension.zip . -x "*.git*" -x "README.md"
```

### 3. Publish to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Pay one-time $5 developer fee
3. Upload `focus-mate-extension.zip`
4. Fill in store listing details
5. Submit for review

### 4. Update Documentation

Provide students with:
- Chrome Web Store link
- Configuration instructions
- Support contact

## Support

For issues or questions:
- Check the main Focus Mate README
- Review backend API documentation
- Check browser console for errors
- Verify all configuration values are correct

## License

See main project LICENSE file.
