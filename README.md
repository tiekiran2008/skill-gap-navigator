# Skill Gap Navigator

An AI-powered career guidance platform that helps users identify skill gaps, get career recommendations, prepare for interviews, and build personalized learning roadmaps.

## Features

- **Resume Analysis** — Upload a PDF resume to auto-extract skills and get structured profile analysis
- **Career Matching** — Get AI-driven career recommendations based on your skills and target role
- **Company Analysis** — Compare your skills against company requirements for specific roles
- **Skill Assessment** — Take skill assessments across 15 technical skills (123 questions)
- **Skill Verification** — Track verified skills with scores from assessments
- **Interview Preparation** — Generate personalized interview study plans
- **Mock Interviews** — Practice with AI-scored mock interviews
- **Learning Roadmaps** — Get personalized learning roadmaps with progress tracking
- **Job Market Intelligence** — Explore market trends, in-demand skills, and company views
- **Project Recommendations** — Get project ideas tailored to close your skill gaps
- **AI Career Assistant** — Chat with an AI assistant for personalized career advice

## Tech Stack

### Backend
- **FastAPI** — Python web framework
- **PyMuPDF** — PDF resume parsing
- **sentence-transformers** — Skill extraction and matching
- **JSON-based persistence** — Lightweight local data storage

### Frontend
- **React 19** — UI library
- **Vite** — Build tool and dev server
- **Tailwind CSS** — Styling

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000` with API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173` and proxies API calls to the backend.

### Production Build

```bash
cd frontend
npm run build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assessments/skills` | GET | List available skills for assessment |
| `/api/v1/assessments/start` | POST | Start a skill assessment |
| `/api/v1/assessments/{id}/answer` | POST | Submit an answer |
| `/api/v1/assessments/{id}/complete` | POST | Complete an assessment |
| `/api/v1/assessments/history` | GET | Get assessment history |
| `/api/v1/interview/plan` | POST | Generate interview study plan |
| `/api/v1/interview/start` | POST | Start a mock interview |
| `/api/v1/interview/history` | GET | Get interview history |
| `/api/v1/companies/recommend` | POST | Get company recommendations |
| `/api/v1/companies/analyze` | POST | Analyze company skill fit |
| `/api/v1/careers/recommend` | POST | Get career recommendations |
| `/api/v1/gap-analysis` | POST | Run skill gap analysis |
| `/api/v1/roadmap/generate` | POST | Generate learning roadmap |
| `/api/v1/projects/recommend` | POST | Get project recommendations |
| `/api/v1/assistant/chat` | POST | Chat with AI career assistant |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── assessment_service.py
│   │   ├── career_assistant_service.py
│   │   ├── interview_preparation_service.py
│   │   ├── mock_interview_service.py
│   │   ├── skill_verification_service.py
│   │   ├── db_service.py
│   │   └── ...
│   ├── data/                    # JSON data stores
│   └── tests/                   # 217 tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/               # 14 page components
│   │   ├── components/
│   │   └── context/
│   └── dist/                    # Production build
└── data/
    └── user_data/               # User-generated data
```

## Testing

```bash
cd backend
python -m pytest tests/ -q
```

All 217 tests should pass.
