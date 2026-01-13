#!/usr/bin/env python3
"""
Complete system test - Registration + Tab Switch Alerts
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def test_registration():
    """Test user registration"""
    print("🧪 Testing Registration...")
    
    # Register teacher
    teacher_data = {
        "email": "teacher@test.com",
        "password": "password123",
        "full_name": "Test Teacher",
        "role": "teacher"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=teacher_data)
    if response.status_code == 200:
        teacher_token = response.json()["access_token"]
        print("✅ Teacher registration successful")
    else:
        print(f"❌ Teacher registration failed: {response.text}")
        return None, None
    
    # Register student
    student_data = {
        "email": "student@test.com", 
        "password": "password123",
        "full_name": "Test Student",
        "role": "student"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=student_data)
    if response.status_code == 200:
        student_token = response.json()["access_token"]
        print("✅ Student registration successful")
    else:
        print(f"❌ Student registration failed: {response.text}")
        return teacher_token, None
    
    return teacher_token, student_token

def test_session_creation(teacher_token):
    """Test session creation"""
    print("\n🧪 Testing Session Creation...")
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    session_data = {
        "topic": "Test Session",
        "code": "TEST123"
    }
    
    response = requests.post(f"{API_BASE}/class/sessions", headers=headers, json=session_data)
    if response.status_code == 200:
        session_id = response.json()["id"]
        print(f"✅ Session created with ID: {session_id}")
        return session_id
    else:
        print(f"❌ Session creation failed: {response.text}")
        return None

def test_student_join(student_token, session_id):
    """Test student joining session"""
    print("\n🧪 Testing Student Join...")
    
    headers = {"Authorization": f"Bearer {student_token}"}
    join_data = {
        "code": "TEST123",
        "lock_mode": False
    }
    
    response = requests.post(f"{API_BASE}/class/{session_id}/join", headers=headers, json=join_data)
    if response.status_code == 200:
        attendance_id = response.json()["attendance_id"]
        print(f"✅ Student joined with attendance ID: {attendance_id}")
        return attendance_id
    else:
        print(f"❌ Student join failed: {response.text}")
        return None

def test_tab_switch_events(student_token, session_id, attendance_id):
    """Test tab switch events"""
    print("\n🧪 Testing Tab Switch Events...")
    
    headers = {"Authorization": f"Bearer {student_token}"}
    
    for i in range(3):
        # Send tab switch event
        event_data = {
            "session_id": session_id,
            "attendance_id": attendance_id,
            "tab_visible": False,
            "event_type": "tab_switch",
            "timestamp": datetime.utcnow().isoformat(),
            "note": f"Test tab switch {i+1}"
        }
        
        response = requests.post(f"{API_BASE}/events/tab-switch", headers=headers, json=event_data)
        if response.status_code == 200:
            print(f"✅ Tab switch event {i+1} sent successfully")
        else:
            print(f"❌ Tab switch event {i+1} failed: {response.text}")
        
        time.sleep(1)

def test_dashboard_alerts(teacher_token, session_id):
    """Test dashboard alerts"""
    print("\n🧪 Testing Dashboard Alerts...")
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    response = requests.get(f"{API_BASE}/class/{session_id}/dashboard", headers=headers)
    
    if response.status_code == 200:
        dashboard = response.json()
        alerts = dashboard.get("tab_switch_alerts", [])
        violations = dashboard.get("lock_violations", [])
        
        print(f"✅ Dashboard loaded successfully")
        print(f"📊 Tab switch alerts: {len(alerts)}")
        print(f"🔒 Lock violations: {len(violations)}")
        
        if alerts:
            print("📋 Recent alerts:")
            for alert in alerts[:3]:
                print(f"   - {alert}")
        else:
            print("⚠️  No alerts found - this might be the issue!")
            
        return len(alerts) > 0
    else:
        print(f"❌ Dashboard failed: {response.text}")
        return False

def main():
    print("🚀 Complete System Test")
    print("=" * 50)
    
    # Test registration
    teacher_token, student_token = test_registration()
    if not teacher_token or not student_token:
        print("❌ Registration failed - stopping test")
        return
    
    # Test session creation
    session_id = test_session_creation(teacher_token)
    if not session_id:
        print("❌ Session creation failed - stopping test")
        return
    
    # Test student join
    attendance_id = test_student_join(student_token, session_id)
    if not attendance_id:
        print("❌ Student join failed - stopping test")
        return
    
    # Test tab switch events
    test_tab_switch_events(student_token, session_id, attendance_id)
    
    # Wait a moment for processing
    print("\n⏳ Waiting for events to process...")
    time.sleep(3)
    
    # Test dashboard alerts
    alerts_working = test_dashboard_alerts(teacher_token, session_id)
    
    print("\n" + "=" * 50)
    if alerts_working:
        print("🎉 SUCCESS: Complete system is working!")
        print("✅ Registration works")
        print("✅ Tab switch alerts work")
    else:
        print("⚠️  PARTIAL SUCCESS:")
        print("✅ Registration works")
        print("❌ Tab switch alerts need debugging")
    
    print(f"\n🌐 Test accounts created:")
    print(f"   Teacher: teacher@test.com / password123")
    print(f"   Student: student@test.com / password123")
    print(f"   Session: TEST123")

if __name__ == "__main__":
    main()