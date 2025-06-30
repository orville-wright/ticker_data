import pytest
import requests

# This assumes a running instance of the application, with a base URL.
# In a real CI/CD pipeline, this would be the URL of the staging environment.
BASE_URL = "http://localhost:5000/api"

# A known stock symbol that should always exist in the test database
KNOWN_STOCK = "AAPL"
# An unlikely stock symbol that should not exist
UNKNOWN_STOCK = "UNKNOWNSTOCKXYZ"


def test_get_prediction_for_known_stock():
    """
    Corresponds to Test ID E2E-01.
    Verifies the success case for retrieving a prediction for a valid stock.
    Completion Criterion: AI can verify the response code and the structure of the JSON payload.
    """
    response = requests.get(f"{BASE_URL}/stocks/{KNOWN_STOCK}/prediction")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "symbol" in data
    assert "name" in data
    assert "signal" in data
    assert "confidence" in data
    assert "timestamp" in data
    assert data["signal"] in ["BUY", "SELL", "HOLD"]
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0


def test_get_prediction_for_unknown_stock():
    """
    Corresponds to Test ID E2E-02.
    Verifies the error case for retrieving a prediction for an invalid stock.
    Completion Criterion: AI can verify the response code is 404.
    """
    response = requests.get(f"{BASE_URL}/stocks/{UNKNOWN_STOCK}/prediction")
    assert response.status_code == 404


def test_search_by_ticker():
    """
    Corresponds to Test ID E2E-03.
    Verifies that searching by a ticker fragment returns a list of stocks.
    Completion Criterion: AI can verify the response code and that the payload is a list of dicts with the correct keys.
    """
    response = requests.get(f"{BASE_URL}/stocks/search?q=AAP")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert "symbol" in item
            assert "name" in item


def test_search_by_name():
    """
    Corresponds to Test ID E2E-04.
    Verifies that searching by a company name fragment returns a list of stocks.
    Completion Criterion: AI can verify the response code and that the payload is a list of dicts with the correct keys.
    """
    response = requests.get(f"{BASE_URL}/stocks/search?q=Apple")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert "symbol" in item
            assert "name" in item