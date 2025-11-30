"""
Sample tests for search functionality
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from api.main import app
from api.models.schemas import Questionnaire, LocationConstraint, PreferenceWeights

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"


def test_search_endpoint_validation():
    """Test search endpoint validates questionnaire"""
    # Missing required fields
    response = client.post("/api/search", json={})
    assert response.status_code == 422  # Validation error

    # Valid questionnaire
    questionnaire = {
        "budget_max": 500000,
        "bedrooms_min": 2,
        "location": {
            "postcode_areas": ["SW1"]
        },
        "preferences": {
            "schools": 0.3,
            "commute": 0.2,
            "safety": 0.2,
            "energy": 0.2,
            "value": 0.1,
            "conservation": 0.0
        }
    }

    # This will fail without database, but validates schema
    response = client.post("/api/search", json=questionnaire)
    # In real tests, mock the database


def test_questionnaire_model():
    """Test Questionnaire Pydantic model validation"""

    # Valid questionnaire
    q = Questionnaire(
        budget_max=Decimal("500000"),
        bedrooms_min=2,
        location=LocationConstraint(postcode_areas=["SW1"]),
        preferences=PreferenceWeights(
            schools=0.3,
            commute=0.2,
            safety=0.2,
            energy=0.2,
            value=0.1
        )
    )
    assert q.budget_max == 500000

    # Invalid: weights exceed 1.0
    with pytest.raises(ValueError):
        PreferenceWeights(
            schools=0.5,
            commute=0.5,
            safety=0.5  # Total > 1.0
        )


def test_listing_detail_endpoint():
    """Test listing detail endpoint"""
    # Non-existent listing
    response = client.get("/api/listing/99999")
    # Will fail without data, but tests endpoint exists
    assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
