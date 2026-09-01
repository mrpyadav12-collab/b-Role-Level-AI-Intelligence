"""Unit tests for the deterministic scoring engine (no AI involved)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scoring


def test_weights_sum_to_one():
    assert abs(sum(scoring.WEIGHTS.values()) - 1.0) < 1e-9


def test_highly_automatable_activity_scores_high():
    factors = {
        "repetitiveness": 0.95, "rule_based": 0.95, "data_availability": 0.95,
        "decision_complexity": 0.1, "human_interaction": 0.1, "ai_capability_fit": 0.9,
    }
    s = scoring.score_activity(1, "Process payments", 1.0, factors)
    assert s.impact >= scoring.AUTOMATE_THRESHOLD
    assert s.classification == "Automate"


def test_human_activity_scores_low():
    factors = {
        "repetitiveness": 0.1, "rule_based": 0.15, "data_availability": 0.2,
        "decision_complexity": 0.9, "human_interaction": 0.95, "ai_capability_fit": 0.2,
    }
    s = scoring.score_activity(2, "Advise client", 1.0, factors)
    assert s.impact < scoring.AUGMENT_THRESHOLD
    assert s.classification == "Human-led"


def test_middle_activity_is_augment():
    factors = {
        "repetitiveness": 0.5, "rule_based": 0.5, "data_availability": 0.5,
        "decision_complexity": 0.5, "human_interaction": 0.5, "ai_capability_fit": 0.5,
    }
    s = scoring.score_activity(3, "Mixed work", 1.0, factors)
    assert s.classification == "Augment"
    assert abs(s.impact - 50.0) < 1e-6


def test_deterministic_same_input_same_output():
    factors = {
        "repetitiveness": 0.7, "rule_based": 0.6, "data_availability": 0.8,
        "decision_complexity": 0.4, "human_interaction": 0.3, "ai_capability_fit": 0.6,
    }
    a = scoring.score_activity(4, "x", 1.0, factors)
    b = scoring.score_activity(4, "x", 1.0, factors)
    assert a.impact == b.impact


def test_contributions_sum_to_impact():
    factors = {
        "repetitiveness": 0.7, "rule_based": 0.6, "data_availability": 0.8,
        "decision_complexity": 0.4, "human_interaction": 0.3, "ai_capability_fit": 0.6,
    }
    s = scoring.score_activity(5, "x", 1.0, factors)
    assert abs(sum(s.contributions.values()) - s.impact) < 1e-6


def test_role_aggregation_and_reskilling():
    auto = scoring.score_activity(1, "auto", 1.0, {
        "repetitiveness": 0.95, "rule_based": 0.95, "data_availability": 0.95,
        "decision_complexity": 0.1, "human_interaction": 0.1, "ai_capability_fit": 0.9})
    human = scoring.score_activity(2, "human", 1.0, {
        "repetitiveness": 0.1, "rule_based": 0.15, "data_availability": 0.2,
        "decision_complexity": 0.9, "human_interaction": 0.95, "ai_capability_fit": 0.2})
    role = scoring.score_role([auto, human])
    assert 0 <= role.overall_impact <= 100
    assert abs((role.automation_pct + role.augmentation_pct + role.human_pct) - 100) < 1e-6
    assert role.reskilling_priority in ("Low", "Medium", "High")


def test_time_share_weights_overall():
    high = scoring.score_activity(1, "auto", 9.0, {
        "repetitiveness": 0.95, "rule_based": 0.95, "data_availability": 0.95,
        "decision_complexity": 0.1, "human_interaction": 0.1, "ai_capability_fit": 0.9})
    low = scoring.score_activity(2, "human", 1.0, {
        "repetitiveness": 0.1, "rule_based": 0.15, "data_availability": 0.2,
        "decision_complexity": 0.9, "human_interaction": 0.95, "ai_capability_fit": 0.2})
    role = scoring.score_role([high, low])
    assert role.overall_impact > 60
