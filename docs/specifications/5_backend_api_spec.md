# Specification: Backend API

This document details the technical specifications for the backend API. The API will be responsible for handling requests from the frontend, interacting with the data and model pipelines, and serving prediction results. A Python web framework like Flask or FastAPI is recommended.

## 1. Overview

The backend will expose a set of RESTful API endpoints to support the core functionalities outlined in the user stories:
-   Searching for stocks.
-   Retrieving prediction signals for a specific stock.
-   Managing a user's watchlist.

The API must handle user authentication (details to be defined, but likely JWT-based) to manage personalized watchlists.

---

## 2. API Endpoints

### 2.1. Stock Search

-   **Endpoint:** `GET /api/stocks/search`
-   **Description:** Searches for stocks based on a query string (ticker or company name).
-   **Query Parameters:**
    -   `q` (str): The search query (e.g., "AAPL" or "Apple").
-   **Success Response (200 OK):**
    -   **Body:**
        ```json
        [
          {
            "symbol": "AAPL",
            "name": "Apple Inc."
          },
          {
            "symbol": "MSFT",
            "name": "Microsoft Corp."
          }
        ]
        ```
-   **Function:** `search_stocks(query: str) -> list[dict]`
    -   **Description:** This function will likely query a database or a cached list of all available stocks to find matches for the given query string.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_search_stocks_by_symbol
        # BEHAVIOR: Should return a list of matching stocks for a ticker symbol query.
        # SETUP: Mock the stock database/cache with sample data.
        # ACTION: Call the endpoint with ?q=AAP
        # ASSERT: The response is a list containing the Apple Inc. dictionary.
        ```

### 2.2. Get Stock Prediction

-   **Endpoint:** `GET /api/stocks/<string:symbol>/prediction`
-   **Description:** Retrieves the latest prediction signal for a specific stock.
-   **URL Parameters:**
    -   `symbol` (str): The stock ticker symbol (e.g., "AAPL").
-   **Success Response (200 OK):**
    -   **Body:**
        ```json
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "signal": "BUY",
          "confidence": 0.82,
          "timestamp": "2024-10-26T07:30:00Z"
        }
        ```
-   **Error Response (404 Not Found):** If the stock symbol is not found or has no prediction.
-   **Function:** `get_prediction(symbol: str) -> dict`
    -   **Description:** This function orchestrates fetching the latest pre-computed prediction for the given stock from a database or cache. If a prediction is not available, it could potentially trigger the prediction pipeline on-demand (for a future version).
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_get_prediction_found
        # BEHAVIOR: Should return the latest prediction data for a valid stock.
        # SETUP: Mock the prediction database to return a sample prediction for 'AAPL'.
        # ACTION: Call the endpoint /api/stocks/AAPL/prediction
        # ASSERT: The response body matches the expected prediction structure.
        ```

### 2.3. Get User Watchlist

-   **Endpoint:** `GET /api/watchlist`
-   **Description:** Retrieves the authenticated user's watchlist.
-   **Authentication:** Required.
-   **Success Response (200 OK):**
    -   **Body:**
        ```json
        [
          {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "signal": "BUY",
            "confidence": 0.82
          },
          {
            "symbol": "MSFT",
            "name": "Microsoft Corp.",
            "signal": "HOLD",
            "confidence": 0.65
          }
        ]
        ```
-   **Function:** `get_watchlist(user_id: int) -> list[dict]`

### 2.4. Add to Watchlist

-   **Endpoint:** `POST /api/watchlist`
-   **Description:** Adds a stock to the authenticated user's watchlist.
-   **Authentication:** Required.
-   **Request Body:**
    ```json
    {
      "symbol": "GOOGL"
    }
    ```
-   **Success Response (201 Created):** Empty body.
-   **Error Response (409 Conflict):** If the stock is already in the watchlist.
-   **Function:** `add_to_watchlist(user_id: int, symbol: str) -> bool`

### 2.5. Remove from Watchlist

-   **Endpoint:** `DELETE /api/watchlist/<string:symbol>`
-   **Description:** Removes a stock from the authenticated user's watchlist.
-   **Authentication:** Required.
-   **URL Parameters:**
    -   `symbol` (str): The stock ticker symbol to remove.
-   **Success Response (204 No Content):** Empty body.
-   **Error Response (404 Not Found):** If the stock is not in the user's watchlist.
-   **Function:** `remove_from_watchlist(user_id: int, symbol: str) -> bool`

---

## 3. Core Backend Logic

### 3.1. Class: `PredictionCache`

A class to manage caching of prediction results to improve API response times. Could be implemented with Redis or a similar in-memory store.

#### Methods

-   `get(self, key: str) -> dict | None`
-   `set(self, key: str, value: dict, ttl: int)`

### 3.2. Scheduled Task: `DailyPredictionJob`

A daily scheduled job (e.g., using `cron` or a library like `APScheduler`) that runs the entire data ingestion, processing, and prediction pipeline for all relevant stocks before the market opens.

-   **Function:** `run_daily_predictions()`
    -   **Description:**
        1.  Get the list of all stocks tracked by users' watchlists.
        2.  Run the full `run_ingestion_pipeline`.
        3.  Run the `run_processing_pipeline`.
        4.  For each stock, load the trained model and generate the new prediction using `PredictionModel.predict()`.
        5.  Store the results in the database and update the `PredictionCache`.