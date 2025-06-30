# High-Level Test Strategy Research Report

## 1. Introduction

This document presents a comprehensive high-level testing strategy for the AI-powered stock prediction platform. The objective is to define a robust testing framework that ensures the reliability, accuracy, and performance of all system components, from data ingestion to the final API-delivered prediction signal.

This strategy is designed to provide a foundation for the `tester-acceptance-plan-writer` to create a detailed master acceptance test plan. The core philosophy is to build confidence in the system at each stage, culminating in a suite of end-to-end tests that, if passed, confirm the entire platform works as intended.

---

## 2. Overall Testing Philosophy

Our testing approach will be a hybrid model, combining the strengths of different methodologies across the Test Pyramid:

*   **White-Box Testing (Unit & Integration):** At the base, we will use white-box testing to verify the internal logic of individual functions, classes, and modules. This is critical for the data processing and feature engineering components, where the correctness of algorithms is paramount.
*   **Grey-Box Testing (Model & API):** For the ML models and the backend API, a grey-box approach is suitable. This involves testing the components with some knowledge of their internal workings, such as verifying model output shapes or testing API endpoints while understanding the underlying database schema.
*   **Black-Box Testing (End-to-End):** At the top, we will use black-box testing for the entire system. These tests will simulate real user scenarios, interacting with the platform solely through its public API, without any knowledge of the internal implementation.

---

## 3. Component-Specific Testing Strategies

### 3.1. Data Ingestion Pipeline

*   **Objective:** Ensure reliable and accurate data fetching from external APIs (Alpha Vantage, Twitter/X).
*   **Methodology:**
    *   **Unit Tests (White-Box):** Test the `AlphaVantageClient` and `TwitterClient` classes in isolation. Use mocking (e.g., with `pytest-mock` or `unittest.mock`) to simulate API responses, including success cases, error codes (404, 429), and malformed JSON. Verify that the clients handle these scenarios gracefully, log appropriate messages, and return data in the expected format.
    *   **Integration Tests (Grey-Box):** Periodically run tests against the live external APIs (in a staging environment, using separate API keys) to catch breaking changes in the API schemas. These should be clearly marked and run less frequently than unit tests to avoid rate limiting and cost issues.

### 3.2. Data Processing & Feature Engineering

*   **Objective:** Verify the correctness of all data cleaning, transformation, and feature calculation logic.
*   **Methodology:**
    *   **Unit Tests (White-Box):** This is the most critical area for unit testing. Each method in `TweetProcessor` and `FeatureEngineer` must be tested with a variety of inputs. Use property-based testing with a library like `Hypothesis` to generate a wide range of data inputs (e.g., different pandas DataFrame structures, tweet texts with unusual characters) to uncover edge cases that might not be considered in example-based tests.
    *   **Example Tests:**
        *   Verify that `TweetProcessor.clean_tweet` correctly removes URLs, mentions, and special characters.
        *   Verify that `FeatureEngineer.calculate_rsi` produces known, correct RSI values for a given sequence of prices.

### 3.3. Machine Learning Models (BERT & LSTM)

*   **Objective:** Ensure the models can be loaded, can process data, and produce predictions in the correct format. The functional correctness of the predictions themselves is handled in the Model Validation section.
*   **Methodology:**
    *   **Unit Tests (White-Box):**
        *   Test the data preparation logic (`PredictionModel.prepare_data`) to ensure it correctly scales data and creates sequences of the proper shape (`[batch_size, sequence_length, num_features]`).
        *   Test the model-building logic (`PredictionModel.build_model`) to assert that the created model has the expected architecture (layer types, input/output dimensions).
    *   **Integration Tests (Grey-Box):**
        *   Test the full `predict` methods of both `SentimentAnalysisModel` and `PredictionModel` with sample, pre-processed data. The goal is not to check accuracy, but to ensure the data flows through the model without raising exceptions and that the output is in the contractually specified format (e.g., a dictionary with 'label' and 'score').

### 3.4. Backend REST API

*   **Objective:** Ensure all API endpoints are functional, secure, and performant.
*   **Methodology:**
    *   **Integration Tests (Black-Box):** Test the API at the HTTP layer. Use a tool like `pytest` with an HTTP client (e.g., `requests` or `httpx`). Spin up the API in a test configuration (with a separate test database) and send requests to every endpoint.
    *   **Test Coverage:**
        *   **Success Cases:** Test all `GET`, `POST`, `DELETE` endpoints with valid inputs (e.g., `GET /api/stocks/AAPL/prediction`).
        *   **Error Cases:** Test for expected error responses (e.g., 404 for a non-existent stock, 409 for adding a duplicate stock to a watchlist).
        *   **Authentication:** Verify that protected endpoints (e.g., `/api/watchlist`) correctly reject requests without a valid token and allow access with one.
---

## 4. ML Model Validation Strategy

Validating the ML models requires more than simple accuracy metrics. The goal is to build trust in their predictive power in a financial context.

### 4.1. Time-Series Prediction Model (LSTM)

*   **Methodology: Walk-Forward Validation**
    *   A simple train-test split is insufficient for time-series data due to lookahead bias. We will use **Walk-Forward Validation**, which better simulates a live trading environment.
    *   **Process:**
        1.  Train the model on an initial chunk of historical data (e.g., 2018-2020).
        2.  Test the model on the next chunk (e.g., Q1 2021).
        3.  Slide the training window forward to include the test data (e.g., train on 2018-Q1 2021) and test on the next chunk (Q2 2021).
        4.  Repeat this process over the entire dataset.

*   **Performance Metrics:**
    *   **Directional Accuracy:** The primary metric. What percentage of the time did the model correctly predict the direction of the price movement (up or down) within the 5-day prediction window? This directly aligns with the SMART goal of 70% accuracy.
    *   **Precision/Recall for Signals:** Treat this as a classification problem.
        *   **Precision (Buy Signal):** Of all the times the model said "BUY", how often did the stock actually go up?
        *   **Recall (Buy Signal):** Of all the times the stock actually went up, how often did the model correctly predict "BUY"?
        *   (Similar metrics for "SELL" signals).
    *   **Backtesting Simulation:** Run a simulated portfolio based on the model's signals to calculate metrics like Sharpe Ratio, Maximum Drawdown, and overall Profit &amp; Loss (P&amp;L). This provides a business-oriented view of the model's performance.

### 4.2. Sentiment Analysis Model (BERT)

*   **Methodology:** Standard classification validation on a labeled test set.
*   **Process:** We need a "golden" dataset of financial tweets that have been manually labeled as positive, negative, or neutral. The model's performance will be evaluated against this set.
*   **Performance Metrics:**
    *   **F1-Score:** A balanced measure of precision and recall, which is suitable for potentially imbalanced datasets (e.g., more neutral tweets than positive/negative).
    *   **Confusion Matrix:** To visualize where the model is making mistakes (e.g., confusing neutral and positive sentiment).

---

## 5. End-to-End (E2E) Testing Strategy

E2E tests are the ultimate validation of the system. They ensure that all the integrated components work together to fulfill the user stories. These tests will be written as black-box tests that interact with the system only via its public API.

### AI-Verifiable E2E Scenarios:

*   **Scenario 1: Full Prediction Workflow for a Known Stock**
    1.  **Trigger:** An automated E2E test runner initiates a request.
    2.  **Action:** The test makes a `GET` request to `/api/stocks/AAPL/prediction`.
    3.  **Verification:**
        *   Assert that the HTTP status code is 200.
        *   Assert that the response body is a valid JSON object.
        *   Assert that the JSON object contains the keys: `symbol`, `name`, `signal`, `confidence`, `timestamp`.
        *   Assert that the `signal` value is one of ["BUY", "SELL", "HOLD"].
        *   Assert that the `confidence` value is a float between 0 and 1.

*   **Scenario 2: Full Watchlist Management Workflow**
    1.  **Trigger:** An automated E2E test runner.
    2.  **Action (Step 1 - Add):** Make a `POST` request to `/api/watchlist` with the body `{"symbol": "GOOGL"}` (assuming valid auth).
    3.  **Verification (Step 1):** Assert the status code is 201.
    4.  **Action (Step 2 - Verify Add):** Make a `GET` request to `/api/watchlist`.
    5.  **Verification (Step 2):** Assert the response is a list of JSON objects and that one of the objects has `"symbol": "GOOGL"`.
    6.  **Action (Step 3 - Remove):** Make a `DELETE` request to `/api/watchlist/GOOGL`.
    7.  **Verification (Step 3):** Assert the status code is 204.
    8.  **Action (Step 4 - Verify Remove):** Make another `GET` request to `/api/watchlist`.
    9.  **Verification (Step 4):** Assert that no object in the response list has `"symbol": "GOOGL"`.

---

## 6. Recommended Tooling (Python Ecosystem)

*   **Test Runner:** `pytest` - For its powerful features like fixtures, parametrization, and extensive plugin ecosystem.
*   **Mocking:** `pytest-mock` / `unittest.mock` - For isolating components and simulating external dependencies.
*   **Property-Based Testing:** `Hypothesis` - For robustly testing data processing functions against a wide range of inputs.
*   **API Testing:** `requests` or `httpx` - For making HTTP requests to the backend API within `pytest`.
*   **Code Coverage:** `pytest-cov` - For measuring the effectiveness of white-box tests.
*   **Performance Testing:** `Locust` - For load testing the API to ensure it can handle concurrent requests, especially during peak market hours.

---

## 7. Test Data Management Strategy

A robust test data strategy is critical for the success of all testing phases.

*   **Unit & Integration Tests:** Use small, static, hand-crafted datasets. For example, a small CSV file with 20 rows of price data to test feature engineering, or a JSON file with a sample API response to test a client. This data should be committed to the repository.
*   **ML Model Validation:**
    *   **Source:** Use the same production data sources (Alpha Vantage).
    *   **Storage:** Download and store a significant, fixed snapshot of historical data (e.g., 5-10 years). This ensures that validation results are reproducible and not subject to changes in the live external data. This dataset should be stored in a cloud bucket (e.g., S3) and versioned.
*   **E2E Tests:**
    *   The E2E tests will run against a staging environment. This environment will have its own database, seeded with a small, deterministic set of data (e.g., a few known stocks, one or two test users with pre-populated watchlists). This ensures that the E2E tests are deterministic and can be run repeatedly with predictable outcomes.

By implementing this multi-faceted strategy, we can build a high degree of confidence in the platform's functionality, performance, and the validity of its core predictive capabilities.