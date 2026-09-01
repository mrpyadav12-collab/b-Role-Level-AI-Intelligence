"""
SQLite database layer.

Design notes
------------
- A single persistent SQLite file (`workforce.db`) is the system of record.
  Every write is committed, so data survives process restarts within the
  running environment (this is what the "persistence test" verifies).
- The schema models the required graph explicitly:
      Role --< role_processes >-- Process --< activities >-- activity_skills >-- Skill
- Ground-truth FACTS (roles, processes, activities, skills, ai_capabilities,
  research_evidence) are stored separately from AI INTERPRETATION
  (activity_assessments, role_profiles). This separation is deliberate so we
  can always show "what is fact" vs "what the model inferred".
- All foreign keys are indexed for scale (thousands of activities).
"""

import os
import sqlite3
import threading
from typing import Any

# Store the DB next to this file so the path is stable regardless of CWD.
DB_PATH = os.environ.get(
    "WORKFORCE_DB_PATH", os.path.join(os.path.dirname(__file__), "workforce.db")
)

_local = threading.local()


def get_conn() -> sqlite3.Connection:
    """Return a thread-local connection with sane defaults."""
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        _local.conn = conn
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    industry      TEXT NOT NULL,
    description   TEXT,
    is_fictional  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS roles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    department      TEXT,
    seniority       TEXT,
    description     TEXT,
    is_ai_generated INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_roles_org ON roles(organization_id);
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(organization_id, name);

CREATE TABLE IF NOT EXISTS processes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_processes (
    role_id     INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    process_id  INTEGER NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, process_id)
);
CREATE INDEX IF NOT EXISTS idx_rp_role ON role_processes(role_id);
CREATE INDEX IF NOT EXISTS idx_rp_process ON role_processes(process_id);

-- Activities are the atomic unit of work and carry the observable, ground-truth
-- characteristics used by the deterministic scoring engine.
CREATE TABLE IF NOT EXISTS activities (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id         INTEGER NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    name               TEXT NOT NULL,
    description        TEXT,
    time_share         REAL NOT NULL DEFAULT 1.0,   -- relative weight of this activity in the process
    repetitiveness     REAL NOT NULL DEFAULT 0.5,   -- 0..1 fact
    rule_based         REAL NOT NULL DEFAULT 0.5,   -- 0..1 fact
    data_availability  REAL NOT NULL DEFAULT 0.5,   -- 0..1 fact
    decision_complexity REAL NOT NULL DEFAULT 0.5,  -- 0..1 fact (higher = harder to automate)
    human_interaction  REAL NOT NULL DEFAULT 0.5    -- 0..1 fact (higher = harder to automate)
);
CREATE INDEX IF NOT EXISTS idx_act_process ON activities(process_id);

CREATE TABLE IF NOT EXISTS skills (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS activity_skills (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    skill_id    INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, skill_id)
);
CREATE INDEX IF NOT EXISTS idx_as_activity ON activity_skills(activity_id);
CREATE INDEX IF NOT EXISTS idx_as_skill ON activity_skills(skill_id);

CREATE TABLE IF NOT EXISTS ai_capabilities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    category    TEXT,
    description TEXT,
    maturity    REAL NOT NULL DEFAULT 0.5  -- 0..1 how proven the capability is today
);

CREATE TABLE IF NOT EXISTS research_evidence (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    title       TEXT NOT NULL,
    url         TEXT,
    year        INTEGER,
    tag         TEXT,       -- keyword this evidence supports (e.g. 'automation', 'reskilling')
    summary     TEXT
);
CREATE INDEX IF NOT EXISTS idx_evidence_tag ON research_evidence(tag);

-- ===== AI INTERPRETATION (kept separate from facts) =====

CREATE TABLE IF NOT EXISTS activity_assessments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id       INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    activity_id   INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    factors_json  TEXT NOT NULL,   -- factors actually used (AI-refined or baseline)
    ai_caps_json  TEXT NOT NULL,   -- suggested AI capabilities + relevance
    rationale     TEXT,            -- natural-language explanation
    source        TEXT NOT NULL,   -- 'ai' | 'fallback'
    content_hash  TEXT NOT NULL,   -- cache key
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_assess_role ON activity_assessments(role_id);
CREATE INDEX IF NOT EXISTS idx_assess_activity ON activity_assessments(activity_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_assess_hash ON activity_assessments(role_id, activity_id, content_hash);

CREATE TABLE IF NOT EXISTS role_profiles (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id                   INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    overall_impact            REAL NOT NULL,
    automation_pct            REAL NOT NULL,
    augmentation_pct          REAL NOT NULL,
    human_pct                 REAL NOT NULL,
    reskilling_priority       TEXT NOT NULL,
    reskilling_index          REAL NOT NULL,
    future_responsibilities_json TEXT NOT NULL,
    future_skills_json        TEXT NOT NULL,
    narrative                 TEXT,
    source                    TEXT NOT NULL,   -- 'ai' | 'fallback'
    content_hash              TEXT NOT NULL,
    created_at                TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_profile_role ON role_profiles(role_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_profile_hash ON role_profiles(role_id, content_hash);
"""


def init_db() -> None:
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]
