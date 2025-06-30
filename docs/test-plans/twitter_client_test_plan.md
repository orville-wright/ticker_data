# Test Plan: TwitterClient

## 1. Introduction

This document provides a comprehensive and granular test plan for the `TwitterClient` class, a key component of the data ingestion module. The purpose of this client is to fetch recent tweets related to specific stock tickers from the Twitter/X API v2.

This plan is derived from the [`docs/specifications/1_data_ingestion_spec.md`](docs/specifications/1_data_ingestion_spec.md), the detailed pseudocode in [`docs/pseudocode/data_ingestion/twitter_client_init.md`](docs/pseudocode/data_ingestion/twitter_client_init.md) and [`docs/pseudocode/data_ingestion/twitter_client_search_tweets.md`](docs/pseudocode/data_ingestion/twitter_client_search_tweets.md), and is explicitly designed to validate the AI-verifiable outcomes defined in the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md).

## 2. Test Scope & AI-Verifiable Outcomes

The primary goal of these tests is to provide verifiable proof that the `TwitterClient` implementation meets its requirements as defined in the project plan.

### 2.1. Targeted AI-Verifiable End Results

This test plan directly targets the following AI-Verifiable End Result from the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md):

-   **"The unit tests `test_search_tweets_success` and `test_search_tweets_rate_limit` for `TwitterClient` pass successfully."**

All test cases outlined below contribute to achieving this outcome.

## 3. Test Strategy

### 3.1. Methodology: London School of TDD

The testing approach will strictly adhere to the **London School of TDD (Interaction-Based Testing)**. This means we will focus on verifying the *observable behavior* of the `TwitterClient` by testing how it interacts with its collaborators. We will not test the internal state of the client. Instead, we will confirm that the client sends the correct messages (i.e., makes the correct API calls) and responds appropriately to the messages it receives (i.e., handles various API responses).

### 3.2. Collaborators and Mocks

The primary external dependency (collaborator) for the `TwitterClient` is the HTTP request/response mechanism. This will be mocked to simulate the Twitter API without making actual network calls.

-   **Primary Collaborator:** An HTTP client library (e.g., `requests`).
-   **Mocking Strategy:** The `requests.get` function (or equivalent) will be mocked to return different `Response` objects, simulating:
    -   Successful API responses (`200 OK`).
    -   Rate-limiting errors (`429 Too Many Requests`).
    -   Client-side and server-side errors (`400`, `500`).
    -   Network exceptions (e.g., `ConnectionError`, `Timeout`).
-   **Other Mocks:** `time.sleep` will be mocked to verify that the exponential backoff delay is being applied correctly without slowing down the test suite. `logging` will be mocked to ensure appropriate error and warning messages are generated.

### 3.3. Recursive Testing (Regression) Strategy

To ensure long-term stability and catch regressions early, a recursive testing strategy will be implemented. This strategy defines when and how these unit tests are re-executed as the project evolves.

-   **Test Triggers (When to re-run):**
    -   **Continuous Integration (CI):** On every push/commit to any branch in the repository. This provides immediate feedback.
    -   **Pre-Merge Check:** Before merging a feature branch into the main development branch, especially if the changes are within the `data_ingestion` module or its dependencies.
    -   **Dependency Updates:** After any update to the project's dependencies, particularly networking libraries like `requests`.
    -   **Scheduled Builds:** As part of a nightly or scheduled full-system build to catch more subtle integration issues.

-   **Test Selection and Tagging:**
    -   Tests will be tagged to define their scope. The tests in this plan will be tagged as `@unit` and `@regression`.
    -   For routine CI on feature branches, running the `@unit` tests for the changed modules is sufficient.
    -   For pre-merge checks and scheduled builds, the entire `@regression` suite (which includes all `@unit` tests) will be executed to ensure no breaking changes were introduced elsewhere in the system.

## 4. Test Cases

Each test case below is designed to be an AI-verifiable step toward implementing a robust `TwitterClient`.

### 4.1. `__init__` Method Tests

These tests verify the correct initialization and validation within the constructor.

---
**Test Case ID:** TC1_INIT_SUCCESS
-   **Test Case Name:** `test_constructor_assigns_properties_correctly`
-   **Target AI Verifiable End Result:** Prerequisite for all other `TwitterClient` tests.
-   **Description:** Verifies that the constructor correctly assigns the `bearer_token` to an instance property and sets the default `base_url`.
-   **Unit Under Test:** `TwitterClient.__init__`
-   **Collaborators to Mock:** None.
-   **Mock Configuration:** None.
-   **Observable Outcome/Assertion:**
    -   Instantiate `TwitterClient` with a valid `bearer_token` string.
    -   Assert that `client.bearer_token` equals the input token.
    -   Assert that `client.base_url` equals "https://api.twitter.com/2/tweets/search/recent".
-   **Recursive Testing Scope:** `@unit`, `@regression`

---
**Test Case ID:** TC2_INIT_INVALID_TOKEN
-   **Test Case Name:** `test_constructor_with_invalid_token`
-   **Target AI Verifiable End Result:** Prerequisite for robust error handling.
-   **Description:** Ensures the constructor raises a `ValueError` if the `bearer_token` is null, empty, or not a string.
-   **Unit Under Test:** `TwitterClient.__init__`
-   **Collaborators to Mock:** None.
-   **Mock Configuration:** None.
-   **Observable Outcome/Assertion:**
    -   Assert that calling `TwitterClient(None)` raises a `ValueError`.
    -   Assert that calling `TwitterClient("")` raises a `ValueError`.
-   **Recursive Testing Scope:** `@unit`, `@regression`
---

### 4.2. `search_tweets` Method Tests

These tests verify the core functionality of searching for tweets and handling various API responses.

---
**Test Case ID:** TC3_SEARCH_SUCCESS
-   **Test Case Name:** `test_search_tweets_success`
-   **Target AI Verifiable End Result:** `test_search_tweets_success` passes.
-   **Description:** Verifies that the method returns a list of tweet dictionaries when the API call is successful (200 OK).
-   **Unit Under Test:** `TwitterClient.search_tweets`
-   **Collaborators to Mock:** `requests.get`, `logging`.
-   **Mock Configuration:**
    -   Configure the mock `requests.get` to return a `Response` object with `status_code=200` and a JSON body like `{"data": [{"id": "123", "text": "Hello $STOCK"}, {"id": "456", "text": "Another tweet"}]}`.
-   **Observable Outcome/Assertion:**
    -   Assert that the method returns a list containing two dictionaries.
    -   Assert that the first element in the list has the keys 'id' and 'text'.
    -   Assert that the correct `Authorization` header and query parameters were passed to `requests.get`.
    -   Assert that a success message was logged.
-   **Recursive Testing Scope:** `@unit`, `@regression`

---
**Test Case ID:** TC4_SEARCH_RATE_LIMIT
-   **Test Case Name:** `test_search_tweets_rate_limit_with_backoff`
-   **Target AI Verifiable End Result:** `test_search_tweets_rate_limit` passes.
-   **Description:** Verifies that the method handles a `429 Too Many Requests` error by retrying with exponential backoff and eventually succeeds.
-   **Unit Under Test:** `TwitterClient.search_tweets`
-   **Collaborators to Mock:** `requests.get`, `time.sleep`, `logging`.
-   **Mock Configuration:**
    -   Configure `requests.get` to have side effects:
        1.  First call: Return a `Response` with `status_code=429`.
        2.  Second call: Return a `Response` with `status_code=200` and a valid JSON body `{"data": [...]}`.
-   **Observable Outcome/Assertion:**
    -   Assert that `requests.get` is called twice.
    -   Assert that `time.sleep` is called once with an initial delay (e.g., 1 second).
    -   Assert that a warning message for the rate limit is logged.
    -   Assert that the method ultimately returns the list of tweets from the successful second call.
-   **Recursive Testing Scope:** `@unit`, `@regression`

---
**Test Case ID:** TC5_SEARCH_RETRY_FAILURE
-   **Test Case Name:** `test_search_tweets_failure_after_all_retries`
-   **Target AI Verifiable End Result:** `test_search_tweets_rate_limit` passes (by implication of handling the full retry loop).
-   **Description:** Verifies that the method returns an empty list after exhausting all retry attempts.
-   **Unit Under Test:** `TwitterClient.search_tweets`
-   **Collaborators to Mock:** `requests.get`, `time.sleep`, `logging`.
-   **Mock Configuration:**
    -   Configure `requests.get` to consistently return a `Response` with `status_code=429` for all calls (e.g., 3 calls if `MAX_RETRIES` is 3).
-   **Observable Outcome/Assertion:**
    -   Assert that `requests.get` is called `MAX_RETRIES` times.
    -   Assert that `time.sleep` is called with increasing delays (e.g., 1, 2).
    -   Assert that a final error message is logged indicating failure after all attempts.
    -   Assert that the method returns an empty list.
-   **Recursive Testing Scope:** `@unit`, `@regression`

---
**Test Case ID:** TC6_SEARCH_HTTP_ERROR
-   **Test Case Name:** `test_search_tweets_handles_other_http_error`
-   **Target AI Verifiable End Result:** Prerequisite for overall robustness.
-   **Description:** Verifies that the method handles a non-429 HTTP error (e.g., 400 Bad Request) gracefully by logging the error and returning an empty list without retrying.
-   **Unit Under Test:** `TwitterClient.search_tweets`
-   **Collaborators to Mock:** `requests.get`, `logging`.
-   **Mock Configuration:**
    -   Configure `requests.get` to return a `Response` with `status_code=400` and a JSON body `{"title": "Invalid Request", "detail": "Invalid 'query' parameter"}`.
-   **Observable Outcome/Assertion:**
    -   Assert that `requests.get` is called only once.
    -   Assert that an error message containing the status code and details is logged.
    -   Assert that the method returns an empty list.
-   **Recursive Testing Scope:** `@unit`, `@regression`

---
**Test Case ID:** TC7_SEARCH_NETWORK_ERROR
-   **Test Case Name:** `test_search_tweets_handles_network_exception`
-   **Target AI Verifiable End Result:** Prerequisite for overall robustness.
-   **Description:** Verifies that the method handles a network-level exception (e.g., `Timeout`) by logging the error and retrying according to the backoff strategy.
-   **Unit Under Test:** `TwitterClient.search_tweets`
-   **Collaborators to Mock:** `requests.get`, `time.sleep`, `logging`.
-   **Mock Configuration:**
    -   Configure `requests.get` to have side effects:
        1.  First call: Raise a `requests.exceptions.Timeout` exception.
        2.  Second call: Return a `Response` with `status_code=200` and a valid JSON body.
-   **Observable Outcome/Assertion:**
    -   Assert that `requests.get` is called twice.
    -   Assert that `time.sleep` is called once.
    -   Assert that a network error message is logged for the first attempt.
    -   Assert that the method returns the list of tweets from the successful second call.
-   **Recursive Testing Scope:** `@unit`, `@regression`

---

## 5. Test Environment and Data

-   **Frameworks:** `pytest` for test execution and `unittest.mock` for mocking collaborators.
-   **Test Data:**
    -   **Success Payload:** A sample JSON string representing a successful response from the Twitter API's recent search endpoint.
      ```json
      {
        "data": [
          {
            "id": "1500000000000000001",
            "text": "Great news for $AAPL today!"
          },
          {
            "id": "1500000000000000002",
            "text": "I'm thinking of selling my $AAPL stock."
          }
        ],
        "meta": {
          "newest_id": "1500000000000000002",
          "oldest_id": "1500000000000000001",
          "result_count": 2
        }
      }
      ```
    -   **Error Payload:** A sample JSON string for a `400 Bad Request`.
      ```json
      {
        "title": "Invalid Request",
        "detail": "One of query, expansions, or tweet.fields is not valid.",
        "type": "https://api.twitter.com/2/problems/invalid-request",
        "status": 400
      }
      ```

## 6. AI-Verifiable Completion Criteria

Every test case defined in this document includes a clear, actionable description of the behavior to be tested, the collaborators to be mocked, the specific mock configuration, and the expected observable outcome. This level of detail ensures that a human programmer or a subsequent AI agent can implement the tests directly from this plan, making the plan itself AI-verifiable. The successful implementation and passing of these tests will satisfy the AI-Verifiable End Results specified in the project plan.