# Virtual Classroom Demo Script

Use this script to demonstrate the end-to-end experience with one teacher tab and two student tabs.

## Pre-requisites
- Install dependencies (`pip install -r backend/requirements.txt`, `npm install` in `frontend/`)
- Start services: `docker-compose up --build`

## Demo Flow
1. **Teacher login**
   - Browse to `http://localhost:5173`.
   - Pick `Demo Teacher` preset and sign in.
   - Create a new session called “Focus Lab”.
   - Note the generated session code displayed in "Session Details".

2. **Student join (tab A)**
   - Open a new browser window (or incognito) and log in as `student1@example.com / study123`.
   - Enter the session code and enable lock mode.
   - Allow webcam permissions.

3. **Student join (tab B)**
   - Repeat with `student2@example.com`.

4. **Engagement monitoring**
   - On each student tab, move away from the window or switch tabs. Observe alerts on the teacher dashboard within ~5 seconds.
   - Toggle lock mode on/off from the teacher dashboard; student pages update instantly (websocket round-trip).

5. **Reporting**
   - From the teacher dashboard, click “Download CSV” to show the generated report.

6. **Wrap-up**
   - End the session (optional via API) or stop docker-compose.

