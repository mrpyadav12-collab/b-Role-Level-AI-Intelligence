# Role-Level AI Intelligence

## Challenge
Modus Enterprise AI Build Challenge

## Problem statement
This project helps an organisation understand how AI may change the future of work across roles. It models roles, processes, activities, skills, AI exposure, automation risk, augmentation potential, and future reskilling needs.

## Objective
The app demonstrates a realistic Enterprise AI use case for workforce planning. It supports:
- role analysis
- process and activity analysis
- AI impact scoring
- future responsibility and skill planning
- role-to-role comparison
- new role analysis without code changes

## Selected industry
Industry: Banking & Financial Services

Organisation context: Meridian Financial Group (fictional organisation used for demonstration only).

Why this industry was chosen:
- strong role structure
- real business processes
- clear AI automation vs human judgement trade-offs
- enough available public research
- easy to explain during a live demo

## Key features
- FastAPI backend
- SQLite persistence
- AI-assisted qualitative assessment with deterministic scoring
- role comparison
- dynamic new role support
- evidence/research support
- tests for scoring and API behaviour

## Architecture overview
- Frontend: Next.js + TypeScript
- Backend: FastAPI
- Database: SQLite
- AI layer: OpenAI-compatible AI gateway with resilient fallback
- Scoring: deterministic Python business logic

## Tech stack
- Python 3.12+
- FastAPI
- SQLite
- Next.js 16
- React 19
- Tailwind CSS
- pytest
- httpx

## Project structure
- backend/: Python app, data models, scoring logic, AI integration
- frontend/: Next.js UI
- docs/: architecture, database, decisions, checklist
- backend/tests/: API and scoring tests

## Setup instructions

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

If you want to use the project dependency file directly:
```bash
pip install fastapi[standard] httpx pytest
```

Run the backend:
```bash
cd backend
python -m uvicorn main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### Free deployment with Render

The repository includes `render.yaml` for a free two-service deployment:

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and select the GitHub repository.
3. Render will create the FastAPI API and Next.js frontend services from `render.yaml`.
4. Open the frontend service URL. The frontend automatically receives the backend service URL.

The free backend uses the existing SQLite database and seeds demo data on startup. Render free services can sleep and their local disk is ephemeral, so newly created roles and analyses are intended for demos rather than permanent storage.

### 3. Environment variables
Set optional variables for AI integration:
```bash
AI_GATEWAY_URL=https://ai-gateway.vercel.sh/v1/chat/completions
AI_MODEL=openai/gpt-4o-mini
AI_GATEWAY_API_KEY=your-key
AI_TIMEOUT=20
WORKFORCE_DB_PATH=./workforce.db
```

If the key is missing, the app uses deterministic fallback analysis.

## Database setup
The database is created automatically on startup. SQLite file is created under `backend/workforce.db` by default.

## How analysis works
1. Role data is stored in SQLite.
2. Activities are modelled with business facts.
3. AI layer interprets activity factors and future responsibilities.
4. Deterministic scoring engine computes AI impact scores.
5. Role-level profile is stored and returned to UI.

## Scoring methodology
The scoring model uses transparent factors:
- repetitiveness
- rule_based
- data_availability
- decision_complexity
- human_interaction
- ai_capability_fit

Each activity is converted to a weighted score, then aggregated into a role-level score.

## Testing
Run backend tests:
```bash
cd backend
pytest -q
```

## Example use cases
- Compare a Finance Analyst to a Procurement Analyst
- See which roles are high automation risk
- Identify reskilling priorities
- Add a new role such as ESG Data Steward and analyze it live

## Limitations
- The current dataset is synthetic but realistic
- AI responses are optional and gracefully fallback
- This is a challenge-scale prototype, not a full enterprise system

## Future improvements
- background async analysis jobs
- richer UI workflows
- multi-organisation support
- role import/export
- improved AI provider abstraction
- authentication and audit logs

## AI coding tools used
This project was built using modern AI-assisted development workflows, but the app itself remains framework-driven and runnable without paid services.

## License
This project is intended for educational and challenge use.
