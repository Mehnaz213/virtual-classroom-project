# Testing Live Alerts - Step by Step

## Prerequisites
1. Backend and frontend running
2. At least one teacher and one student account created

## Test Steps

### Step 1: Create a Session (Teacher)
1. Go to http://localhost:5173
2. Login as teacher
3. Click "Create New Session"
4. Fill in:
   - **Topic**: "Test Session"
   - **Code**: "TEST01"
5. Click "Create Session"
6. Note the session appears in the list

### Step 2: Join Session (Student)
1. Open **incognito window** (or different browser)
2. Go to http://localhost:5173
3. Login as student
4. Enter session code: **TEST01**
5. Click "Join Session"
6. Allow camera permissions
7. You should see the video feed

### Step 3: Monitor Dashboard (Teacher)
1. In teacher window, click on "Test Session"
2. You should see:
   - Student appears in the grid
   - Video feed (if camera allowed)
   - "Live Alerts" section (should be empty initially)

### Step 4: Test Tab Switching (Student)
1. In student window, **switch to another tab** (Ctrl+T or click another tab)
2. Wait 2-3 seconds
3. **Switch back** to the Focus Mate tab
4. Repeat this 2-3 times

### Step 5: Check Alerts (Teacher)
1. In teacher dashboard, look at "Live Alerts" section
2. You should see messages like:
   - "Alice Johnson switched tabs at 2025-01-13T..."
   - Alerts appear within 5-10 seconds

## Troubleshooting

### If alerts don't appear:

1. **Check browser console (Student window)**:
   - Press F12 → Console
   - Look for messages like: `[Tab Switch] Event sent: visible=false`
   - If no messages, the detection isn't working

2. **Check browser console (Teacher window)**:
   - Press F12 → Console
   - Look for API errors or network issues

3. **Check backend logs**:
   - Look at the backend terminal
   - Should see POST requests to `/events/tab-switch`

4. **Verify session is active**:
   - Student must be in a joined session
   - Teacher must have selected the session in dashboard

### Manual Test (If needed):
Run the Python test script:
```bash
python test_tab_switch.py
```

This will simulate tab switch events and you should see alerts appear.

## Expected Results

✅ **Working System**:
- Student tab switches are detected immediately
- Events sent to backend within 2 seconds
- Teacher dashboard shows alerts within 5-10 seconds
- Alerts include student name and timestamp

❌ **Not Working**:
- No console messages in student window
- No alerts in teacher dashboard
- Network errors in console
- Backend not receiving events

## Common Issues

1. **Student not in session**: Must join with valid code
2. **Teacher not viewing session**: Must click on session in list
3. **Browser permissions**: Camera/tab detection blocked
4. **Network issues**: Backend not reachable
5. **Polling delay**: Dashboard updates every 2 seconds

## Success Criteria

The system works correctly when:
1. Student switches tabs → Alert appears in teacher dashboard
2. Multiple students → Multiple alerts
3. Real-time updates (< 10 second delay)
4. Accurate timestamps and student names