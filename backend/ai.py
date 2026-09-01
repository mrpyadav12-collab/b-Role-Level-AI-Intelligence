"""
Replaceable AI layer:-

The LLM is used ONLY for qualitative interpretation:
  * refining activity factor ratings and judging AI-capability fit,
  * suggesting which concrete AI capabilities apply,
  * drafting future responsibilities/skills narratives,
  * proposing a starting Role -> Process -> Activity -> Skill graph for a brand
    new role that has never been seen before.

It NEVER computes scores - that is the deterministic engine's job.

Provider independence:-
We talk to the Vercel AI Gateway over its OpenAI-compatible HTTP endpoint. To
swap providers you only change AI_MODEL (e.g. "openai/gpt-4o-mini",
"anthropic/claude-3-5-haiku", "xai/grok-2"). Nothing else changes.

Resilience:-
Every function has a deterministic fallback. If the key is missing, the network
fails, or the model returns something unparseable, we return a rule-based result
and tag it source="fallback" so the UI can be honest about it. The product is
fully usable with no AI available.
"""

import json
import os
from typing import Any

import httpx

GATEWAY_URL = os.environ.get(
    "AI_GATEWAY_URL", "https://ai-gateway.vercel.sh/v1/chat/completions"
)
AI_MODEL = os.environ.get("AI_MODEL", "openai/gpt-4o-mini")
API_KEY = os.environ.get("AI_GATEWAY_API_KEY")
TIMEOUT = float(os.environ.get("AI_TIMEOUT", "20"))

# Bump this when scoring inputs/prompts change so caches invalidate correctly.
ANALYSIS_VERSION = "v1"


def ai_available() -> bool:
    return bool(API_KEY)


def _call_llm(system: str, user: str) -> dict[str, Any] | None:
    #Return parsed JSON dict from the model, or None on any failure.
    if not API_KEY:
        return None
    try:
        resp = httpx.post(
            GATEWAY_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": AI_MODEL,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001 - resilience is the point
        print(f"[ai] LLM call failed, using fallback: {exc}")
        return None


# 1. Assess a single activity

def _fallback_capability_fit(baseline: dict) -> float:
    """Heuristic AI-capability fit from the activity's observable facts."""
    return round(
        0.45 * baseline["data_availability"]
        + 0.30 * baseline["rule_based"]
        + 0.25 * baseline["repetitiveness"],
        3,
    )


def assess_activity(activity: dict, skills: list[str], ai_capabilities: list[dict]) -> dict:
    """
    Return {factors, ai_capabilities, rationale, source}.
    factors always contains all six scoring inputs (0..1).
    """
    baseline = {
        "repetitiveness": activity["repetitiveness"],
        "rule_based": activity["rule_based"],
        "data_availability": activity["data_availability"],
        "decision_complexity": activity["decision_complexity"],
        "human_interaction": activity["human_interaction"],
    }

    cap_names = [c["name"] for c in ai_capabilities]
    system = (
        "You are an expert workforce analyst assessing how exposed a work activity is to AI. "
        "You output ONLY qualitative 0..1 ratings and short reasoning. You never compute final scores. "
        "Respond in strict JSON."
    )
    user = json.dumps({
        "instruction": (
            "Rate the activity on each factor from 0 to 1. Also rate how well today's proven AI "
            "capabilities fit this activity (ai_capability_fit, 0..1), pick up to 3 relevant "
            "capabilities from the provided list, and give a one-sentence rationale."
        ),
        "activity": {"name": activity["name"], "description": activity.get("description"), "skills": skills},
        "baseline_observations": baseline,
        "available_ai_capabilities": cap_names,
        "response_schema": {
            "factors": {
                "repetitiveness": "0..1", "rule_based": "0..1", "data_availability": "0..1",
                "decision_complexity": "0..1", "human_interaction": "0..1", "ai_capability_fit": "0..1",
            },
            "ai_capabilities": [{"name": "string (from list)", "relevance": "0..1"}],
            "rationale": "string",
        },
    })

    parsed = _call_llm(system, user)
    if parsed and "factors" in parsed:
        f = parsed["factors"]
        factors = {
            "repetitiveness": _num(f.get("repetitiveness"), baseline["repetitiveness"]),
            "rule_based": _num(f.get("rule_based"), baseline["rule_based"]),
            "data_availability": _num(f.get("data_availability"), baseline["data_availability"]),
            "decision_complexity": _num(f.get("decision_complexity"), baseline["decision_complexity"]),
            "human_interaction": _num(f.get("human_interaction"), baseline["human_interaction"]),
            "ai_capability_fit": _num(f.get("ai_capability_fit"), _fallback_capability_fit(baseline)),
        }
        caps = []
        for c in (parsed.get("ai_capabilities") or [])[:3]:
            if isinstance(c, dict) and c.get("name") in cap_names:
                caps.append({"name": c["name"], "relevance": _num(c.get("relevance"), 0.6)})
        if not caps:
            caps = _fallback_caps(baseline, ai_capabilities)
        return {
            "factors": factors,
            "ai_capabilities": caps,
            "rationale": str(parsed.get("rationale") or "").strip()[:500]
            or "AI-refined assessment of the activity's automation exposure.",
            "source": "ai",
        }

    # deterministic fallback --
    factors = dict(baseline)
    factors["ai_capability_fit"] = _fallback_capability_fit(baseline)
    return {
        "factors": factors,
        "ai_capabilities": _fallback_caps(baseline, ai_capabilities),
        "rationale": _fallback_rationale(activity, baseline),
        "source": "fallback",
    }


def _fallback_caps(baseline: dict, ai_capabilities: list[dict]) -> list[dict]:
    #Pick capabilities that match the observable nature of the work.
    picks: list[dict] = []

    def add(name: str, rel: float):
        for c in ai_capabilities:
            if c["name"] == name:
                picks.append({"name": name, "relevance": round(rel, 2)})

    if baseline["data_availability"] > 0.7 and baseline["rule_based"] > 0.7:
        add("Robotic process automation (RPA)", 0.85)
    if baseline["data_availability"] > 0.7:
        add("Document extraction (OCR/NLP)", 0.8)
        add("Automated reconciliation", 0.7)
    if baseline["repetitiveness"] > 0.7:
        add("Predictive analytics / forecasting", 0.65)
    if baseline["human_interaction"] > 0.7:
        add("Conversational AI (assistants)", 0.6)
    if not picks:
        add("Generative drafting (LLM)", 0.6)
        add("Knowledge retrieval (RAG)", 0.55)
    # dedupe, keep top 3
    seen, out = set(), []
    for p in picks:
        if p["name"] not in seen:
            seen.add(p["name"])
            out.append(p)
    return out[:3]


def _fallback_rationale(activity: dict, baseline: dict) -> str:
    if baseline["repetitiveness"] > 0.7 and baseline["rule_based"] > 0.7 and baseline["human_interaction"] < 0.4:
        return "Highly repetitive, rule-based and data-rich work with little human contact - a strong automation candidate."
    if baseline["human_interaction"] > 0.7 or baseline["decision_complexity"] > 0.7:
        return "Complex judgment and/or heavy human interaction keep this activity largely human, with AI as a support tool."
    return "A mix of structured and judgment-based work; best suited to AI augmentation with a human in the loop."



# 2. Future responsibilities & skills for a role
def generate_role_future(role: dict, role_score: dict, activity_summaries: list[dict],
                         top_skills: list[str]) -> dict:
    #Return {future_responsibilities, future_skills, narrative, source}
    system = (
        "You are a workforce strategist. Given a role and its computed AI-impact breakdown, "
        "describe how the role evolves. Be concrete and grounded in the provided numbers. "
        "Respond in strict JSON."
    )
    user = json.dumps({
        "role": {"name": role["name"], "department": role.get("department"),
                 "description": role.get("description")},
        "computed_impact": {
            "overall_impact": role_score["overall_impact"],
            "automation_pct": role_score["automation_pct"],
            "augmentation_pct": role_score["augmentation_pct"],
            "human_pct": role_score["human_pct"],
            "reskilling_priority": role_score["reskilling_priority"],
        },
        "activities": activity_summaries,
        "current_top_skills": top_skills,
        "response_schema": {
            "future_responsibilities": ["string (3-5 items, how the job changes)"],
            "future_skills": ["string (4-6 skills to build, emphasise AI-complementary skills)"],
            "narrative": "string (2-3 sentences)",
        },
    })

    parsed = _call_llm(system, user)
    if parsed and parsed.get("future_responsibilities") and parsed.get("future_skills"):
        return {
            "future_responsibilities": [str(x)[:200] for x in parsed["future_responsibilities"]][:6],
            "future_skills": [str(x)[:120] for x in parsed["future_skills"]][:8],
            "narrative": str(parsed.get("narrative") or "").strip()[:600],
            "source": "ai",
        }

    return _fallback_future(role, role_score, activity_summaries, top_skills)


def _fallback_future(role: dict, role_score: dict, activity_summaries: list[dict],
                     top_skills: list[str]) -> dict:
    automated = [a["name"] for a in activity_summaries if a["classification"] == "Automate"]
    augmented = [a["name"] for a in activity_summaries if a["classification"] == "Augment"]
    human = [a["name"] for a in activity_summaries if a["classification"] == "Human-led"]

    responsibilities = []
    if automated:
        responsibilities.append(
            f"Supervise and quality-check AI systems that now handle: {', '.join(automated[:3])}."
        )
    if augmented:
        responsibilities.append(
            f"Work alongside AI to accelerate: {', '.join(augmented[:3])}, focusing on exceptions and judgment."
        )
    if human:
        responsibilities.append(
            f"Own the human-critical work: {', '.join(human[:3])}."
        )
    responsibilities.append("Continuously validate AI outputs for accuracy, fairness, and compliance.")
    if role_score["reskilling_priority"] in ("High", "Medium"):
        responsibilities.append("Redirect freed-up time toward higher-value client and strategic work.")

    future_skills = ["AI tool orchestration", "Prompt & workflow design", "Exception handling",
                     "Judgment & decision-making", "Data storytelling"]
    for s in top_skills:
        if s not in future_skills and len(future_skills) < 8:
            future_skills.append(s)

    narrative = (
        f"With an overall AI-impact of {role_score['overall_impact']}, the {role['name']} role shifts "
        f"from doing routine work toward directing AI and handling exceptions. Reskilling priority is "
        f"{role_score['reskilling_priority'].lower()}."
    )
    return {
        "future_responsibilities": responsibilities[:6],
        "future_skills": future_skills[:8],
        "narrative": narrative,
        "source": "fallback",
    }


# 3. Discover a brand-new role's process/activity/skill graph
def discover_role_graph(name: str, department: str | None, description: str | None,
                        known_skills: list[str]) -> dict:
    system = (
        "You are a job architecture expert. Decompose a role into 1-3 business processes, each with "
        "2-4 concrete activities. For every activity estimate factors 0..1: repetitiveness, rule_based, "
        "data_availability, decision_complexity, human_interaction, plus a relative time_share (0..1) and "
        "2-4 required skills. Respond in strict JSON."
    )
    user = json.dumps({
        "role": {"name": name, "department": department, "description": description},
        "prefer_skills_from": known_skills,
        "response_schema": {
            "processes": [{
                "name": "string", "description": "string",
                "activities": [{
                    "name": "string", "description": "string", "time_share": "0..1",
                    "repetitiveness": "0..1", "rule_based": "0..1", "data_availability": "0..1",
                    "decision_complexity": "0..1", "human_interaction": "0..1",
                    "skills": ["string"],
                }],
            }],
        },
    })

    parsed = _call_llm(system, user)
    if parsed and parsed.get("processes"):
        processes = []
        for p in parsed["processes"][:3]:
            acts = []
            for a in (p.get("activities") or [])[:4]:
                acts.append((
                    str(a.get("name", "Activity"))[:120],
                    _num(a.get("time_share"), 0.5),
                    _num(a.get("repetitiveness"), 0.5),
                    _num(a.get("rule_based"), 0.5),
                    _num(a.get("data_availability"), 0.5),
                    _num(a.get("decision_complexity"), 0.5),
                    _num(a.get("human_interaction"), 0.5),
                    [str(s)[:60] for s in (a.get("skills") or [])][:4],
                    str(a.get("description", ""))[:300],
                ))
            if acts:
                processes.append({
                    "name": str(p.get("name", "Process"))[:120],
                    "description": str(p.get("description", ""))[:300],
                    "activities": acts,
                })
        if processes:
            return {
                "role": {"name": name, "department": department, "description": description,
                         "processes": processes},
                "source": "ai",
            }

    return _fallback_role_graph(name, department, description)


def _fallback_role_graph(name: str, department: str | None, description: str | None) -> dict:
    """Generic-but-reasonable decomposition when AI is unavailable."""
    processes = [{
        "name": f"{name} Core Workflow",
        "description": f"Primary responsibilities of a {name}.",
        "activities": [
            ("Collect and process routine information", 0.8, 0.8, 0.8, 0.85, 0.3, 0.3,
             ["Data entry", "Attention to detail"], "Gather and record structured information."),
            ("Analyse information and prepare outputs", 0.7, 0.55, 0.6, 0.75, 0.6, 0.35,
             ["Financial analysis", "Spreadsheet modeling"], "Turn inputs into analysis/outputs."),
            ("Communicate and decide with stakeholders", 0.6, 0.3, 0.4, 0.5, 0.8, 0.85,
             ["Communication", "Judgment & decision-making", "Stakeholder management"],
             "Exercise judgment and coordinate with people."),
        ],
    }]
    return {
        "role": {"name": name, "department": department, "description": description,
                 "processes": processes},
        "source": "fallback",
    }

def _num(v: Any, default: float) -> float:
    try:
        x = float(v)
        return max(0.0, min(1.0, x))
    except (TypeError, ValueError):
        return float(default)
