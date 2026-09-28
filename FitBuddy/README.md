# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite + Google Gemini web application based on the supplied FitBuddy specification.

## Features

- Collects name, user ID, age, weight, fitness goal, and workout intensity.
- Generates a personalized 7-day workout plan with Gemini.
- Generates a concise nutrition/recovery tip.
- Accepts feedback and regenerates the plan.
- Persists users and original/updated plans in SQLite.
- Provides an admin-style `/view-all-users` page.
- Includes JSON API endpoints and FastAPI Swagger docs.
- Uses environment variables for the Gemini API key.
- Includes a deterministic demo/fallback mode when no API key is configured, so the UI can still be tested locally.

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── feedback.html
│   │   └── all_users.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Prerequisites

- Python 3.11+ recommended
- VS Code
- Internet connection for Gemini API calls
- A Gemini API key for real AI generation

## 2. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure Gemini

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows:

```cmd
copy .env.example .env
```

Then set:

```env
GEMINI_API_KEY=your_real_key
```

The current Google GenAI Python SDK is used (`google-genai`), rather than the older `google-generativeai` package described in the original project document.

## 5. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

The SQLite database `fitbuddy.db` is created automatically.

## 6. Demo mode

If `GEMINI_API_KEY` is missing, FitBuddy uses a safe deterministic demo generator. This lets you verify routing, templates, database persistence, feedback updates, and the admin page without an API key.

For real AI generation, configure the key in `.env`.

## API endpoints

### GET `/api/health`

Returns application health.

### POST `/api/generate-workout`

JSON body:

```json
{
  "username": "Alex",
  "user_id": "alex01",
  "age": 25,
  "weight": 70,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### POST `/api/submit-feedback`

JSON body:

```json
{
  "user_id": "alex01",
  "feedback": "Add more cardio and one extra recovery day."
}
```

### GET `/api/users`

Returns stored users and plans.

## Important health note

FitBuddy generates general wellness/fitness content and is not a substitute for a qualified healthcare or fitness professional. The generated content should not be treated as medical advice. Users should stop an exercise that causes pain or concerning symptoms and seek appropriate professional advice.

## Original specification mapping

The supplied document calls for:
- FastAPI backend
- Gemini-powered workout generation
- Gemini-powered nutrition/recovery tip
- feedback-based plan updates
- SQLite/SQLAlchemy persistence
- Jinja2 pages: input, results, and all-users/admin
- routes `/`, `/generate-workout`, `/submit-feedback`, `/view-all-users`
- local Uvicorn deployment

This implementation keeps those functional requirements while using the current Google GenAI SDK and configurable model names.
