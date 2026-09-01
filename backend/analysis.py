"""
Analysis orchestration.

Pipeline for a role:
    1. Load the role's activities (facts).
    2. For each activity: get an AI (or fallback) assessment -> factor ratings.
       Assessments are CACHED by a content hash so we don't re-call the LLM for
       unchanged inputs (this is the main LLM-cost control).
    3. Feed factors into the deterministic scoring engine -> per-activity score.
    4. Aggregate to a role-level score (deterministic).
    5. Ask AI (or fallback) for future responsibilities/skills narrative.
    6. Persist the profile (cached by hash) and return it.

The numeric results are 100% deterministic; only the qualitative factor ratings
and narrative come from AI, and both degrade gracefully.
"""

import hashlib
import json

import ai
import repository as repo
import scoring


def _activity_hash(activity: dict) -> str:
    payload = json.dumps({
        "v": ai.ANALYSIS_VERSION,
        "name": activity["name"],
        "facts": {
            "repetitiveness": activity["repetitiveness"],
            "rule_based": activity["rule_based"],
            "data_availability": activity["data_availability"],
            "decision_complexity": activity["decision_complexity"],
            "human_interaction": activity["human_interaction"],
        },
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _assess_activity(role_id: int, activity: dict, ai_caps: list[dict]) -> dict:
    """Return an assessment dict, using cache when possible."""
    content_hash = _activity_hash(activity)
    cached = repo.get_cached_assessment(role_id, activity["id"], content_hash)
    if cached:
        return {
            "factors": cached["factors"],
            "ai_capabilities": cached["ai_capabilities"],
            "rationale": cached["rationale"],
            "source": cached["source"],
            "cached": True,
        }

    skills = [s["name"] for s in repo.get_activity_skills(activity["id"])]
    result = ai.assess_activity(activity, skills, ai_caps)
    repo.save_assessment(
        role_id, activity["id"], result["factors"], result["ai_capabilities"],
        result["rationale"], result["source"], content_hash,
    )
    result["cached"] = False
    return result


def analyze_role(role_id: int, force: bool = False) -> dict | None:
    role = repo.get_role(role_id)
    if role is None:
        return None

    activities = repo.get_all_activities_for_role(role_id)
    ai_caps = repo.list_ai_capabilities()

    # Overall cache key = hash of every activity hash (so any change re-analyses).
    combined = hashlib.sha256(
        ("|".join(_activity_hash(a) for a in activities) + ai.ANALYSIS_VERSION).encode()
    ).hexdigest()[:16]

    if not force:
        cached_profile = repo.get_cached_profile(role_id, combined)
        if cached_profile:
            return _assemble(role, activities, ai_caps, role_id, cached_profile, from_cache=True)

    # Assess every activity and score it deterministically.
    activity_scores = []
    assessments: dict[int, dict] = {}
    sources = set()
    for a in activities:
        assessment = _assess_activity(role_id, a, ai_caps)
        assessments[a["id"]] = assessment
        sources.add(assessment["source"])
        s = scoring.score_activity(a["id"], a["name"], a["time_share"], assessment["factors"])
        activity_scores.append(s)

    role_score = scoring.score_role(activity_scores)
    role_score_dict = role_score.to_dict()

    # Future outlook (AI or fallback).
    top_skills = _top_skills(activities)
    activity_summaries = [
        {"name": s.name, "classification": s.classification, "impact": round(s.impact, 1)}
        for s in activity_scores
    ]
    future = ai.generate_role_future(role, role_score_dict, activity_summaries, top_skills)
    sources.add(future["source"])

    profile = {
        "overall_impact": role_score.overall_impact,
        "automation_pct": role_score.automation_pct,
        "augmentation_pct": role_score.augmentation_pct,
        "human_pct": role_score.human_pct,
        "reskilling_priority": role_score.reskilling_priority,
        "reskilling_index": role_score.reskilling_index,
        "future_responsibilities": future["future_responsibilities"],
        "future_skills": future["future_skills"],
        "narrative": future["narrative"],
    }
    overall_source = "ai" if "ai" in sources else "fallback"
    repo.save_profile(role_id, profile, combined, overall_source)

    return _assemble(role, activities, ai_caps, role_id,
                     {**profile, "source": overall_source}, from_cache=False,
                     precomputed=(activity_scores, assessments))


def _assemble(role, activities, ai_caps, role_id, profile, from_cache, precomputed=None):
    """Build the full response payload including per-activity detail + evidence."""
    if precomputed:
        activity_scores, assessments = precomputed
    else:
        # Rebuild per-activity detail from cache for a cached profile.
        activity_scores, assessments = [], {}
        for a in activities:
            assessment = _assess_activity(role_id, a, ai_caps)
            assessments[a["id"]] = assessment
            activity_scores.append(
                scoring.score_activity(a["id"], a["name"], a["time_share"], assessment["factors"])
            )

    # Map activities to their process for grouping in the UI.
    graph = repo.get_role_graph(role_id)
    process_by_activity = {}
    for p in graph["processes"]:
        for a in p["activities"]:
            process_by_activity[a["id"]] = {"process_id": p["id"], "process_name": p["name"]}

    activities_out = []
    for s in activity_scores:
        assessment = assessments[s.activity_id]
        activities_out.append({
            **s.to_dict(),
            "process": process_by_activity.get(s.activity_id, {}),
            "rationale": assessment["rationale"],
            "ai_capabilities": assessment["ai_capabilities"],
            "assessment_source": assessment["source"],
        })

    tag = _dominant_tag(profile)
    evidence = repo.evidence_for_tag(tag)

    return {
        "role": {k: role[k] for k in role.keys()},
        "profile": {
            "overall_impact": round(profile["overall_impact"], 1),
            "automation_pct": round(profile["automation_pct"], 1),
            "augmentation_pct": round(profile["augmentation_pct"], 1),
            "human_pct": round(profile["human_pct"], 1),
            "reskilling_priority": profile["reskilling_priority"],
            "reskilling_index": round(profile["reskilling_index"], 1),
            "future_responsibilities": profile["future_responsibilities"],
            "future_skills": profile["future_skills"],
            "narrative": profile.get("narrative"),
            "source": profile.get("source", "fallback"),
        },
        "activities": activities_out,
        "methodology": scoring.explain_weights(),
        "evidence": evidence,
        "ai_available": ai.ai_available(),
        "from_cache": from_cache,
    }


def _dominant_tag(profile) -> str:
    if profile["automation_pct"] >= profile["augmentation_pct"] and profile["automation_pct"] >= profile["human_pct"]:
        return "automation"
    if profile["human_pct"] >= profile["augmentation_pct"]:
        return "human"
    return "augmentation"


def _top_skills(activities) -> list[str]:
    counts: dict[str, int] = {}
    for a in activities:
        for s in repo.get_activity_skills(a["id"]):
            counts[s["name"]] = counts.get(s["name"], 0) + 1
    return [k for k, _ in sorted(counts.items(), key=lambda kv: -kv[1])][:8]


def add_new_role(name: str, department: str | None, description: str | None) -> int:
    """Discover the graph for a brand-new role and persist it."""
    known_skills = [s["name"] for s in repo.db.rows_to_dicts(
        repo.db.get_conn().execute("SELECT name FROM skills").fetchall()
    )]
    discovered = ai.discover_role_graph(name, department, description, known_skills)
    role_dict = discovered["role"]
    role_dict.setdefault("seniority", "Mid")
    role_id = repo.create_role(role_dict, is_ai_generated=True)
    return role_id
