"""
Deterministic scoring engine.

This module contains NO AI calls. Given a set of factor ratings (0..1) for an
activity, it produces a reproducible AI-impact score, a classification, and a
full explanation of how the number was reached. The AI layer may *provide* the
factor ratings, but it never computes the score - that keeps results
explainable, testable, and auditable (same inputs -> same outputs).

Score formula
-------------
    impact = 100 * sum(weight_i * signal_i)

where each signal is oriented so that a higher value always means "more
automatable":

    repetitiveness        (as-is)
    rule_based            (as-is)
    data_availability     (as-is)
    ai_capability_fit     (as-is)
    decision_simplicity   = 1 - decision_complexity
    low_human_interaction = 1 - human_interaction

Weights sum to 1.0 (documented below).

Classification thresholds
-------------------------
    impact >= 66            -> "Automate"     (candidate for full automation)
    33 <= impact < 66       -> "Augment"      (AI assists, human stays in loop)
    impact < 33             -> "Human-led"    (remains human work)
"""

from dataclasses import dataclass, field

# Documented, tunable weights. They MUST sum to 1.0 (asserted below).
WEIGHTS: dict[str, float] = {
    "repetitiveness": 0.20,
    "rule_based": 0.20,
    "data_availability": 0.15,
    "decision_simplicity": 0.15,     # derived from 1 - decision_complexity
    "low_human_interaction": 0.15,   # derived from 1 - human_interaction
    "ai_capability_fit": 0.15,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Scoring weights must sum to 1.0"

AUTOMATE_THRESHOLD = 66.0
AUGMENT_THRESHOLD = 33.0

FACTOR_KEYS = [
    "repetitiveness", "rule_based", "data_availability",
    "decision_complexity", "human_interaction", "ai_capability_fit",
]


@dataclass
class ActivityScore:
    activity_id: int
    name: str
    time_share: float
    impact: float
    classification: str
    signals: dict[str, float]
    contributions: dict[str, float]
    factors: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "time_share": self.time_share,
            "impact": round(self.impact, 1),
            "classification": self.classification,
            "signals": {k: round(v, 3) for k, v in self.signals.items()},
            "contributions": {k: round(v, 2) for k, v in self.contributions.items()},
            "factors": {k: round(v, 3) for k, v in self.factors.items()},
        }


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def classify(impact: float) -> str:
    if impact >= AUTOMATE_THRESHOLD:
        return "Automate"
    if impact >= AUGMENT_THRESHOLD:
        return "Augment"
    return "Human-led"


def score_activity(activity_id: int, name: str, time_share: float, factors: dict) -> ActivityScore:
    """Score a single activity from its factor ratings (0..1)."""
    f = {k: _clamp(factors.get(k, 0.5)) for k in FACTOR_KEYS}

    signals = {
        "repetitiveness": f["repetitiveness"],
        "rule_based": f["rule_based"],
        "data_availability": f["data_availability"],
        "decision_simplicity": 1.0 - f["decision_complexity"],
        "low_human_interaction": 1.0 - f["human_interaction"],
        "ai_capability_fit": f["ai_capability_fit"],
    }
    contributions = {k: WEIGHTS[k] * signals[k] * 100.0 for k in WEIGHTS}
    impact = sum(contributions.values())

    return ActivityScore(
        activity_id=activity_id,
        name=name,
        time_share=max(0.0, float(time_share)),
        impact=impact,
        classification=classify(impact),
        signals=signals,
        contributions=contributions,
        factors=f,
    )


@dataclass
class RoleScore:
    overall_impact: float
    automation_pct: float
    augmentation_pct: float
    human_pct: float
    reskilling_index: float
    reskilling_priority: str
    activity_scores: list[ActivityScore] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_impact": round(self.overall_impact, 1),
            "automation_pct": round(self.automation_pct, 1),
            "augmentation_pct": round(self.augmentation_pct, 1),
            "human_pct": round(self.human_pct, 1),
            "reskilling_index": round(self.reskilling_index, 1),
            "reskilling_priority": self.reskilling_priority,
            "activities": [a.to_dict() for a in self.activity_scores],
        }


def reskilling_priority(reskilling_index: float) -> str:
    """Higher index -> more of the role's work is changing -> higher urgency."""
    if reskilling_index >= 60:
        return "High"
    if reskilling_index >= 35:
        return "Medium"
    return "Low"


def score_role(activity_scores: list[ActivityScore]) -> RoleScore:
    """Aggregate activity scores into a role-level result, weighted by time share."""
    if not activity_scores:
        return RoleScore(0, 0, 0, 0, 0, "Low", [])

    total_w = sum(a.time_share for a in activity_scores) or float(len(activity_scores))
    weights = [(a.time_share or 1.0) / total_w for a in activity_scores]

    overall = sum(w * a.impact for w, a in zip(weights, activity_scores))

    auto = sum(w for w, a in zip(weights, activity_scores) if a.classification == "Automate") * 100
    aug = sum(w for w, a in zip(weights, activity_scores) if a.classification == "Augment") * 100
    human = sum(w for w, a in zip(weights, activity_scores) if a.classification == "Human-led") * 100

    # Reskilling need is driven mostly by work that is being automated away, and
    # partly by work that is being augmented (people must learn to work with AI).
    reskilling_index = min(100.0, auto * 1.0 + aug * 0.6)

    return RoleScore(
        overall_impact=overall,
        automation_pct=auto,
        augmentation_pct=aug,
        human_pct=human,
        reskilling_index=reskilling_index,
        reskilling_priority=reskilling_priority(reskilling_index),
        activity_scores=activity_scores,
    )


def explain_weights() -> dict:
    """Expose the methodology so the UI can render a transparent explanation."""
    return {
        "weights": WEIGHTS,
        "thresholds": {
            "automate": AUTOMATE_THRESHOLD,
            "augment": AUGMENT_THRESHOLD,
        },
        "signal_definitions": {
            "repetitiveness": "How repetitive/predictable the activity is (fact).",
            "rule_based": "How well the activity follows explicit rules (fact).",
            "data_availability": "How much structured digital data is available (fact).",
            "decision_simplicity": "1 - decision_complexity: simpler decisions are easier to automate.",
            "low_human_interaction": "1 - human_interaction: less human contact is easier to automate.",
            "ai_capability_fit": "How well current, proven AI capabilities match the activity.",
        },
        "formula": "impact = 100 * sum(weight_i * signal_i)",
    }
