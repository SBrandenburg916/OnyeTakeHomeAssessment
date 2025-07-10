# 🧠 AI-Powered FHIR Query Tool

This project is a take-home assessment for a Full-Stack Engineer position, demonstrating the ability to integrate natural language processing (NLP) with FHIR-compliant healthcare data systems.

## 📌 Project Overview

This app allows users to input natural language queries (e.g., "Show me all diabetic patients over 50") and receive structured, simulated FHIR responses. The app extracts intent from text, builds mock FHIR queries, and displays patient data using charts and tables.

---

## 📁 Project Structure

- `backend/`
  - `fhir_nlp_service.py` – Python Flask backend with NLP-to-FHIR translation logic.
- `frontend/`
  - `App.js` – Main React component with query UI and results dashboard.
- `README.md` – This file.
- `SECURITY.md` – 1-page document outlining HIPAA/security strategy.

---

## 🚀 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/fhir-nlp-app.git
cd fhir-nlp-app

### 2. Start the Backend

cd backend
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install flask flask-cors
python fhir_nlp_service.py


Backend will run at: http://localhost:5050


### 3. Start the Frontend

cd ../frontend
npm install
npm start


Frontend will run at: http://localhost:3000


