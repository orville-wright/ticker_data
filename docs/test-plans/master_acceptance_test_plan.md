# Master Acceptance Test Plan

## 1. Introduction

This document outlines the master plan for acceptance testing of the AI-powered stock prediction platform. It defines the high-level, end-to-end (E2E) test cases that collectively represent the ultimate success criteria for the project.

The primary goal of this plan is to verify that the platform's core functionalities meet the user requirements as defined in the [user stories](docs/specifications/user_stories_and_examples.md) and achieve the performance targets outlined in the [Mutual Understanding Document](docs/Mutual_Understanding_Document.md). This plan is heavily informed by the strategy laid out in the [High-Level Test Strategy Report](docs/research/high_level_test_strategy.md).

## 2. Test Objectives

*   To validate that the complete, integrated system functions as a cohesive whole.
*   To verify that all user-facing features, accessed via the API, behave according to the specifications.
*   To confirm that the system meets the primary business objective--the SMART success criteria for predictive accuracy.
*   To ensure that the API endpoints are robust and handle both success and error scenarios correctly.

## 3. Scope

### In-Scope

*   **Black-Box API Testing:** All tests will be conducted by making HTTP requests to the public-facing backend API endpoints as defined in the [API Specification](docs/specifications/5_backend_api_spec.md). No knowledge of the internal implementation is required.
*   **Core User Workflows:** Testing the complete lifecycle of core features--
    *   Searching for a stock.
    *   Retrieving a prediction for a stock.
    *   Full watchlist management (add, view, remove).
*   **Model Performance Validation:** Executing the Walk-Forward Validation test to measure the directional accuracy of the LSTM prediction model.

### Out-of-Scope

*   **UI/Frontend Testing:** This plan does not cover testing of the graphical user interface. It is assumed the UI will correctly consume the verified API.
*   **Unit & Component Integration Testing:** Testing of individual functions, classes, and modules is covered by separate, lower-level test suites.
*   **Non-Functional Testing:** Performance, load, and security testing are critical but separate activities that will be planned independently.
*   **Data Ingestion Pipeline Testing:** Verification of the data ingestion from third-party sources is handled by component-level integration tests.

## 4. Success Criteria

The ultimate success of the project is defined by the following SMART criteria, updated to reflect the need for true alpha generation as highlighted in the Devil's Advocate Review--

*   **Specific:** Generate a trading signal that produces risk-adjusted returns superior to a standard market benchmark.
*   **Measurable:** The model's simulated portfolio must achieve a **Sharpe Ratio at least 10% higher** than the Sharpe Ratio of a "buy-and-hold" strategy on the **SPY (S&P 500 ETF)** over the same validation period.
*   **Achievable:** This target is challenging but represents a realistic measure of a valuable financial model.
*   **Relevant:** Outperforming a benchmark (generating alpha) is the core value proposition for any active trading or investment strategy.
*   **Time-bound:** This performance will be measured over a comprehensive historical backtest using Walk-Forward Validation.

Passing all test cases defined in this plan, especially the Model Performance Validation, signifies the achievement of these criteria.

## 5. High-Level E2E Test Cases

These tests are AI-verifiable, meaning an automated test runner can execute them and programmatically determine pass/fail status based on API responses.

-- Test ID -- Description -- Steps -- Expected Results (AI-Verifiable) --
-- --- -- --- -- --- -- --- --
-- E2E-01 -- Retrieve Prediction for a Known Stock -- 1. Make a `GET` request to `/api/stocks/<known_symbol>/prediction`. -- - HTTP status code is 200. <br>- Response is valid JSON. <br>- JSON contains keys-- `symbol`, `name`, `signal`, `confidence`, `timestamp`. <br>- `signal` is one of "BUY", "SELL", "HOLD". <br>- `confidence` is a float between 0.0 and 1.0. <br>- `timestamp` is a valid ISO 8601 date-time string. --
-- E2E-02 -- Attempt to Retrieve Prediction for an Unknown Stock -- 1. Make a `GET` request to `/api/stocks/<unknown_symbol>/prediction`. -- - HTTP status code is 404. --
-- E2E-03 -- Search for a Stock by Ticker -- 1. Make a `GET` request to `/api/stocks/search?q=<ticker_fragment>`. -- - HTTP status code is 200. <br>- Response is a JSON list. <br>- Each object in the list contains `symbol` and `name` keys. <br>- At least one returned `symbol` contains the searched fragment. --
-- E2E-04 -- Search for a Stock by Company Name -- 1. Make a `GET` request to `/api/stocks/search?q=<name_fragment>`. -- - HTTP status code is 200. <br>- Response is a JSON list. <br>- Each object in the list contains `symbol` and `name` keys. <br>- At least one returned `name` contains the searched fragment. --
-- E2E-05 -- Full Watchlist Management Workflow -- 1. **Add--** `POST` to `/api/watchlist` with `{"symbol": "TEST"}`. <br> 2. **Verify Add--** `GET` `/api/watchlist`. <br> 3. **Attempt Duplicate Add--** `POST` again to `/api/watchlist` with `{"symbol": "TEST"}`. <br> 4. **Remove--** `DELETE` `/api/watchlist/TEST`. <br> 5. **Verify Remove--** `GET` `/api/watchlist`. <br> 6. **Attempt to Remove Again--** `DELETE` `/api/watchlist/TEST`. -- - **Step 1--** Status code is 201. <br>- **Step 2--** Status code is 200. Response list contains an object with `"symbol": "TEST"`. <br>- **Step 3--** Status code is 409 (Conflict). <br>- **Step 4--** Status code is 204. <br>- **Step 5--** Status code is 200. Response list does not contain an object with `"symbol": "TEST"`. <br>- **Step 6--** Status code is 404. --
-- E2E-06 -- Access Protected Watchlist Endpoints without Authentication -- 1. Make a `GET` request to `/api/watchlist` without an auth token. <br> 2. Make a `POST` request to `/api/watchlist` without an auth token. -- - Both requests return a 401 (Unauthorized) status code. --

## 6. Model Performance Validation

This section details the acceptance test for the primary success criterion-- generating alpha relative to a market benchmark.

*   **Test ID:** `MODEL-ACC-01`
*   **Description:** Measure the risk-adjusted return (Sharpe Ratio) of a portfolio simulated from the model's signals and compare it against a benchmark (SPY).
*   **Methodology:** **Walk-Forward Validation**, as defined in the [High-Level Test Strategy Report](docs/research/high_level_test_strategy.md#41-time-series-prediction-model-lstm). This approach simulates a realistic "live" trading environment where the model is periodically retrained on new data.
*   **Process:**
    1.  An automated script will be created to perform the walk-forward validation backtest.
    2.  **Data:** The script will use historical price data for the target stock and for the SPY ETF.
    3.  **Benchmark Calculation:** First, calculate the daily returns of a simple "buy-and-hold" strategy on SPY over the entire validation period. Compute the benchmark's Sharpe Ratio from these returns.
    4.  **Walk-Forward Iteration:**
        a. **Data Split:** Divide the historical data into an initial training set (e.g., 3 years) and a testing set (e.g., 3 months).
        b. **CRITICAL: Prevent Lookahead Bias:** At each step of the walk-forward validation, the `MinMaxScaler` must be re-instantiated and fit **only** on the current training data fold.
        c. **Train:** Train the LSTM model on the current training set.
        d. **Simulate Trading:** For each day in the testing set, generate a signal ("BUY", "SELL", "HOLD"). Simulate holding a position based on this signal and record the daily portfolio return.
        e. **Slide Window:** "Slide" the validation window forward by incorporating the test period's data into the training set and defining a new testing set.
        f. **Repeat:** Continue until the entire historical dataset is processed.
    5.  **Model Sharpe Ratio:** Calculate the Sharpe Ratio for the model's simulated portfolio from the series of daily returns recorded in step 4d.
*   **Expected Result (AI-Verifiable):**
    *   The **Model's Sharpe Ratio** must be **at least 1.1 times** the **Benchmark's Sharpe Ratio**. The test passes if `(model_sharpe_ratio / benchmark_sharpe_ratio) >= 1.1`. Otherwise, it fails.