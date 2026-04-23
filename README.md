# AI-Powered Fake News Detection System (2026 Edition) 🛡️

A modern, high-fidelity full-stack Flask application that leverages the **Google Gemini 1.5 Pro API** to analyze URLs, images, and videos for misinformation.

## ✨ Key Features
- **Multi-Modal AI Analysis**: Verify news via URLs, image uploads (screenshots), or video clips.
- **Gemini Ensemble Engine**: Deep-learning powered detection with confidence scoring and virality prediction.
- **Premium UI/UX**: Inspired by 2025/26 trends - Glassmorphism, Dark mode gradients, Apple-like smooth animations, and interactive charts.
- **Role-Based Access**: Secure login/registration for Users and a dedicated Admin Panel for system monitoring.
- **Reporting**: Automated PDF generation for analysis results.
- **History Tracking**: Personal dashboard to search and filter previous scans.

## 🚀 Getting Started

### 1. Installation
Clone the repository and install dependencies:
```powershell
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file from the template:
```powershell
cp .env.example .env
```
**Important:** You MUST add your `GEMINI_API_KEY` in the `.env` file. Get one at [Google AI Studio](https://aistudio.google.com/).

### 3. Run the App
```powershell
python app.py
```
The application will be available at `http://127.0.0.1:5000`.

## 🛠️ Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login, Bcrypt.
- **AI**: Google Generative AI (Gemini 1.5 Pro).
- **Frontend**: Tailwind CSS, DaisyUI, Alpine.js, Chart.js.
- **PDF Engine**: ReportLab.
- **Database**: SQLite (Default).

## 🔐 Default Admin Credentials
- **Email**: `admin@fakenews.ai`
- **Password**: `admin123`

## 🎨 UI Aesthetics
Built with a focus on visual excellence:
- **Glassmorphism**: Subtle blurs and translucent backgrounds.
- **Vibrant Gradients**: Interactive and smooth color transitions.
- **Smooth Animations**: Floating elements and fade-in transitions.
- **Responsive Design**: Optimized for desktops and mobile devices.

---
*Built with ❤️ for Truth & Accuracy in the Digital Age.*
"# fakenews" 
