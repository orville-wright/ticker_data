# Test Plan: AlphaVantageClient

**Document Version:** 1.0
**Date:** 2025-06-30

## 1. Introduction

This document outlines the detailed test plan for the `AlphaVantageClient` component. The primary purpose of this client is to fetch historical stock data from the Alpha Vantage API as part of the broader data ingestion module. This plan details the testing strategy, scope, and specific test cases required to ensure the client is robust, reliable, and handles API interactions correctly.

This plan is derived from the [`docs/specifications/1_data_ingestion_spec.md`](docs/specifications/1_data_ingestion_spec.md) and is designed to meet the success criteria defined in the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md).

---

## 2. Test Scope & AI Verifiable Outcomes

### 2.1. In Scope

-   The `AlphaVantageClient` class.
-   The `__init__` method for correct initialization.
-   The `fetch_daily_time_series` method, including its success and failure modes.
-   Interaction with external dependencies (specifically, the HTTP request library).

### 2.2. Out of Scope

-   The Alpha Vantage API service itself.
-   The performance of the network.
-   The orchestrator (`run_ingestion_pipeline`) that calls this client.

### 2.3. Targeted AI Verifiable End Results

This test plan directly targets the following AI-verifiable end results as defined in the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md):

-   **Result 1:** "The unit tests `test_fetch_daily_time_series_success` and `test_fetch_daily_time_series_api_error` for `AlphaVantageClient` pass successfully."
-   **Result 2 (Implicit):** The client must "handle API errors and rate limits gracefully," which necessitates testing the exponential backoff mechanism described in the specification.

---

## 3. Test Strategy

### 3.1. Testing Approach -- London School of TDD

This test plan adopts the **London School of TDD**, which emphasizes interaction-based testing. We will not test the internal state of the `AlphaVantageClient` instance. Instead, we will verify its behavior by observing its interactions with its collaborators.

-   **Unit Under Test (UUT):** The `AlphaVantageClient` instance.
-   **Collaborators:** The primary collaborator is the external HTTP request library (e.g., `requests`) used to make API calls, and the `time` module for handling delays.
-   **Mocking:** All collaborators will be mocked. This allows us to isolate the `AlphaVantageClient` and test its logic under controlled conditions, simulating various API responses (success, errors, rate limiting) without making actual network calls.

### 3.2. Recursive Testing & Regression Strategy

A robust regression testing strategy is crucial for maintaining stability as the project evolves.

-   **Triggers for Re-Execution:** The `AlphaVantageClient` test suite will be re-executed automatically under the following conditions:
    1.  Any code change within the `AlphaVantageClient` class itself.
    2.  An upgrade or change to the underlying HTTP client library it depends on.
    3.  As part of the full `data-ingestion` test suite run, triggered by changes in related components like `run_ingestion_pipeline`.
    4.  As part of the complete project-wide unit test suite run before any deployment or merge to the main branch.

-   **Test Tagging & Selection:**
    -   All tests in this plan will be tagged as `unit` and `data-ingestion`.
    -   For a localized change to the client, a developer can run tests with the `alpha_vantage_client` tag (or by file).
    -   For broader CI/CD pipeline runs, the `data-ingestion` tag will be used to run all related tests.

---

## 4. Test Environment & Data

### 4.1. Test Environment

-   A standard Python testing framework (e.g., `pytest`) will be used.
-   A mocking library (e.g., `unittest.mock`) is required to mock collaborators.

### 4.2. Mock Configurations

-   **`requests.get` mock:** This mock will be configured to return a `MockResponse` object. The `MockResponse` will have its `status_code` and `json()` method's return value controlled by each test case.
-   **`time.sleep` mock:** This mock will be used to verify that the exponential backoff logic calls for a delay without actually pausing test execution. We will assert that it is called with the expected increasing delay values.

### 4.3. Test Data

-   **`SUCCESS_RESPONSE` (dict):** A sample JSON object mimicking a successful Alpha Vantage API response for a daily time series.
    ```json
    {
      "Meta Data": { "2. Symbol": "TEST" },
      "Time Series (Daily)": {
        "2025-06-30": { "1. open": "100.00" },
        "2025-06-29": { "1. open": "99.00" }
      }
    }
    ```
-   **`ERROR_RESPONSE` (dict):** An empty dictionary or a dictionary with an error key, returned by the `json()` method on a failed request.
-   **`API_KEY` (str):** A dummy API key, e.g., `"TEST_KEY"`.
-   **`SYMBOL` (str):** A dummy stock symbol, e.g., `"TEST"`.

---

## 5. Detailed Test Cases

### Test Case: TC-AVC-001 -- Successful Data Fetch

-   **Target AI Verifiable End Result:** `test_fetch_daily_time_series_success` passes.
-   **Description:** Verifies that the client can successfully fetch and return time-series data for a valid symbol when the API returns a 200 status code.
-   **Unit Under Test:** `AlphaVantageClient.fetch_daily_time_series`
-   **Collaborators to Mock:** `requests.get`
-   **Mock Configuration:**
    -   `requests.get` is configured to return a response with `status_code = 200` and `.json()` returning the `SUCCESS_RESPONSE` data.
-   **Test Steps:**
    1.  Initialize `AlphaVantageClient` with `API_KEY`.
    2.  Call `fetch_daily_time_series` with `SYMBOL`.
-   **Observable Outcome & Assertions:**
    -   Assert that `requests.get` was called once with the correct URL and parameters (function=`TIME_SERIES_DAILY`, symbol=`TEST`, apikey=`TEST_KEY`).
    -   Assert that the method returns a dictionary identical to `SUCCESS_RESPONSE`.
-   **AI Verifiable Completion Criterion:** The test case passes when executed by the test runner.

### Test Case: TC-AVC-002 -- API Error Handling

-   **Target AI Verifiable End Result:** `test_fetch_daily_time_series_api_error` passes.
-   **Description:** Verifies that the client handles a generic API error (e.g., a 500 status code) gracefully by logging an error and returning an empty dictionary.
-   **Unit Under Test:** `AlphaVantageClient.fetch_daily_time_series`
-   **Collaborators to Mock:** `requests.get`, `logging` (or equivalent logger).
-   **Mock Configuration:**
    -   `requests.get` is configured to return a response with `status_code = 500`.
-   **Test Steps:**
    1.  Initialize `AlphaVantageClient`.
    2.  Call `fetch_daily_time_series`.
-   **Observable Outcome & Assertions:**
    -   Assert that `requests.get` was called once.
    -   Assert that an error message was logged.
    -   Assert that the method returns an empty dictionary (`{}`).
-   **AI Verifiable Completion Criterion:** The test case passes when executed by the test runner.

### Test Case: TC-AVC-003 -- Rate Limit with Exponential Backoff

-   **Target AI Verifiable End Result:** Implicitly supports the "graceful error handling" requirement.
-   **Description:** Verifies that the client correctly handles a 429 "Too Many Requests" error by retrying the request with an exponential backoff delay.
-   **Unit Under Test:** `AlphaVantageClient.fetch_daily_time_series`
-   **Collaborators to Mock:** `requests.get`, `time.sleep`.
-   **Mock Configuration:**
    -   `requests.get` will be configured with `side_effect` to behave differently on subsequent calls.
    -   **Call 1:** Return a response with `status_code = 429`.
    -   **Call 2:** Return a response with `status_code = 200` and `.json()` returning `SUCCESS_RESPONSE`.
-   **Test Steps:**
    1.  Configure the mock `side_effect`.
    2.  Initialize `AlphaVantageClient`.
    3.  Call `fetch_daily_time_series`.
-   **Observable Outcome & Assertions:**
    -   Assert that `requests.get` was called exactly two times.
    -   Assert that `time.sleep` was called exactly once, with an argument of `1` (the initial delay).
    -   Assert that the method ultimately returns the `SUCCESS_RESPONSE` dictionary.
-   **AI Verifiable Completion Criterion:** The test case passes when executed by the test runner.
