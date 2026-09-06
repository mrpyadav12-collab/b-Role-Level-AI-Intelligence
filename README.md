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

## Scoring methodology
The scoring model uses transparent factors:
- repetitiveness
- rule_based
- data_availability
- decision_complexity
- human_interaction
- ai_capability_fit

Each activity is converted to a weighted score, then aggregated into a role-level score.

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
