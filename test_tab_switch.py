#!/usr/bin/env python3
"""
Test script to simulate tab switch events for testing the teacher dashboard alerts.
Run this while you have a student session active to see alerts appear.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000/api"
STUDENT_EMAIL = "alice.student@school.edu"  # Use your registered student
STUDENT_PASSWORD = "StudentPass123!"
SESSION_ID = 1  # Adjust based on your session

def login_student():
    """Login as student and get token"""
    response = requests.post(f"{API_BASE}/auth/login/json", json={
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def get_attendance_id(token, session_id):
    """Get attendance ID for the session"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/class/{session_id}/join", headers=headers)
    if response.status_code == 200:
        return response.json()["attendance_id"]
    else:
        print(f"Failed to get attendance: {response.text}")
        return None

def send_tab_switch_event(token, session_id, attendance_id, tab_visible=False):
    """Send a tab switch event"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "session_id": session_id,
        "attendance_id": attendance_id,
        "tab_visible": tab_visible,
        "event_type": "tab_switch",
        "timestamp": datetime.utcnow().isoformat(),
        "tab_count": 1,
        "note": "Simulated tab switch for testing"
    }
    
    response = requests.post(f"{API_BASE}/events/tab-switch", 
                           headers=headers, 
                           json=payload)
    
    if response.status_code == 200:
        print(f"✓ Tab switch event sent (tab_visible={tab_visible})")
        return True
    else:
        print(f"✗ Failed to send tab switch: {response.text}")
        return False

def main():
    print("🧪 Testing Tab Switch Alerts")
    print("=" * 40)
    
    # Step 1: Login
    print("1. Logging in as student...")
    token = login_student()
    if not token:
        return
    print("✓ Login successful")
    
    # Step 2: Get attendance ID
    print(f"2. Getting attendance for session {SESSION_ID}...")
    attendance_id = get_attendance_id(token, SESSION_ID)
    if not attendance_id:
        return
    print(f"✓ Attendance ID: {attendance_id}")
    
    # Step 3: Send tab switch events
    print("3. Sending tab switch events...")
    print("   (Check teacher dashboard for live alerts)")
    
    for i in range(5):
        # Simulate tab becoming hidden (student switched away)
        send_tab_switch_event(token, SESSION_ID, attendance_id, tab_visible=False)
        time.sleep(2)
        
        # Simulate tab becoming visible again
        send_tab_switch_event(token, SESSION_ID, attendance_id, tab_visible=True)
        time.sleep(3)
    
    print("\n✓ Test completed!")
    print("Check the teacher dashboard - you should see alerts like:")
    print("  'Alice Johnson switched tabs at 2025-01-13T...'")

if __name__ == "__main__":
    main()