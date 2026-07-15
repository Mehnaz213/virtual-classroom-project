<div align="center">

# 🎓 Focus Mate

### AI-Powered Virtual Classroom Engagement & Attention Monitoring System

Real-time classroom engagement analysis using Computer Vision, Gaze Tracking, Head Pose Estimation, and Chrome Extension-based Exam Monitoring.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![OpenCV](https://img.shields.io/badge/OpenCV-ComputerVision-red)
![MediaPipe](https://img.shields.io/badge/MediaPipe-GazeTracking-orange)
![TensorFlow](https://img.shields.io/badge/TensorFlow-AI-FF6F00)
![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green)
![License](https://img.shields.io/badge/License-MIT-purple)

</div>

## 🚀 Overview

Focus Mate is an AI-powered virtual classroom platform that helps educators monitor student engagement during online learning sessions.

The system combines Computer Vision, Gaze Tracking, Head Pose Estimation, and Browser Activity Monitoring to analyze attention levels in real time. Teachers receive live engagement analytics, while a Chrome Extension detects tab switching and lock mode violations during examinations.

The platform also includes attendance tracking, downloadable reports, WebSocket-based live monitoring, AI-powered engagement classification, and a complete teacher-student management system.

## ✨ Features

### 🎥 AI Attention Monitoring

- Real-time face detection
- Head pose estimation
- Eye gaze tracking
- Attention classification
- Sleepiness detection
- Multiple face detection

### 👨‍🏫 Teacher Dashboard

- Live classroom monitoring
- Student engagement analytics
- Attendance management
- Downloadable PDF reports
- CSV export

### 👨‍🎓 Student Portal

- Join classroom
- AI attention tracking
- Lock Mode
- Automatic attendance
- Live session participation

### 🔒 Exam Monitoring

- Chrome Extension
- Tab-switch detection
- Lock mode
- Visibility tracking
- Retry queue
- Badge notifications

### 🤖 AI Pipeline

- Dataset ingestion
- Image augmentation
- MobileNetV2 training
- TF Lite export
- TF.js inference
- Active learning

### ⚙ Backend

- JWT Authentication
- FastAPI REST APIs
- WebSocket
- SQLAlchemy
- PostgreSQL / SQLite
  
# 🏗️ System Architecture

```text
                         Teacher / Student

                               │
                               ▼

                     React Frontend (Vite)

                               │

                  REST APIs + WebSockets

                               │

                               ▼

                     FastAPI Backend Server

              ┌────────────────┴─────────────────┐

              ▼                                  ▼

        SQLite / PostgreSQL                AI Processing

              │                                  │

              ▼                                  ▼

      Attendance & Events        OpenCV + MediaPipe + TensorFlow

              │                                  │

              └───────────────┬──────────────────┘

                              ▼

                    Engagement Prediction

                              ▼

                  Teacher Dashboard & Reports
```
# 📸 Screenshots

## 🔐 Login

![Login](docs/images/login.png)

---

## 📝 Register

![Register](docs/images/register.png)

---

## 👨‍🏫 Teacher Dashboard

![Teacher Dashboard](docs/images/teacher-dashboard.png)

---

## 👨‍🎓 Student Dashboard

![Student Dashboard](docs/images/student-dashboard.png)

---

## 📊 Active Classroom Sessions

![Active Sessions](docs/images/active-sessions.png)

---

# 🤖 AI Attention Detection

### Focused

![Focused](docs/images/focused.png)

### Looking Left

![Looking Left](docs/images/looking-left.png)

### Looking Right

![Looking Right](docs/images/looking-right.png)

### Looking Up

![Looking Up](docs/images/looking-up.png)

### No Face Detected

![No Face](docs/images/no-face.png)

---

## 🚨 Live Classroom Alerts

![Live Alerts](docs/images/live-alerts.png)

# 🛠️ Tech Stack

| Category | Technologies |
|-----------|--------------|
| **Frontend** | React, TypeScript, Vite, Plotly |
| **Backend** | FastAPI, SQLAlchemy, JWT Authentication |
| **Database** | PostgreSQL, SQLite |
| **Computer Vision** | OpenCV, MediaPipe |
| **Machine Learning** | TensorFlow, MobileNetV2, TF Lite, TF.js |
| **Browser Extension** | Chrome Extension (Manifest V3) |
| **Reporting** | ReportLab, CSV Export |
| **Testing** | Pytest, Vitest |
| **Deployment** | Docker, Docker Compose |

# 📁 Project Structure

```text
Focus-Mate/

├── backend/              FastAPI Backend
├── frontend/             React Frontend
├── extension/            Chrome Extension
├── ml/                   AI Model Training
├── scripts/              Utility Scripts
├── docs/                 Documentation
├── Postman/              API Collection
├── .github/              CI/CD Workflow
├── docker-compose.yml
└── README.md
```

# 🔄 AI Workflow

```text
Student Webcam

      │

      ▼

OpenCV + MediaPipe

      │

      ▼

Face Detection & Landmark Extraction

      │

      ▼

Head Pose & Gaze Estimation

      │

      ▼

Attention Classification

      │

      ▼

FastAPI Backend

      │

      ▼

Database Storage

      │

      ▼

Teacher Dashboard

      │

      ▼

Analytics & Reports
```

# 🌐 API Overview

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/login/json` | User Login |
| GET | `/api/auth/me` | Current User |
| POST | `/api/class/create` | Create Classroom |
| POST | `/api/class/{id}/join` | Join Classroom |
| GET | `/api/class/{id}/dashboard` | Teacher Dashboard |
| POST | `/api/events/

# ✅ Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run test
npm run build
```

### ML Pipeline

```bash
python ml/train.py
python ml/eval.py
```frame` | Upload AI Attention Data |
| POST | `/api/events/tab-switch` | Chrome Extension Events |
| GET | `/api/reports/{id}` | Export Reports |
| WS | `/ws/session/{id}` | Live Monitoring |

> 📌 Complete API documentation is available in the **Postman Collection** included in this repository.

# 🚀 Deployment

The application supports deployment using Docker.

```bash
docker-compose up --build
```

Services Included:

- FastAPI Backend
- React Frontend
- PostgreSQL Database
- AI Inference Pipeline

Production deployment can be hosted on:

- Render
- Railway
- Fly.io
- AWS EC2
- Azure App Service
- Google Cloud Platform
```

# 🚀 Future Enhancements

- 😊 Emotion Recognition
- 📱 Mobile Application
- 🌐 Cloud Deployment
- 📊 Advanced Learning Analytics
- 🤖 AI-Based Student Performance Insights
- 🎓 LMS Integration (Google Classroom, Moodle)
- 🔔 Real-Time Notification System
