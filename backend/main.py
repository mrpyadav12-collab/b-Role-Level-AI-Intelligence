"""
FastAPI backend for the Role-Level AI Intelligence project.

Routes are declared WITHOUT the '/api' prefix; Vercel's services layer strips
the prefix before forwarding, so locally and in production the frontend calls
'/api/...' and this app sees '/...'.
"""

import os
import sys
from contextlib import asynccontextmanager

# Make sibling modules importable regardless of the process working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fastapi
import fastapi.middleware.cors
from pydantic import BaseModel, Field

import analysis
import db
import repository as repo


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    db.init_db()
    # Seed on first boot so the app is immediately usable.
    if not repo.is_seeded():
        repo.seed()
    yield


app = fastapi.FastAPI(title="Role-Level AI Intelligence", lifespan=lifespan)

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "ai_available": bool(os.environ.get("AI_GATEWAY_API_KEY"))}


@app.get("/organization")
async def organization() -> dict:
    org = repo.get_organization()
    if org is None:
        raise fastapi.HTTPException(status_code=404, detail="No organization seeded")
    return org


@app.get("/dashboard")
async def dashboard() -> dict:
    stats = repo.dashboard_stats()
    org = repo.get_organization()
    return {
        "organization": org,
        "stats": stats,
        "departments": repo.list_departments(),
        "ai_available": bool(os.environ.get("AI_GATEWAY_API_KEY")),
    }


@app.get("/roles")
async def roles(search: str | None = None, department: str | None = None) -> dict:
    return {"roles": repo.list_roles(search=search, department=department)}


@app.get("/roles/{role_id}")
async def role_detail(role_id: int) -> dict:
    graph = repo.get_role_graph(role_id)
    if graph is None:
        raise fastapi.HTTPException(status_code=404, detail="Role not found")
    latest = repo.get_latest_profile(role_id)
    return {"role": graph, "profile": latest}


@app.post("/roles/{role_id}/analyze")
async def analyze(role_id: int, force: bool = False) -> dict:
    try:
        result = analysis.analyze_role(role_id, force=force)
    except Exception as exc:  # noqa: BLE001
        raise fastapi.HTTPException(status_code=500, detail=f"Analysis failed: {exc}")
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail="Role not found")
    return result


@app.get("/roles/{role_id}/profile")
async def profile(role_id: int) -> dict:
    p = repo.get_latest_profile(role_id)
    if p is None:
        raise fastapi.HTTPException(
            status_code=404, detail="Role not analyzed yet. Run /analyze first."
        )
    return p


class NewRole(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


@app.post("/roles")
async def create_role(body: NewRole) -> dict:
    """Add a brand-new role: AI proposes its process/activity/skill graph, then it is analyzed."""
    try:
        role_id = analysis.add_new_role(body.name, body.department, body.description)
        result = analysis.analyze_role(role_id, force=True)
    except Exception as exc:  # noqa: BLE001
        raise fastapi.HTTPException(status_code=500, detail=f"Could not create role: {exc}")
    return {"role_id": role_id, "analysis": result}


@app.get("/compare")
async def compare(a: int, b: int) -> dict:
    """Compare two roles side by side."""
    ra = analysis.analyze_role(a)
    rb = analysis.analyze_role(b)
    if ra is None or rb is None:
        raise fastapi.HTTPException(status_code=404, detail="One or both roles not found")
    return {"a": ra, "b": rb}


@app.get("/evidence")
async def evidence() -> dict:
    return {"evidence": repo.all_evidence()}


@app.get("/methodology")
async def methodology() -> dict:
    import scoring
    return scoring.explain_weights()


class SeedBody(BaseModel):
    force: bool = False


@app.post("/seed")
async def seed(body: SeedBody) -> dict:
    counts = repo.seed(force=body.force)
    return {"seeded": True, "counts": counts}
