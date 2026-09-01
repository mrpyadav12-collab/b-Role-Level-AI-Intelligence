"""
Data-access layer. All SQL lives here so the rest of the app never touches
the database directly. Facts and AI interpretation are read/written through
clearly separated helpers.
"""

import json
from typing import Any

import db
import seed_data


# Seeding
def is_seeded() -> bool:
    conn = db.get_conn()
    row = conn.execute("SELECT COUNT(*) AS n FROM organizations").fetchone()
    return row["n"] > 0


def seed(force: bool = False) -> dict[str, int]:
    """Populate the database with the fictional organisation. Idempotent."""
    conn = db.get_conn()
    if force:
        for table in [
            "role_profiles", "activity_assessments", "activity_skills", "activities",
            "role_processes", "processes", "roles", "skills", "ai_capabilities",
            "research_evidence", "organizations",
        ]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()

    if is_seeded():
        return _counts()

    org = seed_data.ORGANIZATION
    cur = conn.execute(
        "INSERT INTO organizations (name, industry, description, is_fictional) VALUES (?,?,?,?)",
        (org["name"], org["industry"], org["description"], org["is_fictional"]),
    )
    org_id = cur.lastrowid

    # Skills
    skill_ids: dict[str, int] = {}
    for name, category, desc in seed_data.SKILLS:
        c = conn.execute(
            "INSERT OR IGNORE INTO skills (name, category, description) VALUES (?,?,?)",
            (name, category, desc),
        )
        skill_ids[name] = c.lastrowid or conn.execute(
            "SELECT id FROM skills WHERE name=?", (name,)
        ).fetchone()["id"]

    # AI capabilities
    for name, category, desc, maturity in seed_data.AI_CAPABILITIES:
        conn.execute(
            "INSERT OR IGNORE INTO ai_capabilities (name, category, description, maturity) VALUES (?,?,?,?)",
            (name, category, desc, maturity),
        )

    # Research evidence
    for source, title, url, year, tag, summary in seed_data.RESEARCH:
        conn.execute(
            "INSERT INTO research_evidence (source, title, url, year, tag, summary) VALUES (?,?,?,?,?,?)",
            (source, title, url, year, tag, summary),
        )

    # Roles -> Processes -> Activities -> Skills
    for role in seed_data.ROLES:
        _insert_role_graph(conn, org_id, role, skill_ids, is_ai_generated=False)

    conn.commit()
    return _counts()


def _insert_role_graph(conn, org_id: int, role: dict, skill_ids: dict[str, int], is_ai_generated: bool) -> int:
    cur = conn.execute(
        "INSERT INTO roles (organization_id, name, department, seniority, description, is_ai_generated) VALUES (?,?,?,?,?,?)",
        (org_id, role["name"], role.get("department"), role.get("seniority"),
         role.get("description"), 1 if is_ai_generated else 0),
    )
    role_id = cur.lastrowid

    for proc in role.get("processes", []):
        pc = conn.execute(
            "INSERT INTO processes (name, description) VALUES (?,?)",
            (proc["name"], proc.get("description")),
        )
        process_id = pc.lastrowid
        conn.execute(
            "INSERT OR IGNORE INTO role_processes (role_id, process_id) VALUES (?,?)",
            (role_id, process_id),
        )
        for act in proc.get("activities", []):
            name, ts, rep, rule, data, dcx, hint, skills, desc = act
            ac = conn.execute(
                """INSERT INTO activities
                   (process_id, name, description, time_share, repetitiveness, rule_based,
                    data_availability, decision_complexity, human_interaction)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (process_id, name, desc, ts, rep, rule, data, dcx, hint),
            )
            activity_id = ac.lastrowid
            for s in skills:
                sid = skill_ids.get(s)
                if sid is None:
                    c = conn.execute(
                        "INSERT OR IGNORE INTO skills (name, category) VALUES (?, 'Other')", (s,)
                    )
                    sid = c.lastrowid or conn.execute(
                        "SELECT id FROM skills WHERE name=?", (s,)
                    ).fetchone()["id"]
                    skill_ids[s] = sid
                conn.execute(
                    "INSERT OR IGNORE INTO activity_skills (activity_id, skill_id) VALUES (?,?)",
                    (activity_id, sid),
                )
    return role_id


def _counts() -> dict[str, int]:
    conn = db.get_conn()
    out = {}
    for t in ["organizations", "roles", "processes", "activities", "skills",
              "ai_capabilities", "research_evidence"]:
        out[t] = conn.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"]
    return out


# Reads (facts)
def get_organization() -> dict[str, Any] | None:
    conn = db.get_conn()
    return db.row_to_dict(conn.execute("SELECT * FROM organizations LIMIT 1").fetchone())


def list_roles(search: str | None = None, department: str | None = None) -> list[dict[str, Any]]:
    conn = db.get_conn()
    q = "SELECT * FROM roles WHERE 1=1"
    params: list[Any] = []
    if search:
        q += " AND (name LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if department:
        q += " AND department = ?"
        params.append(department)
    q += " ORDER BY department, name"
    return db.rows_to_dicts(conn.execute(q, params).fetchall())


def list_departments() -> list[str]:
    conn = db.get_conn()
    rows = conn.execute(
        "SELECT DISTINCT department FROM roles WHERE department IS NOT NULL ORDER BY department"
    ).fetchall()
    return [r["department"] for r in rows]


def get_role(role_id: int) -> dict[str, Any] | None:
    conn = db.get_conn()
    return db.row_to_dict(conn.execute("SELECT * FROM roles WHERE id=?", (role_id,)).fetchone())


def get_role_graph(role_id: int) -> dict[str, Any] | None:
    """Return the full Role -> Process -> Activity -> Skill graph as nested dicts."""
    conn = db.get_conn()
    role = get_role(role_id)
    if role is None:
        return None
    processes = db.rows_to_dicts(conn.execute(
        """SELECT p.* FROM processes p
           JOIN role_processes rp ON rp.process_id = p.id
           WHERE rp.role_id = ? ORDER BY p.id""", (role_id,)
    ).fetchall())
    for p in processes:
        acts = db.rows_to_dicts(conn.execute(
            "SELECT * FROM activities WHERE process_id=? ORDER BY id", (p["id"],)
        ).fetchall())
        for a in acts:
            a["skills"] = db.rows_to_dicts(conn.execute(
                """SELECT s.* FROM skills s
                   JOIN activity_skills a2s ON a2s.skill_id = s.id
                   WHERE a2s.activity_id = ? ORDER BY s.name""", (a["id"],)
            ).fetchall())
        p["activities"] = acts
    role["processes"] = processes
    return role


def get_all_activities_for_role(role_id: int) -> list[dict[str, Any]]:
    conn = db.get_conn()
    return db.rows_to_dicts(conn.execute(
        """SELECT a.* FROM activities a
           JOIN role_processes rp ON rp.process_id = a.process_id
           WHERE rp.role_id = ? ORDER BY a.id""", (role_id,)
    ).fetchall())


def get_activity_skills(activity_id: int) -> list[dict[str, Any]]:
    conn = db.get_conn()
    return db.rows_to_dicts(conn.execute(
        """SELECT s.* FROM skills s
           JOIN activity_skills a2s ON a2s.skill_id = s.id
           WHERE a2s.activity_id=? ORDER BY s.name""", (activity_id,)
    ).fetchall())


def list_ai_capabilities() -> list[dict[str, Any]]:
    conn = db.get_conn()
    return db.rows_to_dicts(conn.execute(
        "SELECT * FROM ai_capabilities ORDER BY name"
    ).fetchall())


def evidence_for_tag(tag: str) -> list[dict[str, Any]]:
    conn = db.get_conn()
    return db.rows_to_dicts(conn.execute(
        "SELECT * FROM research_evidence WHERE tag=? ORDER BY year DESC", (tag,)
    ).fetchall())


def all_evidence() -> list[dict[str, Any]]:
    conn = db.get_conn()
    return db.rows_to_dicts(conn.execute(
        "SELECT * FROM research_evidence ORDER BY year DESC, source"
    ).fetchall())


# Writes (new roles)
def create_role(role: dict, is_ai_generated: bool) -> int:
    conn = db.get_conn()
    org = get_organization()
    org_id = org["id"] if org else None
    skill_ids = {r["name"]: r["id"] for r in db.rows_to_dicts(
        conn.execute("SELECT id, name FROM skills").fetchall()
    )}
    role_id = _insert_role_graph(conn, org_id, role, skill_ids, is_ai_generated)
    conn.commit()
    return role_id


# AI interpretation cache (assessments + profiles)
def get_cached_assessment(role_id: int, activity_id: int, content_hash: str) -> dict[str, Any] | None:
    conn = db.get_conn()
    row = conn.execute(
        "SELECT * FROM activity_assessments WHERE role_id=? AND activity_id=? AND content_hash=?",
        (role_id, activity_id, content_hash),
    ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["factors"] = json.loads(d.pop("factors_json"))
    d["ai_capabilities"] = json.loads(d.pop("ai_caps_json"))
    return d


def save_assessment(role_id: int, activity_id: int, factors: dict, ai_caps: list,
                    rationale: str, source: str, content_hash: str) -> None:
    conn = db.get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO activity_assessments
           (role_id, activity_id, factors_json, ai_caps_json, rationale, source, content_hash)
           VALUES (?,?,?,?,?,?,?)""",
        (role_id, activity_id, json.dumps(factors), json.dumps(ai_caps), rationale, source, content_hash),
    )
    conn.commit()


def get_cached_profile(role_id: int, content_hash: str) -> dict[str, Any] | None:
    conn = db.get_conn()
    row = conn.execute(
        "SELECT * FROM role_profiles WHERE role_id=? AND content_hash=? ORDER BY id DESC LIMIT 1",
        (role_id, content_hash),
    ).fetchone()
    return _hydrate_profile(row)


def get_latest_profile(role_id: int) -> dict[str, Any] | None:
    conn = db.get_conn()
    row = conn.execute(
        "SELECT * FROM role_profiles WHERE role_id=? ORDER BY id DESC LIMIT 1", (role_id,)
    ).fetchone()
    return _hydrate_profile(row)


def _hydrate_profile(row) -> dict[str, Any] | None:
    if row is None:
        return None
    d = dict(row)
    d["future_responsibilities"] = json.loads(d.pop("future_responsibilities_json"))
    d["future_skills"] = json.loads(d.pop("future_skills_json"))
    return d


def save_profile(role_id: int, profile: dict, content_hash: str, source: str) -> None:
    conn = db.get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO role_profiles
           (role_id, overall_impact, automation_pct, augmentation_pct, human_pct,
            reskilling_priority, reskilling_index, future_responsibilities_json,
            future_skills_json, narrative, source, content_hash)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (role_id, profile["overall_impact"], profile["automation_pct"],
         profile["augmentation_pct"], profile["human_pct"], profile["reskilling_priority"],
         profile["reskilling_index"], json.dumps(profile["future_responsibilities"]),
         json.dumps(profile["future_skills"]), profile.get("narrative"), source, content_hash),
    )
    conn.commit()


def dashboard_stats() -> dict[str, Any]:
    conn = db.get_conn()
    total_roles = conn.execute("SELECT COUNT(*) AS n FROM roles").fetchone()["n"]
    total_activities = conn.execute("SELECT COUNT(*) AS n FROM activities").fetchone()["n"]
    analyzed = conn.execute(
        "SELECT COUNT(DISTINCT role_id) AS n FROM role_profiles"
    ).fetchone()["n"]
    return {
        "total_roles": total_roles,
        "total_activities": total_activities,
        "analyzed_roles": analyzed,
    }
