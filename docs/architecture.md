# Architecture document

## System overview
The solution is a modular monolith with a Python backend and a Next.js frontend. It models work as structured data and analyzes it using a mix of AI interpretation and deterministic scoring.

## Components

### Frontend
Responsible for:
- dashboard
- role listing
- role detail
- comparison
- new-role input

### Backend API
Responsible for:
- validating requests
- serving analytics
- orchestration between services

### Business logic
Responsible for:
- activity scoring
- role aggregation
- reskilling priority logic
- methodology exposure

### AI layer
Responsible for:
- interpreting activity factors
- suggesting AI capabilities
- identifying future responsibilities and skills
- generating rationale

### Database
Responsible for:
- persistence
- role/process/activity graphs
- evidence storage
- cached analysis results

### Research evidence
Responsible for:
- storing sources
- capturing justification data
- enriching results with transparency

## Data flow
1. User selects or creates a role.
2. Frontend calls backend API.
3. Backend loads role graph from SQLite.
4. AI is called for qualitative assessment when needed.
5. Scoring engine computes deterministic activity and role impact.
6. Results are persisted.
7. UI displays profile, evidence, and narrative.

## AI flow
AI is not the source of truth. The structured role graph is the source of truth. AI is used only for interpretation, not for final score calculation.

## Persistence
The application uses SQLite to store:
- roles
- processes
- activities
- skills
- assessments
- profiles
- evidence

## Scalability
The architecture is designed for scale by:
- using SQLite indexes
- caching analysis results
- avoiding repeated calls for unchanged inputs
- storing structured results for reuse
- keeping scoring deterministic

## Failure handling
- AI unavailable -> fallback path
- malformed AI response -> fallback
- invalid input -> validation errors
- DB issues -> fail gracefully with logs

## Explainability
Every recommendation can be traced back to:
- activity-level factors
- scoring logic
- evidence
- generated rationale
