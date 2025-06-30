import pytest
import requests
import uuid

# This assumes a running instance of the application, with a base URL.
# In a real CI/CD pipeline, this would be the URL of the staging environment.
BASE_URL = "http://localhost:5000/api"
# In a real test suite, we would have a way to generate a valid JWT for a test user.
# For this example, we'll pass a placeholder header. The API would need to be
# configured in its test environment to accept this placeholder.
TEST_AUTH_HEADER = {"Authorization": "Bearer test-token"}

# A stock that is unlikely to be in the watchlist at the start of a test run
TEST_STOCK = "GOOGL"

@pytest.fixture(scope="module")
def cleanup_watchlist():
    """A fixture to ensure the test stock is not in the watchlist before and after tests."""
    # Ensure cleanup before the test runs, in case a previous run failed
    requests.delete(f"{BASE_URL}/watchlist/{TEST_STOCK}", headers=TEST_AUTH_HEADER)
    yield
    # Cleanup after the test runs
    requests.delete(f"{BASE_URL}/watchlist/{TEST_STOCK}", headers=TEST_AUTH_HEADER)


def test_full_watchlist_management_workflow(cleanup_watchlist):
    """
    Corresponds to Test ID E2E-05.
    Verifies the entire lifecycle of a watchlist item: add, verify, attempt duplicate, remove, verify.
    Completion Criterion: AI can verify the sequence of response codes and payload contents.
    """
    # 1. Add to Watchlist
    add_response = requests.post(
        f"{BASE_URL}/watchlist",
        json={"symbol": TEST_STOCK},
        headers=TEST_AUTH_HEADER
    )
    assert add_response.status_code == 201

    # 2. Verify Add by getting the full watchlist
    get_response_after_add = requests.get(f"{BASE_URL}/watchlist", headers=TEST_AUTH_HEADER)
    assert get_response_after_add.status_code == 200
    watchlist = get_response_after_add.json()
    assert isinstance(watchlist, list)
    assert any(stock["symbol"] == TEST_STOCK for stock in watchlist)

    # 3. Attempt to add the same stock again (Conflict)
    duplicate_add_response = requests.post(
        f"{BASE_URL}/watchlist",
        json={"symbol": TEST_STOCK},
        headers=TEST_AUTH_HEADER
    )
    assert duplicate_add_response.status_code == 409

    # 4. Remove from Watchlist
    remove_response = requests.delete(f"{BASE_URL}/watchlist/{TEST_STOCK}", headers=TEST_AUTH_HEADER)
    assert remove_response.status_code == 204

    # 5. Verify Remove by getting the full watchlist
    get_response_after_remove = requests.get(f"{BASE_URL}/watchlist", headers=TEST_AUTH_HEADER)
    assert get_response_after_remove.status_code == 200
    watchlist_after_remove = get_response_after_remove.json()
    assert not any(stock["symbol"] == TEST_STOCK for stock in watchlist_after_remove)

    # 6. Attempt to remove a stock that is not in the list
    not_found_remove_response = requests.delete(f"{BASE_URL}/watchlist/{TEST_STOCK}", headers=TEST_AUTH_HEADER)
    assert not_found_remove_response.status_code == 404

def test_watchlist_endpoints_require_auth():
    """
    Corresponds to Test ID E2E-06.
    Verifies that protected watchlist endpoints return 401 without a valid auth token.
    Completion Criterion: AI can verify the 401 response codes.
    """
    # Test GET without auth
    get_response = requests.get(f"{BASE_URL}/watchlist")
    assert get_response.status_code == 401

    # Test POST without auth
    post_response = requests.post(f"{BASE_URL}/watchlist", json={"symbol": "ANY"})
    assert post_response.status_code == 401

    # Test DELETE without auth
    delete_response = requests.delete(f"{BASE_URL}/watchlist/ANY")
    assert delete_response.status_code == 401