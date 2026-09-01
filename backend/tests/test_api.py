"""
Integration tests for the API + persistence.

"""

import os
import sys
import tempfile

# Use an isolated temp DB before importing anything that opens a connection.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["WORKFORCE_DB_PATH"] = _tmp.name
os.environ.pop("AI_GATEWAY_API_KEY", None)  # force fallback path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)


def setup_module(_):
    with TestClient(main.app):  # triggers startup -> init_db + seed
        pass


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_roles_seeded_in_range():
    r = client.get("/roles")
    roles = r.json()["roles"]
    assert 20 <= len(roles) <= 50  # challenge requires 20-50 roles


def test_role_graph_structure():
    role_id = client.get("/roles").json()["roles"][0]["id"]
    r = client.get(f"/roles/{role_id}").json()
    role = r["role"]
    assert role["processes"]
    assert role["processes"][0]["activities"]
    assert "skills" in role["processes"][0]["activities"][0]


def test_analyze_is_deterministic_and_persists():
    role_id = client.get("/roles").json()["roles"][0]["id"]
    a = client.post(f"/roles/{role_id}/analyze").json()
    b = client.post(f"/roles/{role_id}/analyze").json()
    assert a["profile"]["overall_impact"] == b["profile"]["overall_impact"]
    # classifications present
    classes = {x["classification"] for x in a["activities"]}
    assert classes.issubset({"Automate", "Augment", "Human-led"})
    # profile persisted and retrievable
    p = client.get(f"/roles/{role_id}/profile")
    assert p.status_code == 200


def test_analyze_percentages_sum_to_100():
    role_id = client.get("/roles").json()["roles"][0]["id"]
    prof = client.post(f"/roles/{role_id}/analyze").json()["profile"]
    total = prof["automation_pct"] + prof["augmentation_pct"] + prof["human_pct"]
    assert abs(total - 100) < 0.5


def test_add_new_unknown_role_gets_analyzed():
    r = client.post("/roles", json={
        "name": "ESG Data Steward",
        "department": "Sustainability",
        "description": "Collects, validates and reports ESG and climate-risk data.",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["role_id"]
    assert body["analysis"]["profile"]["reskilling_priority"] in ("Low", "Medium", "High")
    assert body["analysis"]["activities"]  # a real graph was generated


def test_compare_two_roles():
    roles = client.get("/roles").json()["roles"]
    r = client.get(f"/compare?a={roles[0]['id']}&b={roles[1]['id']}").json()
    assert "a" in r and "b" in r
    assert r["a"]["profile"]["overall_impact"] is not None


def test_methodology_exposed():
    m = client.get("/methodology").json()
    assert abs(sum(m["weights"].values()) - 1.0) < 1e-9
    assert m["thresholds"]["automate"] == 66.0
