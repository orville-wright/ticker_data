# Primary Project Planning Document

## 1. Project Overview

This document serves as the master blueprint for the development of the AI-powered stock prediction platform. The project's goal is to create a platform that analyzes historical market data and real-time social media sentiment to provide individual retail investors with a clear, actionable signal ("buy," "sell," or "hold") for specific stocks, empowering them to make more informed, data-driven decisions.

This plan is a synthesis of all project specifications, constraints, and acceptance criteria. Adherence to this plan is critical for the successful delivery of the project.

---

## 2. Sprint 1: Core Backend & Model Foundation

This sprint focuses on building the foundational data pipelines, machine learning models, and the initial, unauthenticated API endpoints.

### Phase 1.1: Data Ingestion & Processing

This phase involves creating the services to fetch and clean all necessary data.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the `AlphaVantageClient` class. -- The unit tests `test_fetch_daily_time_series_success` and `test_fetch_daily_time_series_api_error` for `AlphaVantageClient` pass successfully. --
-- Implement the `TwitterClient` class. -- The unit tests `test_search_tweets_success` and `test_search_tweets_rate_limit` for `TwitterClient` pass successfully. --
-- Implement the `run_ingestion_pipeline` orchestrator function. -- The unit test `test_run_ingestion_pipeline` passes, confirming that the function correctly orchestrates calls to the client mocks and structures the output. --
-- Implement the `TweetProcessor` class. -- The unit tests `test_clean_tweet` and `test_tokenize_and_remove_stopwords` pass successfully. --
-- Implement the `FeatureEngineer` class. -- The unit test `test_add_all_features` passes, confirming all technical indicators are added to the DataFrame. --
-- Implement the `run_processing_pipeline` orchestrator function. -- The unit test `test_run_processing_pipeline` passes, confirming the function correctly orchestrates cleaning, feature engineering, and sentiment aggregation. --

### Phase 1.2: Sentiment and Prediction Models

This phase focuses on creating the machine learning models that will analyze the data and generate predictions.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the `SentimentAnalysisModel` class. -- The unit tests `test_predict_sentiment_positive`, `test_predict_sentiment_negative`, and `test_bulk_predict_sentiment` all pass successfully. --
-- Implement the `aggregate_daily_sentiment` function. -- The unit test `test_aggregate_daily_sentiment` passes, ensuring the weighted average score is calculated correctly. --
-- Implement the `PredictionModel` class structure and `build_model` method. -- The unit test `test_build_model` passes, verifying the successful creation of a `tf.keras.Model` instance with the correct architecture. --
-- Implement the `predict` method of the `PredictionModel` class. -- The unit test `test_predict_signal` passes, ensuring the method returns a dictionary with the correct 'signal' and 'confidence' keys and values. --
-- Implement `save_model` and `load_model` functionality. -- Unit tests pass for saving a model and scaler to disk and successfully loading them back into a new `PredictionModel` instance. --
-- Create 'golden' labeled dataset for sentiment model fine-tuning. -- A labeled CSV file exists at `data/golden_sentiment_dataset.csv`. --

### Phase 1.3: Initial Backend API

This phase exposes the core prediction and search functionality through public API endpoints.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the `GET /api/stocks/search` endpoint. -- The acceptance tests [`test_search_by_ticker`](tests/acceptance/test_prediction_api.py:45) and [`test_search_by_name`](tests/acceptance/test_prediction_api.py:61) pass successfully. --
-- Implement the `GET /api/stocks/<symbol>/prediction` endpoint. -- The acceptance tests [`test_get_prediction_for_known_stock`](tests/acceptance/test_prediction_api.py:14) and [`test_get_prediction_for_unknown_stock`](tests/acceptance/test_prediction_api.py:35) pass successfully. --
-- Implement the `run_daily_predictions` scheduled job. -- A unit test passes that successfully mocks the pipeline functions and verifies that the job attempts to store a result in the cache. --

---

## 3. Sprint 2: API & Frontend Integration

This sprint focuses on building out the user-facing features, including watchlist management and the frontend UI, culminating in the final validation of the system's accuracy.

### Phase 2.1: Watchlist API & Authentication

This phase implements the user-specific functionality for managing a personalized watchlist, protected by authentication.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the full `POST`, `GET`, and `DELETE` logic for the `/api/watchlist` endpoints. -- The acceptance test [`test_full_watchlist_management_workflow`](tests/acceptance/test_watchlist_api.py:26) passes, verifying the entire add/view/conflict/remove/not-found sequence. --
-- Secure the watchlist endpoints with authentication. -- The acceptance test [`test_watchlist_endpoints_require_auth`](tests/acceptance/test_watchlist_api.py:69) passes, confirming that all endpoints return a 401 status code when no auth token is provided. --

### Phase 2.2: Frontend Component Implementation

This phase involves creating the individual, reusable UI components based on the frontend specification.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the `StockSearchBar` component. -- The component-level test "Should fetch and display suggestions as user types" passes. --
-- Implement the `PredictionDisplay` component. -- The component correctly renders different styles for 'BUY', 'SELL', and 'HOLD' signals in a Storybook or similar test environment. --
-- Implement the `WatchlistButton` component. -- Component tests pass for both the `addToWatchlist` and `removeFromWatchlist` API calls. --
-- Implement the `WatchlistTable` and `WatchlistRow` components. -- The `WatchlistTable` component correctly renders a list of `WatchlistRow` components when passed mock data. --

### Phase 2.3: Frontend Page Integration

This phase assembles the individual components into full-page views.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Implement the `StockDetailPage` view. -- When navigating to `/stock/AAPL`, the page correctly fetches data from the `/api/stocks/AAPL/prediction` endpoint and displays it in the `PredictionDisplay` component. --
-- Implement the `WatchlistPage` view. -- When navigating to `/watchlist`, the page correctly fetches data from the `/api/watchlist` endpoint and displays the items in the `WatchlistTable`. --

### Phase 2.4: Final System Validation

This phase executes the final and most critical acceptance test to verify the project has met its primary success criterion.

-- Task -- AI-Verifiable End Result --
-- --- -- --- --
-- Achieve the primary success criterion for model accuracy. -- The acceptance test [`test_model_directional_accuracy`](tests/acceptance/test_model_accuracy.py:35) passes, with the calculated directional accuracy being greater than or equal to 70.0%. --

---

## 4. Data Acquisition Budget

A cost analysis of required API tiers needs to be performed and a budget allocated.
