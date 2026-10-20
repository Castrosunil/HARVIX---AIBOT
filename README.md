# HARVIX — AI Coding & Mathematics Assistant

HARVIX is a responsive AI workspace for coding help, debugging, code conversion, symbolic mathematics, and general questions. It ships with a React/Vite dashboard, FastAPI service, SymPy-backed math endpoint, optional OpenAI integration, Docker support, and CI.

## Architecture
```text
┌─────────────────────┐       REST JSON        ┌─────────────────────┐
│ React/Vite dashboard│ ─────────────────────▶ │ FastAPI API         │
└─────────────────────┘                       └──────────┬──────────┘
                                                         │
                                              ┌──────────▼──────────┐
                                              │ Intent router       │
                                              └───────┬───────┬──────┘
                                                      │       │
                                      ┌───────────────▼─┐   ┌─▼─────────────────┐
                                      │ SymPy math      │   │ Optional OpenAI   │
                                      │ engine          │   │ provider          │
                                      └─────────────────┘   └───────────────────┘

                                  API configuration is stored in environment variables.
```

## Features
- Auto, Coding, and Math modes with clear conversation UI.
- Exact symbolic math for simplification, equations, derivatives, and integrals.
- Local deterministic fallback when no LLM key is configured.
- Input validation, CORS configuration, health check, tests, Docker, and GitHub Actions.

## Run locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.app.main:app --reload --port 8000
# new terminal
cd frontend && npm install && npm run dev
```
Open http://localhost:5173. API docs are at http://localhost:8000/docs.

## Docker
```bash
cp .env.example .env
docker compose up --build
```

## Example prompts
- `Write a Python program to find prime numbers up to N.`
- `Solve 2*x^2 - 5*x + 3 = 0 step by step.`
- `Find the derivative of x^3*sin(x).`
- `Convert this Java code to Python.`

## Project structure
- `frontend/`: React dashboard and responsive styles.
- `backend/app/main.py`: API, routing, math engine, optional LLM adapter.
- `backend/tests/`: API and math tests.
- `Dockerfile`, `docker-compose.yml`: container setup.
- `.github/workflows/ci.yml`: automated test/build pipeline.
