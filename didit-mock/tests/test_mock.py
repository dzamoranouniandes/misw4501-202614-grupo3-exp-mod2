from fastapi.testclient import TestClient

from app.main import app


def test_mock_returns_passed_for_approved_synthetic_evidence() -> None:
    response = TestClient(app).post(
        "/v1/liveness/checks",
        json={"subject_reference": "customer-1", "selfie_reference": "synthetic-selfie-approved"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "PASSED"


def test_mock_returns_failed_for_rejected_synthetic_evidence() -> None:
    response = TestClient(app).post(
        "/v1/liveness/checks",
        json={"subject_reference": "customer-1", "selfie_reference": "synthetic-selfie-rejected"},
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "FAILED"

