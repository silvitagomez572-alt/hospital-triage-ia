from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_predict_valid_input():
    resp = client.post("/predict", json={
        "age": 70,
        "pain_level": 9,
        "systolic_bp": 80,
        "diastolic_bp": 50,
        "heart_rate": 120,
        "temperature": 38.5
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_level" in data
    assert "probability" in data

def test_predict_invalid_input():
    resp = client.post("/predict", json={
        "age": -5,
        "pain_level": 3,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "heart_rate": 75,
        "temperature": 36.5
    })
    assert resp.status_code == 422
